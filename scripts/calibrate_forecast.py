"""Calibrate the harvest forecast ranges from a replay, and check the calibration on later dates.

Reads `<aoi>_backtest_cells.parquet` from `scripts/backtest_forecast.py`, keeps the dates since the radar
returned to a 6-day pass (the regime that is running now), and takes the 10 % and 90 % quantiles of
actual minus forecast days per forecast kind, at the level of one cell and at the level of one desa
(the median of its cells). This is split conformal prediction: the offsets are added to the point forecast
to make a range that should cover the harvest 80 % of the time.
The offsets are first fitted on the earlier two thirds of the dates and scored on the last third, and the
file is written from all dates.

Output: data/gold/sentinel/<aoi>_calibration.json, read by `harvest_outlook.run_outlook`.
Run from the project root:
    nix develop -c uv run --no-sync python scripts/calibrate_forecast.py [DATA_DIR]
"""

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl

from tikungcrops.pipeline.aoi import resolve
from tikungcrops.pipeline.harvest_outlook import MIN_DESA_CELLS
from tikungcrops.pipeline.load_sentinel import DEFAULT_AOI

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "data")
GOLD = DATA / "gold" / "sentinel"
SLUG = resolve(DEFAULT_AOI).slug
SINCE = date(2025, 6, 1)  # Sentinel-1C calibrated on 19 May 2025, so the 6-day radar pass is back
ALPHA = 0.2


def offsets(residuals: np.ndarray) -> tuple[int, int]:
    """Return the low and high offsets in days that cover 1 - ALPHA of the residuals (split conformal)."""
    n = len(residuals)
    low = np.quantile(residuals, max(0.0, (ALPHA / 2) * (n + 1) / n), method="lower")
    high = np.quantile(residuals, min(1.0, (1 - ALPHA / 2) * (n + 1) / n), method="higher")
    return int(low), int(high)


def cell_level(df: pl.DataFrame) -> pl.DataFrame:
    """One row per forecast cell with the residual in days (actual minus forecast)."""
    return df.select("as_of", "forecast", (pl.col("actual") - pl.col("harvest")).dt.total_days().alias("residual"))


def desa_level(df: pl.DataFrame) -> pl.DataFrame:
    """One row per desa, date and forecast kind with the residual of the median of its cells."""
    return (
        df.with_columns(pl.col("actual").cast(pl.Int32).alias("a"), pl.col("harvest").cast(pl.Int32).alias("h"))
        .group_by("as_of", "unit", "forecast")
        .agg(pl.len().alias("n"), pl.col("a").median().alias("a"), pl.col("h").median().alias("h"))
        .filter(pl.col("n") >= MIN_DESA_CELLS)
        .select("as_of", "forecast", (pl.col("a") - pl.col("h")).round().alias("residual"))
    )


def fit(frame: pl.DataFrame) -> dict[str, dict[str, int]]:
    """Offsets per forecast kind."""
    out = {}
    for kind in ("planting", "peak"):
        r = frame.filter(pl.col("forecast") == kind)["residual"].to_numpy()
        if len(r) >= 50:
            low, high = offsets(r)
            out[kind] = {"low": low, "high": high, "n": len(r)}
    return out


def coverage(frame: pl.DataFrame, fitted: dict[str, dict[str, int]]) -> dict[str, float]:
    """Share of residuals inside the fitted offsets, per forecast kind."""
    out = {}
    for kind, o in fitted.items():
        r = frame.filter(pl.col("forecast") == kind)["residual"].to_numpy()
        if len(r):
            out[kind] = float(np.mean((r >= o["low"]) & (r <= o["high"])))
    return out


def main() -> None:
    """Fit, check on the last third of the dates, and write the calibration file."""
    df = pl.read_parquet(GOLD / f"{SLUG}_backtest_cells.parquet").filter(
        pl.col("actual").is_not_null(), pl.col("as_of") >= pl.lit(SINCE)
    )
    dates = df["as_of"].unique().sort().to_list()
    cut = dates[int(len(dates) * 2 / 3)]
    print(f"{df.height} scored cells on {len(dates)} dates since {SINCE}; fitting before {cut}, testing from {cut}")
    result: dict[str, object] = {
        "alpha": ALPHA,
        "since": SINCE.isoformat(),
        "dates": len(dates),
        "generated": date.today().isoformat(),
    }
    for level, make in (("cell", cell_level), ("desa", desa_level)):
        frame = make(df)
        early, late = frame.filter(pl.col("as_of") < pl.lit(cut)), frame.filter(pl.col("as_of") >= pl.lit(cut))
        check = fit(early)
        print(f"{level}: fitted before the cut {check}")
        print(f"{level}: coverage on the later dates {coverage(late, check)} (target {1 - ALPHA:.0%})")
        result[level] = fit(frame)
        print(f"{level}: offsets from all dates {result[level]}")
    out = GOLD / f"{SLUG}_calibration.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
