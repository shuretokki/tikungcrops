"""Gold pipeline: rice seasons per cell (flooding, green-up, peak, harvest) from the silver time series.

For every cell, each NDVI peak above `PEAK_MIN` that is at least `MIN_SEASON_GAP_DAYS`
from a higher neighbouring peak is one season. Around it:
    - base: lowest NDVI in the `LOOKBACK_DAYS` before the peak (bare or flooded field);
    - green-up: first date after the base where NDVI reaches base + `SOS_FRAC` of the
      amplitude (peak - base), a standard threshold method for start of season;
    - flooding: lowest VH between `FLOOD_BEFORE_DAYS` before and `FLOOD_AFTER_DAYS` after
      green-up. Standing water scatters radar away, so transplanting shows as a VH
      minimum even under clouds;
    - harvest: first date after the peak where NDVI falls below peak - `EOS_FRAC` of
      the amplitude;
    - rice: the field went under standing water around planting, i.e. the flooding VH is
      at most `RICE_FLOOD_VH_DB`, or at least `RICE_VH_DROP_DB` below the field's median
      VH `PRE_SEASON_DAYS` before green-up. Wet-season fields are already wet before
      planting (low VH, little drop); dry-season fields start dry after the previous
      harvest (higher VH, clear drop), so either condition marks transplanted paddy.
      Seasons failing both are other crops (maize, pulses) or dry-seeded fields.
A date is null when the series has no data there (clouds beyond the gap limit), or when
the season runs past the edge of a covered period; `start_truncated` and
`end_truncated` mark the latter. A stretch of `DATA_GAP_DAYS` without any Sentinel-1 or
Sentinel-2 value (e.g. months never extracted) splits the series into separate periods.
Seasons are never dropped, so gaps stay visible.

Tuned for transplanted lowland rice in East Java; elsewhere the output runs but needs
checking before use:
    - the rice thresholds come from Tikung 2020 radar; dry-seeded or rainfed rice, other
      soils and incidence angles shift VH;
    - MT1-MT3 split seasons by NDVI peak month (Jan-Apr, May-Aug, Sep-Dec), which follows
      the Javanese wet-season calendar; temperate regions or other monsoon timings
      need their own split;
    - `PEAK_MIN` and the season gap assume dense irrigated crops two to three times a year.
Sentinel-2 L2A is sparse before late 2017, so earlier seasons are mostly undetectable.

Outputs: data/gold/sentinel/<aoi-slug>_seasons.parquet, one row per cell per season, with
the cell's AOI unit (e.g. its desa) and, after `load_paddy`, its LBS paddy share; and
<aoi-slug>_units.parquet, per unit x year x planting season (see `summarize_units`).
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
# Rice thresholds, chosen from the Tikung 2020 VH distributions (wet season median -18.4 dB
# at flooding; dry season median drop 1.8 dB); not validated on a second BPS year yet.
RICE_FLOOD_VH_DB = -17.0
RICE_VH_DROP_DB = 1.5
PRE_SEASON_DAYS = (75, 30)
# Longer than any cloud gap: S1 sees through clouds, so this only happens without bronze
DATA_GAP_DAYS = 60

SEASON_SCHEMA = {
    "cell_id": pl.Int64,
    "season": pl.Int32,
    "flood_date": pl.Date,
    "flood_vh_db": pl.Float64,
    "vh_drop_db": pl.Float64,
    "rice": pl.Boolean,
    "greenup_date": pl.Date,
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


def seasons_for_cell(dates: np.ndarray, ndvi: np.ndarray, vh: np.ndarray) -> list[dict[str, Any]]:
    """Seasons of one cell from its 5-day NDVI and VH series (dates ascending)."""
    observed = np.flatnonzero(np.isfinite(ndvi))
    if not observed.size:
        return []
    first_ndvi, last_ndvi = dates[observed[0]], dates[observed[-1]]
    # Covered periods: runs of dates with any sensor value, split at long gaps
    any_obs = dates[np.isfinite(ndvi) | np.isfinite(vh)]
    breaks = np.flatnonzero(np.diff(any_obs) > timedelta(days=DATA_GAP_DAYS))
    starts, ends = any_obs[np.r_[0, breaks + 1]], any_obs[np.r_[breaks, len(any_obs) - 1]]
    rows = []
    peaks = find_peaks(dates, ndvi)
    for season, p in enumerate(peaks, start=1):
        # Harvest must come before the next season's peak, or it belongs to that season
        stop = peaks[season] if season < len(peaks) else len(ndvi)
        peak_date = dates[p]
        period = int(np.searchsorted(starts, peak_date, side="right")) - 1
        first_obs, last_obs = max(starts[period], first_ndvi), min(ends[period], last_ndvi)
        back = (dates >= peak_date - timedelta(days=LOOKBACK_DAYS)) & (dates < peak_date) & np.isfinite(ndvi)
        # The look-back reaches before the first observation: the real base may be missing
        start_truncated = peak_date - timedelta(days=LOOKBACK_DAYS) < first_obs
        row: dict[str, Any] = {
            "season": season,
            "peak_date": peak_date,
            "peak_ndvi": float(ndvi[p]),
            "base_ndvi": None,
            "greenup_date": None,
            "flood_date": None,
            "flood_vh_db": None,
            "vh_drop_db": None,
            "rice": None,
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
                window = (
                    (dates >= dates[g] - timedelta(days=FLOOD_BEFORE_DAYS))
                    & (dates <= dates[g] + timedelta(days=FLOOD_AFTER_DAYS))
                    & np.isfinite(vh)
                )
                if window.any():
                    f = int(np.flatnonzero(window)[np.argmin(vh[window])])
                    row["flood_date"], row["flood_vh_db"] = dates[f], float(vh[f])
                    far, near = (dates[g] - timedelta(days=d) for d in PRE_SEASON_DAYS)
                    pre = (dates >= far) & (dates <= near) & np.isfinite(vh)
                    drop = float(np.median(vh[pre])) - float(vh[f]) if pre.any() else None
                    row["vh_drop_db"] = drop
                    row["rice"] = float(vh[f]) <= RICE_FLOOD_VH_DB or (drop is not None and drop >= RICE_VH_DROP_DB)
            idx = np.arange(len(ndvi))
            h = _first((idx > p) & (idx < stop) & (ndvi <= float(ndvi[p]) - EOS_FRAC * amp))
            # A null run between peak and the drop means the drop date is unknown
            if h is not None and np.isfinite(ndvi[p:h]).all():
                row["harvest_date"] = dates[h]
            else:
                row["end_truncated"] = last_obs - peak_date < timedelta(days=LOOKBACK_DAYS)
        rows.append(row)
    return rows


def build_gold(silver: pl.DataFrame) -> pl.DataFrame:
    """One row per cell per detected season."""
    rows: list[dict[str, Any]] = []
    for (cell_id,), cell in silver.sort("date").group_by("cell_id", maintain_order=True):
        dates: np.ndarray = np.array(cell["date"].to_list(), dtype=object)
        ndvi = cell["ndvi"].to_numpy().astype(float)
        vh = cell["vh_db"].to_numpy().astype(float)
        rows += [{"cell_id": cell_id, **r} for r in seasons_for_cell(dates, ndvi, vh)]
    return pl.DataFrame(rows, schema=SEASON_SCHEMA).with_columns(
        (pl.col("harvest_date") - pl.col("greenup_date")).dt.total_days().alias("greenup_to_harvest_days"),
        (pl.col("harvest_date") - pl.col("flood_date")).dt.total_days().alias("flood_to_harvest_days"),
    )


def _date_quantile(col: str, q: float) -> pl.Expr:
    return pl.col(col).cast(pl.Int32).quantile(q).round().cast(pl.Int32).cast(pl.Date)


def summarize_units(gold: pl.DataFrame) -> pl.DataFrame:
    """Per unit, year and planting season (MT1-MT3 by peak month): area and date windows.

    Seasons cut by the edge of the covered period are left out, since their dates are
    incomplete. Areas weight each cell by its paddy share when known, else count it as
    1 ha. Date windows are the 10th, 50th and 90th percentile across cells.
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
    # Paddy share from the LBS map, when `load_paddy` has been run for this AOI
    if (cells_dir / "paddy.parquet").exists():
        cells = cells.join(pl.read_parquet(cells_dir / "paddy.parquet"), on="cell_id", how="left")
    gold = build_gold(silver).join(cells, on="cell_id", how="left")
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
    }


if __name__ == "__main__":
    print(run_gold_sentinel(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI))
