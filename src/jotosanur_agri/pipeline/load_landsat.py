# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Landsat 8 and 9 NDVI and LSWI per 100 m cell, to fill optical gaps (bronze).

Sentinel-1 passes fell from about 57 to about 30 a year in 2022 to 2024, when Sentinel-1B was lost, and
cloud hides many Sentinel-2 dates, so the planting and harvest forecast lost observations.
Landsat Collection 2 Level 2 on Microsoft Planetary Computer is open without a login and adds
about 57 to 72 scenes a year with less than 50 percent cloud over Tikung.

It reuses the cell grid and the block mosaic of `load_sentinel`, so a cell has the same id in both.
Reflectance is the Collection 2 scaling (DN x 0.0000275 - 0.2), a cell counts as clear when no
QA_PIXEL flag from fill to snow is set, and the median NDVI and LSWI of the clear pixels is kept.
No Landsat to Sentinel-2 band adjustment is applied, because the back-test is the judge of whether
the extra dates help.

Output: data/bronze/landsat/<aoi-slug>/<YYYY-MM>.parquet with the same columns as the Sentinel bronze,
sensor "LS". Usage: `python -m jotosanur_agri.pipeline.load_landsat [AOI] [START_MONTH] [END_MONTH]`.
"""

from __future__ import annotations

import json
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
from jotosanur_agri.pipeline.load_sentinel import (
    BRONZE_SCHEMA,
    DEFAULT_AOI,
    PLANETARY,
    WORKERS,
    Block,
    Item,
    _mosaic,
    _per_cell,
    month_range,
    prepare_blocks,
    previous_month,
    stac_search,
)

COLLECTION = "landsat-c2-l2"
TOKEN_URL = "https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2"
SENSOR = "LS"
SCALE, OFFSET = 0.0000275, -0.2
QA_BAD = 0b111111  # fill, dilated cloud, cirrus, cloud, cloud shadow, snow


def token() -> str:
    """Anonymous SAS token for the Landsat storage on Planetary Computer."""
    with urllib.request.urlopen(TOKEN_URL, timeout=60) as resp:
        return json.load(resp)["token"]


def _reflectance(_: Item, values: np.ndarray) -> np.ndarray:
    """Convert Collection 2 digital numbers to surface reflectance, fill value 0 stays missing."""
    return np.where(values > 0, values * SCALE + OFFSET, np.nan)


def ls_rows(day: str, items: list[Item], block: Block, sas: str) -> list[dict[str, Any]]:
    """Per-cell NDVI, LSWI and clear fraction for one Landsat date in one block."""
    items = [i for i in items if {"qa_pixel", "red", "nir08", "swir16"} <= i["assets"].keys()]
    if not items:
        return []
    layers = _mosaic(
        items,
        block,
        "qa_pixel",
        ("red", "nir08", "swir16"),
        lambda i, a: f"{i['assets'][a]['href']}?{sas}",
        _reflectance,
    )
    ids = block.ids
    member = ids >= 0
    qa = layers["qa_pixel"]
    clear = member & np.isfinite(qa) & ((np.nan_to_num(qa).astype("int64") & QA_BAD) == 0)
    red, nir, swir = layers["red"], layers["nir08"], layers["swir16"]
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
            "sensor": SENSOR,
            "clear_frac": float(n_clear.get(c, 0) / n),
            "ndvi": ndvi_by.get(int(c)),
            "lswi": lswi_by.get(int(c)),
            "vv_db": None,
            "vh_db": None,
            "orbit": None,
        }
        for c, n in zip(cells, n_all, strict=True)
    ]


def run_landsat_pipeline(
    aoi_spec: str = DEFAULT_AOI, start: str | None = None, end: str | None = None, out_dir: str | Path = "data"
) -> dict[str, Any]:
    """Build the Landsat bronze table of an AOI, one parquet file per month.

    Args:
        aoi_spec: GADM path (e.g. ``Lamongan/Tikung``) or GeoJSON path, see `aoi.resolve`.
        start: First month, ``YYYY-MM``. Defaults to the previous calendar month.
        end: Last month, ``YYYY-MM``. Defaults to `start`.
        out_dir: Data root.

    Returns:
        Per month, the number of dates and rows.
    """
    start = start or previous_month()
    end = end or start
    aoi = resolve(aoi_spec)
    _, blocks = prepare_blocks(aoi)
    aoi_dir = Path(out_dir) / "bronze" / "landsat" / aoi.slug
    summary: dict[str, Any] = {"aoi": aoi.slug, "months": {}}
    for month in month_range(start, end):
        dates = stac_search(PLANETARY, COLLECTION, aoi.bounds(), month)
        sas = token()
        with ThreadPoolExecutor(WORKERS) as pool:
            futures = [pool.submit(ls_rows, day, items, b, sas) for day, items in dates.items() for b in blocks]
            rows = [row for future in futures for row in future.result()]
        bronze = pl.DataFrame(rows, schema=BRONZE_SCHEMA).sort("date", "cell_id")
        save(bronze, aoi_dir / f"{month}.parquet")
        summary["months"][month] = {"dates": len(dates), "rows": bronze.height}
        print(f"[landsat] {aoi.slug} {month}: {len(dates)} dates, {bronze.height} rows", flush=True)
    return summary


if __name__ == "__main__":
    # load_landsat [AOI] [START_MONTH] [END_MONTH], no months = previous month
    args = sys.argv[1:] + [None] * 3
    print(run_landsat_pipeline(args[0] or DEFAULT_AOI, args[1], args[2]))
