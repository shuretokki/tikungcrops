"""MongoDB connection, schema and document builders for the `jotosanur` database.

Shared by the batch ETL (`pipeline.load_mongo`), the dashboard forms (`store`)
and the aggregations (`mongo_agg`). Spec: documents/local/skema-hibrida.md
section 3.
"""

from __future__ import annotations

import os
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database

ENV_FILE = Path(".env")
SCHEMA_VERSION = 1

SUMBER_KODE = [
    "bps_tikung_2014",
    "bps_tikung_2021",
    "dinas_perikanan_2021",
    "sintetis_pandu",
    "input_mitra",
]

_LOKASI_SCHEMA = {
    "bsonType": "object",
    "required": ["tingkat", "nama"],
    "properties": {"tingkat": {"enum": ["plot", "desa", "kabupaten"]}},
}
_SUMBER_SCHEMA = {
    "bsonType": "object",
    "required": ["kode", "is_synthetic"],
    "properties": {
        "kode": {"enum": SUMBER_KODE},
        "is_synthetic": {"bsonType": "bool"},
    },
}
_TAHUN_SCHEMA = {"bsonType": "int", "minimum": 2000, "maximum": 2100}

VALIDATORS = {
    "panen": {
        "bsonType": "object",
        "required": ["schema_version", "sektor", "komoditas", "lokasi", "periode", "sumber"],
        "properties": {
            "schema_version": {"enum": [SCHEMA_VERSION]},
            "sektor": {"enum": ["tanaman", "perikanan"]},
            "komoditas": {"bsonType": "string", "minLength": 1},
            "lokasi": _LOKASI_SCHEMA,
            "periode": {
                "bsonType": "object",
                "required": ["tahun"],
                "properties": {"tahun": _TAHUN_SCHEMA},
            },
            "luas_ha": {"bsonType": "double", "minimum": 0},
            "produksi_ton": {"bsonType": "double", "minimum": 0},
            "produktivitas_ton_per_ha": {"bsonType": "double", "minimum": 0},
            "atribut": {"bsonType": "object"},
            "sumber": _SUMBER_SCHEMA,
        },
    },
    "ternak": {
        "bsonType": "object",
        "required": ["schema_version", "jenis_ternak", "lokasi", "tanggal", "tahun", "jumlah_ekor", "sumber"],
        "properties": {
            "schema_version": {"enum": [SCHEMA_VERSION]},
            "jenis_ternak": {"bsonType": "string", "minLength": 1},
            "lokasi": _LOKASI_SCHEMA,
            "tanggal": {"bsonType": "date"},
            "tahun": _TAHUN_SCHEMA,
            "jumlah_ekor": {"bsonType": "int", "minimum": 0},
            "rtp": {"bsonType": "int", "minimum": 0},
            "struktur_umur": {"bsonType": "object"},
            "sumber": _SUMBER_SCHEMA,
        },
    },
}

# One index per access pattern A1-A3 (spec section 3.3); A4/A5 need none.
INDEXES = {
    "panen": [
        [("komoditas", ASCENDING), ("periode.tahun", ASCENDING)],
        [("komoditas", ASCENDING), ("lokasi.nama", ASCENDING), ("periode.tanggal_panen", ASCENDING)],
    ],
    "ternak": [
        [("jenis_ternak", ASCENDING), ("lokasi.nama", ASCENDING), ("tanggal", ASCENDING)],
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
    """Create `panen` and `ternak` with strict validators and their indexes.

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


def sumber(kode: str, is_synthetic: bool, dicatat_pada: datetime) -> dict[str, Any]:
    """Build the `sumber` subdocument. `dicatat_oleh` stays None until forms have logins."""
    return {
        "kode": kode,
        "is_synthetic": is_synthetic,
        "dicatat_pada": dicatat_pada,
        "dicatat_oleh": None,
    }


def panen_doc(
    _id: str,
    sektor: str,
    komoditas: str,
    lokasi: dict[str, Any],
    periode: dict[str, Any],
    sumber: dict[str, Any],
    atribut: dict[str, Any] | None = None,
    luas_ha: float | None = None,
    produksi_ton: float | None = None,
    produktivitas_ton_per_ha: float | None = None,
) -> dict[str, Any]:
    """Build a `panen` document. Measures left as None are omitted, not stored as null.

    Args:
        _id: Deterministic id, e.g. ``"pandu:MT1-P01"``.
        sektor: ``"tanaman"`` or ``"perikanan"``.
        komoditas: Commodity, e.g. ``"padi"``.
        lokasi: ``{tingkat, nama, desa?, kecamatan?}``.
        periode: ``{tahun, tanggal_mulai?, tanggal_panen?, siklus_ke?}``.
        sumber: Output of `sumber`.
        atribut: Commodity-specific fields.
        luas_ha: Harvested area.
        produksi_ton: Production.
        produktivitas_ton_per_ha: Yield.

    Returns:
        The document, ready for insert or replace.
    """
    doc = {
        "_id": _id,
        "schema_version": SCHEMA_VERSION,
        "sektor": sektor,
        "komoditas": komoditas,
        "lokasi": lokasi,
        "periode": periode,
        "atribut": atribut or {},
        "sumber": sumber,
    }
    measures = {
        "luas_ha": luas_ha,
        "produksi_ton": produksi_ton,
        "produktivitas_ton_per_ha": produktivitas_ton_per_ha,
    }
    # 0.0 is a real value (failed harvest), so test for None, not falsiness
    doc.update({key: float(value) for key, value in measures.items() if value is not None})
    return doc
