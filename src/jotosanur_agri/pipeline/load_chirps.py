"""CHIRPS v3.0 monthly rainfall per unit of an AOI (bronze and silver).

Source: Climate Hazards Center, UCSB. CHIRPS v3.0 global monthly (final, not prelim),
0.05 deg (~5.5 km), 1981-now, public domain. Final data for a month is typically
complete in the third week of the following month.

Each monthly file is a Cloud-Optimized GeoTIFF, so only the tiles over the AOI are
range-read over HTTP. The raster is warped onto the AOI's 10 m Sentinel grid and
averaged over each unit's monitored cells, so a desa spanning two CHIRPS pixels gets
their area-weighted mean.

Incremental batch: the bronze parquet is the cache. A run fetches months not yet in
bronze, plus the last `REFETCH_LAST` months in case CHC revised them; --refresh
refetches everything.

Outputs:
    - data/bronze/chirps/<aoi-slug>_monthly.parquet: unit x month, mm as read.
    - data/silver/chirps/<aoi-slug>_monthly.parquet: plus days in month, mm/day, the
      1991-2020 normal and anomaly.
    - data/silver/chirps/<aoi-slug>_annual.parquet: yearly totals (complete years only).
Usage: `python -m jotosanur_agri.pipeline.load_chirps [AOI] [--refresh]`.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from jotosanur_agri.pipeline import save
from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI, Grid, cell_ids, make_grid, read_to_grid

BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/cogs"
FILE_RE = re.compile(r"chirps-v3\.0\.(\d{4})\.(\d{2})\.cog")

NORMAL_YEARS = (1991, 2020)  # WMO standard normal period
REFETCH_LAST = 2
WORKERS = 4

BRONZE_SCHEMA = {"unit": pl.Utf8, "year": pl.Int64, "month": pl.Int64, "precip_mm": pl.Float64, "fetched_on": pl.Utf8}


def list_months() -> list[tuple[int, int]]:
    """List the (year, month) pairs published on the CHIRPS server."""
    with urllib.request.urlopen(f"{BASE_URL}/", timeout=60) as resp:
        html = resp.read().decode()
    return sorted({(int(y), int(m)) for y, m in FILE_RE.findall(html)})


def fetch_month(year: int, month: int, grid: Grid, unit_px: np.ndarray, names: list[str]) -> list[dict[str, Any]]:
    """Mean rainfall per unit for one month.

    Args:
        year: Year.
        month: Month.
        grid: AOI grid.
        unit_px: 1-based unit number per pixel, 0 outside the monitored cells.
        names: Unit names, in unit-number order.

    Returns:
        One bronze row per unit; `precip_mm` is None when every pixel is no-data.
    """
    values = read_to_grid(f"/vsicurl/{BASE_URL}/chirps-v3.0.{year}.{month:02d}.cog", grid)
    # Ocean/no-data pixels are negative (-9999)
    ok = (unit_px > 0) & np.isfinite(values) & (values >= 0)
    total = np.bincount(unit_px[ok], weights=values[ok], minlength=len(names) + 1)
    count = np.bincount(unit_px[ok], minlength=len(names) + 1)
    fetched_on = date.today().isoformat()
    return [
        {
            "unit": name,
            "year": year,
            "month": month,
            "precip_mm": float(total[k] / count[k]) if count[k] else None,
            "fetched_on": fetched_on,
        }
        for k, name in enumerate(names, start=1)
    ]


def load_bronze(
    bronze_path: Path, grid: Grid, unit_px: np.ndarray, names: list[str], refresh: bool = False
) -> pl.DataFrame:
    """Return the full bronze table, fetching only months missing from the cache.

    The last `REFETCH_LAST` published months are always refetched, since CHC may
    revise them.

    Args:
        bronze_path: Cached bronze parquet.
        grid: AOI grid.
        unit_px: 1-based unit number per pixel, 0 outside the monitored cells.
        names: Unit names, in unit-number order.
        refresh: Ignore the cache and refetch every month.

    Returns:
        Bronze rows sorted by unit, year and month.
    """
    available = list_months()
    cached = pl.DataFrame(schema=BRONZE_SCHEMA)
    if bronze_path.exists() and not refresh:
        stale = pl.DataFrame(available[-REFETCH_LAST:], schema=["year", "month"], orient="row")
        cached = pl.read_parquet(bronze_path).join(stale, on=["year", "month"], how="anti")
    done = set(cached.select("year", "month").unique().iter_rows())
    todo = [ym for ym in available if ym not in done]

    rows: list[dict[str, Any]] = []
    if todo:
        print(f"[chirps] fetching {len(todo)} months ({todo[0]} .. {todo[-1]})")
        with ThreadPoolExecutor(WORKERS) as pool:
            for batch in pool.map(lambda ym: fetch_month(ym[0], ym[1], grid, unit_px, names), todo):
                rows.extend(batch)
    fresh = pl.DataFrame(rows, schema=BRONZE_SCHEMA)
    return pl.concat([cached, fresh]).sort("unit", "year", "month")


def to_silver(bronze: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Derive the monthly series with 1991-2020 normals and anomalies, and annual totals.

    Returns:
        (monthly, annual). Annual keeps complete years only; a partial year would
        understate the total.
    """
    monthly = bronze.with_columns(
        pl.date(pl.col("year"), pl.col("month"), 1).dt.month_end().dt.day().alias("n_days"),
    ).with_columns((pl.col("precip_mm") / pl.col("n_days")).alias("mm_per_day"))

    lo, hi = NORMAL_YEARS
    normal = (
        monthly.filter(pl.col("year").is_between(lo, hi))
        .group_by("unit", "month")
        .agg(pl.col("precip_mm").mean().alias("normal_mm"))
    )
    monthly = (
        monthly.join(normal, on=["unit", "month"], how="left")
        .with_columns(
            (pl.col("precip_mm") - pl.col("normal_mm")).alias("anomaly_mm"),
            pl.when(pl.col("normal_mm") > 0)
            .then((pl.col("precip_mm") / pl.col("normal_mm") - 1) * 100)
            .alias("anomaly_pct"),
        )
        .select("unit", "year", "month", "n_days", "precip_mm", "mm_per_day", "normal_mm", "anomaly_mm", "anomaly_pct")
        .sort("unit", "year", "month")
    )
    annual = (
        monthly.group_by("unit", "year")
        .agg(
            pl.col("precip_mm").sum().alias("total_precip_mm"),
            pl.col("precip_mm").is_not_null().sum().alias("n_months"),
        )
        .filter(pl.col("n_months") == 12)
        .drop("n_months")
        .sort("unit", "year")
    )
    return monthly, annual


def run_chirps_pipeline(
    aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data", refresh: bool = False
) -> dict[str, Any]:
    """Update bronze for an AOI and write the silver monthly and annual tables.

    Returns:
        Row counts, null count, covered range and output paths.
    """
    aoi = resolve(aoi_spec)
    grid, units = make_grid(aoi)
    cells = pl.read_parquet(Path(data_dir) / "bronze" / "sentinel" / aoi.slug / "cells.parquet")
    monitored = np.isin(cell_ids(grid, np.ones(grid.shape, dtype=bool)), cells["cell_id"].to_numpy())
    unit_px = np.where(monitored, units, 0)
    names = [name for name, _ in aoi.units]

    bronze_path = Path(data_dir) / "bronze" / "chirps" / f"{aoi.slug}_monthly.parquet"
    bronze = load_bronze(bronze_path, grid, unit_px, names, refresh=refresh)
    save(bronze, bronze_path)
    monthly, annual = to_silver(bronze)

    silver_dir = Path(data_dir) / "silver" / "chirps"
    first, last = monthly.row(0, named=True), monthly.row(-1, named=True)
    return {
        "units": monthly["unit"].n_unique(),
        "rows_bronze": bronze.height,
        "rows_silver_annual": annual.height,
        "null_values": monthly["precip_mm"].null_count(),
        "range": f"{first['year']}-{first['month']:02d}..{last['year']}-{last['month']:02d}",
        "bronze_path": str(bronze_path),
        "silver_monthly_path": save(monthly, silver_dir / f"{aoi.slug}_monthly.parquet"),
        "silver_annual_path": save(annual, silver_dir / f"{aoi.slug}_annual.parquet"),
    }


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--refresh"]
    print(run_chirps_pipeline(args[0] if args else DEFAULT_AOI, refresh="--refresh" in sys.argv))
