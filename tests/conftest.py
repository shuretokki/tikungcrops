# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Shared fixtures: synthetic satellite series and a small offline AOI."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from jotosanur_agri.pipeline.aoi import Aoi

SQUARE = {
    "type": "MultiPolygon",
    "coordinates": [[[[112.40, -7.15], [112.41, -7.15], [112.41, -7.16], [112.40, -7.15]]]],
}


def bump(days: np.ndarray, centre: int, width: float) -> np.ndarray:
    """Gaussian bump over day offsets, peak 1 at `centre`."""
    return np.exp(-(((days - centre) / width) ** 2))


@pytest.fixture
def two_season_cell() -> tuple[np.ndarray, np.ndarray, np.ndarray, date, date]:
    """A 5-day series from Sep 2019 to Mar 2021 with rice peaks on 1 Mar and 15 Jul 2020.

    NDVI rests at 0.2 between crops. VH sits at -14 dB and dips to -21 dB for flooding
    about 50 days before each peak, as transplanted paddy does.
    """
    start = date(2019, 9, 1)
    dates = np.array([start + timedelta(days=5 * i) for i in range(110)], dtype=object)
    days = np.array([(d - start).days for d in dates], dtype=float)
    peak1, peak2 = date(2020, 3, 1), date(2020, 7, 15)
    p1, p2 = (peak1 - start).days, (peak2 - start).days
    ndvi = 0.2 + 0.6 * bump(days, p1, 35) + 0.6 * bump(days, p2, 30)
    vh = -14.0 - 7.0 * bump(days, p1 - 50, 8) - 7.0 * bump(days, p2 - 45, 8)
    return dates, ndvi, vh, peak1, peak2


@pytest.fixture
def small_aoi() -> Aoi:
    """Two units, no network needed."""
    return Aoi(slug="test-area", units=[("Desa A", SQUARE), ("Joto Sanur", SQUARE)])
