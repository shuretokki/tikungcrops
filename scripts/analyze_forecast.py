"""Study how to make the harvest forecast better, from the replay saved by `backtest_forecast.py`.

Four questions, each from the research notes in FINDING.local.md:
    1. Does the error follow the radar data era? (rolling-origin evaluation)
    2. Do split-conformal ranges reach their nominal 80 % coverage on later dates?
    3. Does blending the cell model with the desa's own median duration beat either alone?
    4. Does the error fall when a cell has been seen for longer since its anchor date?

Output: a text report on screen and in data/gold/sentinel/forecast_study.txt.
Run from the project root:
    nix develop -c uv run --no-sync python scripts/analyze_forecast.py [DATA_DIR]
"""

import sys
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl

from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

ROOT = Path(__file__).resolve().parent.parent
SLUG = resolve(DEFAULT_AOI).slug
DATA = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "data")
GOLD = DATA / "gold" / "sentinel"
RADAR_RECOVERED = date(2025, 6, 1)  # Sentinel-1C calibrated on 19 May 2025, so 6-day passes are back
CUTOFF = date(2025, 10, 1)  # ranges are calibrated before this date and tested after it
ALPHA = 0.2
MIN_CELLS = 10

OUT: list[str] = []


def show(title: str, frame: pl.DataFrame) -> None:
    """Print a titled table and keep it for the report file."""
    with pl.Config(tbl_rows=40, tbl_cols=14, float_precision=2, tbl_width_chars=160):
        text = f"\n== {title}\n{frame}"
    print(text)
    OUT.append(text)


def load() -> pl.DataFrame:
    """Load the replay, keep forecasts that have a detected harvest, and add signed error, age and era."""
    df = pl.read_parquet(GOLD / f"{SLUG}_backtest_cells.parquet").filter(pl.col("actual").is_not_null())
    return df.with_columns(
        (pl.col("actual") - pl.col("harvest")).dt.total_days().alias("signed"),
        (pl.col("as_of") - pl.col("anchor_date")).dt.total_days().alias("age"),
        (pl.col("harvest_high") - pl.col("harvest_low")).dt.total_days().alias("width"),
        pl.when(pl.col("as_of") < RADAR_RECOVERED)
        .then(pl.lit("1 radar every 12 days"))
        .otherwise(pl.lit("2 radar every 6 days"))
        .alias("era"),
    )


def by_era(df: pl.DataFrame) -> None:
    """Question 1: error and range coverage per forecast kind and radar era."""
    show(
        "1. error by radar era (signed > 0 means the forecast was too early)",
        df.group_by("forecast", "era")
        .agg(
            pl.len().alias("n"),
            pl.col("as_of").n_unique().alias("dates"),
            pl.col("err").mean().alias("mae_days"),
            pl.col("err").median().alias("median_days"),
            pl.col("signed").mean().alias("mean_signed"),
            pl.col("inside").mean().alias("coverage"),
            pl.col("width").mean().alias("width_days"),
        )
        .sort("forecast", "era"),
    )


def conformal(df: pl.DataFrame) -> pl.DataFrame:
    """Question 2: calibrate ranges on dates before the cutoff, test on dates after, and return the new ranges."""
    rows, parts = [], []
    for kind in ("planting", "peak"):
        part = df.filter(pl.col("forecast") == kind)
        cal = part.filter(pl.col("as_of") < pl.lit(CUTOFF))
        test = part.filter(pl.col("as_of") >= pl.lit(CUTOFF))
        if cal.height < 50 or test.height < 50:
            continue
        r = cal["signed"].to_numpy()
        n = len(r)
        lo = float(np.quantile(r, max(0.0, (ALPHA / 2) * (n + 1) / n), method="lower"))
        hi = float(np.quantile(r, min(1.0, (1 - ALPHA / 2) * (n + 1) / n), method="higher"))
        calibrated = test.with_columns(
            (pl.col("harvest") + pl.duration(days=int(lo))).alias("new_low"),
            (pl.col("harvest") + pl.duration(days=int(hi))).alias("new_high"),
        ).with_columns(
            pl.col("actual").is_between("new_low", "new_high").alias("new_inside"),
            (pl.col("new_high") - pl.col("new_low")).dt.total_days().alias("new_width"),
        )
        parts.append(calibrated)
        rows.append(
            {
                "forecast": kind,
                "calibration_n": n,
                "test_n": test.height,
                "offset_low_days": lo,
                "offset_high_days": hi,
                "coverage_before": float(test["inside"].mean()),
                "coverage_after": float(calibrated["new_inside"].mean()),
                "width_before": float(test["width"].mean()),
                "width_after": float(calibrated["new_width"].mean()),
            }
        )
    show(f"2. ranges calibrated before {CUTOFF} and tested after it (target {1 - ALPHA:.0%})", pl.DataFrame(rows))
    return pl.concat(parts, how="diagonal_relaxed") if parts else pl.DataFrame()


def baselines(df: pl.DataFrame) -> pl.DataFrame:
    """Return `df` with the median-duration baseline and the 50/50 blend, using only seasons harvested before each date."""
    seasons = pl.read_parquet(GOLD / f"{SLUG}_seasons.parquet").filter(pl.col("harvest_date").is_not_null())
    seasons = seasons.with_columns(
        (pl.col("harvest_date") - pl.col("flood_date")).dt.total_days().alias("dur_planting"),
        (pl.col("harvest_date") - pl.col("peak_date")).dt.total_days().alias("dur_peak"),
    )
    out = []
    for day in df["as_of"].unique().sort():
        known = seasons.filter(pl.col("harvest_date") <= pl.lit(day))
        med = known.group_by("unit").agg(
            pl.col("dur_planting").median().alias("planting"),
            pl.col("dur_peak").median().alias("peak"),
        )
        long = med.unpivot(index="unit", variable_name="forecast", value_name="base_days")
        out.append(df.filter(pl.col("as_of") == day).join(long, on=["unit", "forecast"], how="left"))
    joined = pl.concat(out).drop_nulls("base_days")
    return joined.with_columns(
        (pl.col("harvest") - pl.col("anchor_date")).dt.total_days().alias("model_days"),
    ).with_columns(
        ((pl.col("model_days") + pl.col("base_days")) / 2).round().cast(pl.Int64).alias("blend_days"),
        (pl.col("actual") - pl.col("anchor_date")).dt.total_days().alias("actual_days"),
    )


def blend(df: pl.DataFrame) -> None:
    """Question 3: error of the cell model, the desa median duration and their average, per cell and per desa."""
    joined = baselines(df).with_columns(
        (pl.col("model_days") - pl.col("actual_days")).abs().alias("e_model"),
        (pl.col("base_days") - pl.col("actual_days")).abs().alias("e_base"),
        (pl.col("blend_days") - pl.col("actual_days")).abs().alias("e_blend"),
    )
    show(
        "3a. per cell: mean absolute error in days",
        joined.group_by("forecast", "era")
        .agg(
            pl.len().alias("n"),
            pl.col("e_model").mean().alias("cell_model"),
            pl.col("e_base").mean().alias("desa_median"),
            pl.col("e_blend").mean().alias("average_of_both"),
        )
        .sort("forecast", "era"),
    )
    per_desa = (
        joined.group_by("as_of", "unit", "forecast", "era")
        .agg(
            pl.len().alias("n"),
            pl.col("model_days").median().alias("m"),
            pl.col("base_days").median().alias("b"),
            pl.col("blend_days").median().alias("bl"),
            pl.col("actual_days").median().alias("a"),
        )
        .filter(pl.col("n") >= MIN_CELLS)
    )
    show(
        "3b. per desa and date (median of its cells): mean absolute error in days",
        per_desa.group_by("forecast", "era")
        .agg(
            pl.len().alias("desa_dates"),
            (pl.col("m") - pl.col("a")).abs().mean().alias("cell_model"),
            (pl.col("b") - pl.col("a")).abs().mean().alias("desa_median"),
            (pl.col("bl") - pl.col("a")).abs().mean().alias("average_of_both"),
        )
        .sort("forecast", "era"),
    )


def by_age(df: pl.DataFrame) -> None:
    """Question 4: error by the days since the anchor, and what keeping only older cells would do."""
    binned = df.with_columns(
        pl.when(pl.col("age") < 10)
        .then(pl.lit("a 0-9 days"))
        .when(pl.col("age") < 20)
        .then(pl.lit("b 10-19 days"))
        .when(pl.col("age") < 30)
        .then(pl.lit("c 20-29 days"))
        .otherwise(pl.lit("d 30+ days"))
        .alias("age_bin")
    )
    show(
        "4a. error by days since the anchor date",
        binned.group_by("forecast", "age_bin")
        .agg(
            pl.len().alias("n"),
            pl.col("err").mean().alias("mae_days"),
            pl.col("signed").mean().alias("mean_signed"),
            pl.col("inside").mean().alias("coverage"),
        )
        .sort("forecast", "age_bin"),
    )
    rows = []
    for kind in ("planting", "peak"):
        part = df.filter(pl.col("forecast") == kind)
        for min_age in (0, 5, 10, 15, 20):
            kept = part.filter(pl.col("age") >= min_age)
            rows.append(
                {
                    "forecast": kind,
                    "min_days_since_anchor": min_age,
                    "kept_share": kept.height / max(part.height, 1),
                    "mae_days": float(kept["err"].mean()),
                    "coverage": float(kept["inside"].mean()),
                }
            )
    show("4b. keeping only cells seen for at least this many days since the anchor", pl.DataFrame(rows))


def main() -> None:
    """Run the four studies and save the report."""
    df = load()
    print(f"{df.height} scored forecasts from {df['as_of'].min()} to {df['as_of'].max()}")
    by_era(df)
    conformal(df)
    blend(df)
    by_age(df)
    (GOLD / "forecast_study.txt").write_text("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
