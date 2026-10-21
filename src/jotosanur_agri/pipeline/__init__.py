# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Batch pipelines.

- Satellite crop monitoring for an area of interest: `aoi`, `load_sentinel` (bronze),
  `silver_sentinel`, `gold_sentinel`, `load_paddy` (official paddy map).
- Context layers: `load_chirps` (rainfall), `load_soilgrids` (soil).
- `load_mongo`: syncs BPS/Dinas tables and satellite season summaries into MongoDB.
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
