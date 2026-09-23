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
      the amplitude.
A date is null when the series has no data there (clouds beyond the gap limit), or when
the season runs past the edge of the covered period; `start_truncated` and
`end_truncated` mark the latter. Seasons are never dropped, so gaps stay visible.

Output: data/gold/sentinel/<aoi-slug>_seasons.parquet, one row per cell per season, with
the cell's AOI unit (e.g. its desa).
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from jotosanur_agri.pipeline import save
from jotosanur_agri.pipeline.aoi import slugify
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

PEAK_MIN = 0.6
MIN_SEASON_GAP_DAYS = 60
LOOKBACK_DAYS = 120
SOS_FRAC = 0.2
EOS_FRAC = 0.5
FLOOD_BEFORE_DAYS = 45
FLOOD_AFTER_DAYS = 20

SEASON_SCHEMA = {
    "cell_id": pl.Int64,
    "season": pl.Int32,
    "flood_date": pl.Date,
    "flood_vh_db": pl.Float64,
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
    first_obs, last_obs = dates[observed[0]], dates[observed[-1]]
    rows = []
    peaks = find_peaks(dates, ndvi)
    for season, p in enumerate(peaks, start=1):
        # Harvest must come before the next season's peak, or it belongs to that season
        stop = peaks[season] if season < len(peaks) else len(ndvi)
        peak_date = dates[p]
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
            idx = np.arange(len(ndvi))
            h = _first((idx > p) & (idx < stop) & (ndvi <= float(ndvi[p]) - EOS_FRAC * amp))
            # A null run between peak and the drop means the drop date is unknown
            if h is not None and np.isfinite(ndvi[p:h]).all():
                row["harvest_date"] = dates[h]
            elif h is None and stop == len(ndvi):
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


def run_gold_sentinel(aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data") -> dict[str, Any]:
    """Detect seasons for an AOI from its silver table.

    Returns:
        Season and cell counts, completeness of each date and the output path.
    """
    slug = slugify(aoi_spec)
    silver = pl.read_parquet(Path(data_dir) / "silver" / "sentinel" / f"{slug}.parquet")
    cells = pl.read_parquet(Path(data_dir) / "bronze" / "sentinel" / slug / "cells.parquet")
    gold = build_gold(silver).join(cells.select("cell_id", "unit"), on="cell_id", how="left")
    return {
        "seasons": gold.height,
        "cells": gold["cell_id"].n_unique(),
        "complete": {
            c: round(1 - gold[c].null_count() / max(gold.height, 1), 2)
            for c in ("flood_date", "greenup_date", "harvest_date")
        },
        "path": save(gold, Path(data_dir) / "gold" / "sentinel" / f"{slug}_seasons.parquet"),
    }


if __name__ == "__main__":
    print(run_gold_sentinel(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI))
