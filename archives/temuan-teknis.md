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

## 7. Skala ke seluruh Kecamatan Tikung (13 desa, Sep 2019 - Des 2020)

Pipeline memakai area of interest umum (`Lamongan/Tikung`, unit = desa), bukan satu desa.
Ekstraksi 16 bulan: 8,5 menit, 4.954 sel lahan pertanian, ~846 ribu baris bronze (8 MB).
Silver 0,8 detik, gold 4 detik, 10.942 musim.

**Validasi luas terhadap BPS 2020 (n = 13 desa):**

| Ukuran satelit | vs luas panen padi BPS | vs padi + jagung BPS |
|---|---|---|
| Luas lahan pertanian | r = 0,77 | **r = 0,90** |
| Luas panen (lahan × jumlah musim 2020) | r = 0,78 | **r = 0,90** |
| Rasio satelit/BPS untuk luas panen | 1,37 | 1,25 |

- Korelasi naik saat jagung ikut dihitung, konsisten dengan WorldCover yang tidak
  membedakan padi dan jagung.
- Urutan antardesa terukur baik, tetapi levelnya lebih tinggi 25-37% dari BPS.
  Penyebab yang mungkin: lahan pertanian WorldCover mencakup tegalan dan tanaman lain,
  sebagian puncak ketiga adalah palawija atau derau, dan batas GADM tidak persis sama
  dengan batas administrasi BPS. Jotosanur sendiri justru lebih rendah (324 vs 459 ha).
- Musim per sel pada 2020: 2 musim 79% sel, 3 musim 19%.

**Waktu tanam seluruh Tikung (musim 1, dari radar):** penggenangan November 1.769 sel dan
Desember 2.581 sel (88% dari musim yang terdeteksi), Oktober 197; panen Maret 1.977 dan
April 1.256. Median penggenangan per desa berkisar dari 15 November (Soko) sampai
20 Desember (Tambakrigadung), selisih sekitar 5 minggu antardesa. Ini konsisten dengan
pernyataan DKPP bahwa sawah irigasi menanam lebih dulu dan puncak tanam November-Desember.
Musim 2: penggenangan terutama April (3.239 sel) dan Mei (1.235).

## 8. Masker padi resmi (Lahan Baku Sawah)

WorldCover kelas 40 mencakup semua lahan pertanian (padi, jagung, tegalan). Peta Lahan Baku
Sawah (BIG Satu Peta, layanan ArcGIS publik) memberi 105 poligon sawah di Tikung, 4.420 ha
di dalam sel yang dipantau; hanya 236 ha sawah LBS berada di luar sel. 93% sel (4.587 dari
4.954) setidaknya separuhnya sawah LBS, jadi masker padi hampir tidak mengubah hasil: luas
panen satelit tetap 1,35 kali BPS (r = 0,78).

Selisih berasal dari **jumlah musim**, bukan luas: satelit menghitung rata-rata 2,18 musim
per tahun di sawah, sementara luas panen padi BPS 2020 (7.145 ha) dibagi luas sawah LBS
setara 1,62 kali panen padi. Sinyal radar mendukung dugaan bahwa musim kedua sering bukan
padi sawah tergenang:

| Musim di sel sawah | Median VH saat "penggenangan" | Porsi dengan VH < -18 dB |
|---|---|---|
| Musim 1 (hujan) | -18,4 dB | 65% |
| Musim 2 (kemarau) | -15,6 dB | 9% |

Musim kemarau tanpa tanda penggenangan kemungkinan palawija (jagung, kedelai, kacang hijau)
atau padi tanam benih langsung. Korelasi selisih musim dengan luas jagung BPS per desa lemah
(r = 0,27), jadi jagung saja belum menjelaskan seluruh selisih. Jotosanur justru kebalikannya:
BPS setara 3,33 kali panen di sawah LBS-nya, kemungkinan karena poligon LBS di desa itu lebih
kecil dari sawah sebenarnya.

## 9. Langkah berikutnya


Klasifikasi padi/non-padi per musim dari tanda penggenangan radar (lalu uji ulang terhadap
BPS), data 2023-2026 untuk melihat perubahan sejak program 2025, dan tampilan hasil per desa
di dashboard.
