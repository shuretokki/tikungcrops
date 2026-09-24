"""Sync MongoDB (db `jotosanur`) with the batch sources.

Sources:
    - BPS Tikung Dalam Angka 2014/2021 CSVs (desa level, data years 2013/2020) -> panen, ternak.
    - Dinas Perikanan Lamongan Profil 2021 CSV (kabupaten level) -> panen.
    - Sentinel season summaries per AOI unit (data/gold/sentinel/<aoi>_units.parquet)
      -> musim_tanam.

Every document has a deterministic `_id` and is replace-upserted. The load owns its
sources: documents from them that it no longer produces are deleted, and documents
from `RETIRED_SOURCES` are removed. Mitra input (`input_mitra`) is never touched. The
`dicatat_pada` timestamp is kept from the first load, so an unchanged rerun modifies
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

from jotosanur_agri.mongo import SCHEMA_VERSION, as_datetime, connect, ensure_collections, panen_doc, sumber
from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

SRC = Path("data/raw/sumber-data")
GOLD = Path("data/gold/sentinel")

# Sources no pipeline produces any more; their documents are deleted on load
RETIRED_SOURCES = ["sintetis_pandu"]

# CSV `sumber` column -> validator enum
CSV_SUMBER = {
    "bps_tikung_dalam_angka_2014": "bps_tikung_2014",
    "bps_tikung_dalam_angka_2021": "bps_tikung_2021",
    "dinas_perikanan_lamongan_profil_2021": "dinas_perikanan_2021",
}

UMUR = ("anak", "muda", "dewasa")

Doc = dict[str, Any]


def bps_panen(csv: Path, now: datetime) -> list[Doc]:
    """Map a BPS crop CSV (one row per desa and commodity) to `panen` documents."""
    return [
        panen_doc(
            _id=f"bps{r['tahun']}:{r['komoditas']}:{r['desa']}",
            sektor="tanaman",
            komoditas=r["komoditas"],
            lokasi={"tingkat": "desa", "nama": r["desa"], "kecamatan": r["kecamatan"]},
            periode={"tahun": r["tahun"]},
            sumber=sumber(CSV_SUMBER[r["sumber"]], False, now),
            luas_ha=r["luas_panen_ha"],
            produksi_ton=r["produksi_ton"],
            produktivitas_ton_per_ha=r["produktivitas_ton_per_ha"],
        )
        for r in pl.read_csv(csv).iter_rows(named=True)
    ]


def bps_ternak(csv: Path, now: datetime) -> list[Doc]:
    """Map a BPS livestock CSV to `ternak` documents.

    The 2020 edition adds `rtp` and an age/sex breakdown; the 2013 one has totals only,
    so those fields are set only when the columns exist.
    """
    df = pl.read_csv(csv)
    has_rtp = "rtp" in df.columns
    has_umur = "anak_jantan" in df.columns
    docs = []
    for r in df.iter_rows(named=True):
        doc = {
            "_id": f"bps{r['tahun']}:{r['jenis_ternak']}:{r['desa']}",
            "schema_version": SCHEMA_VERSION,
            "jenis_ternak": r["jenis_ternak"],
            "lokasi": {"tingkat": "desa", "nama": r["desa"], "kecamatan": r["kecamatan"]},
            # BPS counts are year-end snapshots
            "tanggal": datetime(r["tahun"], 12, 31, tzinfo=UTC),
            "tahun": r["tahun"],
            "jumlah_ekor": r["jumlah_ekor"],
            "sumber": sumber(CSV_SUMBER[r["sumber"]], False, now),
        }
        if has_rtp:
            doc["rtp"] = r["rtp"]
        if has_umur:
            doc["struktur_umur"] = {u: {"jantan": r[f"{u}_jantan"], "betina": r[f"{u}_betina"]} for u in UMUR}
        docs.append(doc)
    return docs


def perikanan_kabupaten(csv: Path, now: datetime) -> list[Doc]:
    """Map the Dinas Perikanan production CSV (kabupaten totals, no area) to `panen` documents."""
    docs = []
    for r in pl.read_csv(csv).iter_rows(named=True):
        komoditas = r["jenis_ikan"].lower()
        docs.append(
            panen_doc(
                _id=f"dinas{r['tahun']}:{komoditas}",
                sektor="perikanan",
                komoditas=komoditas,
                lokasi={"tingkat": "kabupaten", "nama": "Lamongan"},
                periode={"tahun": r["tahun"]},
                sumber=sumber(CSV_SUMBER[r["sumber"]], False, now),
                atribut={"cakupan": r["cakupan"]},
                produksi_ton=r["produksi_ton"],
            )
        )
    return docs


def musim_tanam(units_parquet: Path, aoi: str, now: datetime) -> list[Doc]:
    """Map gold unit summaries (unit x year x season) to `musim_tanam` documents."""

    def window(r: Doc, prefix: str) -> Doc:
        return {k: as_datetime(r[f"{prefix}_{k}"]) if r[f"{prefix}_{k}"] else None for k in ("awal", "median", "akhir")}

    return [
        {
            "_id": f"sentinel:{aoi}:{r['unit']}:{r['tahun']}-{r['musim']}",
            "schema_version": SCHEMA_VERSION,
            "aoi": aoi,
            "unit": r["unit"],
            "tahun": r["tahun"],
            "musim": r["musim"],
            "sel": r["sel"],
            "luas_ha": float(r["luas_ha"]),
            "luas_padi_ha": float(r["luas_padi_ha"]),
            "genang": window(r, "genang"),
            "panen": window(r, "panen"),
            "puncak_ndvi": r["puncak_ndvi"],
            "sumber": sumber("sentinel", False, now),
        }
        for r in pl.read_parquet(units_parquet).iter_rows(named=True)
    ]


def sync(db: Database, collection: str, docs: list[Doc], owned: list[str], scope: Doc | None = None) -> Doc:
    """Replace-upsert `docs` by `_id`, then delete stale documents of the `owned` sources.

    Args:
        db: Target database.
        collection: Collection name.
        docs: Current documents from the owned sources.
        owned: `sumber.kode` values this load is the only writer of.
        scope: Extra filter limiting pruning, e.g. one AOI.

    Returns:
        Inserted, replaced and deleted counts.
    """
    coll = db[collection]
    ids = [d["_id"] for d in docs]
    first_seen = {
        d["_id"]: d["sumber"]["dicatat_pada"] for d in coll.find({"_id": {"$in": ids}}, {"sumber.dicatat_pada": 1})
    }
    for d in docs:
        if d["_id"] in first_seen:
            d["sumber"]["dicatat_pada"] = first_seen[d["_id"]]
    result = coll.bulk_write([ReplaceOne({"_id": d["_id"]}, d, upsert=True) for d in docs]) if docs else None
    stale = coll.delete_many({"sumber.kode": {"$in": owned}, "_id": {"$nin": ids}, **(scope or {})})
    return {
        "inserted": result.upserted_count if result else 0,
        "replaced": result.modified_count if result else 0,
        "deleted": stale.deleted_count,
    }


def main(aoi_spec: str = DEFAULT_AOI) -> None:
    """Create collections if needed, drop retired sources, then sync every source."""
    db = connect()
    ensure_collections(db)
    for collection in ("panen", "ternak"):
        retired = db[collection].delete_many({"sumber.kode": {"$in": RETIRED_SOURCES}}).deleted_count
        if retired:
            print(f"{collection}: deleted {retired} docs from retired sources {RETIRED_SOURCES}")

    now = datetime.now(UTC)
    owned = list(CSV_SUMBER.values())
    panen = (
        bps_panen(SRC / "bps-tikung-2013-pertanian.csv", now)
        + bps_panen(SRC / "bps-tikung-2020-pertanian.csv", now)
        + perikanan_kabupaten(SRC / "perikanan-lamongan-2021-produksi.csv", now)
    )
    ternak = bps_ternak(SRC / "bps-tikung-2013-peternakan-sapi.csv", now) + bps_ternak(
        SRC / "bps-tikung-2020-peternakan-sapi.csv", now
    )
    report = {"panen": sync(db, "panen", panen, owned), "ternak": sync(db, "ternak", ternak, owned)}

    aoi = resolve(aoi_spec).slug
    units = GOLD / f"{aoi}_units.parquet"
    if units.exists():
        report["musim_tanam"] = sync(db, "musim_tanam", musim_tanam(units, aoi, now), ["sentinel"], {"aoi": aoi})
    else:
        print(f"musim_tanam: skipped, {units} not found (run `just gold {aoi_spec}` first)")

    for collection, counts in report.items():
        total = db[collection].count_documents({})
        print(f"{collection}: {counts}, {total} in collection")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI)
