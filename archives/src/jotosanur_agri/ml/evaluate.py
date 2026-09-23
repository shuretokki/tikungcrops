"""Shared evaluation for the scikit-learn baselines: grouped CV on train, then one holdout."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.pipeline import Pipeline


def evaluate(
    pipeline: Pipeline,
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
    target: str,
    group_col: str,
    cv_splits: int,
    n_jobs: int | None = None,
) -> dict[str, Any]:
    """Cross-validate on `train` grouped by `group_col`, then fit on all of `train` and score `test`.

    Grouping keeps rows of one group (a season, a sub-survey) on the same side of every
    fold, so CV does not leak within-group signal. `pipeline` is left fitted on `train`.

    Args:
        pipeline: Unfitted preprocessing + model pipeline.
        train: Training rows.
        test: Holdout rows, never seen during CV or fit.
        features: Feature columns.
        target: Target column.
        group_col: Column whose values define CV groups.
        cv_splits: Number of GroupKFold splits.
        n_jobs: Parallel jobs for cross-validation.

    Returns:
        MAPE for CV (mean, std) and holdout, plus holdout MAE (in target units), R²
        and row counts.
    """
    cv_mape = -cross_val_score(
        pipeline,
        train[features],
        train[target],
        cv=GroupKFold(n_splits=cv_splits),
        groups=train[group_col],
        scoring="neg_mean_absolute_percentage_error",
        n_jobs=n_jobs,
    )
    pipeline.fit(train[features], train[target])
    predicted = pipeline.predict(test[features])
    return {
        "cv_mape_mean": float(np.mean(cv_mape)),
        "cv_mape_std": float(np.std(cv_mape)),
        "holdout_mape": float(mean_absolute_percentage_error(test[target], predicted)),
        "holdout_mae": float(mean_absolute_error(test[target], predicted)),
        "holdout_r2": float(r2_score(test[target], predicted)),
        "n_train": len(train),
        "n_test": len(test),
    }


def save_model(pipeline: Pipeline, path: Path) -> str:
    """Write a fitted pipeline with joblib, creating the directory if needed.

    Returns:
        The written path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)
    return str(path)
