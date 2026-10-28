# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Paddy share per cell from the official Lahan Baku Sawah (LBS) map.

WorldCover's cropland class mixes rice, maize and dry fields. The national paddy field
map (Peta Lahan Baku Sawah, scale 1:50,000 or finer) is published by BIG as an open
ArcGIS REST layer with GeoJSON output. Its polygons are rasterized onto the Sentinel grid
of an AOI and summarised per 100 m cell.

The polygons are cached under data/external/lbs/ (not tracked: redistribution terms are
not stated by the service).

Output: data/bronze/sentinel/<aoi-slug>/paddy.parquet with `cell_id` and `paddy_frac`
(share of the cell's pixels inside LBS paddy), for every cell in cells.parquet.
Usage: `python -m jotosanur_agri.pipeline.load_paddy [AOI]`.
"""

from __future__ import annotations

import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from rasterio.features import rasterize
from rasterio.warp import transform_geom

from jotosanur_agri.pipeline import save
from jotosanur_agri.pipeline.aoi import Aoi, resolve
from jotosanur_agri.pipeline.load_sentinel import CELL_PX, DEFAULT_AOI, cell_ids, make_grid, unit_raster

LBS_URL = (
    "https://kspservices.big.go.id/satupeta/rest/services/PUBLIK/SUMBER_DAYA_ALAM_DAN_LINGKUNGAN/MapServer/36/query"
)
LBS_DIR = Path("data/external/lbs")
PAGE_SIZE = 1000  # service's MaxRecordCount
# The service times out (HTTP 500 after about 60 s) on a kabupaten-sized envelope,
# while a 0.1 degree envelope answers in about 2 s, so large AOIs are queried tile by tile.
TILE_DEG = 0.1
RETRY_WAIT_S = (5, 15, 45)


def _tiles(west: float, south: float, east: float, north: float, step: float = TILE_DEG) -> list[tuple[float, ...]]:
    """Envelopes of at most `step` degrees that cover the bounds, row by row from the south-west."""
    nx = max(1, math.ceil((east - west) / step))
    ny = max(1, math.ceil((north - south) / step))
    dx, dy = (east - west) / nx, (north - south) / ny
    return [
        (west + i * dx, south + j * dy, west + (i + 1) * dx, south + (j + 1) * dy) for j in range(ny) for i in range(nx)
    ]


def _get(params: dict[str, str]) -> list[dict[str, Any]]:
    """One query page, retried on server errors and timeouts with a growing wait."""
    url = f"{LBS_URL}?{urllib.parse.urlencode(params)}"
    for wait in (*RETRY_WAIT_S, None):
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                return json.load(resp)["features"]
        except (urllib.error.URLError, TimeoutError) as err:
            client_error = isinstance(err, urllib.error.HTTPError) and err.code < 500
            if client_error or wait is None:
                raise
            time.sleep(wait)
    raise AssertionError("unreachable")


def fetch_lbs(aoi: Aoi) -> list[dict[str, Any]]:
    """LBS paddy polygons (GeoJSON features, lon/lat) intersecting the AOI bounds, cached per AOI.

    A polygon that crosses a tile edge comes back from both tiles, so features are kept once by
    `objectid`.
    """
    cached = LBS_DIR / f"{aoi.slug}.geojson"
    if cached.exists():
        return json.loads(cached.read_text())["features"]
    by_id: dict[Any, dict[str, Any]] = {}
    for west, south, east, north in _tiles(*aoi.bounds()):
        offset = 0
        while True:
            page = _get(
                {
                    "where": "1=1",
                    "geometry": f"{west},{south},{east},{north}",
                    "geometryType": "esriGeometryEnvelope",
                    "inSR": "4326",
                    "spatialRel": "esriSpatialRelIntersects",
                    "outFields": "objectid,wadmkk,q_name19,luas_polyg",
                    "outSR": "4326",
                    "resultOffset": str(offset),
                    "resultRecordCount": str(PAGE_SIZE),
                    "f": "geojson",
                }
            )
            for f in page:
                by_id.setdefault(f.get("properties", {}).get("objectid", id(f)), f)
            offset += len(page)
            if len(page) < PAGE_SIZE:
                break
    features = list(by_id.values())
    LBS_DIR.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    return features


def run_paddy(aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data") -> dict[str, Any]:
    """Write per-cell paddy shares for an AOI whose bronze cells already exist.

    Returns:
        Polygon and cell counts, the paddy area inside and outside the monitored cells,
        and the output path.
    """
    aoi = resolve(aoi_spec)
    cells_dir = Path(data_dir) / "bronze" / "sentinel" / aoi.slug
    out = cells_dir / "paddy.parquet"
    cells = pl.read_parquet(cells_dir / "cells.parquet")
    full = make_grid(aoi)
    features = [f for f in fetch_lbs(aoi) if f.get("geometry")]
    if not features:
        # no LBS coverage (outside Indonesia, or no mapped paddy)
        # gold then weights cells by 1
        out.unlink(missing_ok=True)
        return {"polygons": 0, "cells": cells.height, "path": None}
    shapes = [(transform_geom("EPSG:4326", full.crs, f["geometry"]), 1) for f in features]

    wanted = cells["cell_id"].to_numpy()
    counts: dict[int, int] = {}
    inside_px = outside_px = 0
    for grid in full.blocks():
        units = unit_raster(aoi, grid)
        if not units.any():
            continue
        paddy = np.asarray(rasterize(shapes, out_shape=grid.shape, transform=grid.transform, dtype="uint8"), dtype=bool)
        paddy &= units > 0
        ids = cell_ids(grid, paddy)
        monitored = np.isin(ids, wanted)
        # how much LBS paddy the cropland cells miss
        # cells were chosen from WorldCover
        inside_px += int(monitored.sum())
        outside_px += int((paddy & ~monitored).sum())
        cell, n = np.unique(ids[monitored], return_counts=True)
        counts.update(zip(cell.tolist(), n.tolist(), strict=True))

    frac = [counts.get(int(c), 0) / CELL_PX**2 for c in wanted]
    table = cells.select("cell_id").with_columns(pl.Series("paddy_frac", frac, dtype=pl.Float64))
    pixel_ha = (full.transform.a**2) / 10_000
    return {
        "polygons": len(shapes),
        "cells": cells.height,
        "cells_mostly_paddy": int((table["paddy_frac"] >= 0.5).sum()),
        "paddy_ha_in_cells": round(inside_px * pixel_ha, 1),
        "paddy_ha_outside_cells": round(outside_px * pixel_ha, 1),
        "path": save(table, out),
    }


if __name__ == "__main__":
    print(run_paddy(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI))
