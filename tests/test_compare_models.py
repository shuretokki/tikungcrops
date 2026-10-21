# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Model comparison on a small synthetic table with a learnable signal."""

from __future__ import annotations

import json

import numpy as np
import polars as pl
import pytest

from jotosanur_agri.pipeline.compare_models import compare


@pytest.fixture
def peak_table() -> pl.DataFrame:
    rng = np.random.default_rng(0)
    n = 240
    greenup = rng.uniform(30, 90, n)
    return pl.DataFrame(
        {
            "year": np.repeat([2019, 2020, 2021, 2022], n // 4),
            "peak_doy": rng.integers(1, 365, n),
            "peak_ndvi": rng.uniform(0.6, 0.9, n),
            "peak_after_flood": greenup + 20,
            "peak_after_greenup": greenup,
            "rice": rng.integers(0, 2, n).astype(float),
            "rain_mm": np.where(rng.random(n) < 0.1, np.nan, rng.uniform(0, 400, n)),
            "unit": rng.choice(["Desa A", "Desa B"], n),
            # harvest comes later after a slow green-up, plus noise
            "peak_to_harvest": 10 + 0.4 * greenup + rng.normal(0, 2, n),
        }
    )


def test_compare_scores_every_year_and_beats_baseline(peak_table):
    out = compare(
        peak_table, "peak", models=("ridge", "gradient_boosting"), n_trials=2, inner_folds=2, min_test_seasons=10
    )
    assert out.height == 4 * 3
    assert set(out["model"]) == {"median_duration", "ridge", "gradient_boosting"}
    mae = dict(out.group_by("model").agg(pl.col("mae_days").mean()).iter_rows())
    assert mae["ridge"] < mae["median_duration"]
    assert "alpha" in json.loads(out.filter(pl.col("model") == "ridge")["params"][0])


def test_compare_rejects_unknown_model(peak_table):
    with pytest.raises(ValueError, match="unknown model"):
        compare(peak_table, "peak", models=("svm",), n_trials=1, inner_folds=2, min_test_seasons=10)
