// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: CC-BY-4.0

= Tinjauan Pustaka

== Tinjauan Teoritis

Studi ini bertumpu pada lima konsep, yaitu fenologi padi, citra optik, citra radar, intensitas pertanaman, dan pengolahan data bertahap. Selain itu, dasar pembelajaran mesin untuk prakiraan waktu panen juga dijelaskan.

=== Fenologi Padi

Fenologi padi adalah urutan fase pertumbuhan tanaman dari tanam sampai panen. Pada padi sawah tanam pindah yang umum di Jawa, petak sawah lebih dulu digenangi air sebelum bibit dipindahkan. Setelah itu, tanaman melewati fase vegetatif, mencapai puncak kehijauan, lalu menguning dan dipanen. Lama satu musim tanam bergantung pada varietas, dan umur panen padi berbeda antarprovinsi di Indonesia @Ardiansyah_2022. Awal musim tanam sendiri sangat ditentukan oleh datangnya hujan, sehingga penentuannya memerlukan kriteria curah hujan yang jelas @Surmaini_2016.

=== Citra Optik dan Indeks Vegetasi

Satelit Sentinel-2 merekam pantulan cahaya pada beberapa panjang gelombang dengan resolusi 10 meter. Dari dua pita, yaitu inframerah dekat (NIR) dan merah (Red), dapat dihitung indeks vegetasi NDVI pada @persamaan-ndvi.

$ "NDVI" = ("NIR" - "Red") / ("NIR" + "Red") $ <persamaan-ndvi>

Nilai NDVI naik ketika tanaman tumbuh hijau dan turun ketika tanaman menguning atau dipanen. Karena itu, puncak NDVI dapat dipakai sebagai penanda fase menjelang panen @Ramadhani_2020. Kelemahan citra optik adalah ketergantungannya pada langit cerah, padahal awan sangat sering menutupi Jawa pada musim hujan.

=== Citra Radar

Satelit Sentinel-1 memancarkan gelombang radar sendiri, sehingga dapat merekam permukaan bumi walaupun langit berawan. Pantulan balik pada polarisasi VH turun tajam ketika sawah tergenang, karena permukaan air memantulkan gelombang menjauhi satelit. Penurunan ini menjadi penanda awal musim tanam @Manago_2020. Deret waktu Sentinel-1 juga dapat dipakai untuk memetakan luas padi dan tahap tumbuhnya secara otomatis @Rudiyanto_2019 @Yang_2021.

=== Intensitas Pertanaman

Intensitas pertanaman adalah jumlah musim tanam pada satu petak sawah dalam satu tahun. Sawah irigasi di Jawa dapat ditanami dua sampai tiga kali setahun, sedangkan sawah tadah hujan biasanya hanya sekali. Peta intensitas pertanaman kini tersedia untuk Asia Tenggara dengan resolusi 10 meter @Ginting_2024 dan untuk Asia Selatan serta Asia Tenggara sejak 1995 @Zhao_2026.

=== Pengolahan Data Bertahap

Data satelit perlu diolah melalui beberapa tahap sebelum siap dianalisis. Pola ekstraksi, transformasi, dan pemuatan (ETL) memisahkan pengambilan data mentah, pembersihan, dan penyajian @yudhistira2023ilkom. Pemisahan tersebut penting pada data pertanian yang volumenya terus bertambah setiap musim @kustanti2021jpi. Dalam studi ini, data disimpan dalam tiga lapis, yaitu data mentah (bronze), data bersih (silver), dan data siap pakai (gold).

=== Pembelajaran Mesin untuk Prakiraan Waktu

Pembelajaran mesin telah dipakai untuk memprediksi produksi padi dari data historis @wijaya2025inti. Dalam studi ini, model memperkirakan tanggal panen dari tanggal tanam, puncak kehijauan, dan curah hujan. Model berbasis pohon keputusan, seperti random forest dan gradient boosting, dipilih karena mampu menangkap hubungan tidak linear antara fitur dan lama musim. Penilaian model dilakukan dengan menahan satu tahun penuh sebagai data uji. Cara tersebut mencegah model belajar dari musim yang sama dengan musim yang diuji.

== Penelitian Sebelumnya

Penelitian pemantauan padi dengan citra satelit di Indonesia telah berkembang pesat dalam lima tahun terakhir. @tabel-penelitian merangkum penelitian yang paling dekat dengan studi ini.

#figure(
  table(
    columns: (auto, 1fr, 1fr),
    stroke: none,
    inset: 6pt,
    align: horizon + center,
    table.hline(stroke: 1.2pt),
    table.header([*Penelitian*], [*Wilayah dan data*], [*Hasil utama*]),
    table.hline(stroke: 0.6pt),
    [@Manago_2020], [Indonesia, Sentinel-1], [Perkiraan tanggal tanam pindah untuk penilaian kerusakan padi],
    [@Rudiyanto_2019], [Asia Tenggara, Sentinel-1 pada Google Earth Engine], [Pemetaan luas, pola tanam, dan tahap tumbuh padi hampir waktu nyata],
    [@Ramadhani_2020], [Jawa, Sentinel-2, MODIS, dan Sentinel-1], [Peta tahap tumbuh padi 10 meter dengan akurasi 90,6% dari model Sentinel-2],
    [@Thorp_2021], [Jawa Barat, citra Sentinel], [Pemetaan tahap produksi padi dengan deep learning],
    [@Gandharum_2025], [Indonesia, intensitas pertanaman], [Kaitan intensitas pertanaman dengan menyusutnya lahan sawah],
    [@Ginting_2024], [Asia Tenggara, Sentinel-1 dan Sentinel-2], [Peta intensitas pertanaman dan luas panen padi 10 meter],
    [@Fino_2026], [Karawang, Sentinel-1, Sentinel-2, dan data iklim], [Prediksi produktivitas padi per kecamatan dengan validasi per tahun, MAPE 7,2% dengan random forest],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Penelitian sebelumnya tentang pemantauan padi dengan citra satelit],
) <tabel-penelitian>

Penelitian tersebut membuktikan bahwa tanggal tanam, tahap tumbuh, dan intensitas pertanaman dapat dibaca dari citra satelit. Meskipun demikian, ada tiga celah yang relevan dengan studi ini. Pertama, sebagian besar penelitian melatih model dengan data lapangan, sedangkan Kecamatan Tikung tidak memiliki data lapangan per petak. Kedua, peta yang dihasilkan umumnya mencakup wilayah luas dan ditujukan bagi peneliti atau pemerintah pusat, bukan bagi warga desa. Ketiga, penelitian prakiraan hasil panen pada kelompok tani masih berfokus pada satu komoditas dan satu kelompok @lasut2024jteksis.

Tren terkini mengarah pada penggabungan citra optik dan radar untuk mengatasi awan, serta pemanfaatan arsip citra terbuka yang dapat diakses tanpa biaya. Penelitian di Karawang, misalnya, memadukan Sentinel-1, Sentinel-2, dan data iklim untuk memprediksi produktivitas padi pada 30 kecamatan @Fino_2026. Penelitian tersebut juga menilai model dengan menahan satu tahun penuh sebagai data uji, sama seperti cara yang dipakai di sini. Berbeda dari Karawang, studi ini memperkirakan waktu panen karena produktivitas padi antardesa di Tikung sangat seragam. Data Sentinel-1 dan Sentinel-2 yang dipakai juga berasal dari katalog terbuka. Sumbangan utamanya terletak pada jadwal tanam per desa yang dirancang untuk diperbarui setiap bulan dan dapat dibaca langsung oleh warga.

=== Variabel yang Diteliti

Variabel dalam studi ini diukur per sel berukuran 100 meter, lalu dirangkum per desa. @tabel-variabel menjelaskan definisi operasional setiap variabel.

#figure(
  table(
    columns: (auto, 1fr),
    stroke: none,
    inset: 6pt,
    align: horizon + center,
    table.hline(stroke: 1.2pt),
    table.header(
      [*Variabel*],
      [*Definisi operasional*]),
    table.hline(stroke: 0.6pt),
    [Luas sawah], [Porsi sel yang berada di dalam peta Lahan Baku Sawah, dikalikan luas sel],
    [Tanggal tanam], [Tanggal nilai VH Sentinel-1 terendah di sekitar tanggal awal tumbuh, yaitu saat NDVI mulai naik dalam satu musim],
    [Puncak kehijauan], [Tanggal NDVI tertinggi dalam satu musim],
    [Tanggal panen], [Tanggal pertama sesudah puncak saat NDVI turun melewati ambang yang dihitung dari selisih puncak dan nilai dasar musim itu],
    [Tahap tanam terkini], [Status sel pada tanggal data terakhir: ditanami, menjelang panen, bera, atau tertutup awan],
    [Curah hujan], [Curah hujan bulanan CHIRPS per desa, dibandingkan dengan normal 1991 sampai 2020],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Definisi operasional variabel],
) <tabel-variabel>

Hubungan antarvariabel mengikuti urutan fenologi. Penggenangan menandai tanam, lalu puncak kehijauan muncul beberapa minggu kemudian. Pada data studi ini, jarak dari puncak ke panen hampir tetap, yaitu sekitar 30 hari, sehingga tanggal puncak menjadi penduga terkuat bagi tanggal panen. Curah hujan memengaruhi awal musim tanam @Surmaini_2016, sehingga dipakai sebagai fitur tambahan pada model prakiraan.

== Luaran Berdampak yang Diusulkan

Studi ini menghasilkan tiga luaran yang dapat langsung dimanfaatkan.

+ *Situs Tanam Padi Lamongan.* \ Situs ini menampilkan kondisi sawah terkini, kalender tanam, jadwal tanam per desa, dan perkiraan panen beberapa minggu ke depan. Dampaknya, warga, buruh tani, dan perangkat desa dapat mengetahui waktu tanam dan panen desanya tanpa menunggu statistik tahunan.
+ *Alur pengolahan data terbuka.* \ Kode program akan dirilis dengan lisensi Apache-2.0 dan data turunannya dengan lisensi CC-BY-4.0. Dampaknya, pemerintah daerah atau peneliti lain dapat menjalankan alur yang sama untuk kecamatan lain.
+ *Data musim tanam per desa.* \ Data tersedia dalam berkas JSON dan basis data MongoDB, mencakup musim tanam sejak Oktober 2017. Dampaknya, data ini dapat menjadi bahan perencanaan dan evaluasi program pertanian di tingkat desa.

Mitra kolaborator studi ini adalah Dicoding Indonesia, sedangkan penerima manfaat utamanya adalah warga dan pemerintah desa di Kecamatan Tikung.
