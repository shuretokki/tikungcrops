# Temuan Teknis: dari Prediksi Hasil Panen ke Pemantauan Tanam Berbasis Satelit

Dicatat 2026-09-23. Semua angka di bawah dihitung dari data nyata dengan kode di repo ini
(skrip eksperimen tidak disimpan; hasilnya dicatat di sini dan di
`archives/README.md`).

## 1. Kenapa modul prediksi hasil panen ditinggalkan

Data operasional Kampung Pandu Sakti tidak pernah ada dan tidak akan datang dari mitra.
Tiga pendekatan prediksi diuji terhadap data nyata; tidak ada yang bermakna untuk
Jotosanur.

| Pendekatan | Hasil | Kesimpulan |
|---|---|---|
| RF dilatih pada data sintetis Jotosanur | R² holdout -0,10; batas atas desain generator ~0,037 | Sirkular: model hanya meniru rumus generator |
| RF dilatih pada survei CIMMYT (44.299 lahan padi nyata, Asia Selatan), hanya fitur yang tersedia untuk Jotosanur (9 sifat tanah SoilGrids, curah hujan tahunan, N/P/K, laju benih, lama tanam, jenis varietas) | Uji leave-one-region-out: R² negatif di keenam wilayah (MAPE 30-84%). Prediksi Jotosanur 4,15 t/ha untuk 2013 dan 2020, padahal BPS mencatat 6,82 dan 7,25 t/ha | Tidak bisa ditransfer. Kadar debu (silt) dan C-organik tanah Jotosanur di luar rentang p5-p95 CIMMYT |
| CIMMYT + koreksi level dengan 26 baris lokal (setara ukuran data BPS Tikung) | Di keenam wilayah uji, model terkoreksi tidak pernah lebih baik dari rata-rata 26 baris lokal itu sendiri (R² ≤ 0) | Model global tidak menambah informasi |
| Baseline naif pada data BPS nyata (produktivitas desa 2020 = nilai 2013, atau = rata-rata kecamatan) | MAPE 3,6% (13 desa) | Produktivitas padi Tikung sangat seragam (6,8-7,8 t/ha); rata-rata lokal sudah prediktor terkuat |

Fuzzy Tsukamoto tidak bisa divalidasi sama sekali karena tidak ada data lokal untuk
menguji aturannya. Seluruh kode ini dipindah ke `archives/`.

## 2. Kelayakan data satelit (tanpa akun, tanpa survei lapangan)

- **Sentinel-2 L2A** (optik, 10 m, Earth Search/AWS): 924 citra di atas Jotosanur,
  Feb 2017 - Sep 2026. Tutupan awan per citra buruk pada Nov-Feb (hanya 4-9 citra jernih
  per bulan dalam 9 tahun) dibanding Jul-Sep (sampai 67), tetapi masker awan per piksel
  (SCL) masih menyisakan tanggal jernih pada musim hujan.
- **Sentinel-1 RTC** (radar, tembus awan, Planetary Computer): 505 citra, 2015-2026,
  polarisasi VV dan VH, sudah dikoreksi medan.
- **ESA WorldCover 2021**: masker lahan pertanian (kelas 40); 75% kotak 3 km di sekitar
  Jotosanur adalah lahan pertanian.
- **GADM 4.1 level 4**: batas ke-13 desa Kecamatan Tikung tersedia, nama cocok persis
  dengan tabel BPS. OpenStreetMap tidak memiliki batas desa/kecamatan di wilayah ini.

Semua nilai berasal dari nilai band terukur (NDVI = (NIR-Red)/(NIR+Red), LSWI dari
NIR dan SWIR, backscatter VH/VV dalam dB), bukan interpretasi visual. Produk turunan
pihak lain yang dipakai: koreksi atmosfer L2A, klasifikasi awan SCL, WorldCover, dan
koreksi medan RTC.

## 3. Validasi awal terhadap BPS (13 desa, 2020, hanya Sentinel-2)

| Uji | r (n = 13) | Kesimpulan |
|---|---|---|
| Luas lahan pertanian dari satelit vs luas panen BPS | 0,78 | Luas dan siklus tanam dapat diukur |
| Puncak NDVI vs produktivitas BPS | 0,07-0,27 (tidak signifikan; batas ~0,55) | Produktivitas tidak dapat diestimasi dari kehijauan; variasinya antardesa terlalu kecil |

## 4. Prototipe pipeline (Jotosanur, Sep 2019 - Des 2020)

- **Bronze** (`load_sentinel`): 196 sel 100 m lahan pertanian; tiap citra menjadi satu
  baris per sel. 2020: 72 tanggal Sentinel-2 + 53 tanggal Sentinel-1, 24.500 baris,
  ~2 menit. Satu berkas parquet per bulan.
- **Silver** (`silver_sentinel`): kalender 5 harian per sel, awan dan kabut dibuang,
  selisih orbit Sentinel-1 dihapus, celah ≤ 30 hari diinterpolasi. 179 dari 196 sel
  (91%) menunjukkan tepat 2 puncak NDVI pada 2020. Desember 2020: Sentinel-2 0% terisi,
  Sentinel-1 100%; radar menutup celah musim hujan.
- **Gold** (`gold_sentinel`): tanggal penggenangan (VH minimum), awal tumbuh, puncak, dan
  panen per sel per musim.

| | Musim 1 (hujan) | Musim 2 (kemarau) |
|---|---|---|
| Penggenangan/tanam | Okt 2019: 13 sel, **Nov: 93**, Des: 40 | Apr: 45, **Mei: 122** |
| Puncak NDVI | Feb-Mar (median 0,86) | Jun (median 0,81) |
| Panen | Mar: 33, **Apr: 98** | **Jul-Agu** |
| Penggenangan → panen | ~120 hari | ~80 hari |
| NDVI sebelum tanam | 0,18 (tanah terbuka) | 0,35 |
| VH saat penggenangan | -18,0 dB | -16,4 dB |

Tanggal panen terisi untuk 84% musim; sisanya sengaja dikosongkan karena tidak ada
penurunan NDVI yang jelas sebelum musim berikutnya. Musim yang terpotong batas periode
data diberi penanda (`start_truncated`, `end_truncated`), bukan ditebak.

## 5. Kecocokan dengan kalender tanam resmi

DKPP Lamongan (November 2024): musim tanam padi dimulai Oktober di sawah irigasi,
dengan intensitas tanam tertinggi pada November dan Desember di sawah tadah hujan
([portal.lamongankab.go.id](https://portal.lamongankab.go.id/posting/19348),
[jatimnow](https://jatimnow.com/baca-73208-dorong-produktivitas-pemkab-lamongan-percepat-musim-tanam-padi)).
Deteksi radar musim 1 tanpa masukan kalender apa pun: sebagian besar November-Desember,
dengan kelompok kecil di Oktober. Sumber itu tentang periode 2024/2025 dan tidak memuat
musim kemarau; musim 2 belum divalidasi dengan kalender.

## 6. Catatan teknis yang perlu diketahui

- Earth Search menandai `boa_offset_applied = true` untuk semua citra (termasuk 2020 yang
  sudah diproses ulang ke baseline 05.x), sementara metadata band masih mencantumkan
  offset -0,1. Nilai piksel air (DN merah < 1000) membuktikan offset sudah dihapus, jadi
  kode tidak mengurangi offset lagi.
- Kesalahan WorldCover (misalnya permukiman terklasifikasi lahan pertanian) langsung
  menjadi kesalahan sel.
- Validasi dengan 13 desa masih sampel kecil.
- Program Kampung Pandu Sakti (6,3 ha) hanya ~3% dari 196 ha lahan pertanian Jotosanur;
  perubahan 2 → 3 kali panen pada lahan program tidak akan terlihat di tingkat desa
  tanpa lokasi petak program.

## 7. Langkah berikutnya

Skala ke seluruh 13 desa Tikung dengan area of interest umum (bukan hanya desa), validasi
luas dan jumlah musim terhadap BPS, lalu tahun-tahun lain untuk melihat tren.
