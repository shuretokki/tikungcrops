// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: CC-BY-4.0

// Kerangka Laporan Akhir PMB Studi Independen.
// Setiap subbab memuat isi wajib dari templat, bobot rubrik, fakta proyek yang sudah terverifikasi, rujukan, panduan menulis, dan data yang masih harus dilengkapi.
// Templat resmi: documents/local/official/laporan-akhir-template.txt (hasil parse PDF, 28 halaman).
// Rubrik: Pedoman PMB 2026, Lampiran 5 (Rubrik Penilaian Laporan Akhir).
// Fakta: FINDING.local.md (F, S, L) dan documents/local/temuan-teknis.md (§).

#import "@preview/jilid:0.2.0": appendix, frontmatter, jilid, signature, signatures

#show: jilid.with(
  title: [Pemantauan Musim Tanam Padi Berbasis Citra Satelit dan Machine Learning di Kecamatan Tikung, Kabupaten Lamongan],
  kind: [Laporan Akhir Program Mahasiswa Berdampak \ Studi Independen],
  cover: (kind-pos: "top"),
  cover-details: (([Mitra Kolaborator:], [Dicoding Indonesia]),),
  students: ((name: "Tri Rianto Utomo", id: "24051204104"),),
  program: "Teknik Informatika",
  faculty: "Teknik",
  university: "Universitas Negeri Surabaya",
  year: "2026",
  bibliography: bibliography("refs.bib", style: "harvard-cite-them-right"),
  typography: (font-family: "Times New Roman"),
  margin: "print",
)

// Kotak catatan kerangka. Hapus semua kotak ini saat naskah final ditulis.
#let kotak(judul, warna, isi) = block(
  width: 100%,
  inset: 8pt,
  radius: 3pt,
  stroke: 0.5pt + warna,
  fill: warna.lighten(92%),
  breakable: true,
)[#text(weight: "bold", fill: warna)[#judul] \ #isi]
#let wajib(isi) = kotak([Isi wajib (templat)], rgb("#3a5a8c"), isi)
#let rubrik(isi) = kotak([Rubrik penilaian], rgb("#7a4a8c"), isi)
#let fakta(isi) = kotak([Fakta proyek (sudah terverifikasi)], rgb("#2f7a4f"), isi)
#let panduan(isi) = kotak([Panduan menulis], rgb("#8c6a2a"), isi)
#let perlu(isi) = kotak([Perlu dilengkapi], rgb("#b03a3a"), isi)

#frontmatter(title: [Lembar Pengesahan])[
  #table(
    columns: (auto, 1fr),
    stroke: 0.5pt,
    inset: 6pt,
    [Judul Kegiatan], [Pemantauan Musim Tanam Padi Berbasis Citra Satelit dan Machine Learning di Kecamatan Tikung, Kabupaten Lamongan],
    [Nama Mitra], [Dicoding Indonesia],
    [Alamat Instansi], [Dicoding Space, Jl. Batik Kumeli No. 50, Sukaluyu, Kec. Cibeunying Kaler, Kota Bandung, Jawa Barat 40123],
    [Nama], [Tri Rianto Utomo],
    [NIM], [24051204104],
    [Prodi/Jurusan], [Teknik Informatika],
    [Fakultas], [Teknik],
    [No. Tlp.], [089678986450],
    [Alamat Email], [24051204104\@mhs.unesa.ac.id],
    [Periode Riset], [Agustus sampai Desember 2026],
  )
  #perlu[
    - Nama dan NIP Dosen Pembimbing Lapangan serta Koordinator Program Studi.
    - Judul baru di atas masih usulan. Judul proposal menyebut sistem informasi manajemen Kampung Pandu Sakti, sedangkan luaran nyata berupa pemantauan tanam berbasis satelit. Pastikan DPL setuju judul berubah.
  ]
  #v(1cm)
  #signatures(
    header: [Mengetahui,],
    signature(role: [Dosen Pembimbing Lapangan], name: "NAMA DPL", id: "NIP"),
    signature(role: [Mahasiswa], name: "Tri Rianto Utomo", id-label: "NIM", id: "24051204104"),
  )
  #v(0.5cm)
  #signatures(header: [Menyetujui,], signature(role: [Koordinator Program Studi], name: "NAMA KOORPRODI", id: "NIP"))
]

#frontmatter(title: [Kata Pengantar])[
  #wajib[Pedoman PMB 2026 bab 10.3 menempatkan Kata Pengantar sesudah Lembar Pengesahan. Templat PDF tidak memuatnya, jadi bagian ini boleh dibuat singkat.]
  #panduan[Satu halaman: ucapan syukur, terima kasih kepada DPL, Dicoding Indonesia, dan Kecamatan Tikung, lalu harapan singkat. Hindari klaim hasil di sini.]
]

#frontmatter(title: [Catatan Kerangka])[
  Dokumen ini adalah kerangka, bukan naskah final. Setiap subbab berisi enam jenis kotak. Kotak biru memuat isi wajib dari templat resmi. Kotak ungu memuat bobot rubrik. Kotak hijau memuat fakta proyek yang sudah diperiksa beserta sumbernya. Kotak cokelat memuat panduan menulis. Kotak merah memuat data yang masih harus dilengkapi.

  Daftar isi templat dan isi templat tidak sama. Daftar isi memuat Rumusan Masalah, Urgensi, dan Temuan yang Ditargetkan pada Bab I, serta Waktu dan Tempat pada Bab III. Isi templat tidak memuatnya. Kerangka ini memakai susunan yang lebih lengkap supaya isi laporan sejalan dengan proposal.

  Bobot rubrik (Pedoman PMB 2026, Lampiran 5): sistematika dan format 10%, analisis permasalahan 15%, perencanaan dan pelaksanaan 15%, hasil dan dampak 20%, luaran berdampak 20%, kesimpulan dan rencana tindak lanjut 10%, bahasa dan gaya ilmiah 10%.

  Gaya bahasa: bahasa baku tingkat B2 dengan skill `indonesian-advanced-writing`. Kalimat 12 sampai 25 kata, paling panjang 30 kata. Jalankan `check.py` dengan batas 30 pada setiap bab sebelum diserahkan.
]

= Pendahuluan

== Latar Belakang

#wajib[Gambaran umum topik, pentingnya topik bagi bidang terkait, masalah atau kekurangan yang mendorong studi, satu atau dua rujukan, dan peran mitra kolaborator.]
#rubrik[Analisis Permasalahan dan Kondisi Masyarakat, 15%. Nilai tertinggi: analisis kritis, berbasis data, dan sesuai kebutuhan masyarakat.]
#fakta[
  - Lamongan adalah penghasil padi terbesar di Jawa Timur pada 2024: 776.290,66 ton GKG dari 9.270.435,29 ton provinsi, atau 8,4% (S18, tabel BPS Jatim).
  - Luas panen padi Lamongan 2024 sekitar 130,67 ribu ha, produksi beras 448,25 ribu ton (S16).
  - Kecamatan Tikung punya 13 desa dan sekitar 4.420 ha sawah yang dipantau (meta.json, data per 29 September 2026).
  - Proposal menargetkan sistem pencatatan Kampung Pandu Sakti. Data operasional program itu tidak pernah tersedia dari mitra (§1).
  - Statistik pertanian resmi terbit tahunan per kecamatan atau kabupaten, sehingga petani dan perangkat desa tidak punya jadwal tanam dan panen per desa yang terbaru.
]
#panduan[
  Susun dalam empat paragraf dengan urutan dari umum ke khusus: peran Lamongan, kebutuhan informasi musim tanam per desa, kesenjangan data, lalu solusi. Pola ini mengikuti model CARS yang biasa dipakai pada pendahuluan artikel ilmiah. Sebut pergeseran dari rencana proposal secara singkat di sini, lalu jelaskan lengkap pada 4.2.
]
#perlu[Satu kalimat tentang peran Dicoding Indonesia sebagai mitra kolaborator, misalnya materi Big Data dan Machine Learning yang dipakai dalam proyek.]

== Rumusan Masalah

#wajib[Daftar isi templat mencantumkan subbab ini. Rumusan harus dijawab satu per satu pada 7.1.]
#fakta[
  Usulan tiga rumusan yang sesuai dengan luaran nyata:
  + Bagaimana membangun alur data otomatis yang mengubah citra Sentinel-1 dan Sentinel-2 menjadi tahap tanam per desa?
  + Seberapa tepat luas tanam dan waktu tanam hasil satelit bila dibandingkan dengan data resmi BPS dan KSA?
  + Bagaimana menyajikan jadwal tanam dan perkiraan panen dalam situs yang mudah dipahami warga desa?
]

== Tujuan Studi Independen

#wajib[Tujuan utama, metode untuk mencapainya, dan hasil yang diharapkan. Tujuan harus spesifik, terukur, dan bisa dicapai dalam waktu program.]
#rubrik[Penilaian Mini Proyek, Kejelasan tujuan, 0 sampai 15 poin: jelas, terukur, relevan.]
#fakta[
  Tiap tujuan memasangkan satu rumusan masalah dengan satu ukuran keberhasilan:
  + Alur data bronze, silver, dan gold berjalan untuk 13 desa Tikung sejak Oktober 2017. Ukuran: 60 uji otomatis lulus.
  + Validasi terhadap BPS 2020 dan KSA 2020 sampai 2023. Ukuran: korelasi luas per desa dan kecocokan pembagian panen per musim.
  + Situs publik dengan ringkasan, jadwal per desa, dan perkiraan panen. Ukuran: halaman berjalan tanpa galat di ponsel dan desktop.
]

== Manfaat Studi Independen

#wajib[Manfaat bagi pengetahuan akademis, bagi praktisi atau masyarakat, dan bagi keterampilan mahasiswa.]
#fakta[
  - Akademis: contoh pemantauan tanam tingkat desa tanpa survei lapangan, dengan evaluasi jujur per tahun (leave-one-year-out) dan daftar generalisasi G1 sampai G20 (temuan-teknis, Riset lanjutan).
  - Masyarakat: warga, buruh tani, dan perangkat desa melihat kapan desanya biasanya mulai tanam dan panen.
  - Mahasiswa: rekayasa data, pembelajaran mesin, pengujian, dan pengembangan web dalam satu proyek nyata.
]

== Urgensi Studi Independen

#wajib[Daftar isi templat mencantumkan subbab ini. Jelaskan mengapa proyek perlu dilakukan sekarang.]
#fakta[
  - Satelit radar Sentinel-1 lebih jarang melintas sejak 2022. Tanpa alur data yang menandai celah ini, data padi tahun 2022 dan 2023 mudah disalahartikan (F08).
  - Musim tanam utama 2026/2027 dimulai November, sehingga jadwal tanam per desa paling berguna bila tersedia sebelum itu.
]

== Temuan yang Ditargetkan

#wajib[Daftar isi templat mencantumkan subbab ini. Bandingkan target proposal dengan target yang direvisi.]
#fakta[
  #table(
    columns: (1fr, 1fr),
    stroke: 0.5pt,
    inset: 5pt,
    [*Target proposal*], [*Target revisi*],
    [Dashboard pencatatan panen, ternak, distribusi], [Situs pemantauan tanam 13 desa dan alur data bulanan],
    [Model prediksi hasil panen, MAPE di bawah 20%], [Prakiraan tanggal panen, galat lebih kecil dari baseline median],
    [Panduan operasional], [Halaman Metode dan dokumentasi kode],
    [Kanal WhatsApp (opsional)], [Tidak dikerjakan],
  )
]

= Tinjauan Pustaka

== Tinjauan Teoritis

#wajib[Teori atau konsep utama, serta model atau kerangka yang dipakai.]
#fakta[
  Empat konsep inti, masing-masing dengan rujukan:
  - Fenologi padi dan indeks vegetasi NDVI dari Sentinel-2 @Ramadhani_2020.
  - Penggenangan sawah pada radar Sentinel-1 (VH turun saat tanam pindah) @Manago_2020 @Rudiyanto_2019.
  - Intensitas tanam sebagai jumlah musim per tahun @Ginting_2024 @Zhao_2026.
  - Kriteria awal musim tanam di Indonesia @Surmaini_2016 dan umur panen padi antarprovinsi @Ardiansyah_2022.
  - Arsitektur data medallion (bronze, silver, gold) dan pemrosesan bertahap: belum ada rujukan ber-DOI.
]
#perlu[Rujukan untuk arsitektur medallion atau ETL. Rujukan proposal @yudhistira2023ilkom membahas ETL data pertanian dan bisa dipakai ulang.]

== Penelitian Sebelumnya

#wajib[Studi sebelumnya, kritik atas kekurangannya, tren terkini, serta definisi operasional dan hubungan antarvariabel.]
#fakta[
  - Tanggal tanam dari Sentinel-1 di DI Cihea, Jawa Barat, dengan galat sekitar 5 sampai 6 hari terhadap wawancara petani @Manago_2020.
  - Pemetaan tahap tumbuh padi di Jawa Barat dengan deep learning @Thorp_2021 dan dengan fusi Sentinel-2, MODIS, dan Sentinel-1 @Ramadhani_2020.
  - Fenologi padi dari deret Sentinel-1 @Yang_2021.
  - Intensitas tanam di Indramayu dari Sentinel-1 @Gandharum_2025.
  - Kritik: studi tersebut memakai data lapangan untuk melatih model, sedangkan proyek ini tidak punya data lapangan. Karena itu label proyek ini berasal dari satelit sendiri dan diuji per tahun (§12, L19).
  - Variabel: tanggal penggenangan (VH minimum), puncak NDVI, tanggal panen, luas sawah per desa, curah hujan CHIRPS.
]
#panduan[Akhiri subbab dengan satu paragraf celah penelitian: belum ada pemantauan tingkat desa yang terbuka untuk warga dan diperbarui tiap bulan tanpa data lapangan.]

== Luaran Berdampak yang Diusulkan

#wajib[Luaran, dampak, dan mitra, dengan format seperti contoh templat.]
#rubrik[Luaran Program yang Berdampak, 20%. Nilai tertinggi: aplikatif, inovatif, dan berkelanjutan.]
#fakta[
  - Luaran 1: situs Tanam Padi Lamongan (beranda, ringkasan, jadwal per desa, metode).
  - Luaran 2: alur data terbuka berlisensi Apache-2.0 (kode) dan CC-BY-4.0 (data), patuh REUSE 3.3.
  - Luaran 3: data per desa dalam berkas JSON dan MongoDB.
  - Dampak: warga melihat jadwal tanam dan panen desanya. Mitra: Dicoding Indonesia, dengan objek studi Kecamatan Tikung.
]

= Metode

== Waktu dan Tempat Pelaksanaan

#wajib[Daftar isi templat mencantumkan subbab ini.]
#fakta[Agustus sampai Desember 2026, daring. Objek: 13 desa Kecamatan Tikung, lalu perluasan ke 27 kecamatan Kabupaten Lamongan.]
#perlu[Tanggal mulai dan selesai resmi dari MELISA.]

== Posisi atau Kedudukan Kegiatan

#wajib[Kedudukan tugas mahasiswa dalam proyek keseluruhan, untuk menunjukkan pemahaman kaitan antara pekerjaan dan hasil.]
#fakta[Pengembang tunggal untuk seluruh siklus: pengambilan data, pemodelan, pengujian, dan situs web, di bawah bimbingan DPL dan materi Dicoding.]

== Metodologi Penyelesaian Tugas

#wajib[Uraikan masalah menjadi topik bahasan. Gunakan teori atau metode untuk menjelaskan kasus, bukan sekadar mendeskripsikan teori. Sebut referensi yang valid.]
#rubrik[Perencanaan dan Pelaksanaan Program, 15%.]
#fakta[
  + Pengambilan data: 924 citra Sentinel-2 dan 505 citra Sentinel-1 di atas Jotosanur, 2015 sampai 2026, tanpa akun berbayar (§2).
  + Bronze: satu baris per sel 100 m per citra. Silver: kalender 5 harian, awan dibuang, celah hingga 30 hari diinterpolasi (§4).
  + Gold: tanggal penggenangan, puncak, dan panen per sel per musim. Masker sawah dari Lahan Baku Sawah (§8).
  + Model prakiraan panen: desain CY-Bench, satu tahun ditahan sebagai uji, baseline median dibandingkan dengan Ridge, random forest, dan gradient boosting (§23, M01).
  + Validasi terhadap BPS 2020 per desa dan KSA bulanan 2020 sampai 2023.
  + Jadwal otomatis bulanan lewat GitHub Actions dan `just monthly`.
]
#panduan[
  Tulis langkah sampai pembaca lain dapat mengulanginya. Rujuk metode yang sudah terbit alih-alih menjelaskannya ulang (Gastel dan Day, How to Write and Publish a Scientific Paper, bab Materials and Methods). Satu diagram alur dengan paket fletcher, seperti contoh pada templat jilid, sudah cukup.
]

== Pembelajaran Hal Baru

#wajib[Temuan pembelajaran baru, perbandingan dengan teori yang dipelajari, dan kendala selama kegiatan.]
#fakta[
  - Data sintetis membuat model sirkular. Random forest pada data sintetis Jotosanur memberi R² holdout -0,10 (§1).
  - Model global CIMMYT tidak bisa dipindahkan ke Jawa. R² negatif di keenam wilayah uji (§1).
  - Skor acak terlalu optimistis. Evaluasi harus per tahun (L19, §20).
  - Layanan data pemerintah dan sains bisa gagal: peta LBS habis waktu pada area besar (F23), CHIRPS memblokir unduhan beruntun.
]
#panduan[Pakai model refleksi 4R @Ryan_2013: reporting (apa yang terjadi), relating (kaitan dengan pengalaman atau teori), reasoning (mengapa terjadi), reconstructing (apa yang akan dilakukan berbeda).]

= Hasil dan Pembahasan

== Hasil

#wajib[Deskripsi kegiatan, data dan hasil pengukuran (tabel, grafik, gambar), luaran konkret, dan capaian dibandingkan rencana awal. Tambahkan gambar hasil.]
#rubrik[Hasil dan Dampak Program, 20%. Nilai tertinggi: berdampak nyata dan dirasakan masyarakat.]
#fakta[
  - Validasi luas 2020: korelasi 0,90 sampai 0,91 untuk semua tanaman, satelit 1,14 sampai 1,25 kali BPS. Padi saja: korelasi 0,77, tetapi ambangnya disetel pada tahun yang sama (F05, F07).
  - Produktivitas tidak terbaca dari puncak NDVI: korelasi 0,07 sampai 0,27, tidak signifikan (§3).
  - Waktu panen terhadap KSA: porsi panen Januari sampai Mei cocok dengan selisih 0,01 sampai 0,08 (§22).
  - Prakiraan panen (galat rata-rata 9 tahun uji): tanggal tanam 11,9 hari dengan gradient boosting, baseline 15,2 hari. Puncak 9,3 hari, baseline 10,1 hari (§23).
  - Backtest musim kemarau (terbit Juni): tanggal median per desa meleset 4 sampai 14 hari. Musim hujan (terbit Januari): 14 sampai 37 hari (§20).
  - Jadwal tanam utama per desa: puncak tanam dari 20 November (Takeranklating) sampai 24 Desember (Tambakrigadung) (F22).
  - Lamongan: unduhan 2024-09 sampai 2026-09 selesai untuk 27 kecamatan dan 109.504 sel. Masker sawah 86.565 ha (F23).
  - Perangkat lunak: 60 uji otomatis lulus, patuh REUSE 3.3.
]
#panduan[
  Sajikan hasil tanpa tafsiran. Tafsiran masuk ke 4.2 (Gastel dan Day, bab Results). Gunakan tabel capaian target lawan rencana seperti pada 1.6, lalu dua sampai empat gambar: peta tahap tanam, kalender tanam, jadwal per desa, dan grafik hujan dari situs.
]
#perlu[Tangkapan layar situs dan peta, serta bukti kegiatan dari logbook MELISA.]

== Pembahasan

#wajib[Tafsiran hasil, kaitan dengan teori dan literatur, kelebihan dan keterbatasan metode, dampak nyata dan keberlanjutan, serta refleksi pribadi.]
#rubrik[Hasil dan Dampak 20%, serta Luaran 20%.]
#fakta[
  - Mengapa rencana berubah: data operasional Kampung Pandu Sakti tidak pernah tersedia, dan fuzzy Tsukamoto tidak bisa divalidasi tanpa data lokal (§1).
  - Mengapa luas satelit lebih besar dari BPS: masker WorldCover mencakup jagung dan lahan kering, dan satelit menghitung lebih banyak musim (F05, F06).
  - Keterbatasan: awan musim hujan menyembunyikan awal musim (§20), celah radar 2022 sampai 2023 (F08), dan belum ada data lapangan petani.
  - Kaitan dengan literatur: galat tanggal tanam dari radar sekitar 5 sampai 6 hari di Cihea @Manago_2020, sedangkan proyek ini 11,9 hari tanpa data lapangan.
]
#panduan[
  Ikuti urutan Hess @Hess_2023: buka dengan jawaban utama, bandingkan dengan penelitian lain, sebut keterbatasan secara terbuka, lalu tutup dengan implikasi. Fokus pada data proyek dan jangan mengulang angka dari 4.1.
]
#perlu[Bukti dampak nyata. Rubrik menilai keterlibatan masyarakat atau mitra. Saat ini belum ada demo ke desa dan belum ada surat pernyataan mitra.]

= Korelasi Program Studi Independen dengan Konversi Mata Kuliah

== Kegiatan Studi Independen yang Dikembangkan

#wajib[Paragraf kegiatan sesuai pola templat, tujuan pengembangan, langkah pengembangan, tabel kegiatan mingguan (posisi, topik, durasi jam, target, metode), serta dampak bagi mitra dan mahasiswa.]
#fakta[
  - Tabel rencana proposal 8 minggu dengan total 240 jam tersedia di proposal.typ, baris 299 sampai 310.
  - Tabel realisasi bisa disusun dari CHANGELOG.local.md dan riwayat git.
]
#perlu[Jam per minggu dari logbook MELISA, supaya tabel realisasi cocok dengan logbook.]

== Relevansi dengan Mata Kuliah Konversi

#wajib[Tabel relevansi kegiatan dengan mata kuliah konversi.]
#fakta[
  #table(
    columns: (auto, auto, 1fr),
    stroke: 0.5pt,
    inset: 5pt,
    [*Mata kuliah*], [*SKS*], [*Bukti kegiatan*],
    [Perencanaan Program], [2], [Proposal, rencana 8 minggu, papan roadmap],
    [Big Data], [3], [Alur bronze, silver, gold, MongoDB, Parquet, pemrosesan 109.504 sel Lamongan],
    [Machine Learning], [3], [Perbandingan baseline, Ridge, random forest, gradient boosting dengan evaluasi per tahun],
    [Evaluasi Program], [2], [Validasi BPS dan KSA, backtest, 60 uji otomatis],
  )
  CPMK tiap mata kuliah ada di documents/local/cpmk-konversi-mk.md.
]

= Rencana Tindak Lanjut dan Rekomendasi

== Rencana Tindak Lanjut

#wajib[Pengembangan produk, pelatihan dan transfer pengetahuan, monitoring berkala, serta pendanaan atau kerja sama.]
#rubrik[Kesimpulan dan Rencana Tindak Lanjut, 10%. Nilai tertinggi: tajam, strategis, berorientasi keberlanjutan.]
#fakta[
  - Pembaruan bulanan otomatis: penyimpanan riwayat citra (R2, Hugging Face, atau runner sendiri), lalu build dan deploy situs (rencana di CHANGELOG.local.md).
  - Deteksi awal musim yang lebih tahan awan sebelum musim hujan 2026/2027 (§20).
  - Brief satu halaman dan demo daring untuk desa.
]
#panduan[Tulis setiap rencana dengan pelaku, waktu, dan ukuran keberhasilan supaya tidak terdengar umum.]

== Rekomendasi

#wajib[Rekomendasi teknis, manajerial, kebijakan, dan penelitian lanjutan.]
#fakta[
  - Teknis: fusi radar dan optik, penghalusan deret waktu, dan sel lebih kecil untuk petak sempit (G14, G15).
  - Kebijakan: statistik desa terbuka akan memudahkan validasi pemantauan seperti ini.
  - Penelitian: uji generalisasi G1 sampai G20 di wilayah lain.
]

= Penutup

== Kesimpulan

#wajib[Templat tidak memberi contoh. Jawab setiap rumusan masalah pada 1.2 secara berurutan.]
#panduan[Satu paragraf per rumusan masalah, tanpa data baru dan tanpa rujukan baru.]

== Refleksi Akhir

#wajib[Templat tidak memberi contoh.]
#panduan[Gunakan model 4R @Ryan_2013 pada satu pengalaman penting, misalnya keputusan meninggalkan model prediksi hasil panen setelah data mitra tidak tersedia.]

#appendix(title: [Biodata Mahasiswa])[
  #wajib[Templat mewajibkan Lampiran 1 berisi biodata mahasiswa.]
]

#appendix(title: [Dokumentasi dan Bukti Kegiatan])[
  #perlu[
    - Surat Pernyataan Implementasi Kegiatan dari mitra (Pedoman PMB 2026, Lampiran 6). Belum ada.
    - Rekap logbook MELISA.
    - Tangkapan layar situs, tautan repositori, dan tautan situs bila sudah dipublikasikan.
  ]
]
