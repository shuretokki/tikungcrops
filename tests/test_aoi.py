# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""AOI slugs and GeoJSON areas, offline."""

from __future__ import annotations

import json

from jotosanur_agri.pipeline.aoi import resolve, slugify


def test_slugify_joins_and_strips():
    # GADM spells the province "JawaTimur", which is why real slugs read idn-jawatimur-...
    assert slugify("IDN", "Jawa Timur", "Lamongan", "Tikung") == "idn-jawa-timur-lamongan-tikung"
    assert slugify(" Kab. ", "Desa/Kel") == "kab-desa-kel"


def test_geojson_aoi_names_units_and_bounds(tmp_path):
    square = [[[112.0, -7.0], [112.1, -7.0], [112.1, -7.1], [112.0, -7.0]]]
    features = [
        {"type": "Feature", "properties": {"name": "Plot 1"}, "geometry": {"type": "Polygon", "coordinates": square}},
        {"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": square}},
    ]
    path = tmp_path / "farm_plots.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    aoi = resolve(str(path))
    assert aoi.slug == "farm-plots"
    assert [name for name, _ in aoi.units] == ["Plot 1", "unit-1"]
    assert aoi.bounds() == (112.0, -7.1, 112.1, -7.0)
