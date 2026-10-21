"""Streamlit dashboard for the Kampung Pandu Sakti management information system.

Run with `just app` (or `uv run streamlit run app.py`).

Shows satellite planting seasons and cropping intensity per desa (MongoDB `planting_seasons`,
`cropping_intensity`) and the mitra input forms: harvests go to MongoDB, distribution records
to SQLite (see `jotosanur_agri.store`). Database names are English, everything on screen is Indonesian.
The earlier version with synthetic data and yield predictors is kept in archives/app.py.
"""

from __future__ import annotations

import datetime as dt
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError, WriteError

from jotosanur_agri import mongo, store

st.set_page_config(page_title="Kampung Pandu Sakti", page_icon="🌾", layout="wide")


@st.cache_resource
def init_sqlite() -> None:
    """Create and seed the SQLite tables once per server process."""
    store.init_sqlite()


@st.cache_resource
def mongo_db() -> Database:
    """Project database, created once per server process."""
    # Streamlit reruns the script on every interaction, so keep one client and pool
    return mongo.connect(timeout_ms=3000)


def get_db() -> Database | None:
    """The project database, or None when the server is down so the rest of the dashboard still works."""
    try:
        db = mongo_db()
        db.client.admin.command("ping")
        return db
    except (KeyError, PyMongoError):
        return None


MONGO_DOWN_MSG = "MongoDB tidak aktif - jalankan `just up` (atau `docker compose up -d`), lalu muat ulang halaman."


DEFAULT_AOI = "idn-jawatimur-lamongan-tikung"
MUSIM_LABEL = {"MT1": "MT1 (musim hujan)", "MT2": "MT2 (kemarau I)", "MT3": "MT3 (kemarau II)"}
# stored codes -> Indonesian labels shown in the forms
LABEL = {
    "crops": "tanaman",
    "fisheries": "perikanan",
    "plot": "plot",
    "village": "desa",
    "seed": "bibit",
    "harvest": "hasil panen",
    "kg": "kg",
    "ton": "ton",
    "head": "ekor",
    "district": "kecamatan",
    "mbg_kitchen": "dapur MBG",
}


def render_musim_tanam(musim: Collection | None):
    """Satellite planting seasons per desa: planted and rice area, flooding and harvest windows."""
    st.subheader("Musim Tanam per Desa (Sentinel-1/2)")
    st.caption(
        "Dideteksi dari citra satelit per sel 100 m lahan sawah: tanggal penggenangan dari radar Sentinel-1, "
        "panen dari penurunan NDVI Sentinel-2. Luas padi = musim dengan tanda penggenangan; sisanya "
        "kemungkinan palawija. Jendela tanggal = persentil 10-90% antar sel."
    )
    if musim is None:
        st.info(MONGO_DOWN_MSG)
        return
    aois = sorted(musim.distinct("aoi"))
    if not aois:
        st.info("Belum ada data musim tanam - jalankan `just gold` lalu `just mongo`.")
        return
    aoi = st.selectbox("Wilayah", aois, index=aois.index(DEFAULT_AOI) if DEFAULT_AOI in aois else 0)
    docs = list(musim.find({"aoi": aoi}, {"_id": 0, "source": 0, "schema_version": 0}))
    if not docs:
        st.info("Belum ada data musim tanam - jalankan `just gold` lalu `just mongo`.")
        return
    df = pd.json_normalize(docs)
    tahun = st.selectbox("Tahun", sorted(df["year"].unique(), reverse=True))
    view = df[df["year"] == tahun].sort_values(["unit", "season"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Desa", view["unit"].nunique())
    col2.metric("Luas tanam (ha, semua musim)", f"{view['area_ha'].sum():,.0f}")
    col3.metric("Luas padi (ha, semua musim)", f"{view['rice_area_ha'].sum():,.0f}")

    fig = px.bar(
        view,
        x="unit",
        y="rice_area_ha",
        color="season",
        barmode="group",
        labels={"unit": "Desa", "rice_area_ha": "Luas padi (ha)", "season": "Musim"},
        title=f"Luas padi per desa dan musim, {tahun}",
    )
    st.plotly_chart(fig, width="stretch")

    windows = view.dropna(subset=["flooding.median", "harvest.median"])
    if not windows.empty:
        timeline = px.timeline(
            windows.assign(season=windows["season"].map(MUSIM_LABEL)),
            x_start="flooding.median",
            x_end="harvest.median",
            y="unit",
            color="season",
            labels={"unit": "Desa", "season": "Musim"},
            title="Median penggenangan (tanam) sampai median panen",
        )
        st.plotly_chart(timeline, width="stretch")

    with st.expander("Tabel"):
        st.dataframe(view, width="stretch", hide_index=True)


def render_outlook(outlook: Collection | None):
    """Expected harvested area per desa and week for seasons still running."""
    st.subheader("Perkiraan Panen per Minggu (Satelit)")
    st.caption(
        "Untuk lahan yang sedang ditanami: tanggal panen diprakirakan dari tanggal genangan (sekitar 2-3 bulan "
        "sebelumnya) atau dari puncak kehijauan (sekitar 1 bulan sebelumnya). Luas tiap lahan disebar merata "
        "pada rentang prakiraan 80%, jadi grafik sudah memuat ketidakpastian. Uji ulang pada tanggal lampau: "
        "prakiraan yang terbit pada musim kemarau meleset sekitar 1-2 minggu per desa, tetapi pada musim hujan "
        "3-5 minggu karena awan menutupi awal musim - anggap perkiraan musim hujan sebagai kasar. Tanggal "
        "adalah deteksi satelit, belum dicek dengan catatan panen petani."
    )
    if outlook is None:
        st.info(MONGO_DOWN_MSG)
        return
    aois = sorted(outlook.distinct("aoi"))
    if not aois:
        st.info("Belum ada perkiraan panen - jalankan `just outlook` lalu `just mongo`.")
        return
    aoi = st.selectbox("Wilayah", aois, index=aois.index(DEFAULT_AOI) if DEFAULT_AOI in aois else 0, key="outlook_aoi")
    df = pd.DataFrame(list(outlook.find({"aoi": aoi}, {"_id": 0, "source": 0, "schema_version": 0})))
    if df.empty:
        st.info("Belum ada perkiraan panen untuk wilayah ini.")
        return
    issued = df["issued_on"].max()
    st.metric(
        "Perkiraan luas panen (ha)", f"{df['expected_ha'].sum():,.0f}", help=f"Data satelit s.d. {issued:%d %b %Y}"
    )
    fig = px.bar(
        df.sort_values("week"),
        x="week",
        y="expected_ha",
        color="unit",
        labels={"week": "Minggu", "expected_ha": "Perkiraan luas panen (ha)", "unit": "Desa"},
        title=f"Perkiraan luas panen per minggu, dikeluarkan {issued:%d %b %Y}",
    )
    fig.add_vline(x=issued, line_dash="dash")
    st.plotly_chart(fig, width="stretch")
    with st.expander("Tabel"):
        st.dataframe(df.sort_values(["week", "unit"]), width="stretch", hide_index=True)


def render_intensitas(intensity: Collection | None):
    """Cropping intensity per desa and year, and the paddy share planted three or more times."""
    st.subheader("Intensitas Tanam per Desa (Satelit)")
    st.caption(
        "Intensitas tanam = jumlah musim tanam per hektare sawah dalam setahun (dihitung dari puncak kehijauan "
        "NDVI per sel 100 m, dibobot luas sawah LBS). Tahun basah bisa terbaca terlalu tinggi karena hujan "
        "membuat puncak kehijauan tambahan, jadi bandingkan antar desa pada tahun yang sama, bukan satu desa "
        "antar tahun. Hanya tahun yang tercakup penuh oleh data satelit yang ditampilkan."
    )
    if intensity is None:
        st.info(MONGO_DOWN_MSG)
        return
    aois = sorted(intensity.distinct("aoi"))
    if not aois:
        st.info("Belum ada data intensitas tanam - jalankan `just gold` lalu `just mongo`.")
        return
    aoi = st.selectbox(
        "Wilayah", aois, index=aois.index(DEFAULT_AOI) if DEFAULT_AOI in aois else 0, key="intensity_aoi"
    )
    df = pd.DataFrame(
        list(intensity.find({"aoi": aoi, "complete": True}, {"_id": 0, "source": 0, "schema_version": 0}))
    )
    if df.empty:
        st.info("Belum ada tahun yang tercakup penuh untuk wilayah ini.")
        return
    desa = sorted(df["unit"].unique())
    fokus = st.selectbox("Desa yang dibandingkan", desa, index=desa.index("Jotosanur") if "Jotosanur" in desa else 0)
    others = df[df["unit"] != fokus].groupby("year", as_index=False)[["ip_all", "share_3plus"]].median()
    compare = pd.concat(
        [df[df["unit"] == fokus].assign(grup=fokus), others.assign(grup="Median desa lain")], ignore_index=True
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(
        px.line(
            compare,
            x="year",
            y="ip_all",
            color="grup",
            markers=True,
            labels={"year": "Tahun", "ip_all": "Musim per ha sawah", "grup": ""},
            title="Intensitas tanam",
        ),
        width="stretch",
    )
    col2.plotly_chart(
        px.line(
            compare.assign(share_3plus=compare["share_3plus"] * 100),
            x="year",
            y="share_3plus",
            color="grup",
            markers=True,
            labels={"year": "Tahun", "share_3plus": "Sawah ditanami 3 kali atau lebih (%)", "grup": ""},
            title="Sawah dengan 3 musim tanam atau lebih",
        ),
        width="stretch",
    )
    with st.expander("Tabel"):
        st.dataframe(df.sort_values(["year", "unit"]), width="stretch", hide_index=True)


def render_input_panen(harvests: Collection | None):
    """Harvest entry form and the list of mitra harvests."""
    st.subheader("Catat Panen (Input Mitra)")
    st.caption(
        "Data riil dari mitra, disimpan ke MongoDB koleksi `harvests` dengan `source.code = partner_input` "
        "dan `is_synthetic = false`. Satu catatan per komoditas, lokasi dan tanggal panen."
    )
    if harvests is None:
        st.info(MONGO_DOWN_MSG)
        return

    with st.form("form_panen", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sektor = st.selectbox("Sektor", ["crops", "fisheries"], format_func=LABEL.__getitem__)
            komoditas = st.text_input("Komoditas", placeholder="padi, jagung, lele, nila, ...")
            tingkat = st.selectbox("Tingkat lokasi", ["plot", "village"], format_func=LABEL.__getitem__)
            lokasi_nama = st.text_input("Nama lokasi", placeholder="mis. P01, Kolam A")
        with col2:
            tanggal_panen = st.date_input("Tanggal panen", value=dt.date.today(), max_value=dt.date.today())
            tanggal_mulai = st.date_input("Tanggal tanam/tebar (opsional)", value=None, max_value=dt.date.today())
            luas_ha = st.number_input("Luas (ha, opsional)", min_value=0.0, value=None, format="%.3f")
            produksi_ton = st.number_input("Produksi (ton, opsional)", min_value=0.0, value=None, format="%.3f")
        submitted = st.form_submit_button("Simpan panen")

    if submitted:
        try:
            _id = store.add_partner_harvest(
                harvests,
                sektor,
                komoditas,
                tingkat,
                lokasi_nama,
                tanggal_panen,
                start_date=tanggal_mulai,
                area_ha=luas_ha,
                production_ton=produksi_ton,
            )
            st.success(f"Tersimpan: `{_id}`")
        except ValueError as e:
            st.error(str(e))
        except DuplicateKeyError:
            st.error("Panen dengan komoditas, lokasi dan tanggal yang sama sudah tercatat.")
        except WriteError as e:
            st.error(f"Ditolak validator MongoDB: {(e.details or {}).get('errmsg', e)}")

    rows = store.list_partner_harvests(harvests)
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.info("Belum ada panen yang dicatat mitra.")


def render_distribusi(harvests: Collection | None):
    """Distribution records, entry form and destination form."""
    st.subheader("Distribusi Bibit & Hasil Panen")
    tujuan = store.list_destinations()
    rows = store.list_distributions()

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
        col2.metric("Tujuan berbeda", df["destination"].nunique())
        st.dataframe(df, width="stretch", hide_index=True)

    st.divider()
    st.markdown("**Catat distribusi**")
    panen_ids = [r["_id"] for r in store.list_partner_harvests(harvests)] if harvests is not None else []
    tujuan_label = {t["id"]: f"{t['name']} ({LABEL[t['type']]}, Kec. {t['district']})" for t in tujuan}

    with st.form("form_distribusi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal", value=dt.date.today(), max_value=dt.date.today())
            jenis_barang = st.selectbox("Jenis barang", store.ITEM_TYPES, format_func=LABEL.__getitem__)
            komoditas = st.text_input("Komoditas", placeholder="beras, bibit padi, ...")
        with col2:
            jumlah = st.number_input("Jumlah", min_value=0.0, value=None, format="%.2f")
            satuan = st.selectbox("Satuan", store.UNITS, format_func=LABEL.__getitem__)
            tujuan_id = st.selectbox("Tujuan", list(tujuan_label), format_func=lambda i: tujuan_label[i])
        panen_ref = st.selectbox(
            "Asal panen (opsional, dari catatan panen mitra)",
            [None, *panen_ids],
            format_func=lambda x: "-" if x is None else x,
            help=None if harvests is not None else MONGO_DOWN_MSG,
        )
        submitted = st.form_submit_button("Simpan distribusi")

    if submitted:
        if not jumlah:
            st.error("Jumlah harus lebih dari 0.")
        elif tujuan_id is None:
            st.error("Pilih tujuan terlebih dahulu.")
        else:
            try:
                store.add_distribution(
                    tanggal,
                    jenis_barang,
                    komoditas,
                    jumlah,
                    satuan,
                    tujuan_id,
                    harvest_ref=panen_ref,
                    harvests=harvests,
                )
                st.toast("Distribusi tersimpan.", icon="✅")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except sqlite3.IntegrityError as e:
                st.error(f"Ditolak SQLite: {e}")

    with st.expander("Tambah tujuan (dapur MBG / kecamatan)"), st.form("form_tujuan", clear_on_submit=True):
        jenis = st.selectbox("Jenis", store.DESTINATION_TYPES, index=1, format_func=LABEL.__getitem__)
        nama = st.text_input("Nama")
        kecamatan = st.text_input("Kecamatan")
        if st.form_submit_button("Tambah tujuan"):
            try:
                store.add_destination(jenis, nama, kecamatan)
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except sqlite3.IntegrityError:
                st.error("Tujuan dengan jenis dan nama itu sudah ada.")


def main():
    """Lay out the tabs."""
    st.title("🌾 Sistem Informasi Manajemen Kampung Pandu Sakti")
    init_sqlite()
    db = get_db()
    harvests = db["harvests"] if db is not None else None

    tab_musim, tab_intensitas, tab_outlook, tab_panen, tab_distribusi = st.tabs(
        ["Musim Tanam (Satelit)", "Intensitas Tanam", "Perkiraan Panen", "Catat Panen", "Distribusi"]
    )
    with tab_musim:
        render_musim_tanam(db["planting_seasons"] if db is not None else None)
    with tab_intensitas:
        render_intensitas(db["cropping_intensity"] if db is not None else None)
    with tab_outlook:
        render_outlook(db["harvest_outlook"] if db is not None else None)
    with tab_panen:
        render_input_panen(harvests)
    with tab_distribusi:
        render_distribusi(harvests)


if __name__ == "__main__":
    main()
