# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Random-forest baseline for rice yield on the synthetic Kampung Pandu Sakti data.

A comparison baseline, not the proposal's main method (that is fuzzy Tsukamoto, see
`predict_panen_tsukamoto`). It proves the bronze -> silver -> features path works end
to end.

Do not cite these scores as evidence of real-world accuracy: the test data comes from
a generator whose formula is known (`pipeline.generate_synthetic`), so a low MAPE here
only shows the pipeline is wired correctly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from jotosanur_agri.ml.evaluate import evaluate, save_model

SILVER_PATH = Path("data/silver/kampung_pandu_harvest.parquet")
MODEL_PATH = Path("models/baseline_rf_produktivitas.joblib")

TARGET = "produktivitas_ton_per_ha"
NUMERIC_FEATURES = ["musim_tanam_ke", "luas_ha", "curah_hujan_mm", "pupuk_kg_per_ha", "siklus_hari"]
# `varietas` is left out: every row is PMJ01, so it carries no signal yet.
CATEGORICAL_FEATURES = ["plot_id"]
GROUP_COL = "musim_tanam_ke"

# Temporal holdout, all plots in a season share the same rainfall,
# so a random split would leak season information between train and test.
TEST_SEASONS = {7, 8}


def build_pipeline() -> Pipeline:
    """Scale numeric features, one-hot the plot id, fit a shallow random forest."""
    preprocess = ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline(
        [
            ("prep", preprocess),
            ("model", RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42)),
        ]
    )


def train_and_evaluate(silver_path: Path = SILVER_PATH) -> tuple[Pipeline, dict[str, Any]]:
    """Train on seasons 1-6 with season-grouped CV and score seasons 7-8.

    Returns:
        The fitted pipeline and its metrics.
    """
    df = pl.read_parquet(silver_path).to_pandas()
    is_test = df[GROUP_COL].isin(TEST_SEASONS)
    train, test = df[~is_test], df[is_test]

    pipeline = build_pipeline()
    metrics = evaluate(
        pipeline,
        train,
        test,
        NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        TARGET,
        GROUP_COL,
        cv_splits=min(5, train[GROUP_COL].nunique()),
    )
    metrics |= {
        "unit": "ton/ha",
        "test_seasons": sorted(TEST_SEASONS),
        "note": "scored on SYNTHETIC data, see module docstring before citing",
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
