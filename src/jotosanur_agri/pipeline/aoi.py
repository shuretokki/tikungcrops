"""Area of interest (AOI): named units to monitor, from GADM admin boundaries or a GeoJSON file.

Spec forms:
    - GADM path, e.g. ``Lamongan/Tikung`` or ``IDN:Jawa Timur/Lamongan``: names matched as
      consecutive admin levels, starting at any level; the country ISO3 prefix defaults
      to IDN. Units are the next level down (desa inside a kecamatan, kecamatan inside a
      kabupaten, ...), or the area itself at the deepest level.
    - Path to a GeoJSON FeatureCollection, e.g. farm plots: each feature is a unit, named
      by its ``name`` property.

GADM 4.1 is free for non-commercial use and must not be redistributed, so it is
downloaded at run time into data/external/gadm/ (not tracked).
"""

from __future__ import annotations

import json
import math
import re
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GADM_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{iso}_{level}.json.zip"
GADM_DIR = Path("data/external/gadm")
DEFAULT_COUNTRY = "IDN"
WORLDCOVER_URL = (
    "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"
)


@dataclass(frozen=True)
class Aoi:
    """An area to monitor, split into named units.

    Attributes:
        slug: Filesystem-safe id used in output paths, e.g. ``lamongan-tikung``.
        units: (name, lon/lat GeoJSON geometry) per unit.
    """

    slug: str
    units: list[tuple[str, dict[str, Any]]]

    def bounds(self) -> tuple[float, float, float, float]:
        """(min lon, min lat, max lon, max lat) over all units."""
        xs, ys = [], []
        for _, geometry in self.units:
            for x, y in _coords(geometry):
                xs.append(x)
                ys.append(y)
        return min(xs), min(ys), max(xs), max(ys)

    def utm_crs(self) -> str:
        """EPSG code of the UTM zone holding the AOI centre."""
        west, south, east, north = self.bounds()
        lon, lat = (west + east) / 2, (south + north) / 2
        zone = int((lon + 180) // 6) + 1
        return f"EPSG:{(32600 if lat >= 0 else 32700) + zone}"

    def worldcover_tiles(self) -> list[str]:
        """URLs of the 3 x 3 degree ESA WorldCover tiles covering the AOI."""
        west, south, east, north = self.bounds()
        urls = []
        for lat in range(math.floor(south / 3) * 3, math.floor(north / 3) * 3 + 1, 3):
            for lon in range(math.floor(west / 3) * 3, math.floor(east / 3) * 3 + 1, 3):
                tile = f"{'N' if lat >= 0 else 'S'}{abs(lat):02d}{'E' if lon >= 0 else 'W'}{abs(lon):03d}"
                urls.append(WORLDCOVER_URL.format(tile=tile))
        return urls


def _coords(geometry: dict[str, Any]) -> list[tuple[float, float]]:
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    return [(x, y) for polygon in polygons for ring in polygon for x, y in ring]


def slugify(spec: str) -> str:
    """Output-path id for an AOI spec: lowercase, non-alphanumerics collapsed to ``-``."""
    body = Path(spec).stem if spec.endswith((".json", ".geojson")) else spec.split(":")[-1]
    return re.sub(r"[^a-z0-9]+", "-", body.lower()).strip("-")


def _gadm_features(iso: str) -> tuple[list[dict[str, Any]], int]:
    """Deepest-level GADM features for a country, downloading the archive once."""
    GADM_DIR.mkdir(parents=True, exist_ok=True)
    for level in range(5, 0, -1):
        archive = GADM_DIR / f"gadm41_{iso}_{level}.json.zip"
        if not archive.exists():
            try:
                urllib.request.urlretrieve(GADM_URL.format(iso=iso, level=level), archive)
            except urllib.error.HTTPError:
                continue
        with zipfile.ZipFile(archive) as z:
            return json.loads(z.read(f"gadm41_{iso}_{level}.json"))["features"], level
    raise ValueError(f"no GADM boundaries found for country {iso!r}")


def _squash(name: str) -> str:
    # GADM drops spaces in some names ("JawaTimur"), so compare without them
    return re.sub(r"\s+", "", name).lower()


def from_gadm(path: str, iso: str = DEFAULT_COUNTRY) -> Aoi:
    """AOI from a GADM name path, with units one admin level below its end."""
    names = [_squash(n) for n in path.split("/") if n.strip()]
    features, max_level = _gadm_features(iso)
    for start in range(1, max_level - len(names) + 2):
        levels = range(start, start + len(names))
        matched = [
            f
            for f in features
            if all(_squash(f["properties"][f"NAME_{lv}"]) == n for lv, n in zip(levels, names, strict=True))
        ]
        if matched:
            unit_level = min(start + len(names), max_level)
            groups: dict[str, list[dict[str, Any]]] = {}
            for f in matched:
                groups.setdefault(f["properties"][f"NAME_{unit_level}"], []).append(f["geometry"])
            units = [(name, _merge(geoms)) for name, geoms in sorted(groups.items())]
            return Aoi(slug=slugify(path), units=units)
    raise ValueError(f"{path!r} does not match any consecutive GADM admin names in {iso}")


def _merge(geometries: list[dict[str, Any]]) -> dict[str, Any]:
    polygons = []
    for g in geometries:
        polygons += g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    return {"type": "MultiPolygon", "coordinates": polygons}


def from_geojson(path: Path) -> Aoi:
    """AOI from a GeoJSON FeatureCollection; each feature is a unit named by its `name` property."""
    features = json.loads(path.read_text())["features"]
    units = [(str(f["properties"].get("name", f"unit-{i}")), f["geometry"]) for i, f in enumerate(features)]
    return Aoi(slug=slugify(str(path)), units=units)


def resolve(spec: str) -> Aoi:
    """Resolve an AOI spec (GADM path, optionally ``ISO3:``-prefixed, or GeoJSON file path)."""
    if spec.endswith((".json", ".geojson")):
        return from_geojson(Path(spec))
    iso, _, path = spec.rpartition(":")
    return from_gadm(path, iso or DEFAULT_COUNTRY)
