"""Compare harvest-date models with leave-one-year-out and tuning inside the training years.

The design follows CY-Bench (Paudel et al., WUR AgML, github.com/WUR-AI/AgML-CY-Bench), the
open benchmark for subnational crop forecasts. It uses an outer loop that holds out one year,
a naive baseline next to Ridge, random forest and gradient boosting, and hyperparameters
tuned only on the training years with year-grouped folds. Tuning on the held-out year would
leak it into the score.

Per held-out year and forecast (`planting`, `peak`, see `forecast_harvest`):
    - `median_duration`: median days from the training years per flooding month and rice
      flag (`planting`) or per rice flag (`peak`). This is the baseline the models must beat.
    - `ridge`, `random_forest`, `gradient_boosting`: skrub DataOps. `TableVectorizer`
      one-hot encodes the desa, an imputer and scaler are added where the model needs them,
      and an Optuna search (`N_TRIALS` trials, `INNER_FOLDS` year-grouped folds, mean
      absolute error) picks the hyperparameters.
Every model sees the same rows and features as the production forecast, so the table
shows what the model choice alone changes.

Output: data/gold/sentinel/<aoi>_model_comparison.csv, one row per forecast, year and model
with mean absolute error in days and the chosen hyperparameters.
Usage: `python -m jotosanur_agri.pipeline.compare_models [AOI]` (default Lamongan/Tikung).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import optuna
import pandas as pd
import polars as pl
import skrub
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.forecast_harvest import FEATURES, MIN_TEST_SEASONS, TARGET, training_table
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

MODELS = ("ridge", "random_forest", "gradient_boosting")
N_TRIALS = 10
INNER_FOLDS = 3
BASELINE_KEYS = {"planting": ["flood_month", "rice"], "peak": ["rice"]}


def _float(low: float, high: float, name: str, log: bool = False) -> Any:
    """Float hyperparameter range for the search, typed Any because sklearn stubs expect a number."""
    return skrub.choose_float(low, high, log=log, name=name)


def _int(low: int, high: int, name: str) -> Any:
    """Integer hyperparameter range on a log scale, typed like `_float`."""
    return skrub.choose_int(low, high, log=True, name=name)


def _data_op(train: pd.DataFrame, forecast: str, model: str, inner_folds: int) -> Any:
    """Prediction DataOp for one model, with its search space and year-grouped folds."""
    data = skrub.var("data", train)
    x = data[FEATURES[forecast]].skb.mark_as_X(
        cv=GroupKFold(n_splits=inner_folds), split_kwargs={"groups": data["year"]}
    )
    y = data[TARGET[forecast]].skb.mark_as_y()
    x = x.skb.apply(skrub.TableVectorizer())
    if model == "ridge":
        x = x.skb.apply(SimpleImputer()).skb.apply(StandardScaler())
        estimator = Ridge(alpha=_float(0.01, 100.0, "alpha", log=True))
    elif model == "random_forest":
        x = x.skb.apply(SimpleImputer())
        estimator = RandomForestRegressor(
            n_estimators=200,
            max_features=_float(0.3, 1.0, "max_features"),
            min_samples_leaf=_int(1, 50, "min_samples_leaf"),
            n_jobs=4,
            random_state=0,
        )
    elif model == "gradient_boosting":
        # trees split on missing values directly, so no imputer
        estimator = HistGradientBoostingRegressor(
            loss="absolute_error",
            learning_rate=_float(0.01, 0.3, "learning_rate", log=True),
            max_leaf_nodes=_int(7, 63, "max_leaf_nodes"),
            min_samples_leaf=_int(10, 200, "min_samples_leaf"),
            l2_regularization=_float(1e-3, 10.0, "l2_regularization", log=True),
            max_iter=300,
            random_state=0,
        )
    else:
        raise ValueError(f"unknown model {model!r}, expected one of {MODELS}")
    return x.skb.apply(estimator, y=y)


def _baseline(train: pl.DataFrame, test: pl.DataFrame, forecast: str) -> np.ndarray:
    """Median training duration per baseline group, overall median for unseen groups."""
    target, keys = TARGET[forecast], BASELINE_KEYS[forecast]
    medians = train.group_by(keys).agg(pl.col(target).median().alias("base"))
    overall = float(np.median(train[target].to_numpy()))
    return test.join(medians, on=keys, how="left")["base"].fill_null(overall).to_numpy()


def compare(
    table: pl.DataFrame,
    forecast: str,
    models: tuple[str, ...] = MODELS,
    n_trials: int = N_TRIALS,
    inner_folds: int = INNER_FOLDS,
    min_test_seasons: int = MIN_TEST_SEASONS,
) -> pl.DataFrame:
    """Leave-one-year-out mean absolute error of the baseline and each tuned model.

    Args:
        table: Output of `forecast_harvest.training_table`.
        forecast: ``"planting"`` or ``"peak"``.
        models: Model names from `MODELS`.
        n_trials: Optuna trials per model and held-out year.
        inner_folds: Year-grouped folds of the inner search.
        min_test_seasons: Years with fewer seasons are only used for training.

    Returns:
        One row per held-out year and model: `forecast`, `year`, `model`, `seasons`,
        `mae_days` and `params` (JSON of the chosen hyperparameters).
    """
    target = TARGET[forecast]
    years = [y for y, n in table.group_by("year").len().sort("year").iter_rows() if n >= min_test_seasons]
    rows: list[dict[str, Any]] = []
    for year in years:
        train, test = table.filter(pl.col("year") != year), table.filter(pl.col("year") == year)
        y_test = test[target].to_numpy()
        common = {"forecast": forecast, "year": year, "seasons": test.height}
        base = _baseline(train, test, forecast)
        rows.append(
            {**common, "model": "median_duration", "mae_days": float(np.mean(np.abs(base - y_test))), "params": "{}"}
        )
        train_pd, test_pd = train.to_pandas(), test.to_pandas()
        folds = min(inner_folds, train["year"].n_unique())
        for model in models:
            search = _data_op(train_pd, forecast, model, folds).skb.make_randomized_search(
                n_iter=n_trials,
                scoring="neg_mean_absolute_error",
                fitted=True,
                random_state=0,
                backend="optuna",
            )
            point = np.asarray(search.predict({"data": test_pd}), dtype=float)
            params = json.dumps(search.best_learner_.describe_params(), default=str)
            rows.append(
                {**common, "model": model, "mae_days": float(np.mean(np.abs(point - y_test))), "params": params}
            )
    return pl.DataFrame(rows)


def run_compare_models(aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data") -> dict[str, Any]:
    """Compare models for both forecasts of an AOI and write the per-year table.

    Returns:
        Mean error over held-out years per forecast and model, and the output path.
    """
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    data = Path(data_dir)
    slug = resolve(aoi_spec).slug
    seasons = pl.read_parquet(data / "gold" / "sentinel" / f"{slug}_seasons.parquet")
    rain = pl.read_parquet(data / "silver" / "chirps" / f"{slug}_monthly.parquet")
    table = training_table(seasons, rain)
    result = pl.concat([compare(table, forecast) for forecast in FEATURES])
    out = data / "gold" / "sentinel" / f"{slug}_model_comparison.csv"
    result.write_csv(out)
    summary = (
        result.group_by("forecast", "model")
        .agg(pl.col("mae_days").mean().round(1), pl.len().alias("years"))
        .sort("forecast", "mae_days")
    )
    return {"aoi": slug, "summary": summary.to_dicts(), "path": str(out)}


if __name__ == "__main__":
    result = run_compare_models(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI)
    for row in result["summary"]:
        print(row)
    print(result["path"])
