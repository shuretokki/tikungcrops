# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""MongoDB connection, schema and document builders for the `jotosanur` database.

Shared by the batch ETL (`pipeline.load_mongo`), the dashboard forms (`store`)
and the aggregations (`mongo_agg`).

Collections:
    - harvests: polymorphic by `sector` (reference statistics per AOI unit, e.g. BPS
      village tables, partner input of crops or fish ponds).
    - planting_seasons: satellite planting seasons per AOI unit, year and season
      (MT1-MT3), from `pipeline.gold_sentinel.summarize_units`.
    - harvest_outlook: expected harvested area per AOI unit and week for seasons still
      running, from `pipeline.harvest_outlook`, replaced on every load.
    - cropping_intensity: seasons per hectare of paddy per AOI unit and year, from
      `pipeline.gold_sentinel.intensity_units`.

Values copied from sources (commodities such as ``padi``,
place names) stay as published. `source.code` is free text: ``partner_input``,
``sentinel``, or a reference publication id such as ``bps_tikung_2021``.
"""

from __future__ import annotations

import os
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database

ENV_FILE = Path(".env")
SCHEMA_VERSION = 2

_LOCATION_SCHEMA = {
    "bsonType": "object",
    "required": ["level", "name"],
    "properties": {"level": {"enum": ["plot", "village", "aoi_unit"]}},
}
_SOURCE_SCHEMA = {
    "bsonType": "object",
    "required": ["code", "is_synthetic"],
    "properties": {
        "code": {"bsonType": "string", "minLength": 1},
        "is_synthetic": {"bsonType": "bool"},
    },
}
# reference statistics can predate the satellites
_YEAR_SCHEMA = {"bsonType": "int", "minimum": 1900, "maximum": 2100}
_WINDOW_SCHEMA = {
    "bsonType": "object",
    "properties": {k: {"bsonType": ["date", "null"]} for k in ("start", "median", "end")},
}

VALIDATORS = {
    "harvests": {
        "bsonType": "object",
        "required": ["schema_version", "sector", "commodity", "location", "period", "source"],
        "properties": {
            "schema_version": {"enum": [SCHEMA_VERSION]},
            "sector": {"enum": ["crops", "fisheries"]},
            "commodity": {"bsonType": "string", "minLength": 1},
            "location": _LOCATION_SCHEMA,
            "period": {
                "bsonType": "object",
                "required": ["year"],
                "properties": {"year": _YEAR_SCHEMA},
            },
            "area_ha": {"bsonType": "double", "minimum": 0},
            "production_ton": {"bsonType": "double", "minimum": 0},
            "yield_ton_per_ha": {"bsonType": "double", "minimum": 0},
            "attributes": {"bsonType": "object"},
            "source": _SOURCE_SCHEMA,
        },
    },
    "planting_seasons": {
        "bsonType": "object",
        "required": [
            "schema_version",
            "aoi",
            "unit",
            "year",
            "season",
            "cells",
            "area_ha",
            "rice_area_ha",
            "source",
        ],
        "properties": {
            "schema_version": {"enum": [SCHEMA_VERSION]},
            "aoi": {"bsonType": "string", "minLength": 1},
            "unit": {"bsonType": "string", "minLength": 1},
            "year": _YEAR_SCHEMA,
            "season": {"enum": ["MT1", "MT2", "MT3"]},
            "cells": {"bsonType": "int", "minimum": 0},
            "area_ha": {"bsonType": "double", "minimum": 0},
            "rice_area_ha": {"bsonType": "double", "minimum": 0},
            "rice_unknown_ha": {"bsonType": "double", "minimum": 0},
            "flooding": _WINDOW_SCHEMA,
            "harvest": _WINDOW_SCHEMA,
            "peak_ndvi": {"bsonType": ["double", "null"]},
            "source": _SOURCE_SCHEMA,
        },
    },
    "harvest_outlook": {
        "bsonType": "object",
        "required": ["schema_version", "aoi", "unit", "week", "expected_ha", "cells", "issued_on", "source"],
        "properties": {
            "schema_version": {"enum": [SCHEMA_VERSION]},
            "aoi": {"bsonType": "string", "minLength": 1},
            "unit": {"bsonType": "string", "minLength": 1},
            "week": {"bsonType": "date"},
            "expected_ha": {"bsonType": "double", "minimum": 0},
            "cells": {"bsonType": "int", "minimum": 0},
            "issued_on": {"bsonType": "date"},
            "source": _SOURCE_SCHEMA,
        },
    },
    "cropping_intensity": {
        "bsonType": "object",
        "required": ["schema_version", "aoi", "unit", "year", "cells", "paddy_ha", "complete", "source"],
        "properties": {
            "schema_version": {"enum": [SCHEMA_VERSION]},
            "aoi": {"bsonType": "string", "minLength": 1},
            "unit": {"bsonType": "string", "minLength": 1},
            "year": _YEAR_SCHEMA,
            "cells": {"bsonType": "int", "minimum": 0},
            "paddy_ha": {"bsonType": "double", "minimum": 0},
            "ip_all": {"bsonType": ["double", "null"], "minimum": 0},
            "ip_rice": {"bsonType": ["double", "null"], "minimum": 0},
            "share_3plus": {"bsonType": ["double", "null"], "minimum": 0, "maximum": 1},
            "complete": {"bsonType": "bool"},
            "source": _SOURCE_SCHEMA,
        },
    },
}

# one index per access pattern: A1-A2 on harvests, A4 on planting_seasons, A3 needs none
INDEXES = {
    "harvests": [
        [("commodity", ASCENDING), ("period.year", ASCENDING)],
        [("commodity", ASCENDING), ("location.name", ASCENDING), ("period.harvest_date", ASCENDING)],
    ],
    "planting_seasons": [
        [("aoi", ASCENDING), ("unit", ASCENDING), ("year", ASCENDING)],
    ],
    "harvest_outlook": [
        [("aoi", ASCENDING), ("week", ASCENDING)],
    ],
    "cropping_intensity": [
        [("aoi", ASCENDING), ("year", ASCENDING)],
    ],
}


def load_env(path: Path = ENV_FILE) -> None:
    """Load KEY=VALUE lines from `path` into `os.environ` without overriding set variables."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def connect(timeout_ms: int = 5000) -> Database:
    """Open the project database from `MONGO_URI` and `MONGO_DB`.

    Args:
        timeout_ms: Server selection timeout, so a stopped container fails fast.

    Returns:
        The `jotosanur` database (or whatever `MONGO_DB` names).

    Raises:
        KeyError: If `MONGO_URI` is not set in the environment or `.env`.
    """
    load_env()
    client = MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=timeout_ms)
    return client[os.environ.get("MONGO_DB", "jotosanur")]


def ensure_collections(db: Database) -> None:
    """Create every collection in `VALIDATORS` with its strict validator and indexes.

    Idempotent: existing collections get the validator re-applied via `collMod`.
    """
    existing = set(db.list_collection_names())
    for name, schema in VALIDATORS.items():
        options = {
            "validator": {"$jsonSchema": schema},
            "validationLevel": "strict",
            "validationAction": "error",
        }
        if name in existing:
            db.command("collMod", name, **options)
        else:
            db.create_collection(name, **options)
        for keys in INDEXES[name]:
            db[name].create_index(keys)


def as_datetime(value: date | datetime) -> datetime:
    """Convert a date or naive datetime to an aware UTC datetime (BSON has no date-only type)."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    return datetime(value.year, value.month, value.day, tzinfo=UTC)


def source(code: str, is_synthetic: bool, recorded_at: datetime) -> dict[str, Any]:
    """Build the `source` subdocument. `recorded_by` stays None until forms have logins."""
    return {
        "code": code,
        "is_synthetic": is_synthetic,
        "recorded_at": recorded_at,
        "recorded_by": None,
    }


def harvest_doc(
    _id: str,
    sector: str,
    commodity: str,
    location: dict[str, Any],
    period: dict[str, Any],
    source: dict[str, Any],
    attributes: dict[str, Any] | None = None,
    area_ha: float | None = None,
    production_ton: float | None = None,
    yield_ton_per_ha: float | None = None,
) -> dict[str, Any]:
    """Build a `harvests` document. Measures left as None are omitted, not stored as null.

    Args:
        _id: Deterministic id, e.g. ``"bps2020:padi:Jotosanur"``.
        sector: ``"crops"`` or ``"fisheries"``.
        commodity: Commodity as the source names it, e.g. ``"padi"``.
        location: ``{level, name, aoi?, village?, district?}``. Reference rows use level
            ``"aoi_unit"`` with the AOI slug.
        period: ``{year, start_date?, harvest_date?, cycle?}``.
        source: Output of `source`.
        attributes: Commodity-specific fields.
        area_ha: Harvested area.
        production_ton: Production.
        yield_ton_per_ha: Yield.

    Returns:
        The document, ready for insert or replace.
    """
    doc = {
        "_id": _id,
        "schema_version": SCHEMA_VERSION,
        "sector": sector,
        "commodity": commodity,
        "location": location,
        "period": period,
        "attributes": attributes or {},
        "source": source,
    }
    measures = {
        "area_ha": area_ha,
        "production_ton": production_ton,
        "yield_ton_per_ha": yield_ton_per_ha,
    }
    # 0.0 is a real value (failed harvest), so test for None, not falsiness
    doc.update({key: float(value) for key, value in measures.items() if value is not None})
    return doc
