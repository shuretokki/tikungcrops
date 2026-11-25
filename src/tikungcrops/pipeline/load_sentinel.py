# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Turn S1 and S2 scenes into a cell x date table for an area of interest.

Sources, all public and read over HTTP as Cloud-Optimized GeoTIFFs:
    - Sentinel-2 L2A, Earth Search STAC
        https://earth-search.aws.element84.com/v1/api.html
      Copernicus Sentinel-2 (processed by ESA), 2021, MSI Level-2A BOA Reflectance Product. Collection 1. European Space Agency. https://doi.org/10.5270/S2_-znk9xsj
    - Sentinel-1 RTC Microsoft Planetary Computer STAC.
        https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc
      Asset URLs need a short-lived anonymous SAS token.
    - ESA WorldCover 2021 v200.
        https://esa-worldcover.org/en
      Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W., Brockmann, C., Kirches, G., Wevers, J., Cartus, O., Santoro, M., Fritz, S., Lesiv, M., Herold, M., Tsendbazar, N.E., Xu, P., Ramoino, F., Arino, O., 2022. ESA WorldCover 10 m 2021 v200. https://doi.org/10.5281/zenodo.7254221
    - Area boundaries from `aoi`: GADM or a user GeoJSON.
        https://gadm.org/
      GADM. (2022). Global Administrative Areas spatial database, version 4.1 [Indonesia, Lamongan/Tikung]. Available online: https://gadm.org [Accessed 25 September 2026].

Rows are 100 m cells (10 x 10 Sentinel-2 pixels) inside the AOI that are at least half
cropland. Each cell belongs to the AOI unit covering most of it. Each acquisition date
becomes one row per cell with per-cell statistics:
    - S2: median NDVI and LSWI over pixels the scene classification marks clear,
      plus the clear fraction.
    - S1: mean VV and VH backscatter in dB. Flooded paddy at transplanting shows as
      a sharp VH drop, visible through the rainy-season clouds that block S2.

An AOI can span several satellite tiles, and a single date often has several partial
products (datastrips, reprocessings). All items of a date are mosaicked: each pixel
comes from the newest product that covers it.

The grid is processed in blocks of at most `BLOCK_PX` x `BLOCK_PX` pixels, so memory
stays bounded for large areas. Cell ids are global across blocks.

Output: data/bronze/sentinel/<aoi-slug>/<YYYY-MM>.parquet plus cells.parquet.
Usage: `python -m tikungcrops.pipeline.load_sentinel [AOI] [START_MONTH] [END_MONTH]`,
e.g. `Lamongan/Tikung 2020-01 2020-12`. Without months it defaults to the previous
calendar month.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
import rasterio
from affine import Affine
from rasterio.errors import RasterioError
from rasterio.features import rasterize
from rasterio.warp import Resampling, reproject, transform, transform_bounds, transform_geom

from tikungcrops.pipeline import save
from tikungcrops.pipeline.aoi import Aoi, resolve

DEFAULT_AOI = "Lamongan/Tikung"
EARTH_SEARCH = "https://earth-search.aws.element84.com/v1/search"
PLANETARY = "https://planetarycomputer.microsoft.com/api/stac/v1/search"

# https://planetarycomputer.microsoft.com/docs/concepts/sas/
PC_TOKEN = "https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-1-rtc"

PIXEL_M = 10
CELL_PX = 10  # 100 m cells
BLOCK_PX = 1500  # multiple of CELL_PX. ~2.25 M pixels per block
MIN_CROP_FRAC = 0.5

# Refer: WorldCover Product User Manual V2.0
WORLDCOVER_CROPLAND = 40

# Refer: Copernicus Space Component Sentinel Optical Imaging MPC
# Document ID: OMPC.TPZ.SUM.003 [Sen2Cor Configuration and User Manual]
# table 2-1 on page 7 contains related classification map for below
# 4:vegetation, 5:bare soil, 6:water
S2_CLEAR = [4, 5, 6]
# processing baseline 04.00 from 2022-01-25 stores reflectance with a +1000 offset
S2_OFFSET_FROM = "2022-01-25"
WORKERS = 12

# Refer: https://gdal.org/en/stable/user/configoptions.html
GDAL_ENV: dict[str, Any] = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "AWS_NO_SIGN_REQUEST": "YES",
    "GDAL_HTTP_MAX_RETRY": "4",
    "GDAL_HTTP_RETRY_DELAY": "5",
}
READ_RETRIES = 3
RETRY_PAUSE_S = 10

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

Item = dict[str, Any]

CELLS_SCHEMA = {
    "cell_id": pl.Int64,
    "unit": pl.Utf8,
    "x": pl.Float64,
    "y": pl.Float64,
    "lon": pl.Float64,
    "lat": pl.Float64,
    "crop_frac": pl.Float64,
}


@dataclass(frozen=True)
class Grid:
    """10 m pixel grid in a UTM CRS, or one block of it.

    Attributes:
        transform: Affine transform of the grid's top-left pixel.
        shape: (rows, cols) in pixels, multiples of `CELL_PX`.
        crs: UTM CRS.
        cells_wide: Cells per row of the full grid, keeps cell ids global across blocks.
        cell_row0: Cell row of this block's first row in the full grid.
        cell_col0: Cell column of this block's first column in the full grid.
    """

    transform: Affine
    shape: tuple[int, int]
    crs: str
    cells_wide: int
    cell_row0: int = 0
    cell_col0: int = 0

    def blocks(self, size: int = BLOCK_PX) -> Iterator[Grid]:
        """Split into blocks of at most `size` x `size` pixels, row-major."""
        rows, cols = self.shape
        for r in range(0, rows, size):
            for c in range(0, cols, size):
                yield Grid(
                    self.transform * Affine.translation(c, r),
                    (min(size, rows - r), min(size, cols - c)),
                    self.crs,
                    self.cells_wide,
                    self.cell_row0 + r // CELL_PX,
                    self.cell_col0 + c // CELL_PX,
                )

    def lonlat_bounds(self) -> tuple[float, float, float, float]:
        """(west, south, east, north) in degrees."""
        rows, cols = self.shape
        west, north = self.transform * (0, 0)
        east, south = self.transform * (cols, rows)
        return transform_bounds(self.crs, "EPSG:4326", west, south, east, north)


def stac_search(url: str, collection: str, bbox: tuple[float, ...], month: str) -> dict[str, list[Item]]:
    """Items of `collection` intersecting `bbox` in `month` (``YYYY-MM``), grouped by date, newest product first."""
    first = date.fromisoformat(f"{month}-01")
    last = date(first.year + first.month // 12, first.month % 12 + 1, 1) - timedelta(days=1)
    body = {
        "collections": [collection],
        "bbox": list(bbox),
        "datetime": f"{first.isoformat()}T00:00:00Z/{last.isoformat()}T23:59:59Z",
        "limit": 100,
    }
    request = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    items: list[Item] = []
    while True:
        with urllib.request.urlopen(request, timeout=120) as resp:
            page = json.load(resp)
        items += page["features"]
        nxt = next((link for link in page.get("links", []) if link["rel"] == "next"), None)
        if nxt is None:
            break
        data = json.dumps(nxt["body"]).encode() if nxt.get("method") == "POST" else None
        request = urllib.request.Request(nxt["href"], data, {"Content-Type": "application/json"})
    by_date: dict[str, list[Item]] = {}
    for item in sorted(items, key=lambda i: i["properties"].get("created", ""), reverse=True):
        by_date.setdefault(item["properties"]["datetime"][:10], []).append(item)
    return dict(sorted(by_date.items()))


def make_grid(aoi: Aoi) -> Grid:
    """Full grid over the AOI bounds, snapped to whole cells."""
    crs = aoi.utm_crs()
    points = [
        (x, y)
        for _, geometry in aoi.units
        for polygon in _polygons(transform_geom("EPSG:4326", crs, geometry))
        for x, y in polygon[0]
    ]
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    step = PIXEL_M * CELL_PX
    x0, y1 = np.floor(min(xs) / step) * step, np.ceil(max(ys) / step) * step
    width = int(np.ceil((max(xs) - x0) / step)) * CELL_PX
    height = int(np.ceil((y1 - min(ys)) / step)) * CELL_PX
    return Grid(Affine(PIXEL_M, 0, x0, 0, -PIXEL_M, y1), (height, width), crs, width // CELL_PX)


def _polygons(geometry: dict[str, Any]) -> list[Any]:
    return geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]


def unit_raster(aoi: Aoi, grid: Grid) -> np.ndarray:
    """Unit number per pixel (1-based, 0 outside the AOI) on `grid` or a block of it."""
    shapes = [(transform_geom("EPSG:4326", grid.crs, g), k + 1) for k, (_, g) in enumerate(aoi.units)]
    return np.asarray(rasterize(shapes, out_shape=grid.shape, transform=grid.transform, fill=0, dtype="int32"))


def read_to_grid(href: str, grid: Grid, resampling: Resampling = Resampling.nearest) -> np.ndarray:
    """Read band 1 of a raster warped onto `grid`. Nodata becomes NaN.

    GDAL retries HTTP errors itself, but a short read (0 bytes for a tile) comes back as a
    plain read error. Such reads are retried `READ_RETRIES` times with a growing pause.
    If they still fail, the scene counts as nodata for this block and the run goes on,
    as stackstac's `errors_as_nodata` does. One lost scene costs a date, a crash costs the month.
    """
    for attempt in range(READ_RETRIES + 1):
        out = np.full(grid.shape, np.nan, dtype="float32")
        try:
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
        except RasterioError as e:
            if attempt == READ_RETRIES:
                print(f"[sentinel] read failed {READ_RETRIES + 1} times, using nodata: {href.split('?')[0]} ({e})")
                return np.full(grid.shape, np.nan, dtype="float32")
            time.sleep(RETRY_PAUSE_S * (attempt + 1))
    raise AssertionError("unreachable")


def read_cropland(aoi: Aoi, grid: Grid) -> np.ndarray:
    """WorldCover cropland mask on `grid`, merged across every tile the AOI touches."""
    cover = np.full(grid.shape, np.nan, dtype="float32")
    for url in aoi.worldcover_tiles():
        tile = read_to_grid(url, grid)
        cover = np.where(np.isnan(cover), tile, cover)
    return cover == WORLDCOVER_CROPLAND


def cell_ids(grid: Grid, keep: np.ndarray) -> np.ndarray:
    """Global cell id per pixel (row-major over the full grid's cells), -1 where `keep` is False."""
    rows, cols = np.indices(grid.shape)
    ids = (rows // CELL_PX + grid.cell_row0) * grid.cells_wide + cols // CELL_PX + grid.cell_col0
    return np.where(keep, ids, -1)


def monitored_blocks(aoi: Aoi, cells: pl.DataFrame) -> Iterator[tuple[Grid, np.ndarray]]:
    """Blocks holding any of `cells`, each with the global cell id per pixel (-1 outside those cells).

    Blocks are multiples of the cell size, so every cell lies wholly in one block and
    per-cell statistics can be computed block by block.
    """
    wanted = cells["cell_id"].to_numpy()
    for grid in make_grid(aoi).blocks():
        ids = cell_ids(grid, np.ones(grid.shape, dtype=bool))
        keep = np.isin(ids, wanted)
        if keep.any():
            yield grid, np.where(keep, ids, -1)


def cells_table(aoi: Aoi, grid: Grid, units: np.ndarray, cropland: np.ndarray) -> pl.DataFrame:
    """Cells of one block inside the AOI that are at least `MIN_CROP_FRAC` cropland, with coordinates and unit."""
    inside = units > 0
    rows, cols = np.indices(grid.shape)
    wide = grid.shape[1] // CELL_PX
    local = (rows // CELL_PX) * wide + cols // CELL_PX
    n = (grid.shape[0] // CELL_PX) * wide
    total = np.bincount(local[inside], minlength=n)
    crop = np.bincount(local[inside & cropland], minlength=n)
    # majority unit per cell: count (cell, unit) pairs, then take the most frequent unit
    n_units = len(aoi.units) + 1
    pairs = np.bincount(local[inside] * n_units + units[inside], minlength=n * n_units).reshape(n, n_units)
    keep = (total > 0) & (crop / np.maximum(total, 1) >= MIN_CROP_FRAC)
    cell_row = np.arange(n) // wide + grid.cell_row0
    cell_col = np.arange(n) % wide + grid.cell_col0
    x = grid.transform.c + (np.arange(n) % wide + 0.5) * PIXEL_M * CELL_PX
    y = grid.transform.f - (np.arange(n) // wide + 0.5) * PIXEL_M * CELL_PX
    lon, lat = transform(grid.crs, "EPSG:4326", x[keep].tolist(), y[keep].tolist())[:2]
    names = [name for name, _ in aoi.units]
    return pl.DataFrame(
        {
            "cell_id": (cell_row * grid.cells_wide + cell_col)[keep],
            "unit": [names[u - 1] for u in pairs[keep].argmax(axis=1)],
            "x": x[keep],
            "y": y[keep],
            "lon": lon,
            "lat": lat,
            "crop_frac": (crop / np.maximum(total, 1))[keep],
        },
        schema=CELLS_SCHEMA,
    )


@dataclass(frozen=True)
class Block:
    """One grid block with the global cell id of each monitored pixel (-1 elsewhere)."""

    grid: Grid
    ids: np.ndarray
    bounds: tuple[float, float, float, float]


def _overlaps(item: Item, bounds: tuple[float, float, float, float]) -> bool:
    west, south, east, north = item.get("bbox") or (-180, -90, 180, 90)
    return not (east < bounds[0] or west > bounds[2] or north < bounds[1] or south > bounds[3])


def _mosaic(
    items: list[Item],
    block: Block,
    first: str,
    rest: tuple[str, ...],
    href: Callable[[Item, str], str],
    adjust: Callable[[Item, np.ndarray], np.ndarray] = lambda _, values: values,
) -> dict[str, np.ndarray]:
    """Fill each monitored pixel from the first item (newest) that has data there.

    `first` is the asset that decides coverage. `rest` are read only where it filled and
    passed through `adjust` (per-item corrections such as a reflectance offset).
    """
    member = block.ids >= 0
    layers = {name: np.full(block.grid.shape, np.nan, dtype="float32") for name in (first, *rest)}
    for item in items:
        need = member & np.isnan(layers[first])
        if not need.any():
            break
        if not _overlaps(item, block.bounds):
            continue
        resampling = Resampling.nearest if first in ("scl", "qa_pixel") else Resampling.bilinear
        base = read_to_grid(href(item, first), block.grid, resampling)
        take = need & np.isfinite(base)
        if not take.any():
            continue
        layers[first][take] = base[take]
        for name in rest:
            layers[name][take] = adjust(item, read_to_grid(href(item, name), block.grid, Resampling.bilinear))[take]
    return layers


def _per_cell(ids: np.ndarray, values: np.ndarray, valid: np.ndarray, stat: str) -> dict[int, float]:
    frame = pl.DataFrame({"cell_id": ids[valid], "v": values[valid]})
    agg = pl.col("v").median() if stat == "median" else pl.col("v").mean()
    return dict(frame.group_by("cell_id").agg(agg).iter_rows())


def _s2_offset(item: Item, values: np.ndarray) -> np.ndarray:
    day = item["properties"]["datetime"][:10]
    applied = item["properties"].get("earthsearch:boa_offset_applied", False)
    return values - 1000 if day >= S2_OFFSET_FROM and not applied else values


def s2_rows(day: str, items: list[Item], block: Block) -> list[dict[str, Any]]:
    """Per-cell NDVI, LSWI and clear fraction for one Sentinel-2 date in one block."""
    layers = _mosaic(
        items, block, "scl", ("red", "nir", "swir16"), lambda item, asset: item["assets"][asset]["href"], _s2_offset
    )
    ids = block.ids
    member = ids >= 0
    red, nir, swir = layers["red"], layers["nir"], layers["swir16"]
    clear = member & np.isin(layers["scl"], S2_CLEAR)
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = (nir - red) / (nir + red)
        lswi = (nir - swir) / (nir + swir)
    ok = clear & np.isfinite(ndvi) & np.isfinite(lswi)
    cells, n_all = np.unique(ids[member], return_counts=True)
    n_clear = dict(zip(*np.unique(ids[ok], return_counts=True), strict=True))
    ndvi_by, lswi_by = _per_cell(ids, ndvi, ok, "median"), _per_cell(ids, lswi, ok, "median")
    return [
        {
            "cell_id": int(c),
            "date": date.fromisoformat(day),
            "sensor": "S2",
            "clear_frac": float(n_clear.get(c, 0) / n),
            "ndvi": ndvi_by.get(int(c)),
            "lswi": lswi_by.get(int(c)),
            "vv_db": None,
            "vh_db": None,
            "orbit": None,
        }
        for c, n in zip(cells, n_all, strict=True)
    ]


def s1_rows(day: str, items: list[Item], block: Block, token: str) -> list[dict[str, Any]]:
    """Per-cell mean VV and VH backscatter (dB) for one Sentinel-1 date in one block.

    Frames of one date from different orbit directions are not mixed: the first
    (newest) item's direction is used, since ascending and descending passes differ.
    Single-polarisation frames (common before 2017) are skipped.
    """
    items = [i for i in items if {"vv", "vh"} <= i["assets"].keys()]
    if not items:
        return []
    orbit = items[0]["properties"].get("sat:orbit_state")
    same_pass = [i for i in items if i["properties"].get("sat:orbit_state") == orbit]
    layers = _mosaic(same_pass, block, "vh", ("vv",), lambda item, pol: f"{item['assets'][pol]['href']}?{token}")
    ids = block.ids
    member = ids >= 0
    by_pol: dict[str, dict[int, float]] = {}
    for pol in ("vv", "vh"):
        # average in linear power, then convert, so the mean is not biased by the log
        ok = member & np.isfinite(layers[pol]) & (layers[pol] > 0)
        by_pol[pol] = {c: float(10 * np.log10(v)) for c, v in _per_cell(ids, layers[pol], ok, "mean").items()}
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
            "orbit": orbit,
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
    """The calendar month before `today`, as ``YYYY-MM``, the default for scheduled runs."""
    today = today or date.today()
    y, m = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
    return f"{y:04d}-{m:02d}"


def prepare_blocks(aoi: Aoi) -> tuple[pl.DataFrame, list[Block]]:
    """Cells table for the whole AOI, and the blocks that contain monitored cells."""
    tables, blocks = [], []
    for grid in make_grid(aoi).blocks():
        units = unit_raster(aoi, grid)
        if not units.any():
            continue
        cropland = read_cropland(aoi, grid)
        table = cells_table(aoi, grid, units, cropland)
        if table.is_empty():
            continue
        keep = np.isin(cell_ids(grid, np.ones(grid.shape, dtype=bool)), table["cell_id"].to_numpy())
        tables.append(table)
        blocks.append(Block(grid, cell_ids(grid, (units > 0) & cropland & keep), grid.lonlat_bounds()))
    return (pl.concat(tables) if tables else pl.DataFrame(schema=CELLS_SCHEMA)), blocks


def run_sentinel_pipeline(
    aoi_spec: str = DEFAULT_AOI, start: str | None = None, end: str | None = None, out_dir: str | Path = "data"
) -> dict[str, Any]:
    """Build bronze cell x date tables for an AOI, one parquet file per month.

    Each month is written on its own, so a scheduled run can process only the month it
    needs without reading earlier output, and a rerun overwrites the same file.

    Args:
        aoi_spec: GADM path (e.g. ``Lamongan/Tikung``) or GeoJSON path, see `aoi.resolve`.
        start: First month, ``YYYY-MM``. Defaults to the previous calendar month.
        end: Last month, ``YYYY-MM``. Defaults to `start`.
        out_dir: Data root.

    Returns:
        Cell, unit and block counts and, per month, date and row counts.

    Raises:
        ValueError: If the AOI has no cropland cells to monitor.
    """
    start = start or previous_month()
    end = end or start
    aoi = resolve(aoi_spec)
    cells, blocks = prepare_blocks(aoi)
    if cells.is_empty():
        raise ValueError(f"{aoi.slug}: no cell is at least {MIN_CROP_FRAC:.0%} WorldCover cropland.")

    aoi_dir = Path(out_dir) / "bronze" / "sentinel" / aoi.slug
    save(cells, aoi_dir / "cells.parquet")
    bbox = aoi.bounds()
    summary: dict[str, Any] = {
        "aoi": aoi.slug,
        "units": len(aoi.units),
        "cells": cells.height,
        "blocks": len(blocks),
        "months": {},
    }
    for month in month_range(start, end):
        s2_dates = stac_search(EARTH_SEARCH, "sentinel-2-l2a", bbox, month)
        s1_dates = stac_search(PLANETARY, "sentinel-1-rtc", bbox, month)
        # SAS tokens expire after about an hour
        # and fetching a month can take minutes
        token = pc_token()
        with ThreadPoolExecutor(WORKERS) as pool:
            futures = [pool.submit(s2_rows, day, items, b) for day, items in s2_dates.items() for b in blocks]
            futures += [pool.submit(s1_rows, day, items, b, token) for day, items in s1_dates.items() for b in blocks]
            rows = [row for future in futures for row in future.result()]
        bronze = pl.DataFrame(rows, schema=BRONZE_SCHEMA).sort("sensor", "date", "cell_id")
        save(bronze, aoi_dir / f"{month}.parquet")
        summary["months"][month] = {"s2_dates": len(s2_dates), "s1_dates": len(s1_dates), "rows": bronze.height}
        print(
            f"[sentinel] {aoi.slug} {month}: {len(s2_dates)} S2 dates, {len(s1_dates)} S1 dates, {bronze.height} rows"
        )
    return summary


if __name__ == "__main__":
    # load_sentinel [AOI] [START_MONTH] [END_MONTH], no months = previous month
    args = sys.argv[1:] + [None] * 3
    print(run_sentinel_pipeline(args[0] or DEFAULT_AOI, args[1], args[2]))
