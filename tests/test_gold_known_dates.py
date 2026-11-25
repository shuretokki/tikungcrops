# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Season detection against curves with known dates, single-rule edge cases and invariants.

Known-date curves follow how phenofit and greenbrown test phenology extraction: build a
double-logistic NDVI series whose start and end of season are known, then check the detected
dates within a tolerance. The property test (Hypothesis) checks invariants on random series.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tikungcrops.pipeline import gold_sentinel as g
from tikungcrops.pipeline.gold_sentinel import current_season, seasons_for_cell

START = date(2019, 9, 1)
N = 110  # 5-day steps, Sep 2019 to Mar 2021


def series(ndvi_of_day, vh_of_day=lambda d: np.full_like(d, -14.0)):
    dates = np.array([START + timedelta(days=5 * i) for i in range(N)], dtype=object)
    days = np.arange(N, dtype=float) * 5
    return dates, ndvi_of_day(days), vh_of_day(days)


def double_logistic(days, sos, eos, base=0.2, top=0.8, rate=0.15):
    """Green-up centred on `sos`, senescence centred on `eos` (day offsets)."""
    return base + (top - base) * (1 / (1 + np.exp(-rate * (days - sos))) - 1 / (1 + np.exp(-rate * (days - eos))))


def crossing(days, values, level, after, rising):
    """First day offset after `after` where `values` crosses `level`, by linear interpolation."""
    fine = np.arange(days[0], days[-1], 0.1)
    v = np.interp(fine, days, values)
    ok = (fine > after) & ((v >= level) if rising else (v <= level))
    return fine[ok][0]


def test_detected_dates_match_known_curve():
    sos, eos = 150.0, 260.0
    dates, ndvi, vh = series(
        lambda d: double_logistic(d, sos, eos), lambda d: -14 - 7 * np.exp(-(((d - 120) / 8) ** 2))
    )
    days = np.arange(N, dtype=float) * 5
    (s,) = seasons_for_cell(dates, ndvi, vh)
    # expectations come from the curve and the specified fractions (20% up, 50% down),
    # never from the module's constants or its detected base, or a changed constant
    # would move the expectation with it
    true_base, true_peak = float(np.nanmin(ndvi[:60])), float(np.nanmax(ndvi))
    amp = true_peak - true_base
    assert s["base_ndvi"] == pytest.approx(true_base, abs=0.02)
    expect_green = crossing(days, ndvi, true_base + 0.2 * amp, after=0, rising=True)
    expect_harvest = crossing(days, ndvi, true_peak - 0.5 * amp, after=float(np.argmax(ndvi) * 5), rising=False)
    # 5-day grid: the detector picks the first grid date past the threshold
    assert 0 <= (s["greenup_date"] - START).days - expect_green < 5
    assert 0 <= (s["harvest_date"] - START).days - expect_harvest < 5
    assert 100 < expect_green < sos < eos < expect_harvest + 10


def test_greenup_too_long_before_peak_is_unreliable():
    # bare until day 112, a fast rise, then a slow climb to a peak at day 230 (lead > 105 days)
    def ndvi_of(d):
        rise = 0.2 + 0.5 / (1 + np.exp(-(d - 116)))
        climb = np.clip((d - 120) / 110, 0, 1) * 0.15
        fall = np.where(d > 230, (d - 230) * 0.01, 0)
        return np.clip(rise + climb - fall, 0.15, None)

    (s,) = seasons_for_cell(*series(ndvi_of))
    lead = (s["peak_date"] - s["greenup_date"]).days
    assert s["base_ndvi"] <= 0.3
    assert lead >= 105
    assert s["greenup_reliable"] is False


def flood_series(pre_vh, flood_vh):
    """One season peaking around day 200, VH at `pre_vh` with a dip to `flood_vh` near planting."""
    return series(
        lambda d: double_logistic(d, 160, 240),
        lambda d: pre_vh + (flood_vh - pre_vh) * np.exp(-(((d - 125) / 8) ** 2)),
    )


def test_rice_by_absolute_rule_alone():
    # wet season: field already wet, deep VH but almost no drop
    (s,) = seasons_for_cell(*flood_series(pre_vh=-17.6, flood_vh=-18.4))
    assert s["flood_vh_db"] <= g.RICE_FLOOD_VH_DB
    assert s["vh_drop_db"] < g.RICE_VH_DROP_DB
    assert s["rice"] is True


def test_rice_by_drop_rule_alone():
    # dry season: dry field floods, VH stays above -17 dB but drops clearly
    (s,) = seasons_for_cell(*flood_series(pre_vh=-12.0, flood_vh=-15.5))
    assert s["flood_vh_db"] > g.RICE_FLOOD_VH_DB
    assert s["vh_drop_db"] >= g.RICE_VH_DROP_DB
    assert s["rice"] is True


def test_not_rice_without_flooding():
    (s,) = seasons_for_cell(*flood_series(pre_vh=-13.0, flood_vh=-13.5))
    assert s["rice"] is False


def test_half_green_base_is_unreliable():
    # clouds hid the bare phase: the series never drops below 0.45 before the peak
    (s,) = seasons_for_cell(*series(lambda d: double_logistic(d, 150, 260, base=0.45, top=0.85)))
    assert s["base_ndvi"] > g.RELIABLE_BASE_NDVI
    assert s["greenup_reliable"] is False


def test_cloud_gap_after_peak_leaves_harvest_unknown():
    dates, ndvi, vh = series(lambda d: double_logistic(d, 150, 260))
    peak_i = int(np.argmax(ndvi))
    ndvi[peak_i + 1 : peak_i + 9] = np.nan
    (s,) = seasons_for_cell(dates, ndvi, vh)
    assert s["harvest_date"] is None


def test_current_season_stages():
    dates, ndvi, vh = series(lambda d: double_logistic(d, 150, 260))
    seasons = seasons_for_cell(dates, ndvi, vh)
    assert current_season(dates, ndvi, vh, seasons)["stage"] == "fallow"

    rising = ndvi.copy()
    rising[-10:] = np.linspace(0.2, 0.45, 10)
    assert current_season(dates, rising, vh, seasons_for_cell(dates, rising, vh))["stage"] == "planted"

    # a new crop past its peak (NDVI falling) but not yet down to harvest level at the series end
    late = double_logistic(np.arange(N, dtype=float) * 5, 150, 260) + 0.6 * np.exp(
        -(((np.arange(N) * 5 - 530) / 25) ** 2)
    )
    state = current_season(dates, late, vh, seasons_for_cell(dates, late, vh))
    assert state["stage"] == "peaked"
    assert (state["peak_date"] - START).days == 530

    # the same crop seen only up to its highest value is still "planted", the peak is unconfirmed
    cut = dates <= START + timedelta(days=530)
    early = current_season(dates[cut], late[cut], vh[cut], seasons_for_cell(dates[cut], late[cut], vh[cut]))
    assert early["stage"] == "planted"


@settings(max_examples=60, deadline=None, derandomize=True)
@given(
    peaks=st.lists(st.integers(60, 490), min_size=1, max_size=4),
    widths=st.lists(st.floats(10, 40), min_size=4, max_size=4),
    holes=st.lists(st.integers(0, N - 1), max_size=15),
)
def test_season_invariants_on_random_series(peaks, widths, holes):
    days = np.arange(N, dtype=float) * 5
    ndvi = 0.2 + sum(0.65 * np.exp(-(((days - p) / w) ** 2)) for p, w in zip(peaks, widths, strict=False))
    ndvi = np.minimum(ndvi, 0.95)
    ndvi[holes] = np.nan
    dates, _, vh = series(lambda d: d)
    seasons = seasons_for_cell(dates, ndvi, vh)
    peak_dates = [s["peak_date"] for s in seasons]
    assert peak_dates == sorted(peak_dates)
    assert all((b - a).days >= g.MIN_SEASON_GAP_DAYS for a, b in zip(peak_dates, peak_dates[1:], strict=False))
    for i, s in enumerate(seasons):
        assert s["peak_ndvi"] >= g.PEAK_MIN
        assert dates[0] <= s["peak_date"] <= dates[-1]
        if s["greenup_date"] is not None:
            assert s["greenup_date"] <= s["peak_date"]
        if s["harvest_date"] is not None:
            assert s["harvest_date"] > s["peak_date"]
            if i + 1 < len(seasons):
                assert s["harvest_date"] < seasons[i + 1]["peak_date"]
        if s["start_truncated"]:
            assert s["greenup_date"] is None
