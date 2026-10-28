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
  Dokumen ini masih kerangka, kecuali Bab I, Bab II, dan Bab III yang sudah berupa naskah. Setiap subbab kerangka berisi enam jenis kotak. Kotak biru memuat isi wajib dari templat resmi. Kotak ungu memuat bobot rubrik. Kotak hijau memuat fakta proyek yang sudah diperiksa beserta sumbernya. Kotak cokelat memuat panduan menulis. Kotak merah memuat data yang masih harus dilengkapi.

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

Data yang diolah untuk Kecamatan Tikung mencakup citra Oktober 2017 sampai September 2026. Rentang ini memuat musim tanam yang berakhir pada tahun 2018 sampai 2026.

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

Studi ini dikerjakan oleh satu mahasiswa, sehingga mahasiswa memegang seluruh tahap pekerjaan, mulai dari pengambilan data sampai penyajian hasil. Topik proyek diusulkan oleh mahasiswa melalui proposal dalam skema Program Mahasiswa Berdampak. Dicoding Indonesia sebagai mitra kolaborator menyediakan materi Big Data dan Machine Learning yang menjadi dasar keterampilan teknis dalam proyek ini. @gambar-kedudukan menunjukkan kedudukan pekerjaan mahasiswa dalam alur studi.

#figure(
  {
    import "@preview/fletcher:0.5.8": diagram, edge, node
    set text(size: 9pt)
    diagram(
      node-stroke: 0.6pt,
      spacing: (1.2em, 1.6em),
      node((0, 0), align(center)[Data terbuka \ Sentinel-1, Sentinel-2, \ CHIRPS, Lahan Baku Sawah]),
      edge("-|>"),
      node((1, 0), align(center)[Alur data \ bronze, silver, gold], fill: luma(225)),
      edge("-|>"),
      node((2, 0), align(center)[Model prakiraan \ waktu panen], fill: luma(225)),
      edge("-|>"),
      node((3, 0), align(center)[Situs web dan \ data per desa], fill: luma(225)),
      edge("-|>"),
      node((4, 0), align(center)[Warga dan \ pemerintah desa]),
      node((1, 1), align(center)[Validasi dengan \ data BPS], fill: luma(225)),
      edge((1, 0), (1, 1), "-|>"),
    )
  },
  caption: [Kedudukan pekerjaan mahasiswa dalam alur studi. Kotak abu-abu adalah bagian yang dikerjakan mahasiswa.],
) <gambar-kedudukan>

Dalam rantai informasi pertanian, proyek ini berada di bawah statistik resmi. Badan Pusat Statistik mengukur luas panen padi setiap bulan melalui Survei Kerangka Sampel Area dan menyajikannya per kabupaten @bpslamongan2025padi. Proyek ini mengisi lapisan setelahnya, yaitu tahap tanam per desa yang diperbarui setiap bulan dari citra satelit. Hasil proyek dibandingkan dengan data BPS, sehingga proyek ini melengkapi statistik resmi dan tidak menggantikannya.

Kedudukan ini berbeda dari rencana proposal. Proposal menempatkan mahasiswa sebagai pengembang sistem bagi Satgas Pandu, dengan koordinasi melalui Kecamatan Tikung. Koordinasi tersebut tidak terlaksana selama masa studi, sehingga pengguna sasaran bergeser ke warga dan pemerintah desa di seluruh Kecamatan Tikung. Desa Jotosanur tetap termasuk dalam wilayah yang dipantau. @tabel-peran merinci pekerjaan mahasiswa pada setiap tahap.

#figure(
  table(
    columns: (auto, 1fr),
    stroke: 0.5pt,
    inset: 5pt,
    align: left,
    table.header([*Tahap*], [*Pekerjaan mahasiswa*]),
    [Pengambilan data], [Mengunduh citra Sentinel-1 dan Sentinel-2, curah hujan CHIRPS, peta Lahan Baku Sawah, dan batas desa],
    [Pengolahan], [Menyusun deret waktu lima harian per sel dan mendeteksi musim tanam],
    [Validasi], [Membandingkan luas dan waktu panen dengan data BPS dan KSA],
    [Pemodelan], [Melatih dan membandingkan model prakiraan waktu panen],
    [Penyajian], [Mengekspor data per desa dan membangun situs web],
    [Pengujian], [Menulis 60 uji otomatis untuk alur data dan model],
    [Otomatisasi], [Menyiapkan jadwal pengambilan data bulanan],
  ),
  caption: [Pekerjaan mahasiswa pada setiap tahap],
) <tabel-peran>

== Metodologi Penyelesaian Tugas

Masalah studi ini diuraikan menjadi enam tahap, yaitu pengambilan data, pengolahan data, validasi, pemodelan, penyajian, dan pengujian. Setiap tahap memakai konsep pada Bab II untuk menjelaskan keadaan sawah di Kecamatan Tikung.

=== Pengambilan Data

Unit analisis studi ini adalah sel persegi berukuran 100 meter, yaitu gabungan 10 × 10 piksel Sentinel-2. Sel hanya dipakai bila paling sedikit setengah luasnya berupa lahan pertanian menurut peta ESA WorldCover 2021 @Zanaga_2022. Dengan aturan ini, Kecamatan Tikung terbagi menjadi 4.954 sel. Setiap sel dimasukkan ke desa yang menutupi bagian terbesarnya. @tabel-sumber-data merangkum data yang diambil untuk setiap sel.

#figure(
  table(
    columns: (auto, 1fr, auto, auto),
    stroke: 0.5pt,
    inset: 5pt,
    align: left,
    table.header([*Data*], [*Sumber*], [*Resolusi*], [*Rentang*]),
    [Citra optik], [Copernicus Sentinel-2 Level-2A, ESA], [10 m], [Okt 2017 sampai Sep 2026],
    [Citra radar VV dan VH], [Copernicus Sentinel-1 RTC, ESA], [10 m], [Okt 2017 sampai Sep 2026],
    [Lahan pertanian], [ESA WorldCover 2021 @Zanaga_2022], [10 m], [2021],
    [Peta sawah], [Lahan Baku Sawah, Badan Informasi Geospasial], [Poligon], [Satu edisi],
    [Curah hujan bulanan], [CHIRPS @Funk_2015], [0,05°], [1981 sampai 2026],
    [Batas desa], [GADM versi 4.1], [Poligon], [Satu edisi],
  ),
  caption: [Sumber data yang dipakai],
) <tabel-sumber-data>

Semua data tersebut tersedia secara terbuka dan dibaca langsung dari server penyedia tanpa akun berbayar. Dari setiap citra Sentinel-2, sistem menghitung NDVI dan LSWI pada piksel yang tidak tertutup awan menurut klasifikasi citra. Dari setiap citra Sentinel-1, sistem menghitung rata-rata pantulan VV dan VH dalam desibel. Hasilnya disimpan sebagai data mentah dengan satu baris untuk setiap sel pada setiap tanggal citra.

=== Pengolahan Data

Data mentah memiliki tanggal yang tidak teratur dan banyak baris berawan. Oleh karena itu, setiap sel disusun ulang menjadi deret waktu dengan selang lima hari. Baris Sentinel-2 hanya dipakai bila paling sedikit 60% sel bebas awan. Penurunan NDVI pada satu tanggal saja juga dibuang karena biasanya berasal dari kabut yang lolos dari klasifikasi awan. Selisih pantulan antara lintasan satelit naik dan turun dihapus agar deret radar tidak bergerigi.

Celah data sampai 30 hari diisi dengan interpolasi linear, sedangkan celah yang lebih panjang dibiarkan kosong. Deret waktu kemudian dihaluskan dengan nilai tengah bergerak selebar 15 hari. Sel juga ditandai tergenang bila nilai LSWI lebih besar daripada NDVI, yang menunjukkan air di permukaan sawah.

Dari deret waktu yang bersih, musim tanam dideteksi dengan urutan fenologi pada subbab 2.1.1. Setiap puncak NDVI di atas 0,6 yang berjarak paling sedikit 60 hari dari puncak lain dianggap satu musim. Awal tumbuh adalah saat NDVI naik melewati 20% selisih antara nilai dasar dan puncak. Tanggal tanam diambil dari nilai VH terendah di sekitar awal tumbuh, karena sawah yang tergenang menurunkan pantulan radar @Manago_2020. Tanggal panen adalah saat NDVI turun melewati 50% selisih tersebut sesudah puncak.

Sebuah musim digolongkan sebagai padi bila VH saat penggenangan paling tinggi -17 desibel atau turun paling sedikit 1,5 desibel dari keadaan sebelum tanam. Ambang ini ditetapkan dari data tahun 2020. Bila satelit radar melintas kurang dari tiga kali pada masa penggenangan, status padi musim itu dicatat tidak diketahui. Luas sawah setiap sel dihitung dari porsi sel yang berada di dalam peta Lahan Baku Sawah. Terakhir, setiap sel diberi tahap tanam terkini pada tanggal data terakhir, yaitu ditanami, menjelang panen, bera, atau tertutup awan.

=== Validasi

Hasil pengolahan dibandingkan dengan dua jenis data resmi. Pertama, luas tanam satelit per desa pada tahun 2020 dan 2021 dibandingkan dengan luas panen per desa dari publikasi Kecamatan Tikung Dalam Angka @bpslamongan2021tikung @bpslamongan2022tikung. Tahun 2021 menjadi uji yang independen karena ambang deteksi padi ditetapkan dari data 2020. Kesesuaiannya diukur dengan koefisien korelasi Pearson dan rasio luas satelit terhadap luas BPS.

Kedua, waktu panen dibandingkan dengan luas panen padi bulanan Kabupaten Lamongan dari Survei Kerangka Sampel Area tahun 2020 sampai 2023 @bpslamongan2023ksa @bpslamongan2024ksa. Karena Tikung hanya satu dari 27 kecamatan, proyek ini membandingkan porsi panen per bulan. Ukurannya adalah korelasi porsi bulanan dan selisih porsi panen pada Januari sampai Mei.

=== Pemodelan Prakiraan Waktu Panen

Studi ini membuat dua prakiraan waktu panen untuk setiap sel. Prakiraan tanam dikeluarkan 20 hari sesudah awal tumbuh dan memperkirakan jumlah hari dari penggenangan sampai panen. Prakiraan puncak dikeluarkan saat NDVI mencapai puncak dan memperkirakan jumlah hari dari puncak sampai panen. Kedua prakiraan hanya memakai informasi yang sudah tersedia pada tanggal dikeluarkannya.

Fitur prakiraan tanam meliputi hari penggenangan dalam tahun, jarak penggenangan ke awal tumbuh, status padi, nilai VH, besar penurunan VH, NDVI dasar, jumlah lintasan radar, curah hujan, dan nama desa. Fitur prakiraan puncak meliputi hari puncak dalam tahun, nilai NDVI puncak, jarak dari penggenangan dan awal tumbuh ke puncak, status padi, curah hujan, dan nama desa. Model hanya dilatih pada musim yang awal tumbuhnya benar-benar teramati, karena celah awan pada musim lain membuat tanggalnya keliru.

Model utama adalah gradient boosting untuk nilai tengah, ditambah dua model kuantil untuk persentil ke-10 dan ke-90. Kedua model kuantil membentuk rentang 80%. Rentang ini kemudian dilebarkan dengan conformalized quantile regression @Romano_2019, memakai seperempat tahun pelatihan sebagai data kalibrasi. Pelebaran ini diperlukan karena musim dalam satu tahun berbagi cuaca yang sama, sehingga rentang dari data gabungan terlalu sempit untuk tahun baru.

Model dinilai dengan _cross-validation_ yang menahan satu tahun panen penuh sebagai data uji. Sebagai pembanding, dipakai perkiraan sederhana berupa lama musim median dari tahun pelatihan. Rancangan pembandingan mengikuti CY-Bench @Kallenberg_2026, yaitu perkiraan sederhana dibandingkan dengan Ridge, random forest, dan gradient boosting. Hiperparameter setiap model dicari dengan Optuna @Akiba_2019 sebanyak 10 percobaan, dengan tiga fold yang dibagi per tahun dan hanya di dalam tahun pelatihan.

Untuk musim yang masih berjalan, luas sawah setiap sel dibagi merata pada rentang 80% tanggal panennya. Hasilnya dijumlahkan per desa dan per minggu sebagai perkiraan luas panen mingguan. Prakiraan ini juga diuji ulang pada tanggal-tanggal di masa lalu. Pada uji ulang tersebut, model hanya dilatih dengan musim yang sudah panen sebelum tanggal itu.

=== Penyajian dan Otomatisasi

Hasil pengolahan diekspor menjadi berkas data per desa dan disimpan dalam basis data MongoDB. Berkas tersebut dibaca oleh situs web statis yang menampilkan kondisi sawah, kalender tanam, jadwal tanam per desa, dan perkiraan panen. Pengambilan citra dan curah hujan bulan sebelumnya dijadwalkan berjalan otomatis setiap tanggal 25.

=== Pengujian

Kebenaran alur data dan model diperiksa dengan 60 uji otomatis. Sebagian uji memakai deret waktu buatan yang tanggal tanam dan panennya sudah diketahui, sehingga hasil deteksi dapat dibandingkan dengan jawaban yang benar. Uji lain memastikan bahwa data dari tahun uji tidak pernah masuk ke data pelatihan.

== Pembelajaran Hal Baru

Pembelajaran selama studi ini disusun dengan model refleksi 4R, yaitu melaporkan kejadian, mengaitkannya dengan konsep, menjelaskan sebabnya, lalu menyusun ulang cara kerja @Ryan_2013. Empat pembelajaran utama dijelaskan pada sub-sub-bab di bawah ini.

=== Model Tidak Dapat Menggantikan Data Lokal

Pada awal studi, model prediksi hasil panen dicoba dengan data buatan karena data mitra belum tersedia. Model random forest pada data buatan tersebut hanya memberi nilai R² -0,10 pada data uji. Model ternyata hanya meniru rumus yang dipakai untuk membuat data. Model lain yang dilatih pada survei 44.299 lahan padi di Asia Selatan juga gagal, karena nilai R²-nya negatif di keenam wilayah uji.

Dalam materi pembelajaran mesin, kemampuan model untuk berlaku di data baru biasanya diuji dengan data dari sumber yang sama. Pengalaman ini menunjukkan bahwa model yang baik di satu wilayah belum tentu berlaku di wilayah lain. Sebabnya, sifat tanah Jotosanur berada di luar rentang data survei tersebut. Sebaliknya, rata-rata produktivitas desa dari data BPS sudah memberi galat hanya 3,6%. Karena itu, ketersediaan dan kecocokan data lokal kini diperiksa sebelum model dipilih.

=== Evaluasi Harus Mengikuti Urutan Waktu

Model prakiraan waktu panen semula dinilai dengan menahan satu tahun penuh sebagai data uji dan memberi galat 11,8 hari. Ketika prakiraan diuji ulang seperti dipakai pada tanggal sebenarnya, hasilnya lebih buruk. Prakiraan tanam yang dikeluarkan pada Januari meleset 21 sampai 41 hari, sedangkan yang dikeluarkan pada Juni meleset 11 sampai 20 hari.

Perbedaan ini muncul karena penilaian awal hanya memakai musim yang belakangan terbukti andal. Padahal, pada saat prakiraan dikeluarkan, informasi itu belum tersedia. Hal tersebut sejalan dengan rancangan CY-Bench yang menahan tahun penuh dan mencari hiperparameter hanya di dalam tahun pelatihan @Kallenberg_2026. Sejak itu, perkiraan panen mingguan juga diuji ulang dengan data yang dipotong pada tanggal prakiraan.

=== Citra Satelit Memiliki Celah

Teori pada Bab II menyebut bahwa radar dapat menembus awan. Dalam praktik, ketersediaan citra tetap menjadi kendala. Pada November sampai Februari, hanya 4 sampai 9 citra Sentinel-2 per bulan yang jernih selama sembilan tahun, dibandingkan dengan sampai 67 citra pada Juli sampai September. Lintasan Sentinel-1 di atas Tikung juga turun dari 53 sampai 57 kali per tahun menjadi 24 kali pada 2023.

Akibatnya, awal musim hujan sering tidak terlihat, dan status padi pada tahun 2022 dan 2023 sebagian tidak diketahui. Celah ini tidak bisa diisi dengan menebak. Oleh karena itu, musim dengan data terlalu sedikit ditandai sebagai tidak diketahui, dan tidak lagi dianggap bukan padi.

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
