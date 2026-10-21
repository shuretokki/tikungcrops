# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Streamlit dashboard for the Kampung Pandu Sakti management information system.

Run with `just app` (or `uv run streamlit run app.py`).

The rice, cattle and pond series shown are SYNTHETIC stand-ins until the mitra shares
real records. Real BPS figures come from MongoDB; mitra input is written through the
forms in the Data Panen (MongoDB) and Distribusi (SQLite) tabs, see
`jotosanur_agri.store`.
"""

from __future__ import annotations

import datetime as dt
import sqlite3

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError, WriteError

from jotosanur_agri import mongo, mongo_agg, store
from jotosanur_agri.ml.predict_panen_tsukamoto import predict_produktivitas
from jotosanur_agri.ml.train import CATEGORICAL_FEATURES, NUMERIC_FEATURES

SILVER_PATH = "data/silver/kampung_pandu_harvest.parquet"
MODEL_PATH = "models/baseline_rf_produktivitas.joblib"
TERNAK_PATH = "data/bronze/ternak_sapi.parquet"
KOLAM_PATH = "data/bronze/kolam_ikan.parquet"

st.set_page_config(page_title="Kampung Pandu Sakti", page_icon="🌾", layout="wide")


@st.cache_data
def load_silver() -> pd.DataFrame:
    """Synthetic rice silver table."""
    return pd.read_parquet(SILVER_PATH)


@st.cache_resource
def load_model():
    """Trained random-forest baseline, or None if not trained yet."""
    try:
        return joblib.load(MODEL_PATH)
    except FileNotFoundError:
        return None


@st.cache_data
def load_ternak() -> pd.DataFrame | None:
    """Synthetic cattle census, or None if not generated yet."""
    try:
        return pd.read_parquet(TERNAK_PATH)
    except FileNotFoundError:
        return None


@st.cache_data
def load_kolam() -> pd.DataFrame | None:
    """Synthetic pond cycles, or None if not generated yet."""
    try:
        return pd.read_parquet(KOLAM_PATH)
    except FileNotFoundError:
        return None


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


def render_banner():
    """Warn that the harvest data is synthetic."""
    st.warning(
        "**Data panen di bawah ini SINTETIS**, bukan data operasional Kampung Pandu Sakti "
        "sebenarnya - mitra desa (Kecamatan Tikung) belum merespons kontak. Parameter "
        "generatornya bersumber (BPS + 9 studi agronomi/risiko produksi padi Indonesia), "
        "tapi ini tetap bukan pengganti data lapangan. Detail: `data/raw/sumber-data/README.md` "
        "dan docstring `src/jotosanur_agri/pipeline/generate_synthetic.py`.",
        icon="⚠️",
    )


def render_overview(df: pd.DataFrame):
    """Summary metrics and per-season yield spread."""
    st.subheader("Ringkasan")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Musim tanam tercatat", df["musim_tanam_ke"].nunique())
    col2.metric("Total petak", df["plot_id"].nunique())
    col3.metric("Rata-rata produktivitas", f"{df['produktivitas_ton_per_ha'].mean():.2f} ton/ha")
    col4.metric("Total produksi", f"{df['produksi_ton'].sum():.1f} ton")

    fig = px.box(
        df,
        x="musim_tanam_ke",
        y="produktivitas_ton_per_ha",
        points="all",
        title="Sebaran produktivitas per musim tanam (per petak)",
        labels={"musim_tanam_ke": "Musim tanam ke-", "produktivitas_ton_per_ha": "Produktivitas (ton/ha)"},
    )
    st.plotly_chart(fig, width="stretch")


def render_data_panen(df: pd.DataFrame):
    """Synthetic harvest table with a season filter."""
    st.subheader("Data Panen")
    musim_options = ["Semua"] + sorted(df["musim_tanam_ke"].unique().tolist())
    musim = st.selectbox("Filter musim tanam", musim_options)
    view = df if musim == "Semua" else df[df["musim_tanam_ke"] == musim]
    st.dataframe(
        view[
            [
                "record_id",
                "musim_tanam_ke",
                "plot_id",
                "tanggal_tanam",
                "tanggal_panen",
                "luas_ha",
                "curah_hujan_mm",
                "pupuk_kg_per_ha",
                "produktivitas_ton_per_ha",
                "produksi_ton",
            ]
        ],
        width="stretch",
        hide_index=True,
    )


def render_prediksi(df: pd.DataFrame, model):
    """Random-forest prediction form."""
    st.subheader("Prediksi Produktivitas (Baseline RF)")
    if model is None:
        st.info("Model belum dilatih. Jalankan `uv run python -m jotosanur_agri.ml.train` dahulu.")
        return

    st.caption(
        "Baseline model - MAPE holdout ~16.8% pada data sintetis, R² rendah (variasi antar-musim "
        "sebagian besar tak terjelaskan fitur yang ada, konsisten dengan literatur risiko produksi "
        "padi). Bukan angka final proposal (metode utama: fuzzy Tsukamoto, belum diimplementasi)."
    )

    plot_options = sorted(df["plot_id"].unique().tolist())
    col1, col2 = st.columns(2)
    with col1:
        musim_tanam_ke = st.number_input("Musim tanam ke-", min_value=1, value=int(df["musim_tanam_ke"].max()) + 1)
        luas_ha = st.number_input("Luas petak (ha)", min_value=0.01, value=float(df["luas_ha"].mean()), format="%.3f")
        curah_hujan_mm = st.slider("Curah hujan (mm/bulan)", 3, 572, 139)
    with col2:
        pupuk_kg_per_ha = st.slider("Pupuk (kg/ha)", 150, 300, 225)
        siklus_hari = st.slider("Siklus tanam (hari)", 80, 85, 82)
        plot_id = st.selectbox("Petak (untuk konteks model, bukan lokasi nyata)", plot_options)

    if st.button("Prediksi"):
        X = pd.DataFrame(
            [
                {
                    "musim_tanam_ke": musim_tanam_ke,
                    "luas_ha": luas_ha,
                    "curah_hujan_mm": curah_hujan_mm,
                    "pupuk_kg_per_ha": pupuk_kg_per_ha,
                    "siklus_hari": siklus_hari,
                    "plot_id": plot_id,
                }
            ]
        )[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        pred = model.predict(X)[0]
        st.metric("Prediksi produktivitas", f"{pred:.2f} ton/ha")


def render_prediksi_tsukamoto():
    """Tsukamoto prediction form with its rule trace."""
    st.subheader("Prediksi Produktivitas (Fuzzy Tsukamoto)")
    st.caption(
        "Metode utama proposal - basis aturan dari pengetahuan pakar & rentang tersumber, BUKAN "
        "dilatih dari data. Satu-satunya modul prediksi yang spesifik Kampung Pandu Sakti/Jotosanur "
        "(baseline RF di atas dilatih pada data sintetis Jotosanur yang sirkular; model CIMMYT "
        "terpisah dilatih pada data real tapi Asia Selatan, bukan Jotosanur - lihat "
        "`documents/local/adr-integrasi-data-cimmyt.md`). Rentang dosis pupuk/bibit BELUM divalidasi ke "
        "praktik Kampung Pandu Sakti sendiri - lihat docstring `predict_panen_tsukamoto.py`."
    )

    col1, col2 = st.columns(2)
    with col1:
        dosis_pupuk = st.slider("Dosis pupuk NPK (kg/ha)", 100, 350, 225)
    with col2:
        dosis_bibit = st.slider("Dosis bibit (kg/ha)", 15, 40, 27)

    if st.button("Prediksi (Tsukamoto)"):
        hasil = predict_produktivitas(dosis_pupuk, dosis_bibit)
        st.metric("Prediksi produktivitas", f"{hasil['produktivitas_ton_ha']:.2f} ton/ha")
        with st.expander("Rincian aturan aktif (alpha-predikat & z)"):
            st.code(hasil["trace"])


def render_ternak(df_sapi: pd.DataFrame | None, df_kolam: pd.DataFrame | None):
    """Cattle and pond charts."""
    st.subheader("Peternakan (Sapi)")
    st.caption(
        "Sintetis, bersumber (`data/raw/sumber-data/README.md` §5, §7): baseline 60 ekor/33 RTP "
        "(BPS Tikung 2020). Tren pertumbuhan dari 2 titik data lokal nyata Jotosanur (78 ekor "
        "2013 -> 60 ekor 2020, ~-3,68%/tahun) - lihat docstring `generate_ternak_perikanan.py` "
        "untuk kenapa proksi provinsi Jawa Timur (arahnya naik) sebelumnya salah arah dan diganti."
    )
    if df_sapi is None:
        st.info("Belum ada data sapi - jalankan `uv run python -m jotosanur_agri.pipeline.generate_ternak_perikanan`.")
    else:
        col1, col2 = st.columns(2)
        latest = df_sapi.sort_values("periode_ke").iloc[-1]
        col1.metric("Populasi sapi (periode terakhir)", f"{int(latest['jumlah_ekor'])} ekor")
        col2.metric("Rumah tangga peternak (RTP)", int(latest["rtp"]))
        fig_sapi = px.line(
            df_sapi.sort_values("periode_ke"),
            x="periode_ke",
            y="jumlah_ekor",
            markers=True,
            title="Populasi sapi per periode sensus (semesteran)",
            labels={"periode_ke": "Periode ke-", "jumlah_ekor": "Jumlah (ekor)"},
        )
        st.plotly_chart(fig_sapi, width="stretch")
        with st.expander("Data mentah sapi"):
            st.dataframe(df_sapi, width="stretch", hide_index=True)

    st.divider()
    st.subheader("Perikanan (Kolam)")
    st.caption(
        "Sintetis, bersumber (`data/raw/sumber-data/README.md` §6): produktivitas dari rasio "
        "produksi lele kabupaten (3.394 ton / 51,35 ha) dibagi 4 siklus/tahun, dengan variasi dari "
        "studi risiko budidaya lele Kabupaten Kediri (CV 0,217). HANYA produktivitas ton/ha - tanpa "
        "luas kolam Kampung Pandu Sakti sendiri (tidak ada angka bersumber), tidak ada kolom luas/"
        "total produksi - lihat docstring `generate_ternak_perikanan.py`."
    )
    if df_kolam is None:
        st.info("Belum ada data kolam - jalankan `uv run python -m jotosanur_agri.pipeline.generate_ternak_perikanan`.")
    else:
        latest = df_kolam.sort_values("siklus_ke").iloc[-1]
        st.metric("Produktivitas (siklus terakhir)", f"{latest['produktivitas_ton_per_ha']:.3f} ton/ha")
        fig_kolam = px.line(
            df_kolam.sort_values("siklus_ke"),
            x="siklus_ke",
            y="produktivitas_ton_per_ha",
            markers=True,
            title="Produktivitas lele per siklus panen",
            labels={"siklus_ke": "Siklus ke-", "produktivitas_ton_per_ha": "Produktivitas (ton/ha)"},
        )
        st.plotly_chart(fig_kolam, width="stretch")
        with st.expander("Data mentah kolam"):
            st.dataframe(df_kolam, width="stretch", hide_index=True)


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
    render_banner()

    df = load_silver()
    model = load_model()
    init_sqlite()
    panen = get_panen_collection()

    tab_overview, tab_panen, tab_prediksi, tab_ternak, tab_distribusi = st.tabs(
        ["Ringkasan", "Data Panen", "Prediksi", "Ternak & Perikanan", "Distribusi"]
    )
    with tab_overview:
        render_overview(df)
        st.divider()
        render_data_riil(panen)
    with tab_panen:
        render_data_panen(df)
        st.divider()
        render_input_panen(panen)
    with tab_prediksi:
        render_prediksi(df, model)
        st.divider()
        render_prediksi_tsukamoto()
    with tab_ternak:
        render_ternak(load_ternak(), load_kolam())
    with tab_distribusi:
        render_distribusi(panen)


if __name__ == "__main__":
    main()
