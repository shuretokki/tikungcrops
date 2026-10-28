# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

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

`--defaults` runs a wider comparison without tuning, in the style of a model zoo: a linear
model with and without spline features, gradient boosting with and without feature
interactions, CatBoost, XGBoost, LightGBM, a CatBoost-LightGBM vote and a stack of the
boosting models. Every model keeps its default settings, so the table shows whether the
model family matters before any time goes into tuning. It writes
<aoi>_model_comparison_defaults.csv.
Usage: `python -m jotosanur_agri.pipeline.compare_models [AOI] [--defaults]` (default Lamongan/Tikung).
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
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from sklearn.ensemble import (
    HistGradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
    VotingRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler
from xgboost import XGBRegressor

from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.forecast_harvest import FEATURES, MIN_TEST_SEASONS, TARGET, training_table
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

MODELS = ("ridge", "random_forest", "gradient_boosting")
DEFAULT_MODELS = (
    "linear",
    "spline",
    "hgb",
    "hgb_no_interactions",
    "catboost",
    "xgboost",
    "lightgbm",
    "voting",
    "stacking",
)
N_TRIALS = 10
INNER_FOLDS = 3
BASELINE_KEYS = {"planting": ["flood_month", "rice"], "peak": ["rice"]}
SEED = 0
THREADS = 4


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


def _catboost() -> CatBoostRegressor:
    return CatBoostRegressor(
        loss_function="MAE", random_seed=SEED, thread_count=THREADS, verbose=0, allow_writing_files=False
    )


def _lightgbm() -> LGBMRegressor:
    return LGBMRegressor(objective="l1", random_state=SEED, n_jobs=THREADS, verbose=-1)


def _default_pipeline(model: str, year_splits: list[tuple[np.ndarray, np.ndarray]]) -> Pipeline:
    """Untuned model in `skrub.tabular_pipeline`, which adds the encoder, imputer and scaler it needs.

    `year_splits` are the stacking model's inner folds. They are built from the training years,
    so the meta-model never learns from a season of a year it also predicts.
    """
    hgb = {"loss": "absolute_error", "random_state": SEED}
    estimators: dict[str, Any] = {
        "linear": RidgeCV(alphas=np.logspace(-2, 2, 20)),
        "spline": RidgeCV(alphas=np.logspace(-2, 2, 20)),
        "hgb": HistGradientBoostingRegressor(**hgb),
        "hgb_no_interactions": HistGradientBoostingRegressor(**hgb, interaction_cst="no_interactions"),
        "catboost": _catboost(),
        "xgboost": XGBRegressor(objective="reg:absoluteerror", random_state=SEED, n_jobs=THREADS),
        "lightgbm": _lightgbm(),
        "voting": VotingRegressor([("catboost", _catboost()), ("lightgbm", _lightgbm())]),
        "stacking": StackingRegressor(
            [("hgb", HistGradientBoostingRegressor(**hgb)), ("catboost", _catboost()), ("lightgbm", _lightgbm())],
            final_estimator=RidgeCV(),
            cv=year_splits,
        ),
    }
    if model not in estimators:
        raise ValueError(f"unknown model {model!r}, expected one of {DEFAULT_MODELS}")
    steps: list[tuple[str, Any]] = []
    if model == "spline":
        # Splines only on numeric columns with many values. Day of year and NDVI bend, flags do not.
        spline = SplineTransformer(extrapolation="linear", handle_missing="zeros")
        # The skrub stubs type a combined selector as And, while ApplyToCols annotates cols as All.
        many_values: Any = skrub.selectors.numeric() & ~skrub.selectors.cardinality_below(20)
        steps.append(("spline", skrub.ApplyToCols(spline, cols=many_values)))
    steps.append(("model", skrub.tabular_pipeline(estimators[model])))
    return Pipeline(steps)


def _held_out_years(table: pl.DataFrame, min_test_seasons: int) -> list[int]:
    return [y for y, n in table.group_by("year").len().sort("year").iter_rows() if n >= min_test_seasons]


def compare_defaults(
    table: pl.DataFrame,
    forecast: str,
    models: tuple[str, ...] = DEFAULT_MODELS,
    inner_folds: int = INNER_FOLDS,
    min_test_seasons: int = MIN_TEST_SEASONS,
) -> pl.DataFrame:
    """Leave-one-year-out mean absolute error of the baseline and each untuned model.

    Args:
        table: Output of `forecast_harvest.training_table`.
        forecast: ``"planting"`` or ``"peak"``.
        models: Model names from `DEFAULT_MODELS`.
        inner_folds: Year-grouped folds for the stacking model.
        min_test_seasons: Years with fewer seasons are only used for training.

    Returns:
        The same columns as `compare`, with `params` always ``"{}"``.
    """
    unknown = set(models) - set(DEFAULT_MODELS)
    if unknown:
        raise ValueError(f"unknown model {sorted(unknown)[0]!r}, expected one of {DEFAULT_MODELS}")
    target, features = TARGET[forecast], FEATURES[forecast]
    rows: list[dict[str, Any]] = []
    for year in _held_out_years(table, min_test_seasons):
        train, test = table.filter(pl.col("year") != year), table.filter(pl.col("year") == year)
        y_test = test[target].to_numpy()
        common = {"forecast": forecast, "year": year, "seasons": test.height, "params": "{}"}
        base = _baseline(train, test, forecast)
        rows.append({**common, "model": "median_duration", "mae_days": float(np.mean(np.abs(base - y_test)))})
        x_train, x_test = train.select(features).to_pandas(), test.select(features).to_pandas()
        years = train["year"].to_numpy()
        n_splits = min(inner_folds, len(np.unique(years)))
        splits = list(GroupKFold(n_splits=n_splits).split(x_train, groups=years))
        for model in models:
            pipe = _default_pipeline(model, splits).fit(x_train, train[target].to_numpy())
            point = np.asarray(pipe.predict(x_test), dtype=float)
            rows.append({**common, "model": model, "mae_days": float(np.mean(np.abs(point - y_test)))})
    return pl.DataFrame(rows)


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
    years = _held_out_years(table, min_test_seasons)
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


def run_compare_models(
    aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data", defaults: bool = False
) -> dict[str, Any]:
    """Compare models for both forecasts of an AOI and write the per-year table.

    Args:
        aoi_spec: Area of interest.
        data_dir: Data root.
        defaults: Run the untuned model zoo instead of the tuned comparison.

    Returns:
        Mean error over held-out years per forecast and model, and the output path.
    """
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    data = Path(data_dir)
    slug = resolve(aoi_spec).slug
    seasons = pl.read_parquet(data / "gold" / "sentinel" / f"{slug}_seasons.parquet")
    rain = pl.read_parquet(data / "silver" / "chirps" / f"{slug}_monthly.parquet")
    table = training_table(seasons, rain)
    run = compare_defaults if defaults else compare
    result = pl.concat([run(table, forecast) for forecast in FEATURES])
    suffix = "_defaults" if defaults else ""
    out = data / "gold" / "sentinel" / f"{slug}_model_comparison{suffix}.csv"
    result.write_csv(out)
    summary = (
        result.group_by("forecast", "model")
        .agg(pl.col("mae_days").mean().round(1), pl.len().alias("years"))
        .sort("forecast", "mae_days")
    )
    return {"aoi": slug, "summary": summary.to_dicts(), "path": str(out)}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    result = run_compare_models(args[0] if args else DEFAULT_AOI, defaults="--defaults" in sys.argv)
    for row in result["summary"]:
        print(row)
    print(result["path"])
