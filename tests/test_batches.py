# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Silver and gold runs give the same tables whether cells come in one batch or many."""

from __future__ import annotations

import json
from datetime import timedelta

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from jotosanur_agri.pipeline import gold_sentinel, silver_sentinel
from jotosanur_agri.pipeline.gold_sentinel import run_gold_sentinel
from jotosanur_agri.pipeline.silver_sentinel import cell_batches, run_silver_sentinel


def test_cell_batches_cover_every_cell_once_in_order():
    ids = pl.Series([7, 3, 3, 9, 1, 5])
    assert cell_batches(ids, 2) == [(1, 3), (5, 7), (9, 9)]
    assert cell_batches(ids, 10) == [(1, 9)]


@pytest.fixture
def area(tmp_path, two_season_cell):
    """Three cells with two rice seasons each, split into monthly bronze files."""
    dates, ndvi, vh, _, _ = two_season_cell
    square = [[[112.0, -7.0], [112.1, -7.0], [112.1, -7.1], [112.0, -7.0]]]
    feature = {
        "type": "Feature",
        "properties": {"name": "Desa A"},
        "geometry": {"type": "Polygon", "coordinates": square},
    }
    aoi = tmp_path / "plots.geojson"
    aoi.write_text(json.dumps({"type": "FeatureCollection", "features": [feature]}))
    rows = []
    for cell, shift in ((10, 0), (20, 10), (30, 25)):
        for i, d in enumerate(dates):
            day = d + timedelta(days=shift)
            rows.append(
                {
                    "cell_id": cell,
                    "date": day,
                    "sensor": "S2",
                    "clear_frac": 1.0,
                    "ndvi": float(ndvi[i]),
                    "lswi": 0.1,
                    "orbit": None,
                    "vh_db": None,
                    "vv_db": None,
                }
            )
            rows.append(
                {
                    "cell_id": cell,
                    "date": day + timedelta(days=2),
                    "sensor": "S1",
                    "clear_frac": None,
                    "ndvi": None,
                    "lswi": None,
                    "orbit": "ascending" if i % 2 else "descending",
                    "vh_db": float(vh[i]),
                    "vv_db": float(vh[i]) + 6,
                }
            )
    bronze = pl.DataFrame(rows, schema_overrides={"clear_frac": pl.Float64, "orbit": pl.Utf8})
    folder = tmp_path / "bronze" / "sentinel" / "plots"
    folder.mkdir(parents=True)
    for (month,), part in bronze.group_by(pl.col("date").dt.strftime("%Y-%m")):
        part.write_parquet(folder / f"{month}.parquet")
    pl.DataFrame({"cell_id": [10, 20, 30], "unit": ["Desa A"] * 3}).write_parquet(folder / "cells.parquet")
    return str(aoi), tmp_path


def _run(area, monkeypatch, batch):
    aoi, data = area
    monkeypatch.setattr(silver_sentinel, "BATCH_CELLS", batch)
    monkeypatch.setattr(gold_sentinel, "BATCH_CELLS", batch)
    run_silver_sentinel(aoi, data)
    run_gold_sentinel(aoi, data)
    return [
        pl.read_parquet(data / sub)
        for sub in (
            "silver/sentinel/plots.parquet",
            "gold/sentinel/plots_seasons.parquet",
            "gold/sentinel/plots_current.parquet",
        )
    ]


def test_batched_runs_match_a_single_batch(area, monkeypatch):
    whole = _run(area, monkeypatch, 100)
    batched = _run(area, monkeypatch, 1)
    assert whole[1].height >= 6  # two seasons per cell were found
    for a, b in zip(whole, batched, strict=True):
        assert_frame_equal(a.sort(a.columns[:2]), b.sort(b.columns[:2]))
