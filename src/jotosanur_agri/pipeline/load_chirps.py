"""CHIRPS v3.0 monthly rainfall per unit of an AOI (bronze and silver).

Source: Climate Hazards Center, UCSB. CHIRPS v3.0 global monthly (final, not prelim),
0.05 deg (~5.5 km), 1981-now, public domain. Final data for a month is typically
complete in the third week of the following month.

Each monthly file is a Cloud-Optimized GeoTIFF, so only the window over the AOI is
range-read over HTTP. The raster is sampled at the centre of every monitored 100 m cell
and averaged per unit, so a desa spanning two CHIRPS pixels gets their area-weighted
mean. CHIRPS covers 50S-50N only, so an AOI outside that band is rejected.

Incremental batch: the bronze parquet is the cache. A run fetches months not yet in
bronze, plus the last `REFETCH_LAST` months in case CHC revised them. --refresh
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
import rasterio
from rasterio.transform import rowcol
from rasterio.windows import from_bounds

from jotosanur_agri.pipeline import save
from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI, GDAL_ENV

BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/cogs"
FILE_RE = re.compile(r"chirps-v3\.0\.(\d{4})\.(\d{2})\.cog")

NORMAL_YEARS = (1991, 2020)  # WMO standard normal period
REFETCH_LAST = 2
WORKERS = 4
MAX_LAT = 50

BRONZE_SCHEMA = {"unit": pl.Utf8, "year": pl.Int64, "month": pl.Int64, "precip_mm": pl.Float64, "fetched_on": pl.Utf8}


def list_months() -> list[tuple[int, int]]:
    """List the (year, month) pairs published on the CHIRPS server."""
    with urllib.request.urlopen(f"{BASE_URL}/", timeout=60) as resp:
        html = resp.read().decode()
    return sorted({(int(y), int(m)) for y, m in FILE_RE.findall(html)})


def fetch_month(year: int, month: int, points: pl.DataFrame, names: list[str]) -> list[dict[str, Any]]:
    """Mean rainfall per unit for one month.

    Args:
        year: Year.
        month: Month.
        points: Monitored cells with ``lon``, ``lat`` and ``unit``.
        names: Unit names, each gets a row.

    Returns:
        One bronze row per unit. `precip_mm` is None when the unit has no cell with data.
    """
    lon, lat = points["lon"].to_numpy(), points["lat"].to_numpy()
    url = f"/vsicurl/{BASE_URL}/chirps-v3.0.{year}.{month:02d}.cog"
    with rasterio.Env(**GDAL_ENV), rasterio.open(url) as src:
        pad = abs(src.transform.a)
        bounds = (lon.min() - pad, lat.min() - pad, lon.max() + pad, lat.max() + pad)
        window = from_bounds(*bounds, transform=src.transform).round_offsets().round_lengths()
        data = src.read(1, window=window, boundless=True, fill_value=-9999)
        rows, cols = rowcol(src.window_transform(window), lon, lat)
    values = data[np.asarray(rows), np.asarray(cols)].astype("float64")
    # ocean/no-data pixels are negative (-9999)
    frame = points.select("unit").with_columns(pl.Series("v", np.where(values >= 0, values, np.nan)).fill_nan(None))
    means = dict(frame.group_by("unit").agg(pl.col("v").mean()).iter_rows())
    fetched_on = date.today().isoformat()
    return [
        {"unit": name, "year": year, "month": month, "precip_mm": means.get(name), "fetched_on": fetched_on}
        for name in names
    ]


def load_bronze(bronze_path: Path, points: pl.DataFrame, names: list[str], refresh: bool = False) -> pl.DataFrame:
    """Return the full bronze table, fetching only months missing from the cache.

    The last `REFETCH_LAST` published months are always refetched, since CHC may
    revise them.

    Args:
        bronze_path: Cached bronze parquet.
        points: Monitored cells with ``lon``, ``lat`` and ``unit``.
        names: Unit names.
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
            for batch in pool.map(lambda ym: fetch_month(ym[0], ym[1], points, names), todo):
                rows.extend(batch)
    fresh = pl.DataFrame(rows, schema=BRONZE_SCHEMA)
    return pl.concat([cached, fresh]).sort("unit", "year", "month")


def to_silver(bronze: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Derive the monthly series with 1991-2020 normals and anomalies, and annual totals.

    Returns:
        (monthly, annual). Annual keeps complete years only, since a partial year would
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

    Raises:
        ValueError: If the AOI reaches beyond CHIRPS' 50S-50N coverage.
    """
    aoi = resolve(aoi_spec)
    _, south, _, north = aoi.bounds()
    if north > MAX_LAT or south < -MAX_LAT:
        raise ValueError(f"{aoi.slug}: CHIRPS covers {MAX_LAT}S-{MAX_LAT}N only (AOI spans {south:.1f}..{north:.1f})")
    points = pl.read_parquet(Path(data_dir) / "bronze" / "sentinel" / aoi.slug / "cells.parquet")
    names = [name for name, _ in aoi.units]

    bronze_path = Path(data_dir) / "bronze" / "chirps" / f"{aoi.slug}_monthly.parquet"
    bronze = load_bronze(bronze_path, points, names, refresh=refresh)
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
