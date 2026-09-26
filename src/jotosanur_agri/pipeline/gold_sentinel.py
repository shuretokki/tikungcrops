"""Rice seasons per cell (flooding, green-up, peak, harvest) from the silver time series.

For every cell, each NDVI peak above `PEAK_MIN` that is at least `MIN_SEASON_GAP_DAYS`
from a higher neighbouring peak is one season. Around it:
    - base: lowest NDVI in the `LOOKBACK_DAYS` before the peak (bare or flooded field).
    - green-up: first date after the base where NDVI reaches base + `SOS_FRAC` of the
      amplitude (peak - base), a standard threshold method for start of season.
    - flooding: lowest VH between `FLOOD_BEFORE_DAYS` before and `FLOOD_AFTER_DAYS` after
      green-up. Standing water scatters radar away, so transplanting shows as a VH
      minimum even under clouds.
    - harvest: first date after the peak where NDVI falls below peak - `EOS_FRAC` of
      the amplitude.
    - greenup_reliable: the green-up was actually seen, i.e. the base is bare or flooded
      (NDVI at most `RELIABLE_BASE_NDVI`) and green-up falls `RELIABLE_GREENUP_DAYS`
      before the peak. Wet-season clouds often hide the bare phase, so the base lands on
      a half-green field (green-up days before the peak) or on the previous crop (at the
      look-back limit), and dates derived from green-up (flooding, season length) are then
      wrong. In Tikung 19-26% of seasons pass, and those give plausible rice seasons
      (flooding to harvest ~115 days wet season, ~80 dry).
    - rice: the field went under standing water around planting, i.e. the flooding VH is
      at most `RICE_FLOOD_VH_DB`, or at least `RICE_VH_DROP_DB` below the field's median
      VH `PRE_SEASON_DAYS` before green-up. Wet-season fields are already wet before
      planting (low VH, little drop). Dry-season fields start dry after the previous
      harvest (higher VH, clear drop), so either condition marks transplanted paddy.
      Seasons failing both are other crops (maize, pulses) or dry-seeded fields. With
      fewer than `MIN_FLOOD_PASSES` Sentinel-1 passes in the flooding window (e.g. Java
      in early 2023, when Sentinel-1A covered it only every few weeks) the brief flooding
      dip is easily missed, so rice is left unknown rather than set to False.
A date is null when the series has no data there (clouds beyond the gap limit), or when
the season runs past the edge of a covered period. `start_truncated` and
`end_truncated` mark the latter. A stretch of `DATA_GAP_DAYS` without any Sentinel-1 or
Sentinel-2 value (e.g. months never extracted) splits the series into separate periods.
Seasons are never dropped, so gaps stay visible.

Tuned for transplanted lowland rice in East Java. Elsewhere the output runs but needs
checking before use:
    - the rice thresholds come from Tikung 2020 radar. Dry-seeded or rainfed rice, other
      soils and incidence angles shift VH. Even in Tikung, dry-season (MT2) rice is
      under-counted in wet dry seasons: rain raises VH across the landscape and fields
      are already wet before planting, so neither condition fires (2022 and 2025: 25% of
      MT2 seasons rice vs 52-66% in dry years, rain vs MT2 rice share r = -0.84).
    - MT1-MT3 split seasons by NDVI peak month (Jan-Apr, May-Aug, Sep-Dec), which follows
      the Javanese wet-season calendar. Temperate regions or other monsoon timings
      need their own split.
    - `PEAK_MIN` and the season gap assume dense irrigated crops two to three times a year.
Sentinel-2 L2A is sparse before late 2017, so earlier seasons are mostly undetectable.

Each cell also gets its state at the end of the series (`current_season`), for
forecasting seasons still running: `peaked` (last peak seen, no harvest yet), `planted`
(since the last harvest the field went bare or flooded, NDVI at most
`RELIABLE_BASE_NDVI`, then rose by `GREENUP_RISE`, or its NDVI is still at its highest
at the series end), `fallow` (bare, no rise yet) or `unknown` (no bare phase seen,
e.g. clouds). Green-up of a running season uses a fixed
rise because its amplitude is not known before the peak. `GREENUP_RISE` is `SOS_FRAC`
of a typical amplitude (0.2 x ~0.6).

Outputs in data/gold/sentinel/:
    - <aoi-slug>_seasons.parquet, one row per cell per season, with the cell's AOI unit
      (e.g. its desa) and, after `load_paddy`, its LBS paddy share.
    - <aoi-slug>_units.parquet, per unit x year x planting season (see `summarize_units`).
    - <aoi-slug>_current.parquet, one row per cell with its state at the end of the series.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from jotosanur_agri.pipeline import save
from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

PEAK_MIN = 0.6
MIN_SEASON_GAP_DAYS = 60
LOOKBACK_DAYS = 120
SOS_FRAC = 0.2
EOS_FRAC = 0.5
FLOOD_BEFORE_DAYS = 45
FLOOD_AFTER_DAYS = 20
# rice thresholds, chosen from the Tikung 2020 VH distributions (wet season median -18.4 dB
# at flooding, dry season median drop 1.8 dB), not validated on a second BPS year yet.
RICE_FLOOD_VH_DB = -17.0
RICE_VH_DROP_DB = 1.5
PRE_SEASON_DAYS = (75, 30)
# longer than any cloud gap: S1 sees through clouds, so this only happens without bronze
DATA_GAP_DAYS = 60
# Tikung: 1 pass in the window -> 1% of seasons rice, 2 -> 23%, 4-8 -> 36-66%
MIN_FLOOD_PASSES = 3
RELIABLE_BASE_NDVI = 0.3
RELIABLE_GREENUP_DAYS = (20, 105)
GREENUP_RISE = 0.12
# NDVI fall after the last peak that confirms it as the season's peak
PEAK_CONFIRM_DROP = 0.05

CURRENT_SCHEMA = {
    "cell_id": pl.Int64,
    "as_of": pl.Date,
    "stage": pl.Utf8,
    "base_ndvi": pl.Float64,
    "greenup_date": pl.Date,
    "greenup_reliable": pl.Boolean,
    "flood_date": pl.Date,
    "flood_vh_db": pl.Float64,
    "vh_drop_db": pl.Float64,
    "rice": pl.Boolean,
    "flood_passes": pl.Int32,
    "peak_date": pl.Date,
    "peak_ndvi": pl.Float64,
}

SEASON_SCHEMA = {
    "cell_id": pl.Int64,
    "season": pl.Int32,
    "flood_date": pl.Date,
    "flood_vh_db": pl.Float64,
    "vh_drop_db": pl.Float64,
    "rice": pl.Boolean,
    "flood_passes": pl.Int32,
    "greenup_date": pl.Date,
    "greenup_reliable": pl.Boolean,
    "peak_date": pl.Date,
    "peak_ndvi": pl.Float64,
    "harvest_date": pl.Date,
    "base_ndvi": pl.Float64,
    "start_truncated": pl.Boolean,
    "end_truncated": pl.Boolean,
}


def find_peaks(dates: np.ndarray, ndvi: np.ndarray) -> list[int]:
    """Indices of local NDVI maxima above `PEAK_MIN`, keeping the higher of any two closer than the season gap."""
    finite = np.where(np.isfinite(ndvi), ndvi, -np.inf)
    candidates = [
        i
        for i in range(len(ndvi))
        if finite[i] >= PEAK_MIN
        and (i == 0 or finite[i] > finite[i - 1])
        and (i == len(ndvi) - 1 or finite[i] >= finite[i + 1])
    ]
    kept: list[int] = []
    for i in sorted(candidates, key=lambda k: -finite[k]):
        if all(abs((dates[i] - dates[k]).days) >= MIN_SEASON_GAP_DAYS for k in kept):
            kept.append(i)
    return sorted(kept)


def _first(mask: np.ndarray) -> int | None:
    hits = np.flatnonzero(mask)
    return int(hits[0]) if hits.size else None


def _flooding(dates: np.ndarray, vh: np.ndarray, g: int, s1_dates: np.ndarray | None) -> dict[str, Any]:
    """Flooding date and VH around green-up index `g`, the VH drop, radar passes and rice flag."""
    out: dict[str, Any] = {}
    lo, hi = dates[g] - timedelta(days=FLOOD_BEFORE_DAYS), dates[g] + timedelta(days=FLOOD_AFTER_DAYS)
    window = (dates >= lo) & (dates <= hi) & np.isfinite(vh)
    if not window.any():
        return out
    f = int(np.flatnonzero(window)[np.argmin(vh[window])])
    out["flood_date"], out["flood_vh_db"] = dates[f], float(vh[f])
    far, near = (dates[g] - timedelta(days=d) for d in PRE_SEASON_DAYS)
    pre = (dates >= far) & (dates <= near) & np.isfinite(vh)
    drop = float(np.median(vh[pre])) - float(vh[f]) if pre.any() else None
    out["vh_drop_db"] = drop
    if s1_dates is not None:
        passes = int(np.searchsorted(s1_dates, hi, side="right") - np.searchsorted(s1_dates, lo))
        out["flood_passes"] = passes
    else:
        passes = MIN_FLOOD_PASSES
    if passes >= MIN_FLOOD_PASSES:
        out["rice"] = float(vh[f]) <= RICE_FLOOD_VH_DB or (drop is not None and drop >= RICE_VH_DROP_DB)
    return out


def current_season(
    dates: np.ndarray,
    ndvi: np.ndarray,
    vh: np.ndarray,
    seasons: list[dict[str, Any]],
    s1_dates: np.ndarray | None = None,
) -> dict[str, Any]:
    """State of one cell at the end of its series, given its detected `seasons`."""
    state: dict[str, Any] = {"as_of": dates[-1], "stage": "unknown"}
    last = seasons[-1] if seasons else None
    if last and last["harvest_date"] is None and last["end_truncated"]:
        # a crop still greening has its highest NDVI at the series end, which counts as a
        # peak, and only a later drop confirms it
        later = (dates > last["peak_date"]) & np.isfinite(ndvi)
        confirmed = bool((ndvi[later] <= last["peak_ndvi"] - PEAK_CONFIRM_DROP).any())
        if confirmed:
            keep = ("peak_date", "peak_ndvi", "base_ndvi", "greenup_date", "greenup_reliable", "flood_date")
            return {**state, "stage": "peaked", **{k: last[k] for k in keep}, **_flood_fields(last)}
        if last["greenup_date"] is None:
            return state
        keep = ("base_ndvi", "greenup_date", "greenup_reliable", "flood_date")
        return {**state, "stage": "planted", **{k: last[k] for k in keep}, **_flood_fields(last)}
    if last is None:
        after = dates >= dates[0]
    elif last["harvest_date"] is not None:
        after = dates > last["harvest_date"]
    else:
        # harvest hidden by clouds: start looking a season gap after the peak
        after = dates > last["peak_date"] + timedelta(days=MIN_SEASON_GAP_DAYS)
    seen = after & np.isfinite(ndvi)
    if not seen.any():
        return state
    b = int(np.flatnonzero(seen)[np.argmin(ndvi[seen])])
    base = float(ndvi[b])
    if base > RELIABLE_BASE_NDVI:
        return {**state, "base_ndvi": base}
    g = _first((np.arange(len(ndvi)) > b) & (ndvi >= base + GREENUP_RISE))
    if g is None:
        return {**state, "stage": "fallow", "base_ndvi": base}
    return {
        **state,
        "stage": "planted",
        "base_ndvi": base,
        "greenup_date": dates[g],
        "greenup_reliable": True,
        **_flooding(dates, vh, g, s1_dates),
    }


def _flood_fields(season: dict[str, Any]) -> dict[str, Any]:
    return {k: season[k] for k in ("flood_vh_db", "vh_drop_db", "rice", "flood_passes")}


def seasons_for_cell(
    dates: np.ndarray, ndvi: np.ndarray, vh: np.ndarray, s1_dates: np.ndarray | None = None
) -> list[dict[str, Any]]:
    """Seasons of one cell from its 5-day NDVI and VH series (dates ascending).

    `s1_dates` are the actual Sentinel-1 acquisition dates (sorted). The 5-day series is
    interpolated, so it cannot tell how many real passes a window had. Without them
    every window counts as well observed.
    """
    observed = np.flatnonzero(np.isfinite(ndvi))
    if not observed.size:
        return []
    first_ndvi, last_ndvi = dates[observed[0]], dates[observed[-1]]
    # covered periods: runs of dates with any sensor value, split at long gaps
    any_obs = dates[np.isfinite(ndvi) | np.isfinite(vh)]
    breaks = np.flatnonzero(np.diff(any_obs) > timedelta(days=DATA_GAP_DAYS))
    starts, ends = any_obs[np.r_[0, breaks + 1]], any_obs[np.r_[breaks, len(any_obs) - 1]]
    rows = []
    peaks = find_peaks(dates, ndvi)
    for season, p in enumerate(peaks, start=1):
        # harvest must come before the next season's peak, or it belongs to that season
        stop = peaks[season] if season < len(peaks) else len(ndvi)
        peak_date = dates[p]
        period = int(np.searchsorted(starts, peak_date, side="right")) - 1
        first_obs, last_obs = max(starts[period], first_ndvi), min(ends[period], last_ndvi)
        back = (dates >= peak_date - timedelta(days=LOOKBACK_DAYS)) & (dates < peak_date) & np.isfinite(ndvi)
        # the look-back reaches before the first observation: the real base may be missing
        start_truncated = peak_date - timedelta(days=LOOKBACK_DAYS) < first_obs
        row: dict[str, Any] = {
            "season": season,
            "peak_date": peak_date,
            "peak_ndvi": float(ndvi[p]),
            "base_ndvi": None,
            "greenup_date": None,
            "greenup_reliable": None,
            "flood_date": None,
            "flood_vh_db": None,
            "vh_drop_db": None,
            "rice": None,
            "flood_passes": None,
            "harvest_date": None,
            "start_truncated": start_truncated,
            "end_truncated": False,
        }
        if back.any():
            b = int(np.flatnonzero(back)[np.argmin(ndvi[back])])
            base = float(ndvi[b])
            amp = float(ndvi[p]) - base
            row["base_ndvi"] = base
            g = _first((np.arange(len(ndvi)) > b) & (np.arange(len(ndvi)) <= p) & (ndvi >= base + SOS_FRAC * amp))
            if g is not None and not start_truncated:
                row["greenup_date"] = dates[g]
                lead = (peak_date - dates[g]).days
                row["greenup_reliable"] = base <= RELIABLE_BASE_NDVI and (
                    RELIABLE_GREENUP_DAYS[0] <= lead < RELIABLE_GREENUP_DAYS[1]
                )
                row.update(_flooding(dates, vh, g, s1_dates))
            idx = np.arange(len(ndvi))
            h = _first((idx > p) & (idx < stop) & (ndvi <= float(ndvi[p]) - EOS_FRAC * amp))
            # a null run between peak and the drop means the drop date is unknown
            if h is not None and np.isfinite(ndvi[p:h]).all():
                row["harvest_date"] = dates[h]
            else:
                row["end_truncated"] = last_obs - peak_date < timedelta(days=LOOKBACK_DAYS)
        rows.append(row)
    return rows


def build_gold(silver: pl.DataFrame, s1_dates: list[Any] | None = None) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Seasons (one row per cell per detected season) and each cell's current state.

    `s1_dates` as in `seasons_for_cell`.
    """
    passes = np.array(sorted(s1_dates), dtype=object) if s1_dates is not None else None
    rows: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    for (cell_id,), cell in silver.sort("date").group_by("cell_id", maintain_order=True):
        dates: np.ndarray = np.array(cell["date"].to_list(), dtype=object)
        ndvi = cell["ndvi"].to_numpy().astype(float)
        vh = cell["vh_db"].to_numpy().astype(float)
        seasons = seasons_for_cell(dates, ndvi, vh, passes)
        rows += [{"cell_id": cell_id, **r} for r in seasons]
        current.append({"cell_id": cell_id, **current_season(dates, ndvi, vh, seasons, passes)})
    gold = pl.DataFrame(rows, schema=SEASON_SCHEMA).with_columns(
        (pl.col("harvest_date") - pl.col("greenup_date")).dt.total_days().alias("greenup_to_harvest_days"),
        (pl.col("harvest_date") - pl.col("flood_date")).dt.total_days().alias("flood_to_harvest_days"),
    )
    return gold, pl.DataFrame(current, schema=CURRENT_SCHEMA)


def _date_quantile(col: str, q: float) -> pl.Expr:
    return pl.col(col).cast(pl.Int32).quantile(q).round().cast(pl.Int32).cast(pl.Date)


def summarize_units(gold: pl.DataFrame) -> pl.DataFrame:
    """Per unit, year and planting season (MT1-MT3 by peak month): area and date windows.

    Seasons cut by the edge of the covered period are left out, since their dates are
    incomplete. Areas weight each cell by its paddy share when known, else count it as
    1 ha. `rice_unknown_ha` is the area whose rice flag could not be decided (too few
    radar passes or no radar in the flooding window). Date windows are the 10th, 50th
    and 90th percentile across cells.
    """
    weight = pl.col("paddy_frac").fill_null(0.0) if "paddy_frac" in gold.columns else pl.lit(1.0)
    month = pl.col("peak_date").dt.month()
    return (
        gold.filter(~pl.col("start_truncated") & ~pl.col("end_truncated"))
        .with_columns(
            weight.alias("w"),
            pl.col("peak_date").dt.year().alias("year"),
            pl.when(month <= 4)
            .then(pl.lit("MT1"))
            .when(month <= 8)
            .then(pl.lit("MT2"))
            .otherwise(pl.lit("MT3"))
            .alias("season"),
        )
        .group_by("unit", "year", "season")
        .agg(
            pl.len().alias("cells"),
            pl.col("w").sum().alias("area_ha"),
            (pl.col("w") * pl.col("rice").fill_null(False)).sum().alias("rice_area_ha"),
            (pl.col("w") * pl.col("rice").is_null()).sum().alias("rice_unknown_ha"),
            *[
                _date_quantile(col, q).alias(f"{prefix}_{name}")
                for col, prefix in (("flood_date", "flood"), ("harvest_date", "harvest"))
                for name, q in (("start", 0.1), ("median", 0.5), ("end", 0.9))
            ],
            pl.col("peak_ndvi").median().alias("peak_ndvi"),
        )
        .sort("unit", "year", "season")
    )


def run_gold_sentinel(aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data") -> dict[str, Any]:
    """Detect seasons for an AOI from its silver table, then summarise them per unit.

    Returns:
        Season, cell and unit-summary counts, completeness of each date and the output paths.
    """
    slug = resolve(aoi_spec).slug
    silver = pl.read_parquet(Path(data_dir) / "silver" / "sentinel" / f"{slug}.parquet")
    cells_dir = Path(data_dir) / "bronze" / "sentinel" / slug
    cells = pl.read_parquet(cells_dir / "cells.parquet").select("cell_id", "unit")
    # paddy share from the LBS map, when `load_paddy` has been run for this AOI
    if (cells_dir / "paddy.parquet").exists():
        cells = cells.join(pl.read_parquet(cells_dir / "paddy.parquet"), on="cell_id", how="left")
    s1_dates = (
        pl.scan_parquet(cells_dir / "[0-9]*.parquet")
        .filter(pl.col("sensor") == "S1")
        .select(pl.col("date").unique())
        .collect()["date"]
        .to_list()
    )
    gold, current = build_gold(silver, s1_dates)
    gold = gold.join(cells, on="cell_id", how="left")
    current = current.join(cells, on="cell_id", how="left")
    units = summarize_units(gold)
    gold_dir = Path(data_dir) / "gold" / "sentinel"
    return {
        "seasons": gold.height,
        "cells": gold["cell_id"].n_unique(),
        "unit_seasons": units.height,
        "complete": {
            c: round(1 - gold[c].null_count() / max(gold.height, 1), 2)
            for c in ("flood_date", "greenup_date", "harvest_date")
        },
        "path": save(gold, gold_dir / f"{slug}_seasons.parquet"),
        "units_path": save(units, gold_dir / f"{slug}_units.parquet"),
        "current": dict(current["stage"].value_counts().iter_rows()),
        "current_path": save(current, gold_dir / f"{slug}_current.parquet"),
    }


if __name__ == "__main__":
    print(run_gold_sentinel(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI))
