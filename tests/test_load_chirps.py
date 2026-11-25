# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""CHIRPS month fetch: a failed remote read is retried, offline with a fake reader."""

from __future__ import annotations

import polars as pl
import pytest
from rasterio.errors import RasterioIOError

from tikungcrops.pipeline import load_chirps

POINTS = pl.DataFrame({"unit": ["Alpha"], "lon": [112.3], "lat": [-7.1]})
ROW = [{"unit": "Alpha", "year": 2020, "month": 1, "precip_mm": 300.0, "fetched_on": "2026-10-28"}]


@pytest.fixture
def no_wait(monkeypatch):
    waits: list[float] = []
    monkeypatch.setattr(load_chirps.time, "sleep", waits.append)
    return waits


def flaky(fails: int):
    calls = {"n": 0}

    def fetch(year, month, points, names):
        calls["n"] += 1
        if calls["n"] <= fails:
            raise RasterioIOError("Read failed")
        return ROW

    return fetch, calls


def test_a_failed_read_is_retried(monkeypatch, no_wait):
    fetch, calls = flaky(2)
    monkeypatch.setattr(load_chirps, "fetch_month", fetch)
    assert load_chirps.fetch_month_retrying(2020, 1, POINTS, ["Alpha"]) == ROW
    assert calls["n"] == 3
    assert no_wait == [5, 15]


def test_gives_up_after_the_last_wait(monkeypatch, no_wait):
    fetch, calls = flaky(99)
    monkeypatch.setattr(load_chirps, "fetch_month", fetch)
    with pytest.raises(RasterioIOError):
        load_chirps.fetch_month_retrying(2020, 1, POINTS, ["Alpha"])
    assert calls["n"] == len(load_chirps.RETRY_WAIT_S) + 1
