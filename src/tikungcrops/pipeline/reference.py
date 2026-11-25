# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Reader for an AOI's reference statistics (data/reference/<aoi>/harvested_area.csv).

The file is typed in by hand, so it is checked before anything uses it, and every
problem is reported at once with its line number:
    - required columns present (order free, extra columns ignored).
    - `year` an integer in `YEARS`, areas and production non-negative numbers, `source`
      not empty.
    - `unit` names match the AOI's units. Spacing and case are forgiven (``joto sanur``
      becomes ``Jotosanur``), anything else is listed next to the valid names.
    - no duplicate unit x year x crop rows, which would be double counted.

Crop names are normalised to lowercase with underscores (``Padi Sawah`` -> ``padi_sawah``).
A spreadsheet export with ``;`` separators and Indonesian number format (``1.234,5``) is
read as well. A missing or header-only file means the AOI has no reference
data.
"""

from __future__ import annotations

import re
from pathlib import Path

import polars as pl

from tikungcrops.pipeline.aoi import Aoi

REQUIRED = ["unit", "year", "crop", "harvested_area_ha", "source"]
MAX_LISTED = 10
# same bounds as the MongoDB validator
YEARS = (1900, 2100)


class ReferenceDataError(ValueError):
    """The reference file exists but cannot be used as is."""


def reference_path(aoi: Aoi, data_dir: str | Path = "data") -> Path:
    """Where an AOI's reference statistics live."""
    return Path(data_dir) / "reference" / aoi.slug / "harvested_area.csv"


def _squash(name: str) -> str:
    return re.sub(r"\s+", "", name).lower()


def _lines(df: pl.DataFrame, mask: pl.Series) -> str:
    lines = [str(i + 2) for i in df.with_row_index().filter(mask)["index"].to_list()]
    more = f" (+{len(lines) - MAX_LISTED} more)" if len(lines) > MAX_LISTED else ""
    return ", ".join(lines[:MAX_LISTED]) + more


def _read_text_table(path: Path) -> pl.DataFrame:
    header = path.read_text(encoding="utf-8-sig").splitlines()[0] if path.stat().st_size else ""
    semicolon = header.count(";") > header.count(",")
    df = pl.read_csv(path, separator=";" if semicolon else ",", infer_schema=False, encoding="utf8-lossy")
    df = df.rename({c: c.lstrip("﻿").strip().lower() for c in df.columns})
    if semicolon:
        # Indonesian number format goes with semicolon separators: 1.234,5 -> 1234.5
        number = r"^-?\d{1,3}(\.\d{3})*(,\d+)?$|^-?\d+(,\d+)?$"
        df = df.with_columns(
            pl.when(pl.col(c).str.contains(number))
            .then(pl.col(c).str.replace_all(r"\.", "").str.replace(",", "."))
            .otherwise(pl.col(c))
            .alias(c)
            for c in df.columns
        )
    return df.with_columns(pl.col(pl.Utf8).str.strip_chars())


def read_reference(aoi: Aoi, data_dir: str | Path = "data") -> pl.DataFrame | None:
    """The AOI's checked reference rows, or None when it has none.

    Returns:
        Columns `unit` (canonical AOI name), `year`, `crop` (normalised),
        `harvested_area_ha`, `production_ton` (null when absent) and `source`.

    Raises:
        ReferenceDataError: Listing every problem found in the file.
    """
    path = reference_path(aoi, data_dir)
    if not path.exists() or path.stat().st_size == 0:
        return None
    raw = _read_text_table(path)
    if raw.is_empty():
        return None

    missing = [c for c in REQUIRED if c not in raw.columns]
    if missing:
        raise ReferenceDataError(
            f"{path}: missing column(s) {missing}, found {raw.columns}. See data/reference/README.md."
        )
    if "production_ton" not in raw.columns:
        raw = raw.with_columns(pl.lit(None, pl.Utf8).alias("production_ton"))

    df = raw.select(
        pl.col("unit"),
        pl.col("year").cast(pl.Int64, strict=False),
        pl.col("crop").str.to_lowercase().str.replace_all(r"[\s\-]+", "_"),
        pl.col("harvested_area_ha").cast(pl.Float64, strict=False),
        pl.col("production_ton").replace("", None).cast(pl.Float64, strict=False),
        pl.col("source"),
    )
    problems = []
    checks = [
        (df["year"].is_null(), "`year` is not an integer"),
        (~df["year"].is_between(*YEARS), f"`year` outside {YEARS[0]}-{YEARS[1]}"),
        (df["harvested_area_ha"].is_null(), "`harvested_area_ha` is not a number"),
        (df["harvested_area_ha"] < 0, "`harvested_area_ha` is negative"),
        (
            raw["production_ton"].is_not_null() & (raw["production_ton"] != "") & df["production_ton"].is_null(),
            "`production_ton` is not a number",
        ),
        (df["production_ton"] < 0, "`production_ton` is negative"),
        (df["unit"].is_null() | (df["unit"] == ""), "`unit` is empty"),
        (df["crop"].is_null() | (df["crop"] == ""), "`crop` is empty"),
        (df["source"].is_null() | (df["source"] == ""), "`source` is empty"),
    ]
    for mask, message in checks:
        mask = mask.fill_null(False)
        if mask.any():
            problems.append(f"{message} on line(s) {_lines(df, mask)}")

    canonical = {_squash(name): name for name, _ in aoi.units}
    df = df.with_columns(pl.col("unit").map_elements(lambda u: canonical.get(_squash(u), u), return_dtype=pl.Utf8))
    unknown = sorted(set(df["unit"].drop_nulls().to_list()) - set(canonical.values()) - {""})
    if unknown:
        listed = ", ".join(unknown[:MAX_LISTED]) + (" ..." if len(unknown) > MAX_LISTED else "")
        problems.append(f"unknown unit(s): {listed}. Units of {aoi.slug}: {', '.join(sorted(canonical.values()))}")

    duplicated = df.select("unit", "year", "crop").is_duplicated()
    if duplicated.any():
        problems.append(f"duplicate unit x year x crop on line(s) {_lines(df, duplicated)}")

    if problems:
        raise ReferenceDataError(f"{path}:\n  - " + "\n  - ".join(problems))
    return df
