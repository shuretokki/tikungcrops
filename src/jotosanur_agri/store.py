"""Storage for the dashboard input forms: SQLite for distribution, MongoDB for partner harvests.

SQLite `data/relational.db` holds users, destinations and distributions (spec section 4).
`destinations` is seeded with the 4 MBG districts named in the news source.
`distributions` is never seeded, because only aggregates are known and splitting them
per kitchen would invent data.

Partner harvests go to Mongo `harvests` with `source.code = "partner_input"`. The
collection validator is the last line of defence. The obvious cases are checked
here first so the form can show a readable error.

`distributions.harvest_ref` points at a Mongo `harvests._id`. Neither database can
enforce that link, so `add_distribution` checks it.
"""

from __future__ import annotations

import re
import sqlite3
from contextlib import closing
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from pymongo import DESCENDING
from pymongo.collection import Collection

from jotosanur_agri.mongo import as_datetime, harvest_doc, source

SQLITE_PATH = Path("data/relational.db")

DDL = """
CREATE TABLE IF NOT EXISTS users (
  id         INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  role       TEXT NOT NULL CHECK (role IN ('admin', 'operator', 'viewer')),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS destinations (
  id       INTEGER PRIMARY KEY,
  type     TEXT NOT NULL CHECK (type IN ('district', 'mbg_kitchen')),
  name     TEXT NOT NULL,
  district TEXT NOT NULL,
  UNIQUE (type, name)
);
CREATE TABLE IF NOT EXISTS distributions (
  id             INTEGER PRIMARY KEY,
  date           TEXT NOT NULL,
  item_type      TEXT NOT NULL CHECK (item_type IN ('seed', 'harvest')),
  commodity      TEXT NOT NULL,
  quantity       REAL NOT NULL CHECK (quantity > 0),
  unit           TEXT NOT NULL CHECK (unit IN ('kg', 'ton', 'head')),
  destination_id INTEGER NOT NULL REFERENCES destinations(id),
  harvest_ref    TEXT,
  user_id        INTEGER REFERENCES users(id),
  source         TEXT NOT NULL CHECK (source IN ('partner_input', 'news'))
);
CREATE INDEX IF NOT EXISTS idx_distributions_date ON distributions (date);
"""

# lamongan.inews.id/read/618426 (2025-07-13): 7 MBG kitchens in these districts
SEED_MBG_DISTRICTS = ["Lamongan", "Babat", "Sugio", "Kembangbahu"]

ITEM_TYPES = ["seed", "harvest"]
UNITS = ["kg", "ton", "head"]
DESTINATION_TYPES = ["district", "mbg_kitchen"]

# Kampung Pandu Sakti's location, partner input is always from there
PARTNER_LOCATION = {"village": "Jotosanur", "district": "Tikung"}

Row = dict[str, Any]


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    # SQLite leaves foreign keys off unless enabled per connection
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_sqlite(path: Path = SQLITE_PATH) -> None:
    """Create the tables and seed `destinations`. Idempotent."""
    with closing(_connect(path)) as conn, conn:
        conn.executescript(DDL)
        conn.executemany(
            "INSERT OR IGNORE INTO destinations (type, name, district) VALUES ('district', ?, ?)",
            [(d, d) for d in SEED_MBG_DISTRICTS],
        )


def list_destinations(path: Path = SQLITE_PATH) -> list[Row]:
    """All destinations, ordered by type then name."""
    with closing(_connect(path)) as conn:
        rows = conn.execute("SELECT id, type, name, district FROM destinations ORDER BY type, name")
        return [dict(r) for r in rows]


def add_destination(type_: str, name: str, district: str, path: Path = SQLITE_PATH) -> int:
    """Add a destination.

    Returns:
        The new row id.

    Raises:
        ValueError: If `name` or `district` is blank.
        sqlite3.IntegrityError: If a destination with the same type and name exists.
    """
    name, district = name.strip(), district.strip()
    if not name or not district:
        raise ValueError("Nama dan kecamatan wajib diisi.")
    with closing(_connect(path)) as conn, conn:
        row = conn.execute(
            "INSERT INTO destinations (type, name, district) VALUES (?, ?, ?) RETURNING id", (type_, name, district)
        ).fetchone()
        return row["id"]


def list_distributions(path: Path = SQLITE_PATH) -> list[Row]:
    """All distribution records joined with their destination, newest first."""
    with closing(_connect(path)) as conn:
        rows = conn.execute(
            """
            SELECT d.id, d.date, d.item_type, d.commodity, d.quantity, d.unit,
                   t.name AS destination, t.type AS destination_type, t.district,
                   d.harvest_ref, d.source
            FROM distributions d JOIN destinations t ON t.id = d.destination_id
            ORDER BY d.date DESC, d.id DESC
            """
        )
        return [dict(r) for r in rows]


def add_distribution(
    day: date,
    item_type: str,
    commodity: str,
    quantity: float,
    unit: str,
    destination_id: int,
    harvest_ref: str | None = None,
    harvests: Collection | None = None,
    path: Path = SQLITE_PATH,
) -> int:
    """Record one distribution entered by the partner.

    Args:
        day: Delivery date.
        item_type: ``"seed"`` or ``"harvest"``.
        commodity: What was delivered, stored lowercase.
        quantity: Quantity, must be > 0 (enforced by a CHECK constraint).
        unit: ``"kg"``, ``"ton"`` or ``"head"``.
        destination_id: `destinations.id` of the destination.
        harvest_ref: Optional Mongo `harvests._id` the goods came from.
        harvests: The `harvests` collection, needed only to verify `harvest_ref`.
        path: SQLite file.

    Returns:
        The new row id.

    Raises:
        ValueError: If `commodity` is blank or `harvest_ref` cannot be verified.
        sqlite3.IntegrityError: If a CHECK or foreign key constraint fails.
    """
    commodity = commodity.strip().lower()
    if not commodity:
        raise ValueError("Komoditas wajib diisi.")
    if harvest_ref:
        if harvests is None:
            raise ValueError("MongoDB tidak tersedia, referensi panen tidak bisa dicek.")
        if harvests.count_documents({"_id": harvest_ref}, limit=1) == 0:
            raise ValueError(f"Referensi panen `{harvest_ref}` tidak ditemukan di MongoDB.")
    with closing(_connect(path)) as conn, conn:
        row = conn.execute(
            """
            INSERT INTO distributions
              (date, item_type, commodity, quantity, unit, destination_id, harvest_ref, user_id, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 'partner_input')
            RETURNING id
            """,
            (day.isoformat(), item_type, commodity, quantity, unit, destination_id, harvest_ref or None),
        ).fetchone()
        return row["id"]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")


def add_partner_harvest(
    harvests: Collection,
    sector: str,
    commodity: str,
    level: str,
    location_name: str,
    harvest_date: date,
    start_date: date | None = None,
    area_ha: float | None = None,
    production_ton: float | None = None,
) -> str:
    """Insert one harvest entered by the partner.

    The `_id` is ``partner:{commodity}:{location}:{harvest_date}``, so the same harvest
    cannot be recorded twice.

    Args:
        harvests: The `harvests` collection.
        sector: ``"crops"`` or ``"fisheries"``.
        commodity: Commodity, normalised to a lowercase slug.
        level: ``"plot"`` or ``"village"``.
        location_name: Plot or pond name.
        harvest_date: Harvest date.
        start_date: Planting or stocking date.
        area_ha: Harvested area.
        production_ton: Production, 0 records a failed harvest.

    Returns:
        The new document id.

    Raises:
        ValueError: If a required field is blank or the dates are out of order.
        pymongo.errors.DuplicateKeyError: If this harvest was already recorded.
        pymongo.errors.WriteError: If the collection validator rejects the document.
    """
    commodity = _slug(commodity)
    location_name = location_name.strip()
    if not commodity or not location_name:
        raise ValueError("Komoditas dan nama lokasi wajib diisi.")
    if start_date and start_date > harvest_date:
        raise ValueError("Tanggal mulai tidak boleh setelah tanggal panen.")

    period = {"year": harvest_date.year, "harvest_date": as_datetime(harvest_date)}
    if start_date:
        period["start_date"] = as_datetime(start_date)
    yield_ = round(production_ton / area_ha, 3) if area_ha and production_ton is not None else None

    doc = harvest_doc(
        _id=f"partner:{commodity}:{_slug(location_name)}:{harvest_date.isoformat()}",
        sector=sector,
        commodity=commodity,
        location={"level": level, "name": location_name, **PARTNER_LOCATION},
        period=period,
        source=source("partner_input", False, datetime.now(UTC)),
        area_ha=area_ha,
        production_ton=production_ton,
        yield_ton_per_ha=yield_,
    )
    harvests.insert_one(doc)
    return doc["_id"]


def list_partner_harvests(harvests: Collection, limit: int = 200) -> list[Row]:
    """Harvests entered by the partner, flattened for a table, latest harvest first."""
    cursor = harvests.find({"source.code": "partner_input"}).sort("period.harvest_date", DESCENDING).limit(limit)
    return [
        {
            "_id": d["_id"],
            "sector": d["sector"],
            "commodity": d["commodity"],
            "location": d["location"]["name"],
            "start_date": d["period"].get("start_date"),
            "harvest_date": d["period"].get("harvest_date"),
            "area_ha": d.get("area_ha"),
            "production_ton": d.get("production_ton"),
            "yield_ton_per_ha": d.get("yield_ton_per_ha"),
            "recorded_at": d["source"]["recorded_at"],
        }
        for d in cursor
    ]
