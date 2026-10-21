"""Export one AOI's gold results as static JSON for the public web app.

The web app has no server: it reads these files at build time. Data changes once a month,
so a static export is enough.

Outputs in data/web/<aoi-slug>/, all row-oriented JSON:
    - meta.json: AOI slug, series end date, export time, units with cell count, paddy
      area and centre, and which of the files below exist.
    - cells.json: one row per 100 m cell with position, unit, paddy share and current
      stage. The map draws these points. GADM boundaries are not exported, because
      their licence forbids redistribution.
    - current.json: paddy hectares per unit and current stage.
    - seasons.json: per unit, year and season (`summarize_units`).
    - intensity.json: cropping intensity per unit and year (`intensity_units`).
    - outlook.json: expected harvested hectares per unit and week (`harvest_outlook`).
    - rain.json: CHIRPS monthly rainfall per unit from `RAIN_FROM_YEAR`.
    - validation.json: satellite vs reference areas, and harvest forecast scores.
A missing input skips its file, e.g. an area without reference data has no validation.

Usage: `python -m jotosanur_agri.pipeline.export_web [AOI]` (default Lamongan/Tikung).
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl

from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

# satellite seasons start in late 2017, older rain adds size but no comparison
RAIN_FROM_YEAR = 2017


def _write(df: pl.DataFrame, path: Path) -> str:
    """Write `df` as a JSON array of row objects with floats rounded to 3 decimals."""
    df = df.with_columns(pl.col(pl.Float64).round(3))
    path.write_text(df.write_json())
    return path.name


def _read(path: Path) -> pl.DataFrame | None:
    """Parquet or CSV at `path`, or None when it is missing or empty."""
    if not path.exists() or not path.stat().st_size:
        return None
    df = pl.read_csv(path) if path.suffix == ".csv" else pl.read_parquet(path)
    return df if df.height else None


def run_export_web(aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data") -> dict[str, Any]:
    """Write the web JSON files for one AOI.

    Returns:
        The output directory and the files written.

    Raises:
        FileNotFoundError: If the AOI has no Sentinel cells or gold seasons yet.
    """
    data = Path(data_dir)
    slug = resolve(aoi_spec).slug
    bronze = data / "bronze" / "sentinel" / slug
    gold = data / "gold" / "sentinel"
    if not (bronze / "cells.parquet").exists() or not (gold / f"{slug}_seasons.parquet").exists():
        raise FileNotFoundError(f"no cells or gold seasons for {slug}, run `just sentinel` and `just setup` first")
    out = data / "web" / slug
    out.mkdir(parents=True, exist_ok=True)

    cells = pl.read_parquet(bronze / "cells.parquet").select("cell_id", "unit", "lon", "lat")
    paddy = _read(bronze / "paddy.parquet")
    cells = (
        cells.join(paddy, on="cell_id", how="left").with_columns(pl.col("paddy_frac").fill_null(0.0))
        if paddy is not None
        else cells.with_columns(pl.lit(1.0).alias("paddy_frac"))
    )
    current = pl.read_parquet(gold / f"{slug}_current.parquet").select("cell_id", "as_of", "stage")
    cells = cells.join(current.drop("as_of"), on="cell_id", how="left")

    files = [_write(cells.with_columns(pl.col("lon", "lat").round(5)), out / "cells.json")]
    files.append(
        _write(
            cells.group_by("unit", "stage").agg(pl.col("paddy_frac").sum().alias("paddy_ha")).sort("unit", "stage"),
            out / "current.json",
        )
    )
    for name, source in (
        ("seasons", gold / f"{slug}_units.parquet"),
        ("intensity", gold / f"{slug}_intensity.parquet"),
        ("outlook", gold / f"{slug}_outlook_weekly.parquet"),
    ):
        df = _read(source)
        if df is not None:
            files.append(_write(df, out / f"{name}.json"))

    rain = _read(data / "silver" / "chirps" / f"{slug}_monthly.parquet")
    if rain is not None:
        rain = rain.filter(pl.col("year") >= RAIN_FROM_YEAR).select(
            "unit", "year", "month", "precip_mm", "normal_mm", "anomaly_pct"
        )
        files.append(_write(rain, out / "rain.json"))

    parts = {
        "area": _read(gold / f"{slug}_validation.csv"),
        "area_units": _read(gold / f"{slug}_validation_units.csv"),
        "forecast": _read(gold / f"{slug}_forecast_eval.csv"),
    }
    if any(df is not None for df in parts.values()):
        validation = {k: json.loads(df.write_json()) if df is not None else [] for k, df in parts.items()}
        (out / "validation.json").write_text(json.dumps(validation))
        files.append("validation.json")

    units = (
        cells.group_by("unit")
        .agg(
            pl.len().alias("cells"),
            pl.col("paddy_frac").sum().round(1).alias("paddy_ha"),
            pl.col("lon").mean().round(5),
            pl.col("lat").mean().round(5),
        )
        .sort("unit")
    )
    meta = {
        "aoi": slug,
        "as_of": str(current["as_of"].max()),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "units": units.to_dicts(),
        "files": files,
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False))
    return {"dir": str(out), "files": ["meta.json", *files]}


if __name__ == "__main__":
    print(run_export_web(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI))
