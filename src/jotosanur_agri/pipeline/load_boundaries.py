"""Publishable unit outlines for the web map, from geoBoundaries.

GADM, which defines the AOI units, must not be redistributed. The web map uses geoBoundaries
gbHumanitarian for Indonesia instead: ADM3 (kecamatan) and ADM4 (desa), from OCHA ROAP based
on BPS 2019, licence CC BY 3.0 IGO.
The files carry only a name and an id, no parent area, so features are matched by location.
A feature belongs to the AOI unit whose GADM outline contains its centre, and the level whose
names match the most units is kept (desa for a kecamatan AOI, kecamatan for a kabupaten).
GADM is only used for this check, its geometry is never written.

Output: data/web/<aoi-slug>/boundaries.geojson. Each feature has `unit` (the GADM name the rest
of the pipeline uses), `name` (the geoBoundaries name), `name_match` and `level`.
Units with no matching outline are listed in the summary.
Usage: `python -m jotosanur_agri.pipeline.load_boundaries [AOI]` (default Lamongan/Tikung).
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

from jotosanur_agri.pipeline.aoi import Aoi, resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

GB_DIR = Path("data/external/geoboundaries")
GB_URL = (
    "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/9469f09592ced973a3448cf66b6100b741b64c0d/"
    "releaseData/gbHumanitarian/IDN/{level}/geoBoundaries-IDN-{level}_simplified.geojson"
)
LEVELS = ("ADM3", "ADM4")
ATTRIBUTION = (
    "Boundaries: geoBoundaries gbHumanitarian (OCHA ROAP, BPS 2019), CC BY 3.0 IGO. "
    "Runfola et al. 2020, PLoS ONE 15(4): e0231866."
)
DECIMALS = 5


def _squash(name: str) -> str:
    return re.sub(r"[\s\-.']+", "", name).lower()


def _polygons(geometry: dict[str, Any]) -> list[list[list[list[float]]]]:
    return geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]


def _inside(x: float, y: float, ring: list[list[float]]) -> bool:
    """Ray casting: True when (x, y) is inside the closed `ring`."""
    hit = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1], strict=True):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def contains(geometry: dict[str, Any], x: float, y: float) -> bool:
    """True when (x, y) is inside a polygon's outer ring and outside its holes."""
    return any(_inside(x, y, p[0]) and not any(_inside(x, y, h) for h in p[1:]) for p in _polygons(geometry))


def centre(geometry: dict[str, Any]) -> tuple[float, float]:
    """Vertex mean of the largest outer ring, a cheap point inside for compact outlines."""
    ring = max((p[0] for p in _polygons(geometry)), key=len)
    return sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)


def _rounded(geometry: dict[str, Any]) -> dict[str, Any]:
    polygons = [
        [[[round(x, DECIMALS), round(y, DECIMALS)] for x, y in ring] for ring in p] for p in _polygons(geometry)
    ]
    return {"type": "MultiPolygon", "coordinates": polygons}


def _features(level: str, gb_dir: Path) -> list[dict[str, Any]]:
    path = gb_dir / f"IDN_{level}_simplified.geojson"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        part = path.with_suffix(".part")
        urllib.request.urlretrieve(GB_URL.format(level=level), part)  # noqa: S310
        part.rename(path)
    return json.loads(path.read_text())["features"]


def _bbox(geometry: dict[str, Any]) -> tuple[float, float, float, float]:
    xs = [x for p in _polygons(geometry) for x, _ in p[0]]
    ys = [y for p in _polygons(geometry) for _, y in p[0]]
    return min(xs), min(ys), max(xs), max(ys)


def match(aoi: Aoi, features: list[dict[str, Any]], level: str) -> tuple[list[dict[str, Any]], int]:
    """Outlines of the AOI's units, labelled with the unit name the pipeline uses.

    A unit takes the nearby outline with its own name first. The two boundary sets differ
    near some borders, so an outline's centre can fall in a neighbouring GADM unit.
    An outline left without a name match joins the unit that contains its centre, for
    renamed or merged units, and is flagged with `name_match` false.

    Returns:
        The labelled outlines, and how many outlines inside the AOI were left unused. A level
        finer than the units leaves many unused, e.g. every desa of a kabupaten.
    """
    west, south, east, north = aoi.bounds()
    near = []
    for f in features:
        fw, fs, fe, fn = _bbox(f["geometry"])
        if fw <= east and fe >= west and fs <= north and fn >= south:
            near.append(f)
    units = {_squash(name): name for name, _ in aoi.units}
    picked: dict[str, tuple[dict[str, Any], str, bool]] = {}
    for f in near:
        key = _squash(f["properties"]["shapeName"])
        x, y = centre(f["geometry"])
        # same name and inside the AOI box, so a namesake elsewhere in Indonesia is skipped
        if key in units and west <= x <= east and south <= y <= north:
            picked[f["properties"]["shapeID"]] = (f, units[key], True)
    named = {unit for _, unit, _ in picked.values()}
    unused = 0
    for f in near:
        if f["properties"]["shapeID"] in picked:
            continue
        x, y = centre(f["geometry"])
        inside = [n for n, geom in aoi.units if contains(geom, x, y)]
        unit = next((n for n in inside if n not in named), None)
        if unit is not None:
            picked[f["properties"]["shapeID"]] = (f, unit, False)
        elif inside:
            unused += 1
    outlines = [
        {
            "type": "Feature",
            "properties": {
                "unit": unit,
                "name": f["properties"]["shapeName"],
                "name_match": name_match,
                "level": level,
                "id": f["properties"]["shapeID"],
            },
            "geometry": _rounded(f["geometry"]),
        }
        for f, unit, name_match in picked.values()
    ]
    return outlines, unused


def run_load_boundaries(
    aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data", gb_dir: Path = GB_DIR
) -> dict[str, Any]:
    """Pick the geoBoundaries level that fits the AOI's units and write the outlines.

    Returns:
        Chosen level, matched and unmatched units, and the output path.

    Raises:
        ValueError: If no level has a single outline inside the AOI, e.g. an area outside Indonesia.
    """
    aoi = resolve(aoi_spec)
    candidates = {level: match(aoi, _features(level, gb_dir), level) for level in LEVELS}

    # many desa share their kecamatan's name, so a too fine level also matches names, but
    # its other outlines inside the AOI are unmatched or unused, and each costs a point
    def score(found: tuple[list[dict[str, Any]], int]) -> int:
        outlines, unused = found
        return sum(1 if f["properties"]["name_match"] else -1 for f in outlines) - unused

    level, (best, _) = max(candidates.items(), key=lambda kv: score(kv[1]))
    if not best:
        raise ValueError(f"{aoi.slug}: no geoBoundaries outline inside the AOI (Indonesia only)")
    out = Path(data_dir) / "web" / aoi.slug / "boundaries.geojson"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"type": "FeatureCollection", "attribution": ATTRIBUTION, "features": best}))
    covered = {f["properties"]["unit"] for f in best}
    return {
        "aoi": aoi.slug,
        "level": level,
        "features": len(best),
        "name_mismatch": sorted(
            f"{f['properties']['unit']} ~ {f['properties']['name']}" for f in best if not f["properties"]["name_match"]
        ),
        "units_without_outline": sorted({name for name, _ in aoi.units} - covered),
        "path": str(out),
    }


if __name__ == "__main__":
    print(run_load_boundaries(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI))
