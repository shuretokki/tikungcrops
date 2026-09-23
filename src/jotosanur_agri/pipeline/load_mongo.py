"""Load harvest and livestock data into MongoDB (db `jotosanur`).

Sources:
    - BPS Tikung Dalam Angka 2014/2021 CSVs (desa level, data years 2013/2020).
    - Dinas Perikanan Lamongan Profil 2021 CSV (kabupaten level).

Every document has a deterministic `_id` and is written with a replace-upsert,
so reruns overwrite instead of duplicating. Spec: documents/local/skema-hibrida.md
section 5.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl
from pymongo import ReplaceOne
from pymongo.database import Database

from jotosanur_agri.mongo import SCHEMA_VERSION, connect, ensure_collections, panen_doc, sumber

SRC = Path("data/raw/sumber-data")

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


def upsert(db: Database, collection: str, docs: list[Doc]) -> tuple[int, int]:
    """Replace-upsert documents by `_id`.

    Returns:
        (inserted, replaced) counts.
    """
    result = db[collection].bulk_write([ReplaceOne({"_id": d["_id"]}, d, upsert=True) for d in docs])
    return result.upserted_count, result.modified_count


def main() -> None:
    """Create collections if needed, then upsert every source."""
    db = connect()
    ensure_collections(db)

    now = datetime.now(UTC)
    panen = (
        bps_panen(SRC / "bps-tikung-2013-pertanian.csv", now)
        + bps_panen(SRC / "bps-tikung-2020-pertanian.csv", now)
        + perikanan_kabupaten(SRC / "perikanan-lamongan-2021-produksi.csv", now)
    )
    ternak = bps_ternak(SRC / "bps-tikung-2013-peternakan-sapi.csv", now) + bps_ternak(
        SRC / "bps-tikung-2020-peternakan-sapi.csv", now
    )

    for collection, docs in (("panen", panen), ("ternak", ternak)):
        inserted, replaced = upsert(db, collection, docs)
        total = db[collection].count_documents({})
        print(f"{collection}: {len(docs)} docs, {inserted} inserted, {replaced} replaced, {total} in collection")


if __name__ == "__main__":
    main()
