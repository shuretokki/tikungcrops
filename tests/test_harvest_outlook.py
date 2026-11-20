# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Selection and week-splitting checks for the harvest outlook."""

from __future__ import annotations

from datetime import date, timedelta

import polars as pl

from jotosanur_agri.pipeline.forecast_harvest import ISSUE_AFTER_GREENUP_DAYS
from jotosanur_agri.pipeline.harvest_outlook import MAX_ISSUE_AGE_DAYS, forecast_rows, weekly

AS_OF = date(2026, 1, 15)


def current(cells: list[dict[str, object]]) -> pl.DataFrame:
    """A `current` table where every cell shares the same flood date and area."""
    base = {
        "unit": "A",
        "as_of": AS_OF,
        "stage": "planted",
        "flood_date": date(2025, 12, 1),
        "peak_date": None,
        "rice": True,
        "flood_passes": 5,
        "w": 1.0,
    }
    rows = [{**base, **c} for c in cells]
    return pl.DataFrame(
        rows,
        schema={
            "cell_id": pl.Int64,
            "unit": pl.String,
            "as_of": pl.Date,
            "stage": pl.String,
            "flood_date": pl.Date,
            "greenup_date": pl.Date,
            "peak_date": pl.Date,
            "rice": pl.Boolean,
            "flood_passes": pl.Int64,
            "w": pl.Float64,
        },
    )


RAIN = pl.DataFrame(
    {
        "unit": ["A", "A"],
        "year": [2025, 2025],
        "month": [11, 12],
        "precip_mm": [180.0, 320.0],
    }
)


def greenup(days_ago: int) -> date:
    return AS_OF - timedelta(days=days_ago)


def test_planting_window_is_inclusive_at_both_ends() -> None:
    cells = [
        {"cell_id": 1, "greenup_date": greenup(ISSUE_AFTER_GREENUP_DAYS - 1)},
        {"cell_id": 2, "greenup_date": greenup(ISSUE_AFTER_GREENUP_DAYS)},
        {"cell_id": 3, "greenup_date": greenup(MAX_ISSUE_AGE_DAYS)},
        {"cell_id": 4, "greenup_date": greenup(MAX_ISSUE_AGE_DAYS + 1)},
    ]
    rows = forecast_rows(current(cells), RAIN)
    assert sorted(rows["planting"]["cell_id"].to_list()) == [2, 3]


def test_planting_needs_a_flood_date_and_the_planted_stage() -> None:
    cells = [
        {"cell_id": 1, "greenup_date": greenup(25), "flood_date": None},
        {"cell_id": 2, "greenup_date": greenup(25), "stage": "fallow"},
        {"cell_id": 3, "greenup_date": greenup(25)},
    ]
    rows = forecast_rows(current(cells), RAIN)
    assert rows["planting"]["cell_id"].to_list() == [3]


def test_peak_forecast_takes_peaked_cells_with_a_peak_date_at_any_age() -> None:
    cells = [
        {"cell_id": 1, "stage": "peaked", "peak_date": date(2026, 1, 5), "greenup_date": greenup(90)},
        {"cell_id": 2, "stage": "peaked", "peak_date": None, "greenup_date": greenup(90)},
    ]
    rows = forecast_rows(current(cells), RAIN)
    assert rows["peak"]["cell_id"].to_list() == [1]
    assert rows["planting"].is_empty()


def test_rain_comes_from_the_month_of_flooding() -> None:
    cells = [{"cell_id": 1, "greenup_date": greenup(25), "flood_date": date(2025, 12, 1)}]
    rows = forecast_rows(current(cells), RAIN)
    assert rows["planting"]["rain_mm"].to_list() == [320.0]


def test_feature_columns_follow_the_flood_and_green_up_dates() -> None:
    cells = [{"cell_id": 1, "greenup_date": date(2025, 12, 16), "flood_date": date(2025, 12, 1)}]
    row = forecast_rows(current(cells), RAIN)["planting"].row(0, named=True)
    assert row["flood_doy"] == 335
    assert row["greenup_after_flood"] == 15


def frame(cells: list[tuple[str, int, date, date, float]]) -> pl.DataFrame:
    return pl.DataFrame(
        cells,
        schema=["unit", "cell_id", "harvest_low", "harvest_high", "w"],
        orient="row",
    )


def test_a_range_inside_one_week_stays_in_that_week() -> None:
    out = weekly(frame([("A", 1, date(2025, 1, 6), date(2025, 1, 12), 7.0)]))
    assert out.to_dicts() == [{"unit": "A", "week": date(2025, 1, 6), "expected_ha": 7.0, "cells": 1}]


def test_a_range_over_a_week_boundary_splits_by_day() -> None:
    out = weekly(frame([("A", 1, date(2025, 1, 11), date(2025, 1, 14), 4.0)]))
    assert out["week"].to_list() == [date(2025, 1, 6), date(2025, 1, 13)]
    assert out["expected_ha"].to_list() == [2.0, 2.0]


def test_units_stay_apart_and_cells_in_one_week_add_up() -> None:
    out = weekly(
        frame(
            [
                ("A", 1, date(2025, 1, 6), date(2025, 1, 6), 1.5),
                ("A", 2, date(2025, 1, 7), date(2025, 1, 7), 2.5),
                ("B", 3, date(2025, 1, 8), date(2025, 1, 8), 4.0),
            ]
        )
    )
    assert out.select("unit", "expected_ha", "cells").to_dicts() == [
        {"unit": "A", "expected_ha": 4.0, "cells": 2},
        {"unit": "B", "expected_ha": 4.0, "cells": 1},
    ]
