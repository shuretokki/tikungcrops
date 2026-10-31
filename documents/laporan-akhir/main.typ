// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: CC-BY-4.0

#import "@preview/jilid:0.2.0": appendix, frontmatter, jilid, signature, signatures

#show: jilid.with(
  title: [Laporan Akhir Program Mahasiswa Berdampak],
  kind: [Studi Independen],
  cover: (kind-pos: "bottom", details: (size: 12pt), title: (size: 12pt), kind: (size: 12pt)),
  cover-details: ((upper()[Pemantauan Musim Tanam Padi Berbasis Citra Satelit dan Machine Learning di Kecamatan Tikung, Kabupaten Lamongan],[]),([MITRA KOLABORATOR:], [DICODING INDONESIA]),),
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
    columns: (auto, auto),
    align: (horizon + left, horizon + left),
    stroke: 0.2pt + luma(160),
    inset: (x: 6pt, y: 6pt),
    [*Judul Kegiatan*], [Pemantauan Musim Tanam Padi Berbasis Citra Satelit dan Machine Learning di Kecamatan Tikung, Kabupaten Lamongan],
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

#include "bab1.typ"

#include "bab2.typ"

= Metode

== Waktu dan Tempat Pelaksanaan

Studi independen ini berlangsung dari Agustus sampai Desember 2026 sesuai jadwal Program Mahasiswa Berdampak. Laporan ini disusun pada akhir Oktober 2026, sehingga hasil yang dilaporkan mencakup pekerjaan sampai saat itu. Pekerjaan sesudah tanggal tersebut dicatat sebagai rencana tindak lanjut pada Bab VI.

Seluruh kegiatan dilaksanakan secara daring. Data citra satelit, curah hujan, dan peta sawah diambil dari katalog data terbuka, sehingga studi ini tidak memerlukan pengukuran lapangan. Pengolahan data, pemodelan, dan pengembangan situs dikerjakan secara mandiri tanpa server berbayar.

Wilayah kajian utama adalah Kecamatan Tikung, Kabupaten Lamongan, Jawa Timur. Wilayah ini terletak antara 112,37° dan 112,45° Bujur Timur serta antara 7,12° dan 7,25° Lintang Selatan. Kecamatan Tikung terdiri atas tiga belas desa, yaitu Bakalanpule, Balongwangi, Botoputih, Dukuhagung, Guminingrejo, Jatirejo, Jotosanur, Kelorarum, Pengumbulanadi, Soko, Takeranklating, Tambakrigadung, dan Wonokromo. Luas sawah yang dipantau di wilayah tersebut berada di sekitar 4.420 hektare.

Data yang diolah untuk Kecamatan Tikung mencakup citra Oktober 2017 sampai September 2026. Rentang ini memuat musim tanam yang berakhir pada tahun 2018 sampai 2026.

#figure(
  table(
    columns: (auto, 1fr),
    stroke: none,
    inset: 6pt,
    align: horizon + center,
    table.hline(stroke: 1.2pt),
    table.header([*Aspek*], [*Keterangan*]),
    table.hline(stroke: 0.6pt),
    [Waktu program], [Agustus s.d. Desember 2026],
    [Bentuk kegiatan], [Daring, tanpa pengukuran lapangan],
    [Wilayah utama], [Kecamatan Tikung, 13 desa, sekitar 4.420 ha sawah],
    [Rentang data Tikung], [Oktober 2017 s.d. September 2026],
    // [Wilayah perluasan], [Kabupaten Lamongan, 27 kecamatan, citra September 2024 sampai September 2026],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Ringkasan waktu dan tempat pelaksanaan],
) <tabel-waktu-tempat>

#perlu[
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
    stroke: none,
    inset: 6pt,
    align: horizon + center,
    table.hline(stroke: 1.2pt),
    table.header([*Tahap*], [*Pekerjaan mahasiswa*]),
    table.hline(stroke: 0.6pt),
    [Pengambilan data], [Mengunduh citra Sentinel-1 dan Sentinel-2, curah hujan CHIRPS, peta Lahan Baku Sawah, dan batas desa],
    [Pengolahan], [Menyusun deret waktu lima harian per sel dan mendeteksi musim tanam],
    [Validasi], [Membandingkan luas dan waktu panen dengan data BPS dan KSA],
    [Pemodelan], [Melatih dan membandingkan model prakiraan waktu panen],
    [Penyajian], [Mengekspor data per desa dan membangun situs web],
    [Pengujian], [Menulis 64 uji otomatis untuk alur data dan model],
    [Otomatisasi], [Menyiapkan jadwal pengambilan data bulanan],
    table.hline(stroke: 0.6pt),
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
    stroke: none,
    inset: 6pt,
    align: horizon + center,
    table.hline(stroke: 1.2pt),
    table.header([*Data*], [*Sumber*], [*Resolusi*], [*Rentang*]),
    table.hline(stroke: 0.6pt),
    [Citra optik], [Copernicus Sentinel-2 Level-2A, ESA], [10 m], [Okt 2017 s.d. Sep 2026],
    [Citra radar VV dan VH], [Copernicus Sentinel-1 RTC, ESA], [10 m], [Okt 2017 s.d. Sep 2026],
    [Lahan pertanian], [ESA WorldCover 2021 @Zanaga_2022], [10 m], [2021],
    [Peta sawah], [Lahan Baku Sawah, Badan Informasi Geospasial], [Poligon], [Satu edisi],
    [Curah hujan bulanan], [CHIRPS @Funk_2015], [0,05°], [1981 s.d. 2026],
    [Batas desa], [GADM versi 4.1], [Poligon], [Satu edisi],
    table.hline(stroke: 0.6pt),
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

Model utama adalah gradient boosting untuk nilai tengah, ditambah dua model kuantil untuk persentil ke-10 dan ke-90. Kedua model kuantil membentuk rentang 80%. Rentang ini kemudian dilebarkan dengan conformalized quantile regression @Romano_2019, memakai seperempat tahun pelatihan sebagai data kalibrasi. Pelebaran tersebut diperlukan karena musim dalam satu tahun berbagi cuaca yang sama, sehingga rentang dari data gabungan terlalu sempit untuk tahun baru.

Model dinilai dengan validasi silang yang menahan satu tahun panen penuh sebagai data uji. Sebagai pembanding, dipakai perkiraan sederhana berupa lama musim median dari tahun pelatihan. Rancangan pembandingan mengikuti CY-Bench @Kallenberg_2026, yaitu perkiraan sederhana dibandingkan dengan Ridge, random forest, dan gradient boosting. Hiperparameter setiap model dicari dengan Optuna @Akiba_2019 sebanyak 10 percobaan, dengan tiga fold yang dibagi per tahun dan hanya di dalam tahun pelatihan.

Untuk musim yang masih berjalan, luas sawah setiap sel dibagi merata pada rentang 80% tanggal panennya. Hasilnya dijumlahkan per desa dan per minggu sebagai perkiraan luas panen mingguan. Prakiraan tersebut juga diuji ulang pada tanggal-tanggal di masa lalu. Pada uji ulang tersebut, model hanya dilatih dengan musim yang sudah panen sebelum tanggal itu.

=== Penyajian dan Otomatisasi

Hasil pengolahan diekspor menjadi berkas data per desa dan disimpan dalam basis data MongoDB. Berkas tersebut dibaca oleh situs web statis yang menampilkan kondisi sawah, kalender tanam, jadwal tanam per desa, dan perkiraan panen. Alur pengambilan citra dan curah hujan bulan sebelumnya setiap tanggal 25 sudah disiapkan, tetapi belum diaktifkan.

=== Pengujian

Kebenaran alur data dan model diperiksa dengan 64 uji otomatis. Sebagian uji memakai deret waktu buatan yang tanggal tanam dan panennya sudah diketahui, sehingga hasil deteksi dapat dibandingkan dengan jawaban yang benar. Uji lain memastikan bahwa data dari tahun uji tidak pernah masuk ke data pelatihan.

== Pembelajaran Hal Baru

Pembelajaran selama studi ini disusun dengan model refleksi 4R, yaitu melaporkan kejadian, mengaitkannya dengan konsep, menjelaskan sebabnya, lalu menyusun ulang cara kerja @Ryan_2013. Empat pembelajaran utama dijelaskan pada sub-sub-bab di bawah ini.

=== Model Tidak Dapat Menggantikan Data Lokal

Pada awal studi, model prediksi hasil panen dicoba dengan data buatan karena data mitra belum tersedia. Model random forest pada data buatan tersebut hanya memberi nilai R² -0,10 pada data uji. Model ternyata hanya meniru rumus yang dipakai untuk membuat data. Model lain yang dilatih pada survei 44.299 lahan padi di Asia Selatan juga gagal, karena nilai R²-nya negatif di keenam wilayah uji.

Dalam materi pembelajaran mesin, kemampuan model untuk berlaku di data baru biasanya diuji dengan data dari sumber yang sama. Pengalaman tersebut menunjukkan bahwa model yang baik di satu wilayah belum tentu berlaku di wilayah lain. Sebabnya, sifat tanah Jotosanur berada di luar rentang data survei tersebut. Sebaliknya, rata-rata produktivitas desa dari data BPS sudah memberi galat hanya 3,6%. Karena itu, ketersediaan dan kecocokan data lokal kini diperiksa sebelum model dipilih.

=== Evaluasi Harus Mengikuti Urutan Waktu

Model prakiraan waktu panen semula dinilai dengan menahan satu tahun penuh sebagai data uji dan memberi galat 11,8 hari. Ketika prakiraan diuji ulang seperti dipakai pada tanggal sebenarnya, hasilnya lebih buruk. Prakiraan tanam yang dikeluarkan pada Januari meleset 21 sampai 41 hari, sedangkan yang dikeluarkan pada Juni meleset 11 sampai 20 hari.

Perbedaan ini muncul karena penilaian awal hanya memakai musim yang belakangan terbukti andal. Padahal, pada saat prakiraan dikeluarkan, informasi itu belum tersedia. Hal tersebut sejalan dengan rancangan CY-Bench yang menahan tahun penuh dan mencari hiperparameter hanya di dalam tahun pelatihan @Kallenberg_2026. Sejak itu, perkiraan panen mingguan juga diuji ulang dengan data yang dipotong pada tanggal prakiraan.

=== Citra Satelit Memiliki Celah

Teori pada Bab II menyebut bahwa radar dapat menembus awan. Dalam praktik, ketersediaan citra tetap menjadi kendala. Pada November sampai Februari, hanya 4 sampai 9 citra Sentinel-2 per bulan yang jernih selama sembilan tahun, dibandingkan dengan sampai 67 citra pada Juli sampai September. Lintasan Sentinel-1 di atas Tikung juga turun dari 53 sampai 57 kali per tahun menjadi 24 kali pada 2023.

Akibatnya, awal musim hujan sering tidak terlihat, dan status padi pada tahun 2022 dan 2023 sebagian tidak diketahui. Celah tersebut tidak bisa diisi dengan menebak. Oleh karena itu, musim dengan data terlalu sedikit ditandai sebagai tidak diketahui, dan tidak lagi dianggap bukan padi.

#include "bab4.typ"

= Korelasi Program Studi Independen dengan Konversi Mata Kuliah

== Kegiatan Studi Independen yang Dikembangkan

Studi independen ini difokuskan pada pengembangan sistem pemantauan musim tanam padi berbasis citra satelit. Kegiatan dijalankan bersama mitra kolaborator Dicoding Indonesia, dengan wilayah sasaran Kecamatan Tikung, termasuk Desa Jotosanur. Masalah nyata yang dijawab adalah belum tersedianya informasi waktu tanam dan waktu panen per desa yang diperbarui secara berkala. Sistem ini dikembangkan untuk membantu petani, buruh tani, penebas, dan pemerintah desa merencanakan kegiatan pada setiap musim tanam.

Tujuan pengembangan studi ini adalah sebagai berikut.
- Menerapkan materi Big Data dan Machine Learning dari Dicoding pada data nyata berskala besar.
- Menghasilkan jadwal tanam dan prakiraan panen per desa yang dapat dibaca warga.
- Menyediakan alur data terbuka yang dapat dijalankan ulang untuk kecamatan lain.
- Menjadi dasar konversi capaian pembelajaran empat mata kuliah.

Pengembangan dijalankan dalam lima langkah. Pertama, kebutuhan diidentifikasi dari rencana awal untuk program Kampung Pandu Sakti. Karena data program tidak tersedia, sasaran dialihkan ke jadwal tanam seluruh desa di Kecamatan Tikung. Kedua, solusi dirancang sebagai alur data bertahap, model prakiraan, dan situs web statis. Ketiga, hasil divalidasi dengan data BPS per desa dan data Survei Kerangka Sampel Area. Keempat, situs dibangun sebagai situs statis dan disiapkan untuk publikasi. Kelima, hasil dievaluasi dan didokumentasikan dalam laporan ini.

@tabel-mingguan merangkum kegiatan per minggu menurut logbook MELISA. Durasi dihitung dari estimasi resmi kelas Dicoding, jadwal sesi wajib, dan catatan sesi kerja proyek.

#figure(
  text(size: 10pt)[
    #table(
      columns: (auto, auto, 1fr, auto, 1fr, auto),
      stroke: none,
      inset: 5pt,
      align: (left, left, left, center, left, left),
      table.hline(stroke: 1.2pt),
      table.header([*Minggu*], [*Posisi*], [*Topik*], [*Jam*], [*Target*], [*Metode*]),
      table.hline(stroke: 0.6pt),
      [3--9 Agu], [Peserta kelas], [Pengenalan kecerdasan buatan], [1,5], [Memahami posisi AI, ML, dan DL], [Kelas daring],
      [10--16 Agu], [Peserta kelas], [Data untuk kecerdasan buatan], [1,4], [Memahami peran data dalam AI], [Kelas daring],
      [17--23 Agu], [Peserta kelas], [Dasar dan logika pemrograman], [15,0], [Menyelesaikan dua kelas matrikulasi], [Kelas daring],
      [24--30 Agu], [Peserta kelas], [Orientasi Asah, Git, Kiro, prompt engineering, cloud AWS, pengantar ML dan DL], [62,1], [Menyelesaikan kelas wajib awal], [Kelas daring, sesi wajib],
      [31 Agu--6 Sep], [Peserta kelas], [Deep learning, ujian Dasar AI, dasar Python], [33,1], [Lulus Belajar Dasar AI], [Kelas daring, ILT],
      [7--13 Sep], [Peserta kelas, pengembang proyek], [Python lanjutan, ML pemula, kebutuhan desa mitra], [38,6], [Lulus kelas Python, memetakan kebutuhan mitra], [Kelas daring, ILT, kerja proyek],
      [14--20 Sep], [Peserta kelas, pengembang proyek], [ML pemula, riset data resmi, proposal], [20,9], [Proposal final], [Kelas daring, ILT, kerja proyek],
      [21--27 Sep], [Peserta kelas, pengembang proyek], [Pembersihan data, alur deteksi musim tanam, validasi dan prakiraan panen], [28,6], [Alur data dan model pertama berjalan], [Kelas daring, ILT, kerja proyek],
      table.hline(stroke: 0.6pt),
    )
  ],
  caption: [Kegiatan mingguan menurut logbook MELISA, Agustus sampai September 2026],
) <tabel-mingguan>

Bagi mitra dan masyarakat, kegiatan ini menghasilkan data musim tanam tiga belas desa sejak 2017 yang sebelumnya tidak tersedia. Dampak tersebut belum sampai ke warga karena situs belum dipublikasikan. Bagi mahasiswa, kegiatan ini memberi pengalaman membangun sistem data dari pengambilan citra sampai penyajian, termasuk menguji hasilnya dengan data resmi.

== Relevansi dengan Mata Kuliah Konversi

@tabel-konversi menunjukkan hubungan antara kegiatan studi independen dan mata kuliah yang dikonversi. Seluruh mata kuliah tersebut berjumlah sepuluh SKS.

#figure(
  table(
    columns: (auto, auto, 1fr),
    stroke: none,
    inset: 6pt,
    align: (left, center, left),
    table.hline(stroke: 1.2pt),
    table.header([*Mata kuliah*], [*SKS*], [*Kegiatan yang relevan*]),
    table.hline(stroke: 0.6pt),
    [Perencanaan Program], [2], [Penyusunan proposal, rencana delapan minggu, dan papan rencana kerja yang diperbarui selama studi],
    [Big Data], [3], [Alur pengolahan bertahap untuk 4.954 sel Tikung dan 109.504 sel di 27 kecamatan Lamongan, pemrosesan per kelompok sel agar sekitar 49 juta baris data muat dalam memori, penyimpanan dalam basis data NoSQL MongoDB, serta visualisasi di situs web],
    [Machine Learning], [3], [Model prakiraan waktu panen, dua tahap perbandingan model dengan dan tanpa penyetelan memakai validasi per tahun, serta rentang prakiraan 80%],
    [Evaluasi Program], [2], [Validasi dengan data BPS per desa, data DKPP per kecamatan, dan Survei Kerangka Sampel Area, uji ulang prakiraan, serta 64 uji otomatis],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Relevansi kegiatan dengan mata kuliah konversi],
) <tabel-konversi>

Kegiatan Big Data memenuhi CPMK tentang alur pemrosesan data, basis data NoSQL, dan visualisasi hasil. CPMK tentang Hadoop dan Spark baru terpenuhi sebagian, karena pengolahan dijalankan dengan pustaka Polars tanpa klaster Hadoop atau Spark. Kegiatan Machine Learning memenuhi ketiga CPMK, yaitu memodelkan masalah, menjelaskan metode, dan mengimplementasikannya dengan bahasa pemrograman.

= Rencana Tindak Lanjut dan Rekomendasi

== Rencana Tindak Lanjut

Rencana tindak lanjut disusun agar hasil studi dapat dipakai warga dan terus diperbarui. Setiap rencana dilengkapi dengan pelaku, waktu, dan ukuran keberhasilan.

=== Pengembangan Produk

Mahasiswa akan memublikasikan situs pada November 2026 sebagai situs statis tanpa biaya hosting. Keberhasilannya diukur dari alamat situs yang dapat dibuka publik. Sebelum puncak tanam musim hujan pada Desember, deteksi awal musim akan diperbaiki agar lebih tahan terhadap awan. Ukurannya adalah galat prakiraan Januari pada uji ulang yang lebih kecil dari 21 sampai 41 hari. Selain itu, hasil untuk 27 kecamatan di Kabupaten Lamongan akan diselesaikan dan dibandingkan dengan data luas panen DKPP 2021.

=== Pelatihan dan Transfer Pengetahuan

Mahasiswa akan menghubungi Kecamatan Tikung untuk meminta kontak resmi Pemerintah Desa Jotosanur. Setelah itu, ringkasan satu halaman dan demo daring akan diberikan kepada perangkat desa. Keberhasilannya diukur dari daftar hadir demo dan masukan tertulis dari perangkat desa. Panduan membaca situs juga akan ditulis dalam bahasa sehari-hari.

=== Monitoring dan Evaluasi Berkala

Alur pengambilan citra bulanan pada setiap tanggal 25 sudah disiapkan dan akan diaktifkan bersama publikasi situs. Hasil setiap musim akan dibandingkan dengan data Survei Kerangka Sampel Area dan edisi Kecamatan Tikung Dalam Angka yang baru. Masukan warga dari demo akan dipakai untuk menilai bagian situs yang perlu diubah.

=== Pendanaan atau Kerja Sama

Pembaruan bulanan membutuhkan tempat penyimpanan riwayat citra, karena deret waktu dibangun dari seluruh bulan sebelumnya. Layanan penyimpanan gratis untuk data terbuka akan dipilih agar tidak menimbulkan biaya. Kerja sama dengan penyuluh pertanian juga perlu dijajaki untuk memperoleh catatan tanggal tanam dari petani.

== Rekomendasi

=== Rekomendasi Teknis

Citra optik dan radar sebaiknya digabungkan lebih erat untuk mengatasi awan pada musim hujan. Ukuran sel yang lebih kecil juga perlu diuji, karena satu sel 100 meter dapat mencakup beberapa petak dengan tanggal tanam berbeda. Selain itu, tanggal tanam dari catatan petani dibutuhkan untuk menguji hasil deteksi secara langsung.

=== Rekomendasi Manajerial dan Operasional

Ketersediaan data mitra sebaiknya dipastikan pada minggu pertama, sebelum ruang lingkup proyek ditetapkan. Komunikasi dengan pemerintah desa juga perlu dimulai sejak awal, sejajar dengan pekerjaan teknis. Dengan cara itu, uji coba bersama pengguna dapat dilakukan sebelum masa studi berakhir.

=== Rekomendasi Kebijakan atau Strategis

Di antara edisi 2022 sampai 2026, tabel luas panen per desa hanya tersedia pada Kecamatan Tikung Dalam Angka 2022. Edisi 2023 sampai 2026 hanya memuat total kecamatan. Penyajian kembali tabel per desa akan memudahkan validasi pemantauan berbasis satelit seperti dalam studi ini.

=== Rekomendasi Penelitian Lanjutan

Penelitian lanjutan perlu menguji apakah alur ini berlaku di wilayah dengan ukuran petak, pola hujan, dan jenis tanaman yang berbeda. Prakiraan waktu panen pada musim hujan juga perlu diteliti lebih lanjut, karena galatnya masih jauh lebih besar daripada musim kemarau.

= Penutup

== Kesimpulan

Pertama, alur pengolahan data otomatis berhasil mengubah citra Sentinel-1 dan Sentinel-2 sejak Oktober 2017 menjadi tahap tanam untuk 4.954 sel di tiga belas desa. Dari hasil tersebut, musim tanam 1 di Kecamatan Tikung biasanya dimulai pada November dan paling banyak dipanen pada April. Puncak tanam antardesa berbeda sampai lima minggu.

Kedua, luas padi dari satelit sesuai dengan luas panen BPS per desa. Rasio luasnya 1,01 pada 2020 dan 2021, dengan korelasi 0,88 pada tahun 2021 yang tidak dipakai untuk penyetelan. Waktu panen juga sesuai dengan data bulanan Survei Kerangka Sampel Area, kecuali panen Maret yang sering terlambat terdeteksi.

Ketiga, waktu panen dapat diprakirakan dengan galat rata-rata 11,9 hari dari tanggal tanam, lebih kecil dari 15,2 hari pada perkiraan sederhana. Hasil ini disajikan dalam situs web dengan tiga halaman yang sudah berfungsi. Akan tetapi, situs tersebut belum dipublikasikan dan belum diuji bersama warga.

== Refleksi Akhir

Refleksi ini memakai model 4R @Ryan_2013 untuk satu pengalaman penting. Pada akhir masa studi, alur data, model, dan situs sudah berfungsi. Namun, komunikasi dengan pemerintah Desa Jotosanur baru disiapkan, sehingga situs belum pernah dicoba oleh pengguna sasarannya.

Pengalaman ini menunjukkan bahwa kemajuan teknis tidak sama dengan dampak. Pedoman program menilai manfaat bagi mitra dan masyarakat, sedangkan sebagian besar waktu studi dipakai untuk memperbaiki data dan menguji ketepatan model. Validasi dengan data BPS menjawab pertanyaan apakah hasil satelit benar, tetapi tidak menjawab apakah hasil itu berguna bagi warga.

Penyebabnya adalah urutan kerja yang menunda keterlibatan pengguna sampai produk dianggap siap. Pada proyek berikutnya, mahasiswa akan menghubungi mitra pada minggu pertama, memastikan ketersediaan data, dan menyepakati waktu uji coba. Versi sederhana produk akan ditunjukkan lebih awal, lalu diperbaiki berdasarkan masukan pengguna.

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
