"""Soil properties per cell and per unit of an AOI from the SoilGrids 2.0 global maps.

Source: ISRIC SoilGrids 2.0 (Poggio et al., 2021), 250 m, CC BY 4.0. The global
predictions are published as Cloud-Optimized GeoTIFFs behind VRT mosaics, so only the
tiles covering the AOI are read over HTTP; no REST API calls or rate limits.

Values are stored as integers in "mapped units"; dividing by `D_FACTOR` gives the
target units (e.g. clay in %, pH in pH units, bulk density in kg/dm3). Each cell gets
the mean of its 10 m pixels (nearest-resampled from 250 m), and each unit the median of
its cells.

Outputs: data/silver/soilgrids/<aoi-slug>_cells.parquet (cell_id plus one column per
property and depth, e.g. `clay_0_5cm`) and <aoi-slug>_units.parquet (median per unit).
Usage: `python -m jotosanur_agri.pipeline.load_soilgrids [AOI]`.
"""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from rasterio.warp import Resampling

from jotosanur_agri.pipeline import save
from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI, monitored_blocks, read_to_grid

VRT_URL = "/vsicurl/https://files.isric.org/soilgrids/latest/data/{prop}/{prop}_{depth}_mean.vrt"

# Mapped value / D_FACTOR = target units (SoilGrids 2.0 documentation)
D_FACTOR = {
    "bdod": 100,  # kg/dm3
    "cfvo": 10,  # vol %
    "clay": 10,  # %
    "nitrogen": 100,  # g/kg
    "ocd": 10,  # kg/m3
    "phh2o": 10,  # pH
    "sand": 10,  # %
    "silt": 10,  # %
    "soc": 10,  # g/kg
}
# Rice roots stay mostly in the top 30 cm
DEPTHS = ["0-5cm", "5-15cm", "15-30cm"]
WORKERS = 4


def column(prop: str, depth: str) -> str:
    """Output column name, e.g. ``clay_0_5cm``."""
    return f"{prop}_{depth.replace('-', '_')}"


def run_soilgrids_pipeline(aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data") -> dict[str, Any]:
    """Read every property and depth onto the AOI's cells and write cell and unit tables.

    Returns:
        Cell and unit counts, the share of cells with complete values, and output paths.
    """
    aoi = resolve(aoi_spec)
    cells = pl.read_parquet(Path(data_dir) / "bronze" / "sentinel" / aoi.slug / "cells.parquet")
    blocks = list(monitored_blocks(aoi, cells))

    def per_cell(layer: tuple[str, str]) -> tuple[str, dict[int, float]]:
        prop, depth = layer
        by_cell: dict[int, float] = {}
        for grid, ids in blocks:
            values = read_to_grid(VRT_URL.format(prop=prop, depth=depth), grid, Resampling.nearest) / D_FACTOR[prop]
            ok = (ids >= 0) & np.isfinite(values)
            frame = pl.DataFrame({"cell_id": ids[ok], "v": values[ok]})
            by_cell.update(frame.group_by("cell_id").agg(pl.col("v").mean()).iter_rows())
        return column(prop, depth), by_cell

    layers = [(prop, depth) for prop in D_FACTOR for depth in DEPTHS]
    with ThreadPoolExecutor(WORKERS) as pool:
        results = dict(pool.map(per_cell, layers))

    table = cells.select("cell_id", "unit").with_columns(
        pl.Series(name, [by_cell.get(c) for c in cells["cell_id"].to_list()], dtype=pl.Float64)
        for name, by_cell in results.items()
    )
    unit_table = table.drop("cell_id").group_by("unit").median().sort("unit")
    out = Path(data_dir) / "silver" / "soilgrids"
    return {
        "cells": table.height,
        "units": unit_table.height,
        "layers": len(layers),
        "complete_cells": round(table.drop_nulls().height / max(table.height, 1), 3),
        "cells_path": save(table, out / f"{aoi.slug}_cells.parquet"),
        "units_path": save(unit_table, out / f"{aoi.slug}_units.parquet"),
    }


if __name__ == "__main__":
    print(run_soilgrids_pipeline(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI))
