# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Cleaned per-cell S1/S2 time series from the monthly bronze files.

Bronze has irregular dates, cloudy Sentinel-2 rows and two Sentinel-1 viewing
geometries. Silver puts every cell on one 5-day calendar:
    1. S2: keep rows whose cell is at least `MIN_CLEAR` cloud-free, then drop
       single-date NDVI dips (haze the scene classification missed).
    2. S1: remove each orbit direction's per-cell offset, so ascending and descending
       passes do not zig-zag.
    3. Interpolate each sensor linearly onto the 5-day grid, only across gaps up to
       `MAX_GAP_DAYS`. Longer gaps stay null rather than invented.
    4. Smooth with a centred rolling median over 3 steps (15 days).
    5. Add the VH-VV difference (dB, the VH/VV ratio) and a water flag (LSWI > NDVI,
       standing water such as flooded paddy at transplanting).

Silver is rebuilt from all bronze months each run, which keeps it consistent when a
month is reprocessed. Cells are processed in batches, so a kabupaten fits in memory.

Output: data/silver/sentinel/<aoi-slug>.parquet, one row per cell per 5-day step.
"""

from __future__ import annotations

import sys
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Any

import polars as pl

from tikungcrops.pipeline.aoi import resolve
from tikungcrops.pipeline.load_sentinel import DEFAULT_AOI

STEP_DAYS = 5
MAX_GAP_DAYS = 30
MIN_CLEAR = 0.6
# NDVI drop below both neighbours that marks an isolated haze dip
SPIKE_NDVI = 0.15
SMOOTH_STEPS = 3
# cells per batch, so a whole kabupaten fits in memory (Tikung is a single batch)
BATCH_CELLS = 5_000

S2_VARS = ["ndvi", "lswi"]
S1_VARS = ["vh_db", "vv_db"]


def clean_s2(bronze: pl.DataFrame) -> pl.DataFrame:
    """Clear-enough Sentinel-2 rows without isolated NDVI dips."""
    s2 = (
        bronze.filter((pl.col("sensor") == "S2") & (pl.col("clear_frac") >= MIN_CLEAR) & pl.col("ndvi").is_not_null())
        .select("cell_id", "date", *S2_VARS)
        .sort("cell_id", "date")
    )
    prev = pl.col("ndvi").shift(1).over("cell_id")
    nxt = pl.col("ndvi").shift(-1).over("cell_id")
    is_dip = (pl.col("ndvi") < prev - SPIKE_NDVI) & (pl.col("ndvi") < nxt - SPIKE_NDVI)
    return s2.filter(~is_dip.fill_null(False))


def clean_s1(bronze: pl.DataFrame) -> pl.DataFrame:
    """Sentinel-1 rows with each orbit direction's per-cell mean offset removed."""
    s1 = bronze.filter((pl.col("sensor") == "S1") & pl.col("vh_db").is_not_null()).select(
        "cell_id", "date", "orbit", *S1_VARS
    )
    # shift each orbit's per-cell mean onto the cell's overall mean
    return (
        s1.with_columns(
            pl.col(v) - pl.col(v).mean().over("cell_id", "orbit") + pl.col(v).mean().over("cell_id") for v in S1_VARS
        )
        .drop("orbit")
        .sort("cell_id", "date")
    )


def time_grid(cells: pl.Series, start: Any, end: Any) -> pl.DataFrame:
    """Every cell x every `STEP_DAYS` step from `start` to `end`."""
    dates = pl.date_range(start, end, timedelta(days=STEP_DAYS), eager=True).alias("date")
    return pl.DataFrame({"cell_id": cells.unique().sort()}).join(dates.to_frame(), how="cross")


def interpolate(grid: pl.DataFrame, obs: pl.DataFrame, variables: list[str], flag: str) -> pl.DataFrame:
    """Linearly interpolate `obs` onto `grid` per cell across gaps of at most `MAX_GAP_DAYS`.

    Adds `flag`, True where a grid date has no observation of its own.
    """
    # join_asof needs both sides sorted on the asof key
    grid, obs = grid.sort("date"), obs.sort("date").rename({"date": "obs_date"})
    before = grid.join_asof(
        obs.rename({v: f"{v}_a" for v in variables} | {"obs_date": "date_a"}),
        left_on="date",
        right_on="date_a",
        by="cell_id",
        strategy="backward",
        check_sortedness=False,
    )
    both = before.join_asof(
        obs.rename({v: f"{v}_b" for v in variables} | {"obs_date": "date_b"}),
        left_on="date",
        right_on="date_b",
        by="cell_id",
        strategy="forward",
        check_sortedness=False,
    )
    span = (pl.col("date_b") - pl.col("date_a")).dt.total_days()
    weight = pl.when(span > 0).then((pl.col("date") - pl.col("date_a")).dt.total_days() / span).otherwise(0.0)
    usable = pl.col("date_a").is_not_null() & pl.col("date_b").is_not_null() & (span <= MAX_GAP_DAYS)
    return both.select(
        "cell_id",
        "date",
        *[
            pl.when(usable).then(pl.col(f"{v}_a") + weight * (pl.col(f"{v}_b") - pl.col(f"{v}_a"))).alias(v)
            for v in variables
        ],
        (pl.col("date_a") != pl.col("date")).fill_null(True).alias(flag),
    )


def build_silver(bronze: pl.DataFrame, start: Any = None, end: Any = None) -> pl.DataFrame:
    """Clean, align, gap-fill and smooth bronze into the 5-day silver table.

    `start` and `end` fix the 5-day calendar, so that cell batches share one grid.
    By default they come from `bronze` itself.
    """
    s2, s1 = clean_s2(bronze), clean_s1(bronze)
    if start is None or end is None:
        start, end = bronze.select(
            pl.col("date").min().dt.month_start().alias("start"), pl.col("date").max().alias("end")
        ).row(0)
    grid = time_grid(bronze["cell_id"], start, end)

    silver = interpolate(grid, s2, S2_VARS, "s2_interpolated").join(
        interpolate(grid, s1, S1_VARS, "s1_interpolated"), on=["cell_id", "date"]
    )
    smooth = [
        pl.col(v).rolling_median(SMOOTH_STEPS, min_samples=1, center=True).over("cell_id").alias(v)
        for v in S2_VARS + S1_VARS
    ]
    return (
        silver.sort("cell_id", "date")
        # rolling_median would fill gaps next to data, keep null where interpolation gave up
        .with_columns(
            pl.when(pl.col(v).is_not_null()).then(expr) for v, expr in zip(S2_VARS + S1_VARS, smooth, strict=True)
        )
        .with_columns(
            (pl.col("vh_db") - pl.col("vv_db")).alias("vh_vv_db"),
            (pl.col("lswi") > pl.col("ndvi")).alias("water"),
        )
    )


def cell_batches(cell_ids: pl.Series, size: int) -> list[tuple[Any, Any]]:
    """Inclusive (first, last) cell_id ranges of at most `size` cells, in cell order."""
    ids = cell_ids.unique().sort()
    return [(ids[i], ids[min(i + size, len(ids)) - 1]) for i in range(0, len(ids), size)]


def run_silver_sentinel(aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data") -> dict[str, Any]:
    """Rebuild the silver table for an AOI from all its bronze months, `BATCH_CELLS` cells at a time.

    Returns:
        Row and cell counts, the covered range, null shares and the output path.

    Raises:
        ValueError: If the AOI has no bronze months or no NDVI at all (e.g. only months
            before Sentinel-2 L2A coverage starts).
    """
    slug = resolve(aoi_spec).slug
    months = sorted((Path(data_dir) / "bronze" / "sentinel" / slug).glob("[0-9]*.parquet"))
    if not months:
        raise ValueError(f"{slug}: no bronze months, run load_sentinel first")
    bronze = pl.scan_parquet(months)
    start, end, has_ndvi = (
        bronze.select(
            pl.col("date").min().dt.month_start().alias("start"),
            pl.col("date").max().alias("end"),
            pl.col("ndvi").is_not_null().any().alias("has_ndvi"),
        )
        .collect()
        .row(0)
    )
    if not has_ndvi:
        raise ValueError(f"{slug}: bronze has no Sentinel-2 NDVI, seasons cannot be detected from radar alone")
    out = Path(data_dir) / "silver" / "sentinel" / f"{slug}.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    cell_ids = bronze.select(pl.col("cell_id").unique()).collect()["cell_id"]
    with tempfile.TemporaryDirectory(dir=out.parent) as tmp:
        parts = []
        for i, (lo, hi) in enumerate(cell_batches(cell_ids, BATCH_CELLS)):
            batch = bronze.filter(pl.col("cell_id").is_between(lo, hi)).collect()
            parts.append(Path(tmp) / f"{i:04d}.parquet")
            build_silver(batch, start, end).write_parquet(parts[-1])
        # batches are disjoint cell ranges in order, so the joined file stays sorted by cell and date
        pl.scan_parquet(parts).sink_parquet(out)
    stats = (
        pl.scan_parquet(out)
        .select(
            pl.len().alias("rows"),
            pl.col("cell_id").n_unique().alias("cells"),
            pl.col("date").min().alias("first"),
            pl.col("date").max().alias("last"),
            pl.col("ndvi").null_count().alias("ndvi_null"),
            pl.col("vh_db").null_count().alias("vh_null"),
        )
        .collect()
        .row(0, named=True)
    )
    return {
        "rows": stats["rows"],
        "cells": stats["cells"],
        "range": f"{stats['first']}..{stats['last']}",
        "ndvi_null_share": round(stats["ndvi_null"] / stats["rows"], 3),
        "vh_null_share": round(stats["vh_null"] / stats["rows"], 3),
        "path": str(out),
    }


if __name__ == "__main__":
    print(run_silver_sentinel(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI))
