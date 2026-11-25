# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Leakage and conservation checks for the forecast table and the weekly outlook.

The leakage tests follow the anti-pattern idea in temporalcv's testing strategy: change only
information from after the issue date and require the features to stay the same.
"""

from __future__ import annotations

from datetime import date, timedelta

import polars as pl
import pytest

from tikungcrops.pipeline.forecast_harvest import FEATURES, training_table
from tikungcrops.pipeline.harvest_outlook import weekly


@pytest.fixture
def seasons() -> pl.DataFrame:
    flood = [date(2020, 11, 10), date(2021, 5, 1)]
    return pl.DataFrame(
        {
            "cell_id": [1, 1],
            "unit": ["A", "A"],
            "greenup_reliable": [True, True],
            "start_truncated": [False, False],
            "end_truncated": [False, False],
            "flood_date": flood,
            "greenup_date": [f + timedelta(days=15) for f in flood],
            "peak_date": [f + timedelta(days=75) for f in flood],
            "harvest_date": [f + timedelta(days=110) for f in flood],
            "rice": [True, False],
            "flood_passes": [6, 4],
            "flood_vh_db": [-18.0, -15.0],
            "vh_drop_db": [0.5, 2.0],
            "base_ndvi": [0.2, 0.25],
            "peak_ndvi": [0.8, 0.75],
        }
    )


@pytest.fixture
def rain() -> pl.DataFrame:
    months = [(y, m) for y in (2020, 2021) for m in range(1, 13)]
    return pl.DataFrame(
        {
            "unit": ["A"] * len(months),
            "year": [y for y, _ in months],
            "month": [m for _, m in months],
            "precip_mm": [float(10 * m) for _, m in months],
        }
    )


def test_planting_features_ignore_peak_and_harvest(seasons, rain):
    base = training_table(seasons, rain).select(FEATURES["planting"])
    later = seasons.with_columns(pl.col("peak_date") + timedelta(days=20), pl.col("harvest_date") + timedelta(days=40))
    assert training_table(later, rain).select(FEATURES["planting"]).equals(base)


def test_peak_features_ignore_harvest(seasons, rain):
    base = training_table(seasons, rain).select(FEATURES["peak"])
    later = seasons.with_columns(pl.col("harvest_date") + timedelta(days=40))
    assert training_table(later, rain).select(FEATURES["peak"]).equals(base)


def test_rain_comes_from_the_flooding_month(seasons, rain):
    table = training_table(seasons, rain).sort("flood_date")
    # November 2020 and May 2021, not the harvest months
    assert table["rain_mm"].to_list() == [110.0, 50.0]


def test_unreliable_and_cut_seasons_are_not_training_rows(seasons, rain):
    bad = seasons.with_columns(pl.Series("greenup_reliable", [False, True]), pl.Series("end_truncated", [False, True]))
    assert training_table(bad, rain).height == 0


def test_weekly_outlook_conserves_area():
    cells = pl.DataFrame(
        {
            "cell_id": [1, 2, 3],
            "unit": ["A", "A", "B"],
            "w": [1.0, 0.5, 0.8],
            "harvest_low": [date(2026, 11, 2), date(2026, 11, 10), date(2026, 11, 20)],
            "harvest_high": [date(2026, 11, 22), date(2026, 11, 10), date(2026, 12, 5)],
        }
    )
    out = weekly(cells)
    totals = dict(out.group_by("unit").agg(pl.col("expected_ha").sum()).iter_rows())
    assert totals == pytest.approx({"A": 1.5, "B": 0.8})
    # each week starts on a Monday
    assert all(w.weekday() == 0 for w in out["week"])
