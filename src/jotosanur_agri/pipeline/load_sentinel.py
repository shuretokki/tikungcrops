"""Bronze pipeline turning Sentinel-1 and Sentinel-2 scenes into a cell x date table for one desa.

Sources, all public and read over HTTP as Cloud-Optimized GeoTIFFs (no login):
    - Sentinel-2 L2A, Earth Search STAC (AWS, Element84).
    - Sentinel-1 RTC (terrain-corrected radar backscatter), Microsoft Planetary
      Computer STAC; asset URLs need a short-lived anonymous SAS token.
    - ESA WorldCover 2021 v200, cropland mask (class 40).
    - GADM 4.1 desa boundaries (free for non-commercial use, not redistributed:
      cached under data/external/, which is not tracked).

Rows are 100 m cells (10 x 10 Sentinel-2 pixels) inside the desa that are at least half
cropland. Each scene becomes one row per cell with per-cell statistics:
    - S2: median NDVI and LSWI over pixels the scene classification marks clear,
      plus the clear fraction.
    - S1: mean VV and VH backscatter in dB. Flooded paddy at transplanting shows as
      a sharp VH drop, visible through the rainy-season clouds that block S2.

Output: data/bronze/sentinel/<desa>/<YYYY-MM>.parquet plus cells.parquet.
Usage: `python -m jotosanur_agri.pipeline.load_sentinel [DESA] [START_MONTH] [END_MONTH]`;
without months it processes the previous calendar month (the scheduled case).
"""

from __future__ import annotations

import json
import sys
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
import rasterio
from affine import Affine
from rasterio.features import rasterize
from rasterio.warp import Resampling, reproject, transform, transform_geom

from jotosanur_agri.pipeline import save

EARTH_SEARCH = "https://earth-search.aws.element84.com/v1/search"
PLANETARY = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
PC_TOKEN = "https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-1-rtc"
WORLDCOVER = (
    "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_S09E111_Map.tif"
)
GADM_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_IDN_4.json.zip"
GADM_DIR = Path("data/external/gadm")

CRS = "EPSG:32749"  # UTM 49S, the Sentinel-2 tile CRS over Lamongan
PIXEL_M = 10
CELL_PX = 10  # 100 m cells
MIN_CROP_FRAC = 0.5
WORLDCOVER_CROPLAND = 40
# Sentinel-2 scene classes treated as clear: vegetation, bare soil, water
S2_CLEAR = [4, 5, 6]
# Processing baseline 04.00 (from 2022-01-25) stores reflectance with a +1000 offset
S2_OFFSET_FROM = "2022-01-25"
WORKERS = 12

GDAL_ENV: dict[str, Any] = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "AWS_NO_SIGN_REQUEST": "YES",
    "GDAL_HTTP_MAX_RETRY": "4",
    "GDAL_HTTP_RETRY_DELAY": "5",
}

Grid = tuple[Affine, tuple[int, int]]

BRONZE_SCHEMA = {
    "cell_id": pl.Int64,
    "date": pl.Date,
    "sensor": pl.Utf8,
    "clear_frac": pl.Float64,
    "ndvi": pl.Float64,
    "lswi": pl.Float64,
    "vv_db": pl.Float64,
    "vh_db": pl.Float64,
    "orbit": pl.Utf8,
}


def desa_geometry(desa: str, kecamatan: str = "Tikung") -> dict[str, Any]:
    """GeoJSON geometry (lon/lat) of one desa from GADM level 4, downloading GADM once."""
    cached = GADM_DIR / f"{kecamatan.lower()}_desa.geojson"
    if not cached.exists():
        GADM_DIR.mkdir(parents=True, exist_ok=True)
        archive = GADM_DIR / "gadm41_IDN_4.json.zip"
        urllib.request.urlretrieve(GADM_URL, archive)
        with zipfile.ZipFile(archive) as z:
            features = json.loads(z.read("gadm41_IDN_4.json"))["features"]
        kec = [
            f for f in features if f["properties"]["NAME_2"] == "Lamongan" and f["properties"]["NAME_3"] == kecamatan
        ]
        cached.write_text(json.dumps({"type": "FeatureCollection", "features": kec}))
        archive.unlink()
    for feature in json.loads(cached.read_text())["features"]:
        if feature["properties"]["NAME_4"] == desa:
            return feature["geometry"]
    raise ValueError(f"desa {desa!r} not found in GADM for kecamatan {kecamatan}")


def stac_search(url: str, collection: str, geometry: dict[str, Any], month: str) -> list[dict[str, Any]]:
    """All items of `collection` intersecting `geometry` in `month` (``YYYY-MM``), one per acquisition date."""
    first = date.fromisoformat(f"{month}-01")
    last = date(first.year + first.month // 12, first.month % 12 + 1, 1) - timedelta(days=1)
    body = {
        "collections": [collection],
        "intersects": geometry,
        "datetime": f"{first.isoformat()}T00:00:00Z/{last.isoformat()}T23:59:59Z",
        "limit": 100,
    }
    request = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    items: list[dict[str, Any]] = []
    while True:
        with urllib.request.urlopen(request, timeout=120) as resp:
            page = json.load(resp)
        items += page["features"]
        nxt = next((link for link in page.get("links", []) if link["rel"] == "next"), None)
        if nxt is None:
            break
        data = json.dumps(nxt["body"]).encode() if nxt.get("method") == "POST" else None
        request = urllib.request.Request(nxt["href"], data, {"Content-Type": "application/json"})
    # Overlapping tiles or reprocessed products can repeat a date; keep the first
    by_date: dict[str, dict[str, Any]] = {}
    for item in sorted(items, key=lambda i: i["properties"]["datetime"]):
        by_date.setdefault(item["properties"]["datetime"][:10], item)
    return list(by_date.values())


def make_grid(geometry: dict[str, Any]) -> tuple[Grid, np.ndarray]:
    """10 m grid over the desa bounding box, snapped to whole cells, plus the desa mask."""
    utm = transform_geom("EPSG:4326", CRS, geometry)
    rings = utm["coordinates"] if utm["type"] == "MultiPolygon" else [utm["coordinates"]]
    xs = [x for poly in rings for x, _ in poly[0]]
    ys = [y for poly in rings for _, y in poly[0]]
    step = PIXEL_M * CELL_PX
    x0, y1 = np.floor(min(xs) / step) * step, np.ceil(max(ys) / step) * step
    width = int(np.ceil((max(xs) - x0) / step)) * CELL_PX
    height = int(np.ceil((y1 - min(ys)) / step)) * CELL_PX
    grid = (Affine(PIXEL_M, 0, x0, 0, -PIXEL_M, y1), (height, width))
    inside = np.asarray(rasterize([(utm, 1)], out_shape=grid[1], transform=grid[0], dtype="uint8"), dtype=bool)
    return grid, inside


def read_to_grid(href: str, grid: Grid, resampling: Resampling = Resampling.nearest) -> np.ndarray:
    """Read band 1 of a raster warped onto `grid`; nodata becomes NaN."""
    tf, shape = grid
    out = np.full(shape, np.nan, dtype="float32")
    with rasterio.Env(**GDAL_ENV), rasterio.open(href) as src:
        reproject(
            rasterio.band(src, 1),
            out,
            src_nodata=src.nodata,
            dst_transform=tf,
            dst_crs=CRS,
            dst_nodata=np.nan,
            resampling=resampling,
        )
    return out


def cell_ids(grid: Grid, keep: np.ndarray) -> np.ndarray:
    """Cell id per pixel (row-major over cells), -1 where `keep` is False."""
    height, width = grid[1]
    rows, cols = np.indices((height, width))
    ids = (rows // CELL_PX) * (width // CELL_PX) + cols // CELL_PX
    return np.where(keep, ids, -1)


def cells_table(grid: Grid, inside: np.ndarray, cropland: np.ndarray) -> pl.DataFrame:
    """Cells that are inside the desa and at least `MIN_CROP_FRAC` cropland, with centre coordinates."""
    ids = cell_ids(grid, inside)
    n = (grid[1][0] // CELL_PX) * (grid[1][1] // CELL_PX)
    total = np.bincount(ids[ids >= 0], minlength=n)
    crop = np.bincount(ids[(ids >= 0) & cropland], minlength=n)
    cell = np.arange(n)
    keep = (total > 0) & (crop / np.maximum(total, 1) >= MIN_CROP_FRAC)
    width_cells = grid[1][1] // CELL_PX
    x = grid[0].c + (cell % width_cells + 0.5) * PIXEL_M * CELL_PX
    y = grid[0].f - (cell // width_cells + 0.5) * PIXEL_M * CELL_PX
    lon, lat = transform(CRS, "EPSG:4326", x[keep].tolist(), y[keep].tolist())[:2]
    return pl.DataFrame(
        {
            "cell_id": cell[keep],
            "x": x[keep],
            "y": y[keep],
            "lon": lon,
            "lat": lat,
            "crop_frac": (crop / np.maximum(total, 1))[keep],
        }
    )


def _per_cell(ids: np.ndarray, values: np.ndarray, valid: np.ndarray, stat: str) -> dict[int, float]:
    frame = pl.DataFrame({"cell_id": ids[valid], "v": values[valid]})
    agg = pl.col("v").median() if stat == "median" else pl.col("v").mean()
    return dict(frame.group_by("cell_id").agg(agg).iter_rows())


def s2_rows(item: dict[str, Any], grid: Grid, ids: np.ndarray) -> list[dict[str, Any]]:
    """Per-cell NDVI, LSWI and clear fraction for one Sentinel-2 scene."""
    assets, day = item["assets"], item["properties"]["datetime"][:10]
    scl = read_to_grid(assets["scl"]["href"], grid)
    red, nir, swir = (read_to_grid(assets[b]["href"], grid, Resampling.bilinear) for b in ("red", "nir", "swir16"))
    if day >= S2_OFFSET_FROM and not item["properties"].get("earthsearch:boa_offset_applied", False):
        red, nir, swir = red - 1000, nir - 1000, swir - 1000
    member = ids >= 0
    clear = member & np.isin(scl, S2_CLEAR)
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = (nir - red) / (nir + red)
        lswi = (nir - swir) / (nir + swir)
    ok = clear & np.isfinite(ndvi) & np.isfinite(lswi)
    n_all = np.bincount(ids[member])
    n_clear = np.bincount(ids[ok], minlength=len(n_all))
    ndvi_by, lswi_by = _per_cell(ids, ndvi, ok, "median"), _per_cell(ids, lswi, ok, "median")
    return [
        {
            "cell_id": int(c),
            "date": date.fromisoformat(day),
            "sensor": "S2",
            "clear_frac": float(n_clear[c] / n_all[c]),
            "ndvi": ndvi_by.get(int(c)),
            "lswi": lswi_by.get(int(c)),
            "vv_db": None,
            "vh_db": None,
            "orbit": None,
        }
        for c in np.flatnonzero(n_all)
    ]


def s1_rows(item: dict[str, Any], grid: Grid, ids: np.ndarray, token: str) -> list[dict[str, Any]]:
    """Per-cell mean VV and VH backscatter (dB) for one Sentinel-1 RTC scene."""
    assets, day = item["assets"], item["properties"]["datetime"][:10]
    member = ids >= 0
    by_pol: dict[str, dict[int, float]] = {}
    for pol in ("vv", "vh"):
        linear = read_to_grid(f"{assets[pol]['href']}?{token}", grid, Resampling.bilinear)
        # Average in linear power, then convert, so the mean is not biased by the log
        ok = member & np.isfinite(linear) & (linear > 0)
        by_pol[pol] = {c: float(10 * np.log10(v)) for c, v in _per_cell(ids, linear, ok, "mean").items()}
    return [
        {
            "cell_id": int(c),
            "date": date.fromisoformat(day),
            "sensor": "S1",
            "clear_frac": 1.0,
            "ndvi": None,
            "lswi": None,
            "vv_db": by_pol["vv"].get(int(c)),
            "vh_db": by_pol["vh"].get(int(c)),
            "orbit": item["properties"].get("sat:orbit_state"),
        }
        for c in np.unique(ids[member])
    ]


def pc_token() -> str:
    """Anonymous SAS token for Planetary Computer's Sentinel-1 RTC storage."""
    with urllib.request.urlopen(PC_TOKEN, timeout=60) as resp:
        return json.load(resp)["token"]


def month_range(start: str, end: str) -> list[str]:
    """Months from `start` to `end` inclusive, as ``YYYY-MM`` strings."""
    y, m = map(int, start.split("-"))
    months = []
    while f"{y:04d}-{m:02d}" <= end:
        months.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return months


def previous_month(today: date | None = None) -> str:
    """The calendar month before `today`, as ``YYYY-MM``; the default for scheduled runs."""
    today = today or date.today()
    y, m = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
    return f"{y:04d}-{m:02d}"


def run_sentinel_pipeline(
    desa: str = "Jotosanur", start: str | None = None, end: str | None = None, out_dir: str | Path = "data"
) -> dict[str, Any]:
    """Build bronze cell x date tables for one desa, one parquet file per month.

    Each month is written on its own, so a scheduled run can process only the month it
    needs without reading earlier output, and a rerun overwrites the same file.

    Args:
        desa: Desa name as spelled in GADM.
        start: First month, ``YYYY-MM``. Defaults to the previous calendar month.
        end: Last month, ``YYYY-MM``. Defaults to `start`.
        out_dir: Data root.

    Returns:
        Cell count and, per month, scene and row counts.
    """
    start = start or previous_month()
    end = end or start
    geometry = desa_geometry(desa)
    grid, inside = make_grid(geometry)
    cropland = read_to_grid(WORLDCOVER, grid) == WORLDCOVER_CROPLAND
    cells = cells_table(grid, inside, cropland)
    keep = np.isin(cell_ids(grid, np.ones_like(inside)), cells["cell_id"].to_numpy())
    ids = cell_ids(grid, inside & cropland & keep)

    desa_dir = Path(out_dir) / "bronze" / "sentinel" / desa.lower()
    save(cells, desa_dir / "cells.parquet")
    token = pc_token()
    summary: dict[str, Any] = {"cells": cells.height, "months": {}}
    for month in month_range(start, end):
        s2_items = stac_search(EARTH_SEARCH, "sentinel-2-l2a", geometry, month)
        s1_items = stac_search(PLANETARY, "sentinel-1-rtc", geometry, month)
        with ThreadPoolExecutor(WORKERS) as pool:
            s2 = pool.map(lambda i: s2_rows(i, grid, ids), s2_items)
            s1 = pool.map(lambda i: s1_rows(i, grid, ids, token), s1_items)
            rows = [row for batch in (*s2, *s1) for row in batch]
        bronze = pl.DataFrame(rows, schema=BRONZE_SCHEMA).sort("sensor", "date", "cell_id")
        save(bronze, desa_dir / f"{month}.parquet")
        summary["months"][month] = {"s2": len(s2_items), "s1": len(s1_items), "rows": bronze.height}
        print(f"[sentinel] {desa} {month}: {len(s2_items)} S2, {len(s1_items)} S1, {bronze.height} rows")
    return summary


if __name__ == "__main__":
    # load_sentinel [DESA] [START_MONTH] [END_MONTH]; no months = previous month
    args = sys.argv[1:] + [None] * 3
    print(run_sentinel_pipeline(args[0] or "Jotosanur", args[1], args[2]))
