# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Silver cleaning: cloud and haze filter, orbit offsets, gap limit and smoothing."""

from __future__ import annotations

from datetime import date, timedelta

import polars as pl
import pytest

from jotosanur_agri.pipeline import silver_sentinel as s
from jotosanur_agri.pipeline.silver_sentinel import build_silver, clean_s1, clean_s2, interpolate, time_grid

D0 = date(2020, 1, 1)


def s2_rows(values, clear=None):
    clear = clear or [1.0] * len(values)
    return pl.DataFrame(
        {
            "cell_id": [1] * len(values),
            "date": [D0 + timedelta(days=5 * i) for i in range(len(values))],
            "sensor": ["S2"] * len(values),
            "clear_frac": clear,
            "ndvi": values,
            "lswi": [0.1] * len(values),
        }
    )


def test_clean_s2_drops_cloudy_rows_and_isolated_dips():
    out = clean_s2(s2_rows([0.8, 0.5, 0.8, 0.7], clear=[1.0, 1.0, 1.0, 0.4]))
    # the 0.5 between two 0.8 values is haze, the last row is too cloudy
    assert out["ndvi"].to_list() == [0.8, 0.8]


def test_clean_s2_keeps_a_real_decline():
    # a harvest drops and stays down, so the low value is not isolated
    assert clean_s2(s2_rows([0.8, 0.5, 0.3]))["ndvi"].to_list() == [0.8, 0.5, 0.3]


def test_clean_s1_removes_orbit_offset():
    rows = pl.DataFrame(
        {
            "cell_id": [1] * 4,
            "date": [D0 + timedelta(days=6 * i) for i in range(4)],
            "sensor": ["S1"] * 4,
            "orbit": ["asc", "desc", "asc", "desc"],
            "vh_db": [-16.0, -13.0, -16.0, -13.0],
            "vv_db": [-10.0, -8.0, -10.0, -8.0],
        }
    )
    out = clean_s1(rows)
    # a constant field looks constant once the two viewing geometries are aligned
    assert out["vh_db"].to_list() == pytest.approx([-14.5] * 4)
    assert out["vv_db"].to_list() == pytest.approx([-9.0] * 4)


def test_interpolate_fills_short_gaps_only():
    obs = pl.DataFrame(
        {
            "cell_id": [1, 1, 1],
            "date": [D0, D0 + timedelta(days=20), D0 + timedelta(days=20 + s.MAX_GAP_DAYS + 5)],
            "v": [0.2, 0.6, 0.8],
        }
    )
    grid = time_grid(pl.Series([1]), D0, D0 + timedelta(days=60))
    out = interpolate(grid, obs, ["v"], "filled").sort("date")
    by_day = {(d - D0).days: (v, f) for d, v, f in out.select("date", "v", "filled").iter_rows()}
    assert by_day[10][0] == pytest.approx(0.4)  # halfway through a 20-day gap
    assert by_day[10][1] is True and by_day[0][1] is False
    assert by_day[30][0] is None  # inside the 35-day gap, too long to invent


def test_build_silver_smoothing_does_not_fill_gaps():
    # observations on days 0-20, then a 60-day hole, then days 80-100
    days = [0, 5, 10, 15, 20, 80, 85, 90, 95, 100]
    bronze = pl.DataFrame(
        {
            "cell_id": [1] * len(days),
            "date": [D0 + timedelta(days=d) for d in days],
            "sensor": ["S2"] * len(days),
            "clear_frac": [1.0] * len(days),
            "ndvi": [0.3] * len(days),
            "lswi": [0.1] * len(days),
            "orbit": [None] * len(days),
            "vh_db": [None] * len(days),
            "vv_db": [None] * len(days),
        },
        schema_overrides={"orbit": pl.Utf8, "vh_db": pl.Float64, "vv_db": pl.Float64},
    )
    out = build_silver(bronze).sort("date")
    mid = out.filter(pl.col("date") == D0 + timedelta(days=50))
    assert mid["ndvi"].item() is None
    assert out.filter(pl.col("date") == D0 + timedelta(days=25))["ndvi"].item() is None


def test_clean_s2_keeps_small_wobble():
    # a dip of 0.08 is normal noise, haze removes much more
    assert clean_s2(s2_rows([0.72, 0.64, 0.73, 0.70]))["ndvi"].to_list() == [0.72, 0.64, 0.73, 0.70]


def test_smoothing_keeps_a_short_real_trough():
    # harvest and quick replanting: two low dates in a row survive the 15-day median
    values = [0.8, 0.8, 0.8, 0.3, 0.3, 0.8, 0.8, 0.8]
    n = len(values)
    bronze = pl.DataFrame(
        {
            "cell_id": [1] * n,
            "date": [D0 + timedelta(days=5 * i) for i in range(n)],
            "sensor": ["S2"] * n,
            "clear_frac": [1.0] * n,
            "ndvi": values,
            "lswi": [0.1] * n,
            "orbit": [None] * n,
            "vh_db": [None] * n,
            "vv_db": [None] * n,
        },
        schema_overrides={"orbit": pl.Utf8, "vh_db": pl.Float64, "vv_db": pl.Float64},
    )
    out = build_silver(bronze).sort("date")["ndvi"].to_list()
    assert out[3:5] == pytest.approx([0.3, 0.3])
    assert out[0] == pytest.approx(0.8)
