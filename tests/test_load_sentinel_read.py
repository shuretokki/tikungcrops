# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Remote reads: a short read is retried, a scene that keeps failing becomes nodata."""

from __future__ import annotations

import numpy as np
import pytest
from affine import Affine
from rasterio.errors import RasterioIOError

from jotosanur_agri.pipeline import load_sentinel as ls


class FakeGrid:
    """Just enough of `Grid` for `read_to_grid`."""

    shape = (4, 4)
    transform = Affine(10, 0, 0, 0, -10, 40)
    crs = "EPSG:32749"


@pytest.fixture(autouse=True)
def no_pause(monkeypatch):
    monkeypatch.setattr(ls.time, "sleep", lambda _: None)


def test_short_read_is_retried(monkeypatch):
    calls = {"n": 0}

    def flaky_open(href):
        calls["n"] += 1
        raise RasterioIOError("TIFFFillTile: got 0 bytes")

    monkeypatch.setattr(ls.rasterio, "open", flaky_open)
    out = ls.read_to_grid("https://example.com/SCL.tif?token", FakeGrid())  # pyright: ignore[reportArgumentType]
    assert calls["n"] == ls.READ_RETRIES + 1
    assert out.shape == FakeGrid.shape and np.isnan(out).all()


def test_read_succeeds_after_one_failure(monkeypatch):
    calls = {"n": 0}
    real_open = ls.rasterio.open

    def once_flaky(href):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RasterioIOError("timeout")
        return real_open(href)

    monkeypatch.setattr(ls.rasterio, "open", once_flaky)
    monkeypatch.setattr(ls, "reproject", lambda src, out, **kw: out.fill(7.0))
    import rasterio

    with rasterio.MemoryFile() as mem:
        with mem.open(
            driver="GTiff", width=4, height=4, count=1, dtype="float32", crs="EPSG:32749", transform=FakeGrid.transform
        ) as dst:
            dst.write(np.ones((1, 4, 4), dtype="float32"))
        out = ls.read_to_grid(mem.name, FakeGrid())  # pyright: ignore[reportArgumentType]
    assert calls["n"] == 2
    assert (out == 7.0).all()
