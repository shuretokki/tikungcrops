# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Boundary matching: the three cases found on real data, offline with toy outlines."""

from __future__ import annotations

import json

from jotosanur_agri.pipeline.aoi import Aoi
from jotosanur_agri.pipeline.load_boundaries import contains, match, run_load_boundaries


def square(x0: float, y0: float, size: float = 1.0) -> dict:
    ring = [[x0, y0], [x0 + size, y0], [x0 + size, y0 + size], [x0, y0 + size], [x0, y0]]
    return {"type": "Polygon", "coordinates": [ring]}


def feature(name: str, geometry: dict, sid: str) -> dict:
    return {"type": "Feature", "properties": {"shapeName": name, "shapeID": sid}, "geometry": geometry}


AOI = Aoi(slug="toy", units=[("Alpha", square(0, 0)), ("Beta", square(1, 0))])


def test_contains_respects_holes():
    donut = {"type": "Polygon", "coordinates": [square(0, 0, 4)["coordinates"][0], square(1, 1, 2)["coordinates"][0]]}
    assert contains(donut, 0.5, 0.5)
    assert not contains(donut, 2.0, 2.0)
    assert not contains(donut, 5.0, 5.0)


def test_name_wins_over_a_shifted_border():
    # Alpha's outline in the other data set sits mostly over Beta, as Dukuhagung did in Tikung
    shifted = feature("alpha", square(0.6, 0), "a")
    out, _ = match(AOI, [shifted, feature("Beta", square(1, 0), "b")], "ADM4")
    assert {f["properties"]["unit"] for f in out} == {"Alpha", "Beta"}
    assert all(f["properties"]["name_match"] for f in out)


def test_namesake_far_away_is_ignored_and_unnamed_outline_joins_by_location():
    far = feature("Alpha", square(50, 50), "far")
    renamed = feature("Old Beta", square(1.1, 0.1, 0.8), "renamed")
    out, _ = match(AOI, [far, renamed, feature("Alpha", square(0, 0), "a")], "ADM4")
    by_id = {f["properties"]["id"]: f["properties"] for f in out}
    assert "far" not in by_id
    assert by_id["renamed"]["unit"] == "Beta" and by_id["renamed"]["name_match"] is False


def test_level_with_namesake_desa_loses(tmp_path):
    gb = tmp_path / "gb"
    gb.mkdir()
    # ADM3: one outline per unit. ADM4: a desa named like each unit plus three other desa.
    adm3 = [feature("Alpha", square(0, 0), "k1"), feature("Beta", square(1, 0), "k2")]
    adm4 = [feature("Alpha", square(0, 0, 0.5), "d1"), feature("Beta", square(1, 0, 0.5), "d2")]
    # a unit split in two outlines adds a third namesake, so counting name matches alone picks ADM4
    adm4.append(feature("Beta", square(1.5, 0, 0.4), "d6"))
    adm4 += [feature(f"Desa {i}", square(0.5 + i * 0.3, 0.5, 0.2), f"d{i + 3}") for i in range(3)]
    for level, feats in (("ADM3", adm3), ("ADM4", adm4)):
        (gb / f"IDN_{level}_simplified.geojson").write_text(json.dumps({"features": feats}))
    aoi_file = tmp_path / "toy.geojson"
    aoi_file.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [{"type": "Feature", "properties": {"name": n}, "geometry": g} for n, g in AOI.units],
            }
        )
    )
    result = run_load_boundaries(str(aoi_file), tmp_path, gb_dir=gb)
    assert result["level"] == "ADM3"
    assert result["units_without_outline"] == []
    written = json.loads((tmp_path / "web" / "toy" / "boundaries.geojson").read_text())
    assert "CC BY 3.0 IGO" in written["attribution"]
