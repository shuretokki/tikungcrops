# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Web export on a tiny fake area: files written, optional inputs skipped."""

from __future__ import annotations

import json
from datetime import date

import polars as pl
import pytest

from tikungcrops.pipeline.export_web import run_export_web


@pytest.fixture
def fake_area(tmp_path):
    path = tmp_path / "plots.geojson"
    square = [[[112.0, -7.0], [112.1, -7.0], [112.1, -7.1], [112.0, -7.0]]]
    feature = {
        "type": "Feature",
        "properties": {"name": "Plot 1"},
        "geometry": {"type": "Polygon", "coordinates": square},
    }
    path.write_text(json.dumps({"type": "FeatureCollection", "features": [feature]}))
    bronze, gold = tmp_path / "bronze" / "sentinel" / "plots", tmp_path / "gold" / "sentinel"
    bronze.mkdir(parents=True)
    gold.mkdir(parents=True)
    pl.DataFrame(
        {"cell_id": [1, 2], "unit": ["Plot 1"] * 2, "lon": [112.01, 112.02], "lat": [-7.01, -7.02]}
    ).write_parquet(bronze / "cells.parquet")
    pl.DataFrame({"cell_id": [1], "peak_date": [date(2020, 3, 1)]}).write_parquet(gold / "plots_seasons.parquet")
    pl.DataFrame(
        {"cell_id": [1, 2], "as_of": [date(2020, 9, 29)] * 2, "stage": ["planted", "fallow"]},
    ).write_parquet(gold / "plots_current.parquet")
    return str(path), tmp_path


def test_export_writes_core_files_and_skips_missing(fake_area):
    spec, data = fake_area
    result = run_export_web(spec, data)
    out = data / "web" / "plots"
    assert result["files"] == ["meta.json", "cells.json", "current.json"]
    meta = json.loads((out / "meta.json").read_text())
    assert meta["as_of"] == "2020-09-29"
    assert meta["units"][0] == {"unit": "Plot 1", "cells": 2, "paddy_ha": 2.0, "lon": 112.015, "lat": -7.015}
    current = json.loads((out / "current.json").read_text())
    assert {r["stage"]: r["paddy_ha"] for r in current} == {"fallow": 1.0, "planted": 1.0}


def test_export_fails_clearly_without_gold(fake_area):
    spec, data = fake_area
    (data / "gold" / "sentinel" / "plots_seasons.parquet").unlink()
    with pytest.raises(FileNotFoundError, match="just setup"):
        run_export_web(spec, data)
