"""Sync MongoDB (db `jotosanur`) with the batch outputs of one AOI.

Sources:
    - Reference statistics for the AOI, if any
      (data/reference/<aoi>/harvested_area.csv, see its README) -> harvests.
    - Sentinel season summaries per AOI unit (data/gold/sentinel/<aoi>_units.parquet)
      -> planting_seasons.

Every document has a deterministic `_id` and is replace-upserted. Documents of the AOI
that the load no longer produces are deleted, and documents from `RETIRED_SOURCES` are
removed. Partner input (`partner_input`) is never touched. The `recorded_at`
timestamp is kept from the first load, so an unchanged rerun modifies nothing.

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
from jotosanur_agri.pipeline.reference import ReferenceDataError, read_reference

GOLD = Path("data/gold/sentinel")

# Sources no pipeline produces any more; their documents are deleted on load
RETIRED_SOURCES = ["sintetis_pandu", "dinas_perikanan_2021"]

Doc = dict[str, Any]


def reference_harvests(reference: pl.DataFrame, aoi: str, now: datetime) -> list[Doc]:
    """Map an AOI's checked reference rows (see `reference.read_reference`) to `harvests` documents."""
    docs = []
    for r in reference.iter_rows(named=True):
        area, production = r["harvested_area_ha"], r["production_ton"]
        docs.append(
            harvest_doc(
                _id=f"ref:{aoi}:{r['year']}:{r['crop']}:{r['unit']}",
                sector="crops",
                commodity=r["crop"],
                location={"level": "aoi_unit", "name": r["unit"], "aoi": aoi},
                period={"year": r["year"]},
                source=source(r["source"], False, now),
                area_ha=area,
                production_ton=production,
                yield_ton_per_ha=round(production / area, 3) if area and production is not None else None,
            )
        )
    return docs


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


def sync(db: Database, collection: str, docs: list[Doc], owned: Doc) -> Doc:
    """Replace-upsert `docs` by `_id`, then delete the `owned` documents not among them.

    Args:
        db: Target database.
        collection: Collection name.
        docs: Current documents.
        owned: Filter matching every document this load is the only writer of, e.g. one
            AOI's satellite seasons.

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
    stale = coll.delete_many({**owned, "_id": {"$nin": ids}})
    return {
        "inserted": result.upserted_count if result else 0,
        "replaced": result.modified_count if result else 0,
        "deleted": stale.deleted_count,
    }


def main(aoi_spec: str = DEFAULT_AOI) -> None:
    """Check the inputs, create collections if needed, drop retired sources, then sync every source."""
    area = resolve(aoi_spec)
    aoi = area.slug
    # Checked before anything is written, so a bad file leaves the database untouched
    reference = read_reference(area)

    db = connect()
    ensure_collections(db)
    retired = db["harvests"].delete_many({"source.code": {"$in": RETIRED_SOURCES}}).deleted_count
    if retired:
        print(f"harvests: deleted {retired} docs from retired sources {RETIRED_SOURCES}")

    now = datetime.now(UTC)
    harvests = reference_harvests(reference, aoi, now) if reference is not None else []
    if not harvests:
        print(f"harvests: no reference statistics for {aoi}")
    # Partner input carries no `location.aoi`, so it is never in this filter
    report = {"harvests": sync(db, "harvests", harvests, {"location.aoi": aoi})}

    units = GOLD / f"{aoi}_units.parquet"
    if units.exists():
        seasons = planting_seasons(units, aoi, now)
        report["planting_seasons"] = sync(db, "planting_seasons", seasons, {"source.code": "sentinel", "aoi": aoi})
    else:
        print(f"planting_seasons: skipped, {units} not found (run `just gold {aoi_spec}` first)")

    for collection, counts in report.items():
        total = db[collection].count_documents({})
        print(f"{collection}: {counts}, {total} in collection")


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI)
    except ReferenceDataError as e:
        sys.exit(f"reference data rejected, nothing written:\n{e}")
