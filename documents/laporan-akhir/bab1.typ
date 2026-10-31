// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: CC-BY-4.0

= Pendahuluan

== Latar Belakang

Padi adalah tanaman pangan utama di Jawa Timur, dan Kabupaten Lamongan memegang peran besar di dalamnya. Pada 2025, Lamongan menjadi kabupaten dengan produksi padi tertinggi di Jawa Timur, yaitu 879.993,80 ton gabah kering giling @bpsjatim2026padi. Keunggulan ini sangat tipis karena Kabupaten Bojonegoro mencatat 879.685,13 ton pada tahun yang sama. Luas panen padi Lamongan pada 2025 mencapai sekitar 152,56 ribu hektare @bpsjatim2026padi. Kecamatan Tikung, dengan tiga belas desa dan sekitar 4.420 hektare sawah, adalah salah satu wilayah penyumbang produksi tersebut.

Bagi petani dan pemerintah desa, informasi waktu tanam dan waktu panen per desa sangat berguna. Waktu tanam yang serempak antardesa membantu pembagian air irigasi dan pengendalian hama. Informasi waktu panen juga dibutuhkan buruh tani, pemilik mesin panen, dan pedagang gabah untuk merencanakan pekerjaan. Akan tetapi, statistik pertanian resmi umumnya disajikan per kecamatan atau per kabupaten dan terbit setelah musim berlalu @bpslamongan2024. Akibatnya, warga belum memiliki gambaran musim tanam per desa yang diperbarui secara berkala.

Studi independen ini semula dirancang untuk membangun sistem informasi manajemen bagi program Kampung Pandu Sakti di Desa Jotosanur. Program pangan terpadu ini dikelola Kodim 0812/Lamongan di bekas lahan sirkuit seluas 10,5 hektare @kabarbaik2025pandu @portallamongan2025. Rencana tersebut membutuhkan data operasional program, seperti hasil panen per siklus dan distribusi bibit. Data itu ternyata tidak tersedia selama masa studi, sehingga sistem pencatatan dan model prediksi hasil panen tidak dapat dibangun maupun diuji. Kendala serupa juga ditemukan pada program digitalisasi desa lain, yang infrastruktur datanya masih harus dibangun dari awal @riantis2025jpes.

Citra satelit terbuka menawarkan jalan keluar dari keterbatasan data tersebut. Penelitian di Jawa menunjukkan bahwa tanggal tanam padi dapat diperkirakan dari citra radar Sentinel-1 @Manago_2020. Tahap pertumbuhan padi juga dapat dipetakan dari gabungan citra optik dan radar @Ramadhani_2020 @Thorp_2021. Oleh karena itu, studi ini dialihkan menjadi pemantauan musim tanam padi berbasis citra satelit untuk seluruh desa di Kecamatan Tikung, termasuk Desa Jotosanur. Hasil studi tersebut, disajikan dalam situs web yang dapat dibaca oleh warga.

== Rumusan Masalah

Berdasarkan latar belakang tersebut, rumusan masalah studi ini adalah sebagai berikut.

+ Bagaimana membangun alur pengolahan data otomatis yang mengubah citra Sentinel-1 dan Sentinel-2 menjadi informasi tahap tanam per desa di Kecamatan Tikung?
+ Seberapa sesuai luas tanam dan waktu panen hasil pengolahan citra satelit dengan data resmi Badan Pusat Statistik?
+ Bagaimana memperkirakan waktu panen dan menyajikan jadwal tanam per desa dalam situs web yang mudah dipahami warga?

== Tujuan Studi Independen

Sesuai dengan rumusan masalah, studi independen ini memiliki tiga tujuan.

+ Membangun alur pengolahan data bertahap yang memproses citra Sentinel-1 dan Sentinel-2 sejak Oktober 2017 untuk tiga belas desa di Kecamatan Tikung.
+ Menguji kesesuaian hasil satelit dengan data luas panen BPS 2020 per desa dan data waktu panen bulanan Kerangka Sampel Area 2020 sampai 2023.
+ Mengembangkan model prakiraan waktu panen dan situs web yang menampilkan kondisi sawah, jadwal tanam per desa, dan perkiraan panen.

== Manfaat Studi Independen

Studi ini diharapkan memberi manfaat bagi tiga pihak, yaitu bidang keilmuan, masyarakat, dan mahasiswa.

=== Manfaat bagi Pengetahuan Akademis

Studi ini memberi contoh pemantauan musim tanam tingkat desa yang tidak memerlukan survei lapangan. Evaluasi model dilakukan per tahun, sehingga hasilnya lebih jujur daripada pengujian dengan pembagian data acak. Selain itu, setiap temuan yang hanya berlaku di Jawa dicatat sebagai bahan penelitian lanjutan di wilayah lain.

=== Manfaat bagi Masyarakat dan Pemerintah Desa

Warga dan perangkat desa dapat melihat kapan biasanya desa mereka mulai tanam dan panen. Buruh tani dan pemilik mesin panen dapat melihat desa yang akan panen dalam beberapa minggu ke depan. Informasi ini tersedia tanpa biaya dan diperbarui seiring datangnya citra baru.

=== Pengembangan Keterampilan Mahasiswa

Mahasiswa menerapkan rekayasa data, pembelajaran mesin, pengujian perangkat lunak, dan pengembangan web dalam satu proyek nyata. Mahasiswa juga belajar menyesuaikan rencana ketika data yang diharapkan ternyata tidak tersedia.

== Urgensi Studi Independen

Studi ini perlu dilakukan sekarang karena dua alasan. Pertama, musim tanam utama 2026/2027 di Kecamatan Tikung biasanya dimulai pada November, sehingga jadwal tanam per desa paling berguna bila tersedia sebelum bulan itu. Kedua, jumlah lintasan satelit radar Sentinel-1 di atas Tikung turun dari 53 sampai 57 kali per tahun pada 2018 sampai 2021 menjadi 24 kali pada 2023. Tanpa alur data yang menandai celah tersebut, data padi tahun 2022 dan 2023 mudah disalahartikan sebagai penurunan luas tanam.

== Temuan yang Ditargetkan

Perubahan arah studi membuat sebagian target proposal disesuaikan. @tabel-target membandingkan target proposal dengan target yang direvisi.
#figure(
  table(
    columns: (1fr, 1fr),
    stroke: none,
    inset: 6pt,
    align: horizon + center,
    table.hline(stroke: 1.2pt),
    table.header(
      table.cell(align: center)[*Target proposal*],
      table.cell(align: center)[*Target revisi*]
    ),
    table.hline(stroke: 0.6pt),
    [Dashboard pencatatan panen, ternak, dan distribusi bibit], [Situs pemantauan tanam untuk tiga belas desa dengan pembaruan bulanan],
    [Model prediksi hasil panen dengan MAPE di bawah 20%], [Model prakiraan waktu panen dengan galat lebih kecil daripada perkiraan nilai tengah],
    [Panduan operasional sistem], [Halaman Tentang Data di situs dan dokumentasi kode],
    [Kanal pelaporan WhatsApp], [Tidak dikerjakan],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Perbandingan target proposal dan target revisi],
) <tabel-target>

Target prediksi hasil panen diganti karena produktivitas padi antardesa di Tikung sangat seragam, yaitu 6,8 sampai 7,8 ton per hektare. Pada kondisi ini, rata-rata lokal sudah menjadi penduga yang kuat, sedangkan waktu tanam dan waktu panen jauh lebih bervariasi antardesa dan antarmusim.
