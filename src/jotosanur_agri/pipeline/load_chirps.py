"""Bronze/Silver pipeline for CHIRPS v3.0 monthly rainfall at Desa Jotosanur.

Source: Climate Hazards Center, UCSB. CHIRPS v3.0 global monthly (final,
not prelim), 0.05 deg, 1981-now, public domain. Final data for a month is
typically complete in the third week of the following month.

Files are Cloud-Optimized GeoTIFFs (~30 MB each, 512x512 tiles), so only
the tile holding each pixel is range-read over HTTP (GDAL /vsicurl/)
instead of downloading whole rasters.

Incremental batch: bronze parquet is the cache. A run fetches months not
yet in bronze, plus the last REFETCH_LAST months in case CHC revised them.
--refresh refetches everything.

Bronze = one row per point/month, raw pixel value as read.
Silver = monthly series with 1991-2020 normal and anomaly, plus an annual
total_precip table matching the CIMMYT column ("Total precipitation during
year of surveyed rice crop, according to CHIRPS"). CIMMYT's other weather
columns (dry/wet days, spells, monsoon onset) need daily data and are not
derived here.

Points are the same as load_soilgrids.py. Both fall in the same CHIRPS
pixel (~5.5 km), so their series are identical.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from typing import Any

import polars as pl
import rasterio

from jotosanur_agri.pipeline import save
from jotosanur_agri.pipeline.load_soilgrids import POINTS

BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/cogs"
FILE_RE = re.compile(r"chirps-v3\.0\.(\d{4})\.(\d{2})\.cog")

NORMAL_YEARS = (1991, 2020)  # WMO standard normal period
REFETCH_LAST = 2
WORKERS = 4

GDAL_ENV: dict[str, Any] = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "GDAL_HTTP_MAX_RETRY": "4",
    "GDAL_HTTP_RETRY_DELAY": "5",
}


def list_months() -> list[tuple[int, int]]:
    """List the (year, month) pairs published on the CHIRPS server."""
    with urllib.request.urlopen(f"{BASE_URL}/", timeout=60) as resp:
        html = resp.read().decode()
    return sorted({(int(y), int(m)) for y, m in FILE_RE.findall(html)})


def fetch_month(year: int, month: int) -> list[dict[str, Any]]:
    """Read the pixel value at each point from one monthly COG.

    Returns:
        One bronze row per point.
    """
    url = f"/vsicurl/{BASE_URL}/chirps-v3.0.{year}.{month:02d}.cog"
    coords = [(pt["lon"], pt["lat"]) for pt in POINTS.values()]
    with rasterio.Env(**GDAL_ENV), rasterio.open(url) as src:
        values = [float(v[0]) for v in src.sample(coords)]
        pixels = [src.index(lon, lat) for lon, lat in coords]
    fetched_on = date.today().isoformat()
    return [
        {
            "point": name,
            "lat": pt["lat"],
            "lon": pt["lon"],
            "pixel_row": row,
            "pixel_col": col,
            "year": year,
            "month": month,
            "raw_value": value,
            "fetched_on": fetched_on,
        }
        for (name, pt), value, (row, col) in zip(POINTS.items(), values, pixels, strict=True)
    ]


def load_bronze(bronze_path: Path, refresh: bool = False) -> pl.DataFrame:
    """Return the full bronze table, fetching only months missing from the cache.

    The last `REFETCH_LAST` published months are always refetched, since CHC may
    revise them.

    Args:
        bronze_path: Cached bronze parquet.
        refresh: Ignore the cache and refetch every month.

    Returns:
        Bronze rows sorted by point, year and month.
    """
    available = list_months()
    cached = pl.DataFrame()
    if bronze_path.exists() and not refresh:
        stale = pl.DataFrame(available[-REFETCH_LAST:], schema=["year", "month"], orient="row")
        cached = pl.read_parquet(bronze_path)
        cached = cached.join(stale, on=["year", "month"], how="anti")
    done = set(cached.select("year", "month").unique().iter_rows()) if cached.height else set()
    todo = [ym for ym in available if ym not in done]

    rows: list[dict[str, Any]] = []
    if todo:
        print(f"[chirps] fetching {len(todo)} months ({todo[0]} .. {todo[-1]})")
        with ThreadPoolExecutor(WORKERS) as pool:
            for batch in pool.map(lambda ym: fetch_month(*ym), todo):
                rows.extend(batch)

    fresh = pl.DataFrame(rows, schema=cached.schema if cached.height else None)
    bronze = pl.concat([cached, fresh]) if cached.height else fresh
    return bronze.sort("point", "year", "month")


def to_silver(bronze: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Derive the monthly series with 1991-2020 normals and anomalies, and annual totals.

    Returns:
        (monthly, annual). Annual keeps complete years only.
    """
    # Ocean/no-data pixels are negative (-9999); treat as missing.
    monthly = bronze.with_columns(
        pl.when(pl.col("raw_value") >= 0).then(pl.col("raw_value")).alias("precip_mm"),
        pl.date(pl.col("year"), pl.col("month"), 1).dt.month_end().dt.day().alias("n_days"),
    ).with_columns((pl.col("precip_mm") / pl.col("n_days")).alias("mm_per_day"))

    lo, hi = NORMAL_YEARS
    normal = (
        monthly.filter(pl.col("year").is_between(lo, hi))
        .group_by("point", "month")
        .agg(pl.col("precip_mm").mean().alias("normal_mm"))
    )
    monthly = (
        monthly.join(normal, on=["point", "month"], how="left")
        .with_columns(
            (pl.col("precip_mm") - pl.col("normal_mm")).alias("anomaly_mm"),
            pl.when(pl.col("normal_mm") > 0)
            .then((pl.col("precip_mm") / pl.col("normal_mm") - 1) * 100)
            .alias("anomaly_pct"),
        )
        .select(
            "point",
            "lat",
            "lon",
            "pixel_row",
            "pixel_col",
            "year",
            "month",
            "n_days",
            "precip_mm",
            "mm_per_day",
            "normal_mm",
            "anomaly_mm",
            "anomaly_pct",
        )
        .sort("point", "year", "month")
    )

    # Complete years only; a partial year would understate total_precip.
    annual = (
        monthly.group_by("point", "lat", "lon", "year")
        .agg(
            pl.col("precip_mm").sum().alias("total_precip"),
            pl.col("precip_mm").is_not_null().sum().alias("n_months"),
        )
        .filter(pl.col("n_months") == 12)
        .drop("n_months")
        .sort("point", "year")
    )
    return monthly, annual


def run_chirps_pipeline(out_dir: str | Path = "data", refresh: bool = False) -> dict[str, Any]:
    """Update bronze and write the silver monthly and annual tables.

    Returns:
        Row counts, null count, covered range and output paths.
    """
    bronze_path = Path(out_dir) / "bronze" / "chirps" / "chirps_monthly.parquet"
    silver_dir = Path(out_dir) / "silver" / "chirps"

    bronze = load_bronze(bronze_path, refresh=refresh)
    save(bronze, bronze_path)
    monthly, annual = to_silver(bronze)

    first, last = monthly.row(0, named=True), monthly.row(-1, named=True)
    return {
        "rows_bronze": bronze.height,
        "rows_silver_monthly": monthly.height,
        "rows_silver_annual": annual.height,
        "null_values": monthly.filter(pl.col("precip_mm").is_null()).height,
        "range": f"{first['year']}-{first['month']:02d}..{last['year']}-{last['month']:02d}",
        "bronze_path": str(bronze_path),
        "silver_monthly_path": save(monthly, silver_dir / "chirps_monthly.parquet"),
        "silver_annual_path": save(annual, silver_dir / "chirps_annual_cimmyt.parquet"),
    }


if __name__ == "__main__":
    print(run_chirps_pipeline(refresh="--refresh" in sys.argv))
