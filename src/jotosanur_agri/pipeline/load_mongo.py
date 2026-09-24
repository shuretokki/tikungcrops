"""Sync MongoDB (db `jotosanur`) with the batch sources.

Sources:
    - BPS Tikung Dalam Angka 2014/2021 crop CSVs (village level, data years 2013/2020)
      -> harvests; the reference the satellite areas are checked against.
    - Sentinel season summaries per AOI unit (data/gold/sentinel/<aoi>_units.parquet)
      -> planting_seasons.

The source CSVs keep their Indonesian column names; this module maps them to the
English document fields.

Every document has a deterministic `_id` and is replace-upserted. The load owns its
sources: documents from them that it no longer produces are deleted, and documents
from `RETIRED_SOURCES` are removed. Partner input (`partner_input`) is never touched.
The `recorded_at` timestamp is kept from the first load, so an unchanged rerun modifies
nothing.

Usage: `python -m jotosanur_agri.pipeline.load_mongo [AOI]` (default Lamongan/Tikung).
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl
from pymongo import ReplaceOne
from pymongo.database import Database

from jotosanur_agri.mongo import SCHEMA_VERSION, as_datetime, connect, ensure_collections, harvest_doc, source
from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

SRC = Path("data/raw/sumber-data")
GOLD = Path("data/gold/sentinel")

# Sources no pipeline produces any more; their documents are deleted on load
RETIRED_SOURCES = ["sintetis_pandu", "dinas_perikanan_2021"]

# CSV `sumber` column -> validator enum
CSV_SOURCES = {
    "bps_tikung_dalam_angka_2014": "bps_tikung_2014",
    "bps_tikung_dalam_angka_2021": "bps_tikung_2021",
}


Doc = dict[str, Any]


def bps_harvests(csv: Path, now: datetime) -> list[Doc]:
    """Map a BPS crop CSV (one row per village and commodity) to `harvests` documents."""
    return [
        harvest_doc(
            _id=f"bps{r['tahun']}:{r['komoditas']}:{r['desa']}",
            sector="crops",
            commodity=r["komoditas"],
            location={"level": "village", "name": r["desa"], "district": r["kecamatan"]},
            period={"year": r["tahun"]},
            source=source(CSV_SOURCES[r["sumber"]], False, now),
            area_ha=r["luas_panen_ha"],
            production_ton=r["produksi_ton"],
            yield_ton_per_ha=r["produktivitas_ton_per_ha"],
        )
        for r in pl.read_csv(csv).iter_rows(named=True)
    ]


def planting_seasons(units_parquet: Path, aoi: str, now: datetime) -> list[Doc]:
    """Map gold unit summaries (unit x year x season) to `planting_seasons` documents."""

    def window(r: Doc, prefix: str) -> Doc:
        return {k: as_datetime(r[f"{prefix}_{k}"]) if r[f"{prefix}_{k}"] else None for k in ("start", "median", "end")}

    return [
        {
            "_id": f"sentinel:{aoi}:{r['unit']}:{r['year']}-{r['season']}",
            "schema_version": SCHEMA_VERSION,
            "aoi": aoi,
            "unit": r["unit"],
            "year": r["year"],
            "season": r["season"],
            "cells": r["cells"],
            "area_ha": float(r["area_ha"]),
            "rice_area_ha": float(r["rice_area_ha"]),
            "flooding": window(r, "flood"),
            "harvest": window(r, "harvest"),
            "peak_ndvi": r["peak_ndvi"],
            "source": source("sentinel", False, now),
        }
        for r in pl.read_parquet(units_parquet).iter_rows(named=True)
    ]


def sync(db: Database, collection: str, docs: list[Doc], owned: list[str], scope: Doc | None = None) -> Doc:
    """Replace-upsert `docs` by `_id`, then delete stale documents of the `owned` sources.

    Args:
        db: Target database.
        collection: Collection name.
        docs: Current documents from the owned sources.
        owned: `source.code` values this load is the only writer of.
        scope: Extra filter limiting pruning, e.g. one AOI.

    Returns:
        Inserted, replaced and deleted counts.
    """
    coll = db[collection]
    ids = [d["_id"] for d in docs]
    first_seen = {
        d["_id"]: d["source"]["recorded_at"] for d in coll.find({"_id": {"$in": ids}}, {"source.recorded_at": 1})
    }
    for d in docs:
        if d["_id"] in first_seen:
            d["source"]["recorded_at"] = first_seen[d["_id"]]
    result = coll.bulk_write([ReplaceOne({"_id": d["_id"]}, d, upsert=True) for d in docs]) if docs else None
    stale = coll.delete_many({"source.code": {"$in": owned}, "_id": {"$nin": ids}, **(scope or {})})
    return {
        "inserted": result.upserted_count if result else 0,
        "replaced": result.modified_count if result else 0,
        "deleted": stale.deleted_count,
    }


def main(aoi_spec: str = DEFAULT_AOI) -> None:
    """Create collections if needed, drop retired sources, then sync every source."""
    db = connect()
    ensure_collections(db)
    retired = db["harvests"].delete_many({"source.code": {"$in": RETIRED_SOURCES}}).deleted_count
    if retired:
        print(f"harvests: deleted {retired} docs from retired sources {RETIRED_SOURCES}")

    now = datetime.now(UTC)
    owned = list(CSV_SOURCES.values())
    harvests = bps_harvests(SRC / "bps-tikung-2013-pertanian.csv", now) + bps_harvests(
        SRC / "bps-tikung-2020-pertanian.csv", now
    )
    report = {"harvests": sync(db, "harvests", harvests, owned)}

    aoi = resolve(aoi_spec).slug
    units = GOLD / f"{aoi}_units.parquet"
    if units.exists():
        seasons = planting_seasons(units, aoi, now)
        report["planting_seasons"] = sync(db, "planting_seasons", seasons, ["sentinel"], {"aoi": aoi})
    else:
        print(f"planting_seasons: skipped, {units} not found (run `just gold {aoi_spec}` first)")

    for collection, counts in report.items():
        total = db[collection].count_documents({})
        print(f"{collection}: {counts}, {total} in collection")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI)
