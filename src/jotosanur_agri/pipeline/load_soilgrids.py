"""Bronze/Silver pipeline for SoilGrids v2.0 soil properties at Desa Jotosanur.

Source: ISRIC SoilGrids 2.0 (Poggio et al., 2021), 250 m resolution,
CC-BY 4.0. REST endpoint is beta with no uptime guarantee; responses are
cached as raw JSON (one file per point and property), so this is a one-time pull,
re-fetched only with --refresh. WCS fallback (manual): https://maps.isric.org/mapserv?map=/map/<property>.map

Bronze = raw JSON per point/property + a flattened long table of mapped (integer)
values, exactly as returned.
Silver = values divided by d_factor into target units, plus a wide 0-5 cm
mean table using the same SoilGrids_* columns as the CIMMYT dataset
(CIMMYT's dictionary: "toipsoil (0-5cm) ... according to SoilGrids"), so
Jotosanur can be fed to the CIMMYT-trained model.

Jotosanur has no official coordinate in our documents, so two public
points are queried (~1 km apart, i.e. ~4 SoilGrids pixels):
- osm: OSM node 1308667031 (place=village)
- wikidata: Q14633038 P625 (P131 = Tikung, confirms the kecamatan)
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

import polars as pl

from jotosanur_agri.pipeline import save

API_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"

POINTS = {
    "osm": {"lat": -7.1520910, "lon": 112.4025416},
    "wikidata": {"lat": -7.1583333, "lon": 112.4108333},
}

# Same 9 properties as the CIMMYT SoilGrids_* columns.
PROPERTIES = ["bdod", "cfvo", "clay", "nitrogen", "ocd", "phh2o", "sand", "silt", "soc"]
DEPTHS = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]
VALUES = ["mean", "Q0.05", "Q0.5", "Q0.95", "uncertainty"]

CIMMYT_DEPTH = "0-5cm"
REQUEST_GAP_S = 12


def _query_url(lat: float, lon: float, prop: str) -> str:
    params = [("lon", lon), ("lat", lat), ("property", prop)]
    params += [("depth", d) for d in DEPTHS]
    params += [("value", v) for v in VALUES]
    return f"{API_URL}?{urllib.parse.urlencode(params)}"


def fetch_property(lat: float, lon: float, prop: str, retries: int = 4, timeout: int = 120) -> dict[str, Any]:
    """Query one property at one point, retrying with a growing back-off.

    Raises:
        RuntimeError: If every attempt fails.
    """
    url = _query_url(lat, lon, prop)
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                return json.load(resp)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
            last_err = err
            if attempt < retries:
                time.sleep(15 * attempt)
    raise RuntimeError(f"SoilGrids {prop} query failed after {retries} attempts: {last_err}")


def load_raw(raw_dir: Path, refresh: bool = False) -> dict[str, dict[str, Any]]:
    """Load every point's layers, fetching only properties not cached as JSON yet.

    One request per property, because the beta API times out on the full 9-property
    query. Each response is cached on its own, so an interrupted run resumes.

    Args:
        raw_dir: Directory for the cached JSON responses.
        refresh: Refetch even when a cached response exists.

    Returns:
        Per point: lat, lon and the list of property layers.
    """
    raw = {}
    for name, pt in POINTS.items():
        point_dir = raw_dir / name
        point_dir.mkdir(parents=True, exist_ok=True)
        layers = []
        for prop in PROPERTIES:
            path = point_dir / f"{prop}.json"
            if not path.exists() or refresh:
                payload = fetch_property(pt["lat"], pt["lon"], prop)
                payload["_fetched_on"] = date.today().isoformat()
                path.write_text(json.dumps(payload, indent=2))
                print(f"[soilgrids] fetched {name}/{prop}")
                # ISRIC fair use: max 5 calls/min.
                time.sleep(REQUEST_GAP_S)
            payload = json.loads(path.read_text())
            for layer in payload["properties"]["layers"]:
                layer["_fetched_on"] = payload["_fetched_on"]
                layers.append(layer)
        raw[name] = {"lat": pt["lat"], "lon": pt["lon"], "layers": layers}
    return raw


def to_bronze(raw: dict[str, dict[str, Any]]) -> pl.DataFrame:
    """Flatten the layers to one row per point, property, depth and statistic, values as mapped."""
    rows = []
    for name, payload in raw.items():
        lat, lon = payload["lat"], payload["lon"]
        for layer in payload["layers"]:
            um = layer["unit_measure"]
            for depth in layer["depths"]:
                for stat, value in depth["values"].items():
                    rows.append(
                        {
                            "point": name,
                            "lat": lat,
                            "lon": lon,
                            "property": layer["name"],
                            "depth": depth["label"],
                            "top_cm": depth["range"]["top_depth"],
                            "bottom_cm": depth["range"]["bottom_depth"],
                            "stat": stat,
                            "mapped_value": value,
                            "d_factor": um["d_factor"],
                            "mapped_units": um["mapped_units"],
                            "target_units": um["target_units"],
                            "fetched_on": layer["_fetched_on"],
                        }
                    )
    return pl.DataFrame(rows, schema_overrides={"mapped_value": pl.Float64})


def to_silver(bronze: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Convert to target units and build the 0-5 cm mean table in CIMMYT's column layout.

    Returns:
        (long table in target units, one wide row per point with `SoilGrids_*` columns).
    """
    # Uncertainty is a ratio index, not in property units; keep it unscaled.
    long = bronze.with_columns(
        pl.when(pl.col("stat") == "uncertainty")
        .then(pl.col("mapped_value"))
        .otherwise(pl.col("mapped_value") / pl.col("d_factor"))
        .alias("value"),
        pl.when(pl.col("stat") == "uncertainty").then(pl.lit("index")).otherwise(pl.col("target_units")).alias("units"),
    ).select("point", "lat", "lon", "property", "depth", "top_cm", "bottom_cm", "stat", "value", "units")

    # CIMMYT's SoilGrids_ocd is 10x smaller than the API's hg/m³ value:
    # in CIMMYT, soc*bdod/ocd has median 10.2 (p10-p90 8.1-12.4), so rescale
    # ocd to match the scale the model was trained on.
    cimmyt_wide = (
        long.filter((pl.col("depth") == CIMMYT_DEPTH) & (pl.col("stat") == "mean"))
        .with_columns(
            pl.when(pl.col("property") == "ocd").then(pl.col("value") / 10).otherwise(pl.col("value")).alias("value")
        )
        .pivot(on="property", index=["point", "lat", "lon"], values="value")
        .rename({p: f"SoilGrids_{p}" for p in PROPERTIES})
        .select("point", "lat", "lon", *[f"SoilGrids_{p}" for p in PROPERTIES])
    )
    return long, cimmyt_wide


def run_soilgrids_pipeline(out_dir: str | Path = "data", refresh: bool = False) -> dict[str, Any]:
    """Fetch or reuse the raw responses and write bronze and silver tables.

    Returns:
        Row counts, null count and output paths.
    """
    bronze_dir = Path(out_dir) / "bronze" / "soilgrids"
    silver_dir = Path(out_dir) / "silver" / "soilgrids"

    bronze = to_bronze(load_raw(bronze_dir / "raw", refresh=refresh))
    bronze_path = save(bronze, bronze_dir / "soilgrids_long.parquet")
    long, cimmyt_wide = to_silver(bronze)

    n_null = long.filter(pl.col("value").is_null()).height
    if n_null:
        # SoilGrids masks urban/water pixels as null.
        print(f"[soilgrids] {n_null} null values (masked pixels?)")

    return {
        "rows_bronze": bronze.height,
        "rows_silver_long": long.height,
        "null_values": n_null,
        "bronze_path": bronze_path,
        "silver_long_path": save(long, silver_dir / "soilgrids_long.parquet"),
        "silver_cimmyt_path": save(cimmyt_wide, silver_dir / "soilgrids_cimmyt_0-5cm.parquet"),
    }


if __name__ == "__main__":
    print(run_soilgrids_pipeline(refresh="--refresh" in sys.argv))
