// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: CC-BY-4.0

#import "@preview/jilid:0.2.0": appendix, frontmatter, jilid, signature, signatures

#show: jilid.with(
  title: [Laporan Akhir Program Mahasiswa Berdampak],
  kind: [Studi Independen],
  cover: (kind-pos: "bottom", details: (size: 12pt), title: (size: 12pt), kind: (size: 12pt)),
  cover-details: ((upper()[Pemantauan Musim Tanam Padi Berbasis Citra Satelit dan Machine Learning di Kecamatan Tikung, Kabupaten Lamongan],[]),([Mitra Kolaborator:], [Dicoding Indonesia]),),
  students: ((name: "Tri Rianto Utomo", id: "24051204104"),),
  program: "Teknik Informatika",
  faculty: "Teknik",
  university: "Universitas Negeri Surabaya",
  year: "2026",
  bibliography: bibliography("refs.bib", style: "harvard-cite-them-right"),
  typography: (font-family: "Times New Roman"),
  margin: "digital",
  numbering: (position: "top"),
)

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
    columns: 2,
    align: (left, left),
    stroke: 0.5pt + luma(80),
    inset: (x: 6pt, y: 6pt),
    [*Judul Kegiatan*], [Studi Independen],
    [*Nama Mitra*], [Dicoding Indonesia],
    [*Alamat Instansi*], [Dicoding Space Jl. Batik Kumeli No.50, Sukaluyu, Kec. Cibeunying Kaler, Kota Bandung Jawa Barat 40123],
    [*Identitas Mahasiswa*], [
      #grid(
        columns: (auto, 1fr),
        row-gutter: 0.5em,
        column-gutter: 0.4em,
        [*Nama*], [: Tri Rianto Utomo],
        [*NIM*], [: 24051204104],
        [*Prodi/Jurusan*], [: Teknik Informatika],
        [*Fakultas*], [: Teknik],
        [*No Tlp.*], [: 089678986450],
        [*Alamat Email*], [: 24051204104\@mhs.unesa.ac.id],
      )
    ],
    [*Periode Studi Independen*], [2026],
  )

  // #table(
  //   columns: (auto, 1fr),
  //   stroke: 0.5pt,
  //   inset: 6pt,
  //   [Judul Kegiatan], [Pemantauan Musim Tanam Padi Berbasis Citra Satelit dan Machine Learning di Kecamatan Tikung, Kabupaten Lamongan],
  //   [Nama Mitra], [Dicoding Indonesia],
  //   [Alamat Instansi], [Dicoding Space, Jl. Batik Kumeli No. 50, Sukaluyu, Kec. Cibeunying Kaler, Kota Bandung, Jawa Barat 40123],
  //   [Nama], [Tri Rianto Utomo],
  //   [NIM], [24051204104],
  //   [Prodi/Jurusan], [Teknik Informatika],
  //   [Fakultas], [Teknik],
  //   [No. Tlp.], [089678986450],
  //   [Alamat Email], [24051204104\@mhs.unesa.ac.id],
  //   [Periode Riset], [Agustus sampai Desember 2026],
  // )


  #v(1cm)
  #signatures(
    header: [Mengetahui,],
    signature(role: [Dosen Pembimbing Lapangan], name: "Rifqi Abdillah, S.Tr.T., M.Kom.", id: "199911012024061001"),
    signature(role: [Mahasiswa], name: "Tri Rianto Utomo", id-label: "NIM", id: "24051204104"),
  )
  #v(0.5cm)
  #signatures(header: [Menyetujui,], signature(role: [Koordinator Program Studi], name: "Paramitha Nerisafitra, S.ST., M.Kom.", id: "198905292019032013"))
]

#frontmatter(title: [Catatan Kerangka])[
  Dokumen ini masih kerangka, kecuali Bab I, Bab II, dan subbab 3.1 yang sudah berupa naskah. Setiap subbab kerangka berisi enam jenis kotak. Kotak biru memuat isi wajib dari templat resmi. Kotak ungu memuat bobot rubrik. Kotak hijau memuat fakta proyek yang sudah diperiksa beserta sumbernya. Kotak cokelat memuat panduan menulis. Kotak merah memuat data yang masih harus dilengkapi.

  Daftar isi templat dan isi templat tidak sama. Daftar isi memuat Rumusan Masalah, Urgensi, dan Temuan yang Ditargetkan pada Bab I, serta Waktu dan Tempat pada Bab III. Isi templat tidak memuatnya. Kerangka ini memakai susunan yang lebih lengkap supaya isi laporan sejalan dengan proposal.

  Bobot rubrik (Pedoman PMB 2026, Lampiran 5): sistematika dan format 10%, analisis permasalahan 15%, perencanaan dan pelaksanaan 15%, hasil dan dampak 20%, luaran berdampak 20%, kesimpulan dan rencana tindak lanjut 10%, bahasa dan gaya ilmiah 10%.

  Gaya bahasa: bahasa baku tingkat B2 dengan skill `indonesian-advanced-writing`. Kalimat 12 sampai 25 kata, paling panjang 30 kata. Jalankan `check.py` dengan batas 30 pada setiap bab sebelum diserahkan.
]

#include "bab1.typ"

#include "bab2.typ"

= Metode

== Waktu dan Tempat Pelaksanaan

Studi independen ini berlangsung dari Agustus sampai Desember 2026 sesuai jadwal Program Mahasiswa Berdampak. Laporan ini disusun pada akhir Oktober 2026, sehingga hasil yang dilaporkan mencakup pekerjaan sampai saat itu. Pekerjaan sesudah tanggal tersebut dicatat sebagai rencana tindak lanjut pada Bab VI.

Seluruh kegiatan dilaksanakan secara daring. Data citra satelit, curah hujan, dan peta sawah diambil dari katalog data terbuka, sehingga studi ini tidak memerlukan pengukuran lapangan. Pengolahan data, pemodelan, dan pengembangan situs dikerjakan di komputer mahasiswa.

Wilayah kajian utama adalah Kecamatan Tikung, Kabupaten Lamongan, Jawa Timur. Wilayah ini terletak antara 112,37° dan 112,45° Bujur Timur serta antara 7,12° dan 7,25° Lintang Selatan. Kecamatan Tikung terdiri atas tiga belas desa, yaitu Bakalanpule, Balongwangi, Botoputih, Dukuhagung, Guminingrejo, Jatirejo, Jotosanur, Kelorarum, Pengumbulanadi, Soko, Takeranklating, Tambakrigadung, dan Wonokromo. Luas sawah yang dipantau di wilayah ini sekitar 4.420 hektare.

Data yang diolah untuk Kecamatan Tikung mencakup citra Oktober 2017 sampai September 2026. Rentang ini memuat musim tanam yang berakhir pada tahun 2018 sampai 2026. Selain itu, citra September 2024 sampai September 2026 untuk 27 kecamatan di Kabupaten Lamongan sudah diunduh sebagai tahap perluasan. Pengolahan data kabupaten tersebut masih berlangsung pada saat laporan ini disusun.

#figure(
  table(
    columns: (auto, 1fr),
    stroke: 0.5pt,
    inset: 5pt,
    align: left,
    table.header([*Aspek*], [*Keterangan*]),
    [Waktu program], [Agustus sampai Desember 2026],
    [Bentuk kegiatan], [Daring, tanpa pengukuran lapangan],
    [Wilayah utama], [Kecamatan Tikung, 13 desa, sekitar 4.420 ha sawah],
    [Rentang data Tikung], [Oktober 2017 sampai September 2026],
    [Wilayah perluasan], [Kabupaten Lamongan, 27 kecamatan, citra September 2024 sampai September 2026],
  ),
  caption: [Ringkasan waktu dan tempat pelaksanaan],
) <tabel-waktu-tempat>

#perlu[
  - Tanggal mulai dan selesai resmi dari MELISA. Ganti "Agustus sampai Desember 2026" bila tanggalnya berbeda.
  - Cara bimbingan dengan DPL (daring, luring, atau campuran), bila ingin disebut pada subbab ini.
  - Peta lokasi Kecamatan Tikung sebagai gambar. Peta bisa diambil dari situs dengan label desa.
]

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
