# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Random-forest benchmark trained on real rice data: the CIMMYT survey of 44,607 South Asian fields.

A "real data" benchmark, separate from the Jotosanur-specific Tsukamoto system and
from the synthetic-data baseline in `ml.train`. Context:
documents/local/adr-integrasi-data-cimmyt.md.

Evaluation:
    - GroupKFold by `Dataset` (13 sub-surveys), so rows from one sub-survey never
      split across train and validation folds.
    - The holdout is two whole regions the model never sees (Andhra Pradesh and
      Odisha, the smallest), which tests geographic generalisation rather than
      interpolation between random rows of the same distribution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from jotosanur_agri.ml.evaluate import evaluate, save_model
from jotosanur_agri.pipeline.load_cimmyt import (
    GROUP_KEY,
    NOMINAL_CATEGORICAL,
    NUMERIC_OTHER,
    NUMERIC_SKEWED,
    ORDINAL_CATEGORICAL,
    TARGET,
)

SILVER_PATH = Path("data/silver/cimmyt.parquet")
MODEL_PATH = Path("models/cimmyt_rf_yield.joblib")

HOLDOUT_REGIONS = {"AP", "Odisha"}

# Ordinals are already ordered integers in the source (EDU 1-7, *SEV 0-3), so they are
# used as numeric features without an OrdinalEncoder.
NUMERIC_FEATURES = NUMERIC_SKEWED + NUMERIC_OTHER + ORDINAL_CATEGORICAL
CATEGORICAL_FEATURES = NOMINAL_CATEGORICAL


def build_pipeline() -> Pipeline:
    """Impute and scale numerics (log1p for skewed ones), impute and one-hot categoricals, fit a random forest."""
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    skewed = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocess = ColumnTransformer(
        [
            ("num_skewed", skewed, NUMERIC_SKEWED),
            ("num", numeric, NUMERIC_OTHER + ORDINAL_CATEGORICAL),
            ("cat", categorical, CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline(
        [
            ("prep", preprocess),
            ("model", RandomForestRegressor(n_estimators=300, max_depth=12, random_state=42, n_jobs=-1)),
        ]
    )


def train_and_evaluate(silver_path: Path = SILVER_PATH) -> tuple[Pipeline, dict[str, Any]]:
    """Train on all regions except the holdout with sub-survey-grouped CV, then score the holdout.

    Returns:
        The fitted pipeline and its metrics.
    """
    df = pl.read_parquet(silver_path).to_pandas()
    is_test = df["Region"].isin(HOLDOUT_REGIONS)
    train, test = df[~is_test], df[is_test]

    pipeline = build_pipeline()
    metrics = evaluate(
        pipeline,
        train,
        test,
        NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        TARGET,
        GROUP_KEY,
        cv_splits=5,
        n_jobs=-1,
    )
    metrics |= {
        "unit": "kg/ha",
        "holdout_regions": sorted(HOLDOUT_REGIONS),
        "note": "trained and scored on REAL data (CIMMYT), independent of the Jotosanur system",
    }
    return pipeline, metrics


def main() -> None:
    """Train, save the model and print the metrics."""
    pipeline, metrics = train_and_evaluate()
    metrics["model_path"] = save_model(pipeline, MODEL_PATH)
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
