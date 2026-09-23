# Sumber Data — Kampung Pandu Sakti / Desa Jotosanur

Dikumpulkan 2026-09-18. Semua data di bawah adalah **fakta bersumber** (bukan
sintetis) — dipakai untuk menetapkan rentang/parameter realistis pada
pembangkit data sintetis di `src/jotosanur_agri/`. Jangan campur dengan angka
sintetis tanpa penanda jelas.

## 1. BPS — Kecamatan Tikung Dalam Angka 2021 (data tahun 2020)

- **File:** `bps-kecamatan-tikung-dalam-angka-2021.pdf` (199 hlm, diunduh dari
  `web-api.bps.go.id/download.php`, publikasi BPS Kabupaten Lamongan,
  No. Publikasi 35240, ISSN 2798-7892)
- **Diekstrak ke:** `bps-tikung-2020-pertanian.csv` (Tabel 5.1–5.5, hlm. 119–123)
- **Cakupan:** 13 desa Kec. Tikung termasuk **Jotosanur**, tahun data 2020
- **Catatan penting:** data ini **mendahului** berdirinya Kampung Pandu Sakti
  (~2025) dan varietas padi PMJ 01/02. Perlakukan sebagai **baseline
  pra-program**, bukan hasil program itu sendiri — jangan dicampur dengan
  angka PMJ 01 di bawah.

## 2. Berita — Kampung Pandu Sakti (program berjalan, 2025–2026)

Bukan tabel terstruktur — kutipan angka dari artikel berita, dicatat manual:

| Fakta | Nilai | Sumber |
|---|---|---|
| Luas lahan total | 10,5 ha | infolamongan.com, 22 Okt 2025 |
| Porsi lahan pertanian | 60% (~6,3 ha) | inews.id, 13 Jul 2025 |
| Varietas padi | PMJ 01 / PMJ 02 | tribunnews.com, 23 Okt 2025 |
| Siklus tanam PMJ 01 | 80–85 hari | kabarbaik.co, 18 Agu 2025 |
| Panen/tahun | 3× | infolamongan.com |
| Produksi tercatat (panen ke-2) | 10 ton beras → 7 dapur MBG | inews.id |
| Bibit PMJ 01 dibagikan | 700 kg (panen 1), 1.200 kg (panen 2), ke 27 kecamatan | kabarbaik.co |
| Sektor lain | Ternak (ayam petelur/potong, bebek, kambing, sapi, entok), Perikanan (lele, nila) | infolamongan.com |

**Belum ada angka ton/ha resmi untuk PMJ 01/02** — ini justru target yang mau
diprediksi modul ML, bukan data yang sudah tersedia.

## 3. Portal Data Lamongan (CKAN, `data.lamongankab.go.id`)

- Organisasi `kecamatan-tikung`: **tidak ada dataset pertanian** — hanya data
  administratif (Dana Desa, PBB, jumlah dusun, luas wilayah per desa).
  Dicek 2026-09-18, jangan diulang tanpa alasan baru.

## 4. Satu Data Kabupaten Lamongan — TIDAK DIPAKAI

Halaman `satudata.lamongankab.go.id/admin/data` berisi tabel Luas Panen per
kecamatan tapi berbasis form JS — nilai numerik tidak bisa dipasangkan ke
label kecamatan secara statis (hasil fetch memisahkan keduanya). Diganti
dengan BPS Dalam Angka (§1) yang tabelnya bersih dan sudah diverifikasi
per-baris.

## 5. BPS — Peternakan Sapi Potong, Kecamatan Tikung Dalam Angka 2021 (data 2020)

- **File:** sama dengan §1 (`bps-kecamatan-tikung-dalam-angka-2021.pdf`), Tabel 5.10, hlm. 128-129
- **Diekstrak ke:** `bps-tikung-2020-peternakan-sapi.csv`
- **Cakupan:** 13 desa Kec. Tikung, sapi potong saja (RTP, anak/muda/dewasa per jenis kelamin)
- **Jotosanur:** 33 RTP, 60 ekor sapi total (2020)
- **Catatan:** hanya sapi potong yang punya tabel desa-level di publikasi ini. Ayam,
  bebek, kambing, entok (juga dipelihara Kampung Pandu Sakti) TIDAK ada di
  level desa - hanya angka kabupaten (lihat sumber terpisah, belum diunduh:
  appejawa.navperencanaan.com, populasi per jenis ternak Kab. Lamongan).

## 6. Dinas Perikanan Kabupaten Lamongan — Profil Perikanan 2021

- **File:** `dinas-perikanan-lamongan-profil-2021.pdf` (28 hlm, resmi
  lamongankab.go.id/beranda/documents/perikanan/), diparse via `llamaparse`
  ke `dinas-perikanan-lamongan-profil-2021-parsed.md`
- **Diekstrak ke:**
  - `perikanan-lamongan-2021-produksi.csv` — produksi per jenis ikan,
    **kabupaten-level saja** (tidak ada breakdown kecamatan untuk produksi)
  - `perikanan-tikung-2021-desa.csv` — luas lahan kolam & daftar desa
    potensi budidaya, kecamatan Tikung
- **Temuan spesifik Tikung/Jotosanur:**
  - Tabel "Data Luasan Kawasan Lahan Kolam": Tikung = **8 desa potensi,
    27.588 m² (2,76 ha)** total (tidak dipecah per desa)
  - Tabel "Data Kawasan Budidaya Ikan" (daftar nama desa per kecamatan):
    Tikung mencantumkan **10 desa** termasuk **Jotosanur** - Pengumbulanadi,
    Balongwangi, Kelorarum, Soko, Jotosanur, Dukuhagung, Bakalanpule,
    Tambakrigadung, Guminingrejo, Jatirejo
- **KONTRADIKSI SUMBER, tidak direkonsiliasi:** tabel luasan bilang 8 desa,
  tabel daftar nama bilang 10 desa, dalam dokumen resmi yang sama. Kedua
  angka dipakai apa adanya di CSV (`jumlah_desa_potensi_kecamatan=8` dari
  tabel luasan, daftar 10 nama dari tabel kawasan) - TIDAK dipilih salah
  satu sebagai "yang benar". Sebutkan ketidakcocokan ini bila dikutip.

## 7. BPS — Kecamatan Tikung Dalam Angka 2014 (data tahun 2013)

- **File:** `bps-kecamatan-tikung-dalam-angka-2014.pdf` (102 hlm, publikasi BPS
  Kabupaten Lamongan, Katalog 1102001.3524140)
- **Diekstrak ke:** `bps-tikung-2013-pertanian.csv` (Tabel 5.3, hlm. 56),
  `bps-tikung-2013-peternakan-sapi.csv` (Tabel 5.13, hlm. 66)
- **Cakupan:** 13 desa Kec. Tikung termasuk Jotosanur, tahun data 2013
- **Kenapa dicari:** untuk keluar dari satu-tahun-saja (2020) - lihat
  diskusi 2026-09-22 soal training data butuh lebih dari satu titik waktu.
  2016/2022/2023/2024 juga TERKONFIRMASI ADA (dikutip di beberapa skripsi/
  jurnal) tapi tidak ditemukan link unduhan langsungnya setelah 7 kali
  percobaan pencarian - bukan berarti tidak ada, hanya belum ter-crawl di
  indeks yang bisa diakses. 2014 dipilih karena satu-satunya yang berhasil
  ditemukan selain 2021.
- **Temuan penting - Jotosanur, 2013 vs 2020:**

  | | 2013 | 2020 |
  |---|---|---|
  | Padi produktivitas | 6,82 ton/ha | 7,25 ton/ha |
  | Sapi (ekor) | 78 | 60 |

  Padi naik ~0,88%/tahun (arah masuk akal, konsisten perbaikan varietas/
  praktik umum). **Sapi justru TURUN ~3,68%/tahun** - kebalikan dari tren
  Jawa Timur (+1,47% s.d. +2,9%/tahun) yang sempat dipakai sebagai proksi
  di `generate_ternak_perikanan.py`. Proksi provinsi itu sudah diganti
  dengan tren lokal ini begitu datanya ada - lihat docstring modul
  tersebut untuk detail.
- **Dipakai juga untuk:** copula padi di `realistic_baseline.py` sekarang
  dilatih dari 26 baris (13 desa x 2 tahun: 2013+2020), bukan cuma 13
  (1 tahun) - copula ini sekarang menangkap variasi antar-TAHUN yang nyata,
  bukan cuma proksi antar-desa untuk komponen itu.

## 8. CIMMYT/CSISA — Farmer Field Survey Dataset (South Asia, real per-field data)

- **Sumber:** Coggins, S. et al. (2024), "Farmer field survey dataset
  underpinning 'Data-driven strategies to improve nitrogen use efficiency of
  rice farming in South Asia'", CIMMYT Research Data & Software Repository
  Network, V3. `hdl.handle.net/11529/10549105`. Terkait publikasi peer-review:
  Coggins et al., *Nature Sustainability* 8, 22–33 (2025),
  `doi.org/10.1038/s41893-024-01496-3`
- **File:** diunduh dari `data.cimmyt.org` (Dataverse), disimpan di
  `data/external/cimmyt/` (di luar git - lihat `.gitignore` `/data/`):
  `NUE_survey_dataset_v2.csv` (versi terkoreksi, dipakai), `Variable_Details_v2.xlsx`
  (kamus data), `MANIFEST.TXT`
- **Lisensi: CC0 1.0 (public domain)** - dikonfirmasi via Dataverse API
  (`license.name: "CC0 1.0"`, `termsOfUse: null`, `termsOfAccess: null`,
  `fileAccessRequest: false`). Tidak ada pembatasan penggunaan, atribusi
  tidak wajib secara hukum (tapi tetap dikutip sebagai praktik akademik baik).
- **Cakupan:** 45.643 field petani REAL yang menanam padi, 2016-2021, di 6
  wilayah Asia Selatan: Bangladesh (20.329), Bihar/E. Uttar Pradesh (9.693),
  Nepal/Terai (6.097), Punjab-Haryana (5.833), Odisha (1.947), Andhra
  Pradesh (1.744). **BUKAN Indonesia** - dipakai sebagai benchmark ML
  real-data, bukan prediksi spesifik Jotosanur (lihat keputusan arsitektur
  2026-09-22: 3 komponen terpisah - ML benchmark real/CIMMYT, sistem fuzzy
  Tsukamoto berbasis-pengetahuan untuk Jotosanur, generator sintetis untuk
  demo dashboard).
- **136 kolom**, termasuk `yield_kg_ha` (target), data pupuk N/P/K per jenis
  & waktu aplikasi, 7 properti tanah (SoilGrids), irigasi, tingkat gangguan
  gulma/hama/penyakit/kekeringan/banjir, varietas, tanggal tanam & musim
  hujan, dan data sosioekonomi petani (pendidikan, kategori sosial, jumlah
  anggota rumah tangga, luas lahan total).
- **Kualitas data, diverifikasi bukan diasumsikan:** 45.643 baris mentah,
  1.017 (2,23%) dibuang karena `yield_kg_ha` implausible (NaN/inf/≤0/>15.000
  kg/ha) - **cocok persis dengan peringatan resmi dataset ini**
  ("original survey datasets contain inaccuracies... excluding obvious
  inaccuracies is recommended"). 44.607 baris bersih tersisa. Yield bersih:
  rata-rata 5.121 kg/ha, median 5.000 kg/ha - masuk akal untuk padi sawah
  smallholder Asia Selatan, sedikit lebih rendah & lebih bervariasi dari
  Jotosanur (~7 ton/ha) - wajar, ini 6 wilayah beragam bukan satu kecamatan
  ber-irigasi baik.

## 9. ISRIC SoilGrids 2.0 — properti tanah titik Jotosanur

- **Sumber:** ISRIC SoilGrids 2.0, REST API
  `https://rest.isric.org/soilgrids/v2.0/properties/query`. Sitasi: Poggio,
  L. et al. (2021). SoilGrids 2.0: producing soil information for the globe
  with quantified spatial uncertainty. *SOIL*, 7, 217-240.
  doi:10.5194/soil-7-217-2021
- **Lisensi: CC-BY 4.0** - atribusi wajib (sitasi di atas).
- **Resolusi:** 250 m, estimasi model global (bukan sampel tanah lapangan).
- **Catatan API:** masih **beta**, tanpa jaminan uptime, batas 5 panggilan/menit.
  Query 9 properti sekaligus timeout (2026-09-23) → skrip query **1 properti
  per panggilan**, jeda 12 s, retry, dan cache JSON per titik/properti.
  Cadangan manual: WCS `https://maps.isric.org/mapserv?map=/map/<properti>.map`
- **Titik (tidak ada koordinat resmi Jotosanur di dokumen kita):**
  - `osm` - OSM node 1308667031: -7,1520910, 112,4025416
  - `wikidata` - Q14633038: -7,1583333, 112,4108333 (P131 = Tikung)
  - Jarak ~1 km (~4 piksel SoilGrids).
- **Query:** 9 properti (sama dengan kolom `SoilGrids_*` CIMMYT §8) × 6
  kedalaman (0-5 s/d 100-200 cm) × 5 nilai (mean, Q0.05, Q0.5, Q0.95,
  uncertainty).
- **Skrip:** `src/jotosanur_agri/pipeline/load_soilgrids.py`
  (`uv run python -m jotosanur_agri.pipeline.load_soilgrids [--refresh]`).
  Tarikan satu kali; hanya diambil ulang dengan `--refresh`.
- **Diekstrak ke** (di luar git - `.gitignore` `/data/`):
  - `data/bronze/soilgrids/raw/<titik>/<properti>.json` (respons mentah)
  - `data/bronze/soilgrids/soilgrids_long.parquet` (nilai mapped integer)
  - `data/silver/soilgrids/soilgrids_long.parquet` (540 baris, 0 null;
    nilai = mapped / d_factor, uncertainty tetap indeks tanpa skala)
  - `data/silver/soilgrids/soilgrids_cimmyt_0-5cm.parquet` (format kolom
    CIMMYT, siap dimasukkan ke model benchmark)
- **Temuan skala ocd:** `SoilGrids_ocd` CIMMYT = ocd API (hg/m³) / 10.
  Bukti: di CIMMYT, soc×bdod/ocd bermedian 10,2 (p10-p90 8,1-12,4),
  sedangkan dari API 1,65. Label unit ocd di API tidak konsisten. Skrip
  membagi ocd /10 **hanya** di tabel format CIMMYT; tabel long tetap unit API.

**Hasil 0-5 cm (mean), diambil 2026-09-23** - semua dalam rentang CIMMYT:

| Properti | osm | wikidata | Rentang CIMMYT |
|---|---|---|---|
| bdod (g/cm³) | 1,30 | 1,31 | 1,1-1,6 |
| cfvo (% vol) | 9,9 | 10,8 | 3-23 |
| clay (%) | 35,1 | 34,3 | 16-56 |
| nitrogen (g/kg) | 2,10 | 2,04 | 0,9-5,2 |
| ocd (skala CIMMYT) | 2,85 | 2,77 | 1,6-4,0 |
| phh2o | 6,0 | 5,9 | 5,3-8,6 |
| sand (%) | 35,8 | 38,4 | 9-53 |
| silt (%) | 29,1 | 27,2 | 19-62 |
| soc (g/kg) | 36,2 | 31,8 | 10,3-55,5 |

- **Batasan:** nilai prediksi model 250 m, bukan uji tanah sawah Jotosanur.
  Dua titik berdekatan memberi hasil hampir sama, tapi keduanya bisa sama-sama
  meleset dari kondisi lapangan.

