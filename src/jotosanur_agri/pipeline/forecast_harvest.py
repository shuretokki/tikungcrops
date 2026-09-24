"""Evaluate harvest-date forecasts per cell, trained on satellite-detected seasons.

Two forecasts, each issued as soon as its inputs are known (nothing after the issue
date is used):
    - `planting`: issued `ISSUE_AFTER_GREENUP_DAYS` after green-up, when the flooding
      date and rice flag are settled; predicts flooding -> harvest days (~2-3 months ahead).
    - `peak`: issued at the NDVI peak; predicts peak -> harvest days (~1 month ahead).

Training rows are complete seasons whose green-up was actually observed
(`greenup_reliable`): elsewhere cloud gaps corrupt the dates (see `gold_sentinel`), and a
model trained on them would learn the noise.

Models: scikit-learn histogram gradient boosting, one for the median (absolute error)
and two quantile models (10th and 90th percentile) for an 80% range. Seasons of one year
share weather and timing, so ranges fitted on pooled rows come out too narrow for a new
year (~60% coverage in Tikung). They are widened by conformalized quantile regression:
the quantile models are refitted without `CALIBRATION_SHARE` of the training years, and
the range is widened by the 80th percentile of how far those years fall outside it.
Baseline: median duration from the training years, per flooding month and rice flag
(`planting`) or per rice flag (`peak`). Evaluation is leave-one-year-out by harvest year, so every score
comes from a year the model never saw.

Reported per forecast and held-out year: seasons, baseline and model mean absolute
error in days, and the share of seasons whose true harvest falls inside the predicted
80% range. Per unit (desa), the median predicted harvest date of a year's season is
compared with the median detected one.

Output: data/gold/sentinel/<aoi>_forecast_eval.csv.
Usage: `python -m jotosanur_agri.pipeline.forecast_harvest [AOI]`.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from sklearn.ensemble import HistGradientBoostingRegressor

from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

ISSUE_AFTER_GREENUP_DAYS = 20
QUANTILES = (0.1, 0.9)
MIN_TEST_SEASONS = 200
CALIBRATION_SHARE = 0.25

FEATURES = {
    "planting": [
        "flood_doy",
        "greenup_after_flood",
        "rice",
        "flood_vh_db",
        "vh_drop_db",
        "base_ndvi",
        "flood_passes",
        "rain_mm",
        "unit",
    ],
    "peak": ["peak_doy", "peak_ndvi", "peak_after_flood", "peak_after_greenup", "rice", "rain_mm", "unit"],
}
TARGET = {"planting": "flood_to_harvest", "peak": "peak_to_harvest"}


def training_table(seasons: pl.DataFrame, rain: pl.DataFrame) -> pl.DataFrame:
    """Reliable complete seasons with features and targets for both forecasts."""
    s = seasons.filter(
        pl.col("greenup_reliable").fill_null(False),
        ~pl.col("start_truncated"),
        ~pl.col("end_truncated"),
        pl.col("harvest_date").is_not_null(),
        pl.col("flood_date").is_not_null(),
    ).with_columns(
        pl.col("harvest_date").dt.year().alias("year"),
        pl.col("flood_date").dt.ordinal_day().alias("flood_doy"),
        pl.col("flood_date").dt.month().alias("flood_month"),
        pl.col("peak_date").dt.ordinal_day().alias("peak_doy"),
        (pl.col("greenup_date") - pl.col("flood_date")).dt.total_days().alias("greenup_after_flood"),
        (pl.col("peak_date") - pl.col("flood_date")).dt.total_days().alias("peak_after_flood"),
        (pl.col("peak_date") - pl.col("greenup_date")).dt.total_days().alias("peak_after_greenup"),
        (pl.col("harvest_date") - pl.col("flood_date")).dt.total_days().alias("flood_to_harvest"),
        (pl.col("harvest_date") - pl.col("peak_date")).dt.total_days().alias("peak_to_harvest"),
        pl.col("rice").cast(pl.Float64),
        pl.col("flood_passes").cast(pl.Float64),
    )
    # Rainfall of the unit in the flooding month: known once flooding is seen
    return s.join(
        rain.select("unit", "year", "month", pl.col("precip_mm").alias("rain_mm")),
        left_on=["unit", pl.col("flood_date").dt.year(), "flood_month"],
        right_on=["unit", "year", "month"],
        how="left",
    )


def _matrix(df: pl.DataFrame, features: list[str], units: list[str]) -> np.ndarray:
    cols = [
        df["unit"].replace_strict({u: i for i, u in enumerate(units)}, default=-1).cast(pl.Float64).to_numpy()
        if f == "unit"
        else df[f].cast(pl.Float64).to_numpy()
        for f in features
    ]
    return np.column_stack(cols)


def _model(loss: str, quantile: float | None, categorical: list[bool]) -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        loss=loss,
        quantile=quantile,
        # A boolean mask is valid; the local sklearn stubs only list the string forms
        categorical_features=categorical,  # pyright: ignore[reportArgumentType]
        max_iter=300,
        learning_rate=0.05,
        random_state=0,
    )


def _calibrated_range(
    train: pl.DataFrame,
    test: pl.DataFrame,
    features: list[str],
    target: str,
    units: list[str],
    categorical: list[bool],
) -> tuple[np.ndarray, np.ndarray]:
    """80% range for `test`, conformally widened using held-out training years."""
    years = sorted(train["year"].unique().to_list())
    n_cal = max(1, round(len(years) * CALIBRATION_SHARE))
    # Spread calibration years over the period rather than taking the latest ones
    cal_years = years[:: max(1, len(years) // n_cal)][:n_cal]
    fit, cal = train.filter(~pl.col("year").is_in(cal_years)), train.filter(pl.col("year").is_in(cal_years))
    x_fit, x_cal, x_all, x_test = (_matrix(d, features, units) for d in (fit, cal, train, test))
    y_fit, y_cal = fit[target].to_numpy(), cal[target].to_numpy()
    lo_m, hi_m = (_model("quantile", q, categorical).fit(x_fit, y_fit) for q in QUANTILES)
    scores = np.maximum(lo_m.predict(x_cal) - y_cal, y_cal - hi_m.predict(x_cal))
    level = QUANTILES[1] - QUANTILES[0]
    widen = float(np.quantile(scores, min(1.0, level * (1 + 1 / len(scores)))))
    # Final quantile models use every training year; the widening comes from the calibration fit
    lo, hi = (
        _model("quantile", q, categorical).fit(x_all, train[target].to_numpy()).predict(x_test) for q in QUANTILES
    )
    return lo - widen, hi + widen


def evaluate(table: pl.DataFrame, forecast: str) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Leave-one-year-out scores per held-out year, and per-unit median date errors."""
    features, target = FEATURES[forecast], TARGET[forecast]
    baseline_keys = ["flood_month", "rice"] if forecast == "planting" else ["rice"]
    units = sorted(table["unit"].unique().to_list())
    categorical = [f == "unit" for f in features]
    years = [y for y, n in table.group_by("year").len().sort("year").iter_rows() if n >= MIN_TEST_SEASONS]
    rows, unit_rows = [], []
    for year in years:
        train, test = table.filter(pl.col("year") != year), table.filter(pl.col("year") == year)
        x_train, x_test = _matrix(train, features, units), _matrix(test, features, units)
        y_train, y_test = train[target].to_numpy(), test[target].to_numpy()

        medians = train.group_by(baseline_keys).agg(pl.col(target).median().alias("base"))
        base = test.join(medians, on=baseline_keys, how="left")["base"].fill_null(float(np.median(y_train))).to_numpy()
        point = _model("absolute_error", None, categorical).fit(x_train, y_train).predict(x_test)
        low, high = _calibrated_range(train, test, features, target, units, categorical)

        rows.append(
            {
                "forecast": forecast,
                "year": year,
                "seasons": test.height,
                "baseline_mae_days": float(np.mean(np.abs(base - y_test))),
                "model_mae_days": float(np.mean(np.abs(point - y_test))),
                "range_coverage": float(np.mean((y_test >= low) & (y_test <= high))),
                "range_width_days": float(np.median(high - low)),
            }
        )
        # Per unit: median predicted vs detected harvest day of the year's seasons
        anchor = "flood_date" if forecast == "planting" else "peak_date"
        per_unit = (
            test.select("unit", anchor, "harvest_date")
            .with_columns(
                pl.Series("point_days", np.round(point).astype("int64")),
                pl.Series("base_days", np.round(base).astype("int64")),
            )
            .with_columns(
                (pl.col(anchor) + pl.duration(days=pl.col("point_days"))).alias("predicted"),
                (pl.col(anchor) + pl.duration(days=pl.col("base_days"))).alias("baseline"),
                pl.col(anchor).dt.month().alias("month"),
            )
            .group_by("unit", "month")
            .agg(
                pl.len().alias("seasons"),
                *(pl.col(c).cast(pl.Int32).median().alias(c) for c in ("harvest_date", "predicted", "baseline")),
            )
            .filter(pl.col("seasons") >= 20)
        )
        unit_rows.append(
            per_unit.select(
                pl.lit(forecast).alias("forecast"),
                pl.lit(year).alias("year"),
                (pl.col("predicted") - pl.col("harvest_date")).abs().alias("model_err"),
                (pl.col("baseline") - pl.col("harvest_date")).abs().alias("baseline_err"),
            )
        )
    return pl.DataFrame(rows), pl.concat(unit_rows)


def run_forecast_evaluation(aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data") -> dict[str, Any]:
    """Build the training table for an AOI and score both forecasts.

    Returns:
        Training row count, per-forecast summaries (mean over held-out years) and the
        output path.
    """
    data = Path(data_dir)
    slug = resolve(aoi_spec).slug
    seasons = pl.read_parquet(data / "gold" / "sentinel" / f"{slug}_seasons.parquet")
    rain = pl.read_parquet(data / "silver" / "chirps" / f"{slug}_monthly.parquet")
    table = training_table(seasons, rain)
    scores, units = [], []
    for forecast in FEATURES:
        s, u = evaluate(table, forecast)
        scores.append(s)
        units.append(u)
    scores_df, units_df = pl.concat(scores), pl.concat(units)
    out = data / "gold" / "sentinel" / f"{slug}_forecast_eval.csv"
    scores_df.write_csv(out)
    summary = {
        f: {
            "baseline_mae_days": round(g["baseline_mae_days"].mean(), 1),
            "model_mae_days": round(g["model_mae_days"].mean(), 1),
            "range_coverage": round(g["range_coverage"].mean(), 2),
            "range_width_days": round(g["range_width_days"].median(), 1),
            "unit_baseline_err_days": round(units_df.filter(pl.col("forecast") == f)["baseline_err"].mean(), 1),
            "unit_model_err_days": round(units_df.filter(pl.col("forecast") == f)["model_err"].mean(), 1),
        }
        for (f,), g in scores_df.group_by("forecast")
    }
    return {"aoi": slug, "training_seasons": table.height, "summary": summary, "path": str(out)}


if __name__ == "__main__":
    result = run_forecast_evaluation(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI)
    print(f"{result['aoi']}: {result['training_seasons']} reliable seasons")
    for forecast, s in result["summary"].items():
        print(f"  {forecast}: {s}")
    print(pl.read_csv(result["path"]))
