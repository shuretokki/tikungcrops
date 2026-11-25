# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""LBS fetch: tiling, paging, de-duplication and retries, offline with a fake service."""

from __future__ import annotations

import io
import json
import urllib.error
import urllib.parse
from email.message import Message

import pytest

from tikungcrops.pipeline import load_paddy
from tikungcrops.pipeline.aoi import Aoi


def rect(x0: float, y0: float, w: float, h: float) -> dict:
    ring = [[x0, y0], [x0 + w, y0], [x0 + w, y0 + h], [x0, y0 + h], [x0, y0]]
    return {"type": "Polygon", "coordinates": [ring]}


# 0.25 x 0.15 degrees, so 3 x 2 tiles of at most 0.1 degree
AOI = Aoi(slug="toy", units=[("Alpha", rect(112.0, -7.0, 0.25, 0.15))])


def feature(oid: int) -> dict:
    return {"type": "Feature", "properties": {"objectid": oid}, "geometry": rect(0, 0, 1, 1)}


class FakeService:
    """Answers each envelope from a table, with an optional run of server errors first."""

    def __init__(self, per_tile: dict[int, list[int]], fail_first: int = 0, fail_code: int = 500):
        """Set the object ids per tile index and how many calls fail first."""
        self.per_tile = per_tile
        self.fail_left = fail_first
        self.fail_code = fail_code
        self.calls: list[dict[str, str]] = []
        self.tiles: list[str] = []

    def __call__(self, url: str, timeout: float):
        """Stand in for urlopen and return one page of features as a file-like body."""
        if self.fail_left:
            self.fail_left -= 1
            raise urllib.error.HTTPError(url, self.fail_code, "boom", Message(), io.BytesIO(b""))
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
        self.calls.append(params)
        if params["geometry"] not in self.tiles:
            self.tiles.append(params["geometry"])
        ids = self.per_tile.get(self.tiles.index(params["geometry"]), [])
        offset, size = int(params["resultOffset"]), int(params["resultRecordCount"])
        body = {"features": [feature(i) for i in ids[offset : offset + size]]}
        return io.BytesIO(json.dumps(body).encode())


@pytest.fixture
def offline(tmp_path, monkeypatch):
    monkeypatch.setattr(load_paddy, "LBS_DIR", tmp_path)
    monkeypatch.setattr(load_paddy.time, "sleep", lambda s: None)

    def install(service: FakeService) -> FakeService:
        monkeypatch.setattr(load_paddy.urllib.request, "urlopen", service)
        return service

    return install


def test_tiles_cover_the_bounds_without_gaps():
    tiles = load_paddy._tiles(112.0, -7.0, 112.25, -6.85)
    assert len(tiles) == 6
    assert min(t[0] for t in tiles) == pytest.approx(112.0)
    assert max(t[2] for t in tiles) == pytest.approx(112.25)
    assert all(t[2] - t[0] <= 0.1 + 1e-9 and t[3] - t[1] <= 0.1 + 1e-9 for t in tiles)


def test_small_bounds_stay_one_tile():
    assert len(load_paddy._tiles(112.30, -7.15, 112.38, -7.07)) == 1


def test_edge_polygons_are_kept_once_and_pages_are_followed(offline, monkeypatch):
    monkeypatch.setattr(load_paddy, "PAGE_SIZE", 2)
    # polygon 3 crosses the edge between tiles 0 and 1; tile 0 needs two pages
    service = offline(FakeService({0: [1, 2, 3], 1: [3, 4]}))
    features = load_paddy.fetch_lbs(AOI)
    assert sorted(f["properties"]["objectid"] for f in features) == [1, 2, 3, 4]
    assert len(service.tiles) == 6
    assert [c["resultOffset"] for c in service.calls if c["geometry"] == service.tiles[0]] == ["0", "2"]


def test_server_errors_are_retried(offline):
    service = offline(FakeService({0: [7]}, fail_first=2))
    assert [f["properties"]["objectid"] for f in load_paddy.fetch_lbs(AOI)] == [7]
    assert len(service.calls) == 6


def test_client_errors_are_not_retried(offline):
    offline(FakeService({0: [7]}, fail_first=1, fail_code=400))
    with pytest.raises(urllib.error.HTTPError):
        load_paddy.fetch_lbs(AOI)


def test_cache_is_written_and_reused(offline, tmp_path):
    offline(FakeService({0: [5]}))
    load_paddy.fetch_lbs(AOI)
    assert (tmp_path / "toy.geojson").exists()
    offline(FakeService({}, fail_first=99))
    assert [f["properties"]["objectid"] for f in load_paddy.fetch_lbs(AOI)] == [5]
