"""Streamlit dashboard for the Kampung Pandu Sakti management information system.

Run with `just app` (or `uv run streamlit run app.py`).

Shows real BPS figures aggregated in MongoDB and the mitra input forms: harvests go to
MongoDB, distribution records to SQLite (see `jotosanur_agri.store`). The earlier version
with synthetic data and yield predictors is kept in archives/app.py.
"""

from __future__ import annotations

import datetime as dt
import sqlite3

import pandas as pd
import streamlit as st
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError, WriteError

from jotosanur_agri import mongo, mongo_agg, store

st.set_page_config(page_title="Kampung Pandu Sakti", page_icon="🌾", layout="wide")


@st.cache_resource
def init_sqlite() -> None:
    """Create and seed the SQLite tables once per server process."""
    store.init_sqlite()


@st.cache_resource
def mongo_db() -> Database:
    """Project database, created once per server process."""
    # Streamlit reruns the script on every interaction; keep one client and pool.
    return mongo.connect(timeout_ms=3000)


def get_panen_collection() -> Collection | None:
    """Mongo `panen`, or None when the server is down so the rest of the dashboard still works."""
    try:
        db = mongo_db()
        db.client.admin.command("ping")
        return db["panen"]
    except (KeyError, PyMongoError):
        return None


MONGO_DOWN_MSG = "MongoDB tidak aktif - jalankan `just up` (atau `docker compose up -d`), lalu muat ulang halaman."


def render_data_riil(panen: Collection | None):
    """Real BPS production per commodity and year, aggregated in MongoDB."""
    st.subheader("Data Riil BPS (Agregasi MongoDB)")
    st.caption(
        "Produksi 13 desa Kecamatan Tikung dari BPS Tikung Dalam Angka 2014 dan 2021, dijumlahkan "
        "di MongoDB (`mongo_agg.produksi_per_tahun_pipeline`). Produktivitas = total produksi / total luas."
    )
    if panen is None:
        st.info(MONGO_DOWN_MSG)
        return
    rows = list(panen.aggregate(mongo_agg.produksi_per_tahun_pipeline(["padi", "jagung_hibrida"])))
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_input_panen(panen: Collection | None):
    """Harvest entry form and the list of mitra harvests."""
    st.subheader("Catat Panen (Input Mitra)")
    st.caption(
        "Data riil dari mitra, disimpan ke MongoDB koleksi `panen` dengan `sumber.kode = input_mitra` "
        "dan `is_synthetic = false`. Satu catatan per komoditas, lokasi dan tanggal panen."
    )
    if panen is None:
        st.info(MONGO_DOWN_MSG)
        return

    with st.form("form_panen", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sektor = st.selectbox("Sektor", ["tanaman", "perikanan"])
            komoditas = st.text_input("Komoditas", placeholder="padi, jagung, lele, nila, ...")
            tingkat = st.selectbox("Tingkat lokasi", ["plot", "desa"])
            lokasi_nama = st.text_input("Nama lokasi", placeholder="mis. P01, Kolam A")
        with col2:
            tanggal_panen = st.date_input("Tanggal panen", value=dt.date.today(), max_value=dt.date.today())
            tanggal_mulai = st.date_input("Tanggal tanam/tebar (opsional)", value=None, max_value=dt.date.today())
            luas_ha = st.number_input("Luas (ha, opsional)", min_value=0.0, value=None, format="%.3f")
            produksi_ton = st.number_input("Produksi (ton, opsional)", min_value=0.0, value=None, format="%.3f")
        submitted = st.form_submit_button("Simpan panen")

    if submitted:
        try:
            _id = store.add_panen_mitra(
                panen,
                sektor,
                komoditas,
                tingkat,
                lokasi_nama,
                tanggal_panen,
                tanggal_mulai=tanggal_mulai,
                luas_ha=luas_ha,
                produksi_ton=produksi_ton,
            )
            st.success(f"Tersimpan: `{_id}`")
        except ValueError as e:
            st.error(str(e))
        except DuplicateKeyError:
            st.error("Panen dengan komoditas, lokasi dan tanggal yang sama sudah tercatat.")
        except WriteError as e:
            st.error(f"Ditolak validator MongoDB: {(e.details or {}).get('errmsg', e)}")

    rows = store.list_panen_mitra(panen)
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.info("Belum ada panen yang dicatat mitra.")


def render_distribusi(panen: Collection | None):
    """Distribution records, entry form and destination form."""
    st.subheader("Distribusi Bibit & Hasil Panen")
    tujuan = store.list_tujuan()
    rows = store.list_distribusi()

    if not rows:
        st.info(
            "Belum ada distribusi yang dicatat. Yang diketahui dari berita hanya angka agregat, "
            "tanpa rincian per dapur/kecamatan/tanggal, sehingga tidak dipecah menjadi baris data:\n\n"
            "- Panen ke-2: 10 ton beras ke 7 dapur MBG di 4 kecamatan (Lamongan, Babat, Sugio, "
            "Kembangbahu) - [iNews Lamongan, 13 Jul 2025](https://lamongan.inews.id/read/618426)\n"
            "- Bibit gratis: 7 kuintal (panen 1) dan 1.200 kg (panen 2) ke 27 kecamatan - "
            "[Kabar Baik, 18 Agu 2025](https://kabarbaik.co/petani-rasakan-manfaat-kampung-pandu-lamongan-solusi-panen-lebih-cepat/)"
        )
    else:
        df = pd.DataFrame(rows)
        col1, col2 = st.columns(2)
        col1.metric("Catatan distribusi", len(df))
        col2.metric("Tujuan berbeda", df["tujuan"].nunique())
        st.dataframe(df, width="stretch", hide_index=True)

    st.divider()
    st.markdown("**Catat distribusi**")
    panen_ids = [r["_id"] for r in store.list_panen_mitra(panen)] if panen is not None else []
    tujuan_label = {t["id"]: f"{t['nama']} ({t['jenis']}, Kec. {t['kecamatan']})" for t in tujuan}

    with st.form("form_distribusi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal", value=dt.date.today(), max_value=dt.date.today())
            jenis_barang = st.selectbox("Jenis barang", store.JENIS_BARANG)
            komoditas = st.text_input("Komoditas", placeholder="beras, bibit padi, ...")
        with col2:
            jumlah = st.number_input("Jumlah", min_value=0.0, value=None, format="%.2f")
            satuan = st.selectbox("Satuan", store.SATUAN)
            tujuan_id = st.selectbox("Tujuan", list(tujuan_label), format_func=lambda i: tujuan_label[i])
        panen_ref = st.selectbox(
            "Asal panen (opsional, dari catatan panen mitra)",
            [None, *panen_ids],
            format_func=lambda x: "-" if x is None else x,
            help=None if panen is not None else MONGO_DOWN_MSG,
        )
        submitted = st.form_submit_button("Simpan distribusi")

    if submitted:
        if not jumlah:
            st.error("Jumlah harus lebih dari 0.")
        elif tujuan_id is None:
            st.error("Pilih tujuan terlebih dahulu.")
        else:
            try:
                store.add_distribusi(
                    tanggal,
                    jenis_barang,
                    komoditas,
                    jumlah,
                    satuan,
                    tujuan_id,
                    panen_ref=panen_ref,
                    panen=panen,
                )
                st.toast("Distribusi tersimpan.", icon="✅")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except sqlite3.IntegrityError as e:
                st.error(f"Ditolak SQLite: {e}")

    with st.expander("Tambah tujuan (dapur MBG / kecamatan)"), st.form("form_tujuan", clear_on_submit=True):
        jenis = st.selectbox("Jenis", store.JENIS_TUJUAN, index=1)
        nama = st.text_input("Nama")
        kecamatan = st.text_input("Kecamatan")
        if st.form_submit_button("Tambah tujuan"):
            try:
                store.add_tujuan(jenis, nama, kecamatan)
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except sqlite3.IntegrityError:
                st.error("Tujuan dengan jenis dan nama itu sudah ada.")


def main():
    """Lay out the tabs."""
    st.title("🌾 Sistem Informasi Manajemen Kampung Pandu Sakti")
    init_sqlite()
    panen = get_panen_collection()

    tab_riil, tab_panen, tab_distribusi = st.tabs(["Data Riil BPS", "Catat Panen", "Distribusi"])
    with tab_riil:
        render_data_riil(panen)
    with tab_panen:
        render_input_panen(panen)
    with tab_distribusi:
        render_distribusi(panen)


if __name__ == "__main__":
    main()
