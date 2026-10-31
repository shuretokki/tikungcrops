// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: CC-BY-4.0

= Hasil dan Pembahasan

== Hasil

Bagian ini menyajikan hasil studi tanpa tafsiran. Tafsiran dan perbandingan dengan penelitian lain dibahas pada subbab 4.2.

=== Luaran yang Dihasilkan

Studi ini menghasilkan tiga luaran utama. Luaran pertama adalah situs web Tanam Padi Lamongan dengan tiga halaman yang sudah berfungsi, yaitu Beranda, Ringkasan, dan Metode. Luaran kedua adalah alur pengolahan data yang berjalan dari pengambilan citra sampai ekspor data per desa. Luaran ketiga adalah data musim tanam untuk tiga belas desa sejak Oktober 2017.

Halaman Beranda menampilkan peta tahap tanam, kalender tanam, curah hujan, dan daftar desa. Halaman Ringkasan menampilkan kondisi sawah, jadwal tanam per desa, perkiraan panen delapan minggu ke depan, dan tabel semua desa. Halaman Metode menjelaskan sumber data, cara kerja, ketepatan, dan keterbatasan. Halaman Perbandingan, Data, dan rincian per desa masih berupa kerangka. Situs ini masih dijalankan di komputer mahasiswa dan belum dipublikasikan.

#figure(
  image("gambar/peta-beranda.png", width: 70%),
  caption: [Peta tahap tanam per sel di Kecamatan Tikung pada halaman Beranda menggunakan OpenFreeMap, © OpenStreetMap contributors.],
) <gambar-peta>

#figure(
  image("gambar/cari-desamu.png", width: 100%),
  caption: [Daftar desa dengan peta letak, luas sawah, dan tahap tanam terkini],
) <gambar-desa>

=== Kondisi Sawah Terkini

Data terakhir yang diolah berasal dari 29 September 2026. Pada tanggal itu, sekitar 4.216 hektare atau 95% sawah di Kecamatan Tikung sedang bera. Sawah yang sedang ditanami sekitar 74 hektare, sawah yang menjelang panen sekitar 22 hektare, dan sekitar 108 hektare tertutup awan. Perkiraan panen untuk delapan minggu berikutnya hanya muncul di dua desa. Desa Jotosanur diperkirakan memanen sekitar 10 hektare dengan puncak pada minggu 12 Oktober 2026, sedangkan Desa Guminingrejo sekitar 1 hektare.

=== Pola Musim Tanam

@gambar-kalender menunjukkan pola musim tanam rata-rata di Kecamatan Tikung. Musim tanam 1 biasanya mulai pada November, mencapai puncak tanam pada Desember, dan dipanen paling banyak pada April. Musim tanam 2 mulai pada Maret dan dipanen paling banyak pada Juli. Musim tanam 3 berlangsung pada Oktober sampai Januari, tetapi tidak muncul setiap tahun.

#figure(
  image("gambar/kalender-tanam.png", width: 100%),
  caption: [Kalender tanam rata-rata Kecamatan Tikung sejak 2017],
) <gambar-kalender>

Waktu tanam berbeda antardesa. Puncak tanam musim utama paling awal terjadi di Desa Takeranklating sekitar 20 November dan paling akhir di Desa Tambakrigadung sekitar 24 Desember. Puncak panennya berkisar antara 19 Maret dan 10 Mei. @gambar-jadwal menampilkan urutan tersebut untuk ketiga belas desa.

#figure(
  image("gambar/jadwal-per-desa.png", width: 100%),
  caption: [Jadwal puncak tanam dan puncak panen musim tanam 1 per desa],
) <gambar-jadwal>

Sawah di Kecamatan Tikung tercatat ditanami 2,02 sampai 2,85 kali per tahun pada 2019 sampai 2025. Angka ini mencakup padi dan tanaman lain. Curah hujan bulanan per desa juga ditampilkan bersama nilai normalnya, seperti pada @gambar-hujan.

#figure(
  image("gambar/hujan-bulanan.png", width: 100%),
  caption: [Curah hujan dua belas bulan terakhir dibandingkan dengan nilai normal 1991 s.d. 2020],
) <gambar-hujan>

=== Kesesuaian dengan Data BPS

@tabel-validasi merangkum perbandingan luas dari satelit dengan luas panen BPS per desa. Untuk padi, rasio luas satelit terhadap luas BPS hampir tepat satu pada kedua tahun. Korelasi padi naik dari 0,77 pada 2020 menjadi 0,88 pada 2021.

#figure(
  table(
    columns: (auto, auto, auto, auto, auto),
    stroke: none,
    inset: 6pt,
    align: horizon + center, // (horizon + left, left, right, right, right),
    table.hline(stroke: 1.2pt),
    table.header([*Tahun*], [*Tanaman*], [*Korelasi*], [*Satelit / BPS*], [*Selisih median per desa*]),
    table.hline(stroke: 0.6pt),
    [2020], [Padi], [0,77], [1,01], [23%],
    [2020], [Semua tanaman], [0,91], [1,14], [26%],
    [2021], [Padi], [0,88], [1,01], [17%],
    [2021], [Semua tanaman], [0,89], [1,46], [33%],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Kesesuaian luas dari satelit dengan luas panen BPS per desa, 13 desa],
) <tabel-validasi>

#figure(
  image("gambar/validasi-bps.png", width: 100%),
  caption: [Ringkasan validasi dan sebaran luas padi per desa tahun 2021 pada halaman Metode],
) <gambar-validasi>

Waktu panen satelit juga dibandingkan dengan luas panen bulanan Kabupaten Lamongan dari Survei Kerangka Sampel Area. Porsi panen pada Januari sampai Mei hanya berselisih 0,01 sampai 0,08 dari data resmi pada 2020 sampai 2023. Meskipun demikian, korelasi porsi bulanan turun dari 0,61 pada 2020 menjadi 0,05 pada 2023. Data resmi mencatat 20 sampai 29% panen tahunan pada Maret, sedangkan satelit hanya mencatat 1 sampai 11% pada Maret 2021 sampai 2023.

=== Kinerja Prakiraan Waktu Panen

@tabel-model membandingkan galat rata-rata empat model pada sembilan tahun uji. Gradient boosting memberi galat terkecil untuk kedua prakiraan. Di antara empat model tersebut, gradient boosting menjadi yang terbaik pada enam dari sembilan tahun untuk prakiraan tanam dan pada empat dari sembilan tahun untuk prakiraan puncak.

#figure(
  table(
    columns: (auto, auto, auto, auto, auto),
    stroke: none,
    inset: 6pt,
    align: horizon + center, // (left, right, right, right, right),
    table.hline(stroke: 1.2pt),
    table.header([*Prakiraan*], [*Perkiraan median*], [*Ridge*], [*Random forest*], [*Gradient boosting*]),
    table.hline(stroke: 0.6pt),
    [Dari tanam], [15,2 hari], [13,7 hari], [12,1 hari], [11,9 hari],
    [Dari puncak], [10,1 hari], [9,8 hari], [9,7 hari], [9,3 hari],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Galat rata-rata prakiraan tanggal panen pada sembilan tahun uji],
) <tabel-model>

Pengujian kedua membandingkan sembilan model dengan pengaturan bawaan pada sembilan tahun uji yang sama (@tabel-model-bawaan). Untuk prakiraan dari tanam, gradient boosting tetap memberi galat terkecil, yaitu 11,7 hari. Enam model lain, termasuk tiga pustaka boosting serta model gabungan voting dan stacking, berada pada 12,0 sampai 12,2 hari. Regresi linear memberi galat 13,8 hari, sedangkan gradient boosting tanpa interaksi antarfitur memberi galat 12,8 hari. Untuk prakiraan dari puncak, semua model berada pada 9,2 sampai 10,3 hari, dekat dengan perkiraan median sebesar 10,1 hari. Oleh karena itu, model gradient boosting yang sudah dipakai di situs dipertahankan.

#figure(
  table(
    columns: (auto, auto, auto),
    stroke: none,
    inset: 6pt,
    align: (left, center, center),
    table.hline(stroke: 1.2pt),
    table.header([*Model*], [*Dari tanam*], [*Dari puncak*]),
    table.hline(stroke: 0.6pt),
    [Gradient boosting], [11,7 hari], [9,4 hari],
    [XGBoost], [12,0 hari], [10,0 hari],
    [Voting], [12,0 hari], [9,3 hari],
    [LightGBM], [12,1 hari], [9,4 hari],
    [Spline], [12,1 hari], [9,2 hari],
    [CatBoost], [12,2 hari], [9,3 hari],
    [Stacking], [12,2 hari], [9,3 hari],
    [Gradient boosting tanpa interaksi], [12,8 hari], [10,3 hari],
    [Regresi linear], [13,8 hari], [9,7 hari],
    [Perkiraan median], [15,2 hari], [10,1 hari],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Galat rata-rata sembilan model dengan pengaturan bawaan pada sembilan tahun uji],
) <tabel-model-bawaan>

Rentang 80% dari model mencakup tanggal panen sebenarnya pada 72 sampai 73% musim. Hasil uji ulang pada tanggal-tanggal di masa lalu dirangkum pada @tabel-ujiulang. Prakiraan yang dikeluarkan pada Juni jauh lebih tepat daripada prakiraan yang dikeluarkan pada Januari.

#figure(
  table(
    columns: (auto, 1fr, 1fr, 1fr),
    stroke: none,
    inset: 6pt,
    align: horizon + center,
    table.hline(stroke: 1.2pt),
    table.header([*Tanggal prakiraan*], [*Galat prakiraan tanam*], [*Galat prakiraan puncak*], [*Galat tanggal median per desa*]),
    table.hline(stroke: 0.6pt),
    [Juni 2022, 2024, 2025], [11 s.d. 20 hari], [9 s.d. 13 hari], [4 s.d. 14 hari],
    [Januari 2022, 2024, 2025], [21 s.d. 41 hari], [40 s.d. 47 hari], [14 s.d. 37 hari],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Galat prakiraan pada uji ulang dengan data yang dipotong pada tanggal prakiraan],
) <tabel-ujiulang>

=== Capaian Dibandingkan dengan Rencana

@tabel-capaian membandingkan target proposal dengan hasil yang dicapai sampai akhir Oktober 2026.

#figure(
  table(
    columns: (1fr, 1fr, auto),
    stroke: none,
    inset: 6pt,
    align: horizon + center,
    table.hline(stroke: 1.2pt),
    table.header([*Target proposal*], [*Realisasi*], [*Status*]),
    table.hline(stroke: 0.6pt),
    [Dashboard pencatatan panen, ternak, dan distribusi], [Situs pemantauan tanam dengan tiga halaman berfungsi], [Diganti],
    [Prediksi hasil panen dengan MAPE di bawah 20%], [Prakiraan waktu panen dengan galat 11,9 hari, lebih kecil dari 15,2 hari], [Diganti, tercapai],
    [Panduan operasional sistem], [Halaman Metode di situs], [Sebagian],
    [Kanal pelaporan WhatsApp], [Tidak dikerjakan], [Tidak tercapai],
    [Tidak direncanakan], [Validasi dua tahun dengan BPS dan 60 uji otomatis], [Tambahan],
    [Tidak direncanakan], [Perluasan ke 27 kecamatan Kabupaten Lamongan], [Berjalan],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Capaian dibandingkan dengan rencana proposal],
) <tabel-capaian>

== Pembahasan

=== Jawaban atas Rumusan Masalah

Hasil studi menunjukkan bahwa citra satelit terbuka cukup untuk menyusun jadwal tanam per desa tanpa survei lapangan. Luas padi dari satelit hampir sama dengan luas panen BPS, dan korelasi per desa mencapai 0,88 pada 2021. Tahun 2021 tidak dipakai untuk menyetel ambang deteksi, sehingga hasil ini menjadi bukti yang independen. Dengan demikian, rumusan masalah pertama dan kedua terjawab, sedangkan rumusan ketiga terjawab melalui situs yang sudah berfungsi di komputer mahasiswa.

=== Tafsiran Hasil

Rasio luas semua tanaman lebih besar dari satu karena peta lahan pertanian juga mencakup jagung dan lahan kering. Rasio ini naik menjadi 1,46 pada 2021 karena tahun basah menambah puncak kehijauan yang terhitung sebagai musim tambahan. Hal yang sama menjelaskan intensitas tanam 2,85 kali pada 2021, yang terlalu tinggi untuk padi di Jawa. Oleh karena itu, angka intensitas lebih tepat dipakai untuk membandingkan desa pada tahun yang sama daripada sebagai angka mutlak.

Pembagian panen antara paruh pertama dan kedua tahun sesuai dengan data resmi. Akan tetapi, panen Maret sering terlambat terdeteksi atau hilang. Penyebabnya adalah awan musim hujan yang menutupi citra optik pada akhir musim tanam 1. Keterbatasan ini sejalan dengan alasan penelitian lain menggabungkan citra optik dan radar untuk memetakan tahap tumbuh padi di Jawa @Ramadhani_2020.

=== Perbandingan dengan Penelitian Lain

Penelitian di Indonesia memperkirakan tanggal tanam dari citra radar dengan galat sekitar 5 sampai 6 hari terhadap wawancara petani @Manago_2020. Studi ini menyelesaikan tugas yang berbeda, yaitu memprakirakan tanggal panen dua sampai tiga bulan sebelumnya tanpa data lapangan. Karena itu, galat 11,9 hari tidak dapat dibandingkan secara langsung. Penelitian di Karawang juga memakai validasi per tahun, tetapi memprediksi produktivitas padi per kecamatan @Fino_2026. Di Tikung, produktivitas antardesa sangat seragam, sehingga waktu tanam dan panen memberi informasi yang lebih bermanfaat bagi warga.

=== Kelebihan dan Keterbatasan

Kelebihan utama metode ini adalah biaya yang rendah dan pembaruan yang dapat berjalan setiap bulan. Seluruh data bersifat terbuka, sehingga alur yang sama dapat dijalankan untuk kecamatan lain. Selain itu, evaluasi per tahun dan uji ulang memberi gambaran ketepatan yang jujur.

Studi ini juga memiliki empat keterbatasan. Pertama, tanggal tanam dan panen berasal dari deteksi satelit dan belum dicocokkan dengan catatan petani. Kedua, prakiraan pada musim hujan masih lemah, dengan galat sampai 41 hari. Ketiga, berkurangnya lintasan radar sejak 2022 membuat sebagian status padi tidak diketahui. Keempat, lokasi petak program Kampung Pandu Sakti belum diketahui, sehingga dampak program itu belum dapat dipisahkan dari data desa.

=== Dampak dan Keberlanjutan

Sampai laporan ini disusun, situs belum dipublikasikan dan belum diuji bersama warga atau pemerintah desa. Oleh karena itu, dampak nyata bagi masyarakat belum dapat diukur. Meskipun demikian, studi ini sudah menyiapkan syarat keberlanjutan. Pengambilan data bulanan sudah dijadwalkan, kode dan data dirilis dengan lisensi terbuka, dan validasi dua tahun memberi dasar kepercayaan bagi pengguna. Langkah untuk menghadirkan dampak tersebut dijelaskan pada Bab VI.
