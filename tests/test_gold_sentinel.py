# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Season detection and cropping intensity on synthetic series."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest

from tikungcrops.pipeline.gold_sentinel import find_peaks, intensity_units, seasons_for_cell


def test_find_peaks_keeps_higher_of_two_close_peaks():
    dates = np.array([date(2020, 1, 1) + timedelta(days=5 * i) for i in range(7)], dtype=object)
    ndvi = np.array([0.2, 0.7, 0.3, 0.8, 0.3, 0.2, 0.2])
    # the two maxima are 10 days apart, well inside the season gap
    assert find_peaks(dates, ndvi) == [3]


def test_find_peaks_ignores_low_maxima_and_nan():
    dates = np.array([date(2020, 1, 1) + timedelta(days=5 * i) for i in range(5)], dtype=object)
    assert find_peaks(dates, np.array([0.2, 0.5, np.nan, 0.4, 0.2])) == []


def test_seasons_for_cell_finds_two_rice_seasons(two_season_cell):
    dates, ndvi, vh, peak1, peak2 = two_season_cell
    seasons = seasons_for_cell(dates, ndvi, vh)
    assert len(seasons) == 2
    for s, peak in zip(seasons, (peak1, peak2), strict=True):
        assert abs((s["peak_date"] - peak).days) <= 5
        assert s["rice"] is True
        assert s["greenup_reliable"] is True
        assert s["flood_date"] < s["greenup_date"] < s["peak_date"] < s["harvest_date"]
        assert not s["start_truncated"] and not s["end_truncated"]


def test_seasons_for_cell_marks_rice_unknown_with_few_radar_passes(two_season_cell):
    dates, ndvi, vh, _, _ = two_season_cell
    # one Sentinel-1 pass in the whole period: too few to see the flooding dip
    seasons = seasons_for_cell(dates, ndvi, vh, s1_dates=np.array([date(2019, 9, 1)], dtype=object))
    assert [s["rice"] for s in seasons] == [None, None]


def test_seasons_for_cell_flags_season_cut_by_series_start(two_season_cell):
    dates, ndvi, vh, _, _ = two_season_cell
    # start the series 40 days before the first peak, inside its look-back window
    keep = dates >= date(2020, 1, 21)
    first = seasons_for_cell(dates[keep], ndvi[keep], vh[keep])[0]
    assert first["start_truncated"]
    assert first["greenup_date"] is None


def test_seasons_for_cell_empty_without_ndvi():
    dates = np.array([date(2020, 1, 1) + timedelta(days=5 * i) for i in range(10)], dtype=object)
    assert seasons_for_cell(dates, np.full(10, np.nan), np.full(10, -15.0)) == []


@pytest.fixture
def intensity_inputs() -> tuple[pl.DataFrame, pl.DataFrame]:
    cells = pl.DataFrame(
        {"cell_id": [1, 2, 3], "unit": ["A", "A", "B"], "paddy_frac": [1.0, 0.5, 0.0]},
    )
    peaks = [date(2020, 3, 1), date(2020, 7, 1), date(2020, 11, 1), date(2020, 3, 1), date(2020, 4, 1)]
    gold = pl.DataFrame(
        {"cell_id": [1, 1, 1, 2, 3], "peak_date": peaks, "rice": [True, True, None, False, True]},
    )
    return gold, cells


def test_intensity_units_weights_by_paddy_and_counts_idle_cells(intensity_inputs):
    gold, cells = intensity_inputs
    out = intensity_units(gold, cells, date(2019, 1, 1), date(2021, 12, 31))
    a2020 = out.filter(pl.col("unit") == "A", pl.col("year") == 2020).row(0, named=True)
    # cell 1 (1 ha) has 3 seasons, cell 2 (0.5 ha) has 1
    assert a2020["paddy_ha"] == pytest.approx(1.5)
    assert a2020["ip_all"] == pytest.approx((3 * 1.0 + 1 * 0.5) / 1.5)
    # unknown rice counts as not rice
    assert a2020["ip_rice"] == pytest.approx(2 / 1.5)
    assert a2020["share_3plus"] == pytest.approx(1 / 1.5)
    # a year without seasons still appears, at zero
    assert out.filter(pl.col("unit") == "A", pl.col("year") == 2021)["ip_all"].item() == 0


def test_intensity_units_null_without_paddy_and_flags_edge_years(intensity_inputs):
    gold, cells = intensity_inputs
    # a year is complete only if data starts LOOKBACK_DAYS (120) before 1 January
    out = intensity_units(gold, cells, date(2019, 9, 1), date(2021, 6, 30))
    assert out.filter(pl.col("unit") == "B")["ip_all"].is_null().all()
    complete = dict(out.filter(pl.col("unit") == "A").select("year", "complete").iter_rows())
    assert complete == {2019: False, 2020: True, 2021: False}
