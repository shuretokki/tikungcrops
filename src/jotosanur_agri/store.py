"""Storage for the dashboard input forms: SQLite for distribution, MongoDB for mitra harvests.

SQLite `data/relasional.db` holds pengguna, tujuan and distribusi (spec section 4).
`tujuan` is seeded with the 4 MBG kecamatan named in the news source; `distribusi`
is never seeded, because only aggregates are known and splitting them per dapur
would invent data.

Mitra harvests go to Mongo `panen` with `sumber.kode = "input_mitra"`. The
collection validator is the last line of defence; the obvious cases are checked
here first so the form can show a readable error.

`distribusi.panen_ref` points at a Mongo `panen._id`. Neither database can enforce
that link, so `add_distribusi` checks it.
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

from jotosanur_agri.mongo import as_datetime, panen_doc, sumber

SQLITE_PATH = Path("data/relasional.db")

DDL = """
CREATE TABLE IF NOT EXISTS pengguna (
  id          INTEGER PRIMARY KEY,
  nama        TEXT NOT NULL,
  peran       TEXT NOT NULL CHECK (peran IN ('admin', 'operator', 'viewer')),
  dibuat_pada TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS tujuan (
  id        INTEGER PRIMARY KEY,
  jenis     TEXT NOT NULL CHECK (jenis IN ('kecamatan', 'dapur_mbg')),
  nama      TEXT NOT NULL,
  kecamatan TEXT NOT NULL,
  UNIQUE (jenis, nama)
);
CREATE TABLE IF NOT EXISTS distribusi (
  id           INTEGER PRIMARY KEY,
  tanggal      TEXT NOT NULL,
  jenis_barang TEXT NOT NULL CHECK (jenis_barang IN ('bibit', 'hasil_panen')),
  komoditas    TEXT NOT NULL,
  jumlah       REAL NOT NULL CHECK (jumlah > 0),
  satuan       TEXT NOT NULL CHECK (satuan IN ('kg', 'ton', 'ekor')),
  tujuan_id    INTEGER NOT NULL REFERENCES tujuan(id),
  panen_ref    TEXT,
  pengguna_id  INTEGER REFERENCES pengguna(id),
  sumber       TEXT NOT NULL CHECK (sumber IN ('input_mitra', 'berita'))
);
CREATE INDEX IF NOT EXISTS idx_distribusi_tanggal ON distribusi (tanggal);
"""

# lamongan.inews.id/read/618426 (2025-07-13): 7 dapur MBG in these kecamatan
SEED_KECAMATAN_MBG = ["Lamongan", "Babat", "Sugio", "Kembangbahu"]

JENIS_BARANG = ["bibit", "hasil_panen"]
SATUAN = ["kg", "ton", "ekor"]
JENIS_TUJUAN = ["kecamatan", "dapur_mbg"]

# Kampung Pandu Sakti's location; mitra input is always from there
MITRA_LOKASI = {"desa": "Jotosanur", "kecamatan": "Tikung"}

Row = dict[str, Any]


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    # SQLite leaves foreign keys off unless enabled per connection
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_sqlite(path: Path = SQLITE_PATH) -> None:
    """Create the tables and seed `tujuan`. Idempotent."""
    with closing(_connect(path)) as conn, conn:
        conn.executescript(DDL)
        conn.executemany(
            "INSERT OR IGNORE INTO tujuan (jenis, nama, kecamatan) VALUES ('kecamatan', ?, ?)",
            [(k, k) for k in SEED_KECAMATAN_MBG],
        )


def list_tujuan(path: Path = SQLITE_PATH) -> list[Row]:
    """All destinations, ordered by type then name."""
    with closing(_connect(path)) as conn:
        rows = conn.execute("SELECT id, jenis, nama, kecamatan FROM tujuan ORDER BY jenis, nama")
        return [dict(r) for r in rows]


def add_tujuan(jenis: str, nama: str, kecamatan: str, path: Path = SQLITE_PATH) -> int:
    """Add a destination.

    Returns:
        The new row id.

    Raises:
        ValueError: If `nama` or `kecamatan` is blank.
        sqlite3.IntegrityError: If a destination with the same type and name exists.
    """
    nama, kecamatan = nama.strip(), kecamatan.strip()
    if not nama or not kecamatan:
        raise ValueError("Nama dan kecamatan wajib diisi.")
    with closing(_connect(path)) as conn, conn:
        row = conn.execute(
            "INSERT INTO tujuan (jenis, nama, kecamatan) VALUES (?, ?, ?) RETURNING id", (jenis, nama, kecamatan)
        ).fetchone()
        return row["id"]


def list_distribusi(path: Path = SQLITE_PATH) -> list[Row]:
    """All distribution records joined with their destination, newest first."""
    with closing(_connect(path)) as conn:
        rows = conn.execute(
            """
            SELECT d.id, d.tanggal, d.jenis_barang, d.komoditas, d.jumlah, d.satuan,
                   t.nama AS tujuan, t.jenis AS jenis_tujuan, t.kecamatan,
                   d.panen_ref, d.sumber
            FROM distribusi d JOIN tujuan t ON t.id = d.tujuan_id
            ORDER BY d.tanggal DESC, d.id DESC
            """
        )
        return [dict(r) for r in rows]


def add_distribusi(
    tanggal: date,
    jenis_barang: str,
    komoditas: str,
    jumlah: float,
    satuan: str,
    tujuan_id: int,
    panen_ref: str | None = None,
    panen: Collection | None = None,
    path: Path = SQLITE_PATH,
) -> int:
    """Record one distribution entered by the mitra.

    Args:
        tanggal: Delivery date.
        jenis_barang: ``"bibit"`` or ``"hasil_panen"``.
        komoditas: What was delivered; stored lowercase.
        jumlah: Quantity, must be > 0 (enforced by a CHECK constraint).
        satuan: ``"kg"``, ``"ton"`` or ``"ekor"``.
        tujuan_id: `tujuan.id` of the destination.
        panen_ref: Optional Mongo `panen._id` the goods came from.
        panen: The `panen` collection, needed only to verify `panen_ref`.
        path: SQLite file.

    Returns:
        The new row id.

    Raises:
        ValueError: If `komoditas` is blank or `panen_ref` cannot be verified.
        sqlite3.IntegrityError: If a CHECK or foreign key constraint fails.
    """
    komoditas = komoditas.strip().lower()
    if not komoditas:
        raise ValueError("Komoditas wajib diisi.")
    if panen_ref:
        if panen is None:
            raise ValueError("MongoDB tidak tersedia, referensi panen tidak bisa dicek.")
        if panen.count_documents({"_id": panen_ref}, limit=1) == 0:
            raise ValueError(f"Referensi panen `{panen_ref}` tidak ditemukan di MongoDB.")
    with closing(_connect(path)) as conn, conn:
        row = conn.execute(
            """
            INSERT INTO distribusi
              (tanggal, jenis_barang, komoditas, jumlah, satuan, tujuan_id, panen_ref, pengguna_id, sumber)
            VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 'input_mitra')
            RETURNING id
            """,
            (tanggal.isoformat(), jenis_barang, komoditas, jumlah, satuan, tujuan_id, panen_ref or None),
        ).fetchone()
        return row["id"]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")


def add_panen_mitra(
    panen: Collection,
    sektor: str,
    komoditas: str,
    tingkat: str,
    lokasi_nama: str,
    tanggal_panen: date,
    tanggal_mulai: date | None = None,
    luas_ha: float | None = None,
    produksi_ton: float | None = None,
) -> str:
    """Insert one harvest entered by the mitra.

    The `_id` is ``mitra:{komoditas}:{lokasi}:{tanggal_panen}``, so the same harvest
    cannot be recorded twice.

    Args:
        panen: The `panen` collection.
        sektor: ``"tanaman"`` or ``"perikanan"``.
        komoditas: Commodity, normalised to a lowercase slug.
        tingkat: ``"plot"`` or ``"desa"``.
        lokasi_nama: Plot or pond name.
        tanggal_panen: Harvest date.
        tanggal_mulai: Planting or stocking date.
        luas_ha: Harvested area.
        produksi_ton: Production; 0 records a failed harvest.

    Returns:
        The new document id.

    Raises:
        ValueError: If a required field is blank or the dates are out of order.
        pymongo.errors.DuplicateKeyError: If this harvest was already recorded.
        pymongo.errors.WriteError: If the collection validator rejects the document.
    """
    komoditas = _slug(komoditas)
    lokasi_nama = lokasi_nama.strip()
    if not komoditas or not lokasi_nama:
        raise ValueError("Komoditas dan nama lokasi wajib diisi.")
    if tanggal_mulai and tanggal_mulai > tanggal_panen:
        raise ValueError("Tanggal mulai tidak boleh setelah tanggal panen.")

    periode = {"tahun": tanggal_panen.year, "tanggal_panen": as_datetime(tanggal_panen)}
    if tanggal_mulai:
        periode["tanggal_mulai"] = as_datetime(tanggal_mulai)
    produktivitas = round(produksi_ton / luas_ha, 3) if luas_ha and produksi_ton is not None else None

    doc = panen_doc(
        _id=f"mitra:{komoditas}:{_slug(lokasi_nama)}:{tanggal_panen.isoformat()}",
        sektor=sektor,
        komoditas=komoditas,
        lokasi={"tingkat": tingkat, "nama": lokasi_nama, **MITRA_LOKASI},
        periode=periode,
        sumber=sumber("input_mitra", False, datetime.now(UTC)),
        luas_ha=luas_ha,
        produksi_ton=produksi_ton,
        produktivitas_ton_per_ha=produktivitas,
    )
    panen.insert_one(doc)
    return doc["_id"]


def list_panen_mitra(panen: Collection, limit: int = 200) -> list[Row]:
    """Harvests entered by the mitra, flattened for a table, latest harvest first."""
    cursor = panen.find({"sumber.kode": "input_mitra"}).sort("periode.tanggal_panen", DESCENDING).limit(limit)
    return [
        {
            "_id": d["_id"],
            "sektor": d["sektor"],
            "komoditas": d["komoditas"],
            "lokasi": d["lokasi"]["nama"],
            "tanggal_mulai": d["periode"].get("tanggal_mulai"),
            "tanggal_panen": d["periode"].get("tanggal_panen"),
            "luas_ha": d.get("luas_ha"),
            "produksi_ton": d.get("produksi_ton"),
            "produktivitas_ton_per_ha": d.get("produktivitas_ton_per_ha"),
            "dicatat_pada": d["sumber"]["dicatat_pada"],
        }
        for d in cursor
    ]
