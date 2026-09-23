"""Bronze pipeline turning Sentinel-1 and Sentinel-2 scenes into a cell x date table for an area of interest.

Sources, all public and read over HTTP as Cloud-Optimized GeoTIFFs (no login):
    - Sentinel-2 L2A, Earth Search STAC (AWS, Element84).
    - Sentinel-1 RTC (terrain-corrected radar backscatter), Microsoft Planetary
      Computer STAC; asset URLs need a short-lived anonymous SAS token.
    - ESA WorldCover 2021 v200, cropland mask (class 40).
    - Area boundaries from `aoi` (GADM or a user GeoJSON).

Rows are 100 m cells (10 x 10 Sentinel-2 pixels) inside the AOI that are at least half
cropland; each cell belongs to the AOI unit covering most of it. Each scene becomes one
row per cell with per-cell statistics:
    - S2: median NDVI and LSWI over pixels the scene classification marks clear,
      plus the clear fraction.
    - S1: mean VV and VH backscatter in dB. Flooded paddy at transplanting shows as
      a sharp VH drop, visible through the rainy-season clouds that block S2.

Output: data/bronze/sentinel/<aoi-slug>/<YYYY-MM>.parquet plus cells.parquet.
Usage: `python -m jotosanur_agri.pipeline.load_sentinel [AOI] [START_MONTH] [END_MONTH]`,
e.g. `Lamongan/Tikung 2020-01 2020-12`; without months it processes the previous
calendar month (the scheduled case).
"""

from __future__ import annotations

import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
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
from jotosanur_agri.pipeline.aoi import Aoi, resolve

DEFAULT_AOI = "Lamongan/Tikung"
EARTH_SEARCH = "https://earth-search.aws.element84.com/v1/search"
PLANETARY = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
PC_TOKEN = "https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-1-rtc"

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


@dataclass(frozen=True)
class Grid:
    """10 m pixel grid in a UTM CRS, sized to whole cells."""

    transform: Affine
    shape: tuple[int, int]
    crs: str

    @property
    def cells_wide(self) -> int:
        """Number of cells per grid row."""
        return self.shape[1] // CELL_PX


def stac_search(url: str, collection: str, bbox: tuple[float, ...], month: str) -> list[dict[str, Any]]:
    """All items of `collection` intersecting `bbox` in `month` (``YYYY-MM``), one per acquisition date."""
    first = date.fromisoformat(f"{month}-01")
    last = date(first.year + first.month // 12, first.month % 12 + 1, 1) - timedelta(days=1)
    body = {
        "collections": [collection],
        "bbox": list(bbox),
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


def make_grid(aoi: Aoi) -> tuple[Grid, np.ndarray]:
    """Grid over the AOI bounds, snapped to whole cells, plus a raster of unit numbers (1-based, 0 outside)."""
    crs = aoi.utm_crs()
    utm = [transform_geom("EPSG:4326", crs, geometry) for _, geometry in aoi.units]
    points = [
        (x, y)
        for g in utm
        for polygon in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]])
        for x, y in polygon[0]
    ]
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    step = PIXEL_M * CELL_PX
    x0, y1 = np.floor(min(xs) / step) * step, np.ceil(max(ys) / step) * step
    width = int(np.ceil((max(xs) - x0) / step)) * CELL_PX
    height = int(np.ceil((y1 - min(ys)) / step)) * CELL_PX
    grid = Grid(Affine(PIXEL_M, 0, x0, 0, -PIXEL_M, y1), (height, width), crs)
    units = rasterize(
        [(g, k + 1) for k, g in enumerate(utm)], out_shape=grid.shape, transform=grid.transform, dtype="int32"
    )
    return grid, np.asarray(units)


def read_to_grid(href: str, grid: Grid, resampling: Resampling = Resampling.nearest) -> np.ndarray:
    """Read band 1 of a raster warped onto `grid`; nodata becomes NaN."""
    out = np.full(grid.shape, np.nan, dtype="float32")
    with rasterio.Env(**GDAL_ENV), rasterio.open(href) as src:
        reproject(
            rasterio.band(src, 1),
            out,
            src_nodata=src.nodata,
            dst_transform=grid.transform,
            dst_crs=grid.crs,
            dst_nodata=np.nan,
            resampling=resampling,
        )
    return out


def read_cropland(aoi: Aoi, grid: Grid) -> np.ndarray:
    """WorldCover cropland mask on `grid`, merged across every tile the AOI touches."""
    cover = np.full(grid.shape, np.nan, dtype="float32")
    for url in aoi.worldcover_tiles():
        tile = read_to_grid(url, grid)
        cover = np.where(np.isnan(cover), tile, cover)
    return cover == WORLDCOVER_CROPLAND


def cell_ids(grid: Grid, keep: np.ndarray) -> np.ndarray:
    """Cell id per pixel (row-major over cells), -1 where `keep` is False."""
    rows, cols = np.indices(grid.shape)
    ids = (rows // CELL_PX) * grid.cells_wide + cols // CELL_PX
    return np.where(keep, ids, -1)


def cells_table(aoi: Aoi, grid: Grid, units: np.ndarray, cropland: np.ndarray) -> pl.DataFrame:
    """Cells inside the AOI that are at least `MIN_CROP_FRAC` cropland, with centre coordinates and unit."""
    inside = units > 0
    ids = cell_ids(grid, inside)
    n = (grid.shape[0] // CELL_PX) * grid.cells_wide
    total = np.bincount(ids[inside], minlength=n)
    crop = np.bincount(ids[inside & cropland], minlength=n)
    # Majority unit per cell: count (cell, unit) pairs, then take the most frequent unit
    n_units = len(aoi.units) + 1
    pairs = np.bincount(ids[inside] * n_units + units[inside], minlength=n * n_units).reshape(n, n_units)
    cell = np.arange(n)
    keep = (total > 0) & (crop / np.maximum(total, 1) >= MIN_CROP_FRAC)
    x = grid.transform.c + (cell % grid.cells_wide + 0.5) * PIXEL_M * CELL_PX
    y = grid.transform.f - (cell // grid.cells_wide + 0.5) * PIXEL_M * CELL_PX
    lon, lat = transform(grid.crs, "EPSG:4326", x[keep].tolist(), y[keep].tolist())[:2]
    names = [name for name, _ in aoi.units]
    return pl.DataFrame(
        {
            "cell_id": cell[keep],
            "unit": [names[u - 1] for u in pairs[keep].argmax(axis=1)],
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
    aoi_spec: str = DEFAULT_AOI, start: str | None = None, end: str | None = None, out_dir: str | Path = "data"
) -> dict[str, Any]:
    """Build bronze cell x date tables for an AOI, one parquet file per month.

    Each month is written on its own, so a scheduled run can process only the month it
    needs without reading earlier output, and a rerun overwrites the same file.

    Args:
        aoi_spec: GADM path (e.g. ``Lamongan/Tikung``) or GeoJSON path; see `aoi.resolve`.
        start: First month, ``YYYY-MM``. Defaults to the previous calendar month.
        end: Last month, ``YYYY-MM``. Defaults to `start`.
        out_dir: Data root.

    Returns:
        Cell and unit counts and, per month, scene and row counts.
    """
    start = start or previous_month()
    end = end or start
    aoi = resolve(aoi_spec)
    grid, units = make_grid(aoi)
    cropland = read_cropland(aoi, grid)
    cells = cells_table(aoi, grid, units, cropland)
    keep = np.isin(cell_ids(grid, np.ones(grid.shape, dtype=bool)), cells["cell_id"].to_numpy())
    ids = cell_ids(grid, (units > 0) & cropland & keep)

    aoi_dir = Path(out_dir) / "bronze" / "sentinel" / aoi.slug
    save(cells, aoi_dir / "cells.parquet")
    token = pc_token()
    bbox = aoi.bounds()
    summary: dict[str, Any] = {"aoi": aoi.slug, "units": len(aoi.units), "cells": cells.height, "months": {}}
    for month in month_range(start, end):
        s2_items = stac_search(EARTH_SEARCH, "sentinel-2-l2a", bbox, month)
        s1_items = stac_search(PLANETARY, "sentinel-1-rtc", bbox, month)
        with ThreadPoolExecutor(WORKERS) as pool:
            s2 = pool.map(lambda i: s2_rows(i, grid, ids), s2_items)
            s1 = pool.map(lambda i: s1_rows(i, grid, ids, token), s1_items)
            rows = [row for batch in (*s2, *s1) for row in batch]
        bronze = pl.DataFrame(rows, schema=BRONZE_SCHEMA).sort("sensor", "date", "cell_id")
        save(bronze, aoi_dir / f"{month}.parquet")
        summary["months"][month] = {"s2": len(s2_items), "s1": len(s1_items), "rows": bronze.height}
        print(f"[sentinel] {aoi.slug} {month}: {len(s2_items)} S2, {len(s1_items)} S1, {bronze.height} rows")
    return summary


if __name__ == "__main__":
    # load_sentinel [AOI] [START_MONTH] [END_MONTH]; no months = previous month
    args = sys.argv[1:] + [None] * 3
    print(run_sentinel_pipeline(args[0] or DEFAULT_AOI, args[1], args[2]))
