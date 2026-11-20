"""Download a true-colour Sentinel-2 picture of every desa for the site.

The picture is the clearest recent scene over the kecamatan, cut to the bounding box of each desa and enlarged three times.
The outline of the desa is saved as an SVG path in picture pixels, so the page can draw it over the picture.
Output: site/public/desa/<slug>.jpg and site/app/data/desa-images.json.

Run from the project root:
    nix shell nixpkgs#imagemagick -c nix develop -c uv run --no-sync python scripts/desa_images.py
Needs the network, and ImageMagick (`magick`) on the PATH for the JPEG step.
"""

import json
import subprocess
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import transform, transform_bounds

ROOT = Path(__file__).resolve().parent.parent
SLUG = "idn-jawatimur-lamongan-tikung"
BOUNDARIES = ROOT / "data" / "web" / SLUG / "boundaries.geojson"
OUT_DIR = ROOT / "site" / "public" / "desa"
MANIFEST = ROOT / "site" / "app" / "data" / "desa-images.json"
SEARCH = "https://earth-search.aws.element84.com/v1/search"
DATETIME = "2026-05-01T00:00:00Z/2026-10-31T23:59:59Z"
MARGIN = 0.15  # share of the desa box that is added on every side
SCALE = 3  # the picture is enlarged three times with cubic resampling
CLOUDY = (3, 8, 9, 10)  # scene classification: shadow, medium and high cloud, cirrus


def slug(name: str) -> str:
    """Return the name in lower case without spaces, for file names."""
    return "".join(c for c in name.lower() if c.isalnum())


def rings(geometry: dict) -> list[list[list[float]]]:
    """Return the outer ring of every polygon in a GeoJSON geometry."""
    polys = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    return [p[0] for p in polys]


def bbox_of(features: list[dict]) -> tuple[float, float, float, float]:
    """Return the bounding box (west, south, east, north) of the features."""
    xs: list[float] = []
    ys: list[float] = []
    for f in features:
        for ring in rings(f["geometry"]):
            xs += [p[0] for p in ring]
            ys += [p[1] for p in ring]
    return min(xs), min(ys), max(xs), max(ys)


def search(bbox: tuple[float, float, float, float]) -> list[dict]:
    """Return Sentinel-2 scenes that cover the whole box."""
    body = {
        "collections": ["sentinel-2-l2a"],
        "bbox": list(bbox),
        "datetime": DATETIME,
        "limit": 100,
        "query": {"eo:cloud_cover": {"lt": 30}},
    }
    req = urllib.request.Request(SEARCH, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        items = json.load(r)["features"]
    # Keep scenes that cover the whole kecamatan, so every desa comes from one date.
    return [
        i
        for i in items
        if i["bbox"][0] <= bbox[0] and i["bbox"][1] <= bbox[1] and i["bbox"][2] >= bbox[2] and i["bbox"][3] >= bbox[3]
    ]


def cloud_share(item: dict, bbox: tuple[float, float, float, float]) -> float:
    """Return the share of the box that the scene classification marks as cloud or shadow."""
    with rasterio.open(item["assets"]["scl"]["href"]) as src:
        left, bottom, right, top = transform_bounds("EPSG:4326", src.crs, *bbox)
        win = src.window(left, bottom, right, top).round_offsets().round_lengths()
        scl = src.read(1, window=win)
    return float(np.isin(scl, CLOUDY).mean())


def main() -> None:
    """Pick the clearest scene and write one picture per desa."""
    features = json.loads(BOUNDARIES.read_text())["features"]
    kec_bbox = bbox_of(features)
    items = search(kec_bbox)
    if not items:
        raise SystemExit("no scene covers the kecamatan in the date range")
    scored = sorted(
        ((cloud_share(i, kec_bbox), i["properties"]["datetime"], i) for i in items), key=lambda t: (t[0], t[1])
    )
    best_share, best_date, scene = scored[0]
    print(f"{len(items)} scenes, best {best_date[:10]} with {best_share:.1%} cloud over the kecamatan")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict] = {}
    with rasterio.open(scene["assets"]["visual"]["href"]) as src:
        for f in features:
            name = f["properties"]["unit"]
            x0, y0, x1, y1 = bbox_of([f])
            dx, dy = (x1 - x0) * MARGIN, (y1 - y0) * MARGIN
            box = (x0 - dx, y0 - dy, x1 + dx, y1 + dy)
            left, bottom, right, top = transform_bounds("EPSG:4326", src.crs, *box)
            win = src.window(left, bottom, right, top).round_offsets().round_lengths()
            w, h = int(win.width) * SCALE, int(win.height) * SCALE
            data = src.read(window=win, out_shape=(3, h, w), resampling=Resampling.cubic)
            fine = src.window_transform(win) * rasterio.Affine.scale(1 / SCALE, 1 / SCALE)
            tif = OUT_DIR / f"{slug(name)}.tif"
            with rasterio.open(
                tif, "w", driver="GTiff", width=w, height=h, count=3, dtype="uint8", crs=src.crs, transform=fine
            ) as dst:
                dst.write(data.clip(0, 255).astype("uint8"))
            jpg = OUT_DIR / f"{slug(name)}.jpg"
            subprocess.run(
                ["magick", str(tif), "-quality", "80", "-strip", "-interlace", "Plane", str(jpg)], check=True
            )
            tif.unlink()

            # Outline in picture pixels: lon/lat to the scene projection, then to pixels of the enlarged picture.
            inverse = ~fine
            parts = []
            for ring in rings(f["geometry"]):
                xs, ys = transform("EPSG:4326", src.crs, [p[0] for p in ring], [p[1] for p in ring])
                pts = [inverse * (x, y) for x, y in zip(xs, ys, strict=True)]
                parts.append("M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in pts) + "Z")
            manifest[name] = {
                "file": f"/desa/{slug(name)}.jpg",
                "width": w,
                "height": h,
                "outline": "".join(parts),
                "date": scene["properties"]["datetime"][:10],
            }
            print(f"{name}: {w}x{h}, {jpg.stat().st_size // 1024} KB")
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    print("wrote", MANIFEST)


if __name__ == "__main__":
    main()
