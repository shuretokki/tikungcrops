"""Batch pipelines: synthetic generators, external sources (SoilGrids, CHIRPS, CIMMYT) and the MongoDB load.

Synthetic data is a stand-in while the mitra has not supplied real records. Its
parameters come from sources (data/raw/sumber-data/README.md), and every row carries
its seed and generation time.
"""

from pathlib import Path

import polars as pl


def save(df: pl.DataFrame, path: Path) -> str:
    """Write `df` as parquet, creating parent directories.

    Returns:
        The written path, for the run summary.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path)
    return str(path)
