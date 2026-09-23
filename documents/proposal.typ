// Format dan Sistematika Proposal
/*
Format Penulisan Proposal:
  - Jenis dan Ukuran Kertas: Kertas HVS 70gram ukuran A4
  - Cover Proposal: Jika dicetak maka cover berwarna Oranye
  - Jenis Huruf: Times New Roman, Normal, 12pt (Judul), 11pt (Isi).
  - Teks menggunakan jarak baris 1.15 spasi dan perataan teks menggunakan rata kiri dan kanan (justify).
  - Layout menggunakan ukuran kertas A4, satu kolom, margin kiri 4cm, margin kanan, atas, dan bawah masing-masing 3cm.
  - Lembar pengesahan dengan dasar polos berwarna putih.
*/


#import "laporan/asp.typ": asp, frontmatter, backmatter, signature-block
#import "@preview/baler:0.1.0": baled-table

#let verbatim(body) = highlight(fill: rgb(yellow), body)
#show: asp.with(
  include-cover: true,
  title: [PROPOSAL PROGRAM MAHASISWA BERDAMPAK],
  type: [STUDI INDEPENDEN],
  extra-title: [Pengembangan Sistem Informasi Manajemen dan Monitoring Kampung Pandu Sakti Berbasis Web dengan Modul Prediksi Machine Learning di Desa Jotosanur, Kabupaten Lamongan],
  partner: [Dicoding Indonesia],
  students: (
    (name: "Tri Rianto Utomo", id: "24051204104"),
    (name: " ", id: " ")
  ),
  program: "Teknik Informatika",
  faculty: "Teknik",
  university: "Universitas Negeri Surabaya",
  year: "2026",
  numbering-config: (
    bib-chapter: true,
  ),
  outlines-attr: (
    lampiran: true,
  ),
  cover: (
    title-size: 12pt,
    type-size: 12pt,
    logo-width: 6cm,
  ),
  typography: (
    font-size: 11pt,
    table-size: 11pt,
  ),
  i18n: (
    students: (
      id: [*Penyusun*],
    ),
  ),
  margin: "print",
  // footer-text: [Proposal Mobilitas Akademik  Studi Independen Tahun X],
  bib-file: "ref.bib",
  bib-style: "harvard-cite-them-right"
)

#frontmatter(
  outlined: true,
  title: [LEMBAR PENGESAHAN]
)[
  #baled-table(
    columns: 2,
    align: (left, left),
    stroke: 0.5pt + luma(80),
    inset: (x: 8pt, y: 7pt),
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

  #v(1.2cm)

  #align(center)[Mengetahui]
  #v(0.4em)

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1cm,
    signature-block(
      role: [Dosen Pembimbing Lapangan],
      name: "Rifqi Abdillah, S.Tr.T., M.Kom.",
      id-label: "NIP.",
      id: "199911012024061001",
    ),
    signature-block(
      role: [Mahasiswa],
      name: "Tri Rianto Utomo",
      id-label: "NIM.",
      id: "24051204104",
    ),
  )

  #v(1.2cm)

  #align(center)[
    #block(width: 100%)[
      #text()[Menyetujui,] \
      #signature-block(
        role: [Koordinator Program Studi],
        name: "Paramitha Nerisafitra, S.ST., M.Kom.",
        id-label: "NIP.",
        id: "198905292019032013",
      )
    ]
  ]
]

// Bab I
= PENDAHULUAN

== Latar Belakang

Ketahanan pangan nasional saat ini banyak digarap lewat program lintas sektor yang melibatkan TNI Angkatan Darat, salah satunya program pertanian terpadu berbasis komando teritorial. Program semacam ini biasa disebut "kampung pangan" atau lumbung pangan terpadu: sektor pertanian, peternakan, dan perikanan digabung dalam satu kawasan sebagai model percontohan ketahanan pangan tingkat desa.

Di Kabupaten Lamongan, Jawa Timur, inisiatif tersebut diwujudkan melalui program *Kampung Pandu Sakti* (Kampung Pangan Terpadu) di Desa Jotosanur, Kecamatan Tikung. Kawasan seluas 10,5 hektare ini merupakan bekas lahan sirkuit motocross yang tidak produktif, dikembangkan Komando Distrik Militer (Kodim) 0812/Lamongan sejak awal 2025 menjadi kawasan pertanian, peternakan, dan perikanan terpadu tanpa limbah (zero-waste) @kabarbaik2025pandu @portallamongan2025 @inews2025zerowaste. Program ini dikelola oleh 58 anggota Satuan Tugas (Satgas) Pandu dari Kodim 0812 @bojonegorotimes2025dandim, dengan sekitar 60 persen dari total lahan (~6,3 hektare) difungsikan sebagai lahan padi menggunakan varietas unggul lokal PMJ 01 hasil pengembangan mandiri tim @inews2025lahan60. Dalam waktu kurang dari satu tahun sejak diinisiasi, capaian Kampung Pandu Sakti telah mendapat pengakuan luas: program ini ditinjau langsung oleh Gubernur Jawa Timur dan tim Kantor Staf Presiden Republik Indonesia sebagai salah satu model ketahanan pangan berbasis komunitas yang berhasil, dan direplikasikan ke 27 kecamatan lain melalui distribusi bibit gratis serta pendampingan pembukaan demonstration plot (demplot) seluas total 60 hektare @kspri2025 @kabarbaikreplikasi2025 @tribunnews2025unisla.

Meski telah diposisikan secara eksplisit sebagai model yang harus direplikasi ke daerah lain, status yang secara logis menuntut adanya sistem pencatatan terukur dan dapat diaudit, penelusuran terhadap seluruh pemberitaan resmi dan publikasi terkait Kampung Pandu Sakti tidak menemukan adanya sistem digital, basis data, atau dashboard pencatatan untuk memantau hasil panen per siklus, inventaris ternak, maupun distribusi bibit dan hasil produksi ke berbagai kecamatan penerima. Seluruh data operasional, termasuk capaian panen kedua sebesar 10 ton beras yang didistribusikan ke tujuh dapur Makan Bergizi Gratis (MBG) di empat kecamatan, serta distribusi bibit 1.200 kilogram ke 27 kecamatan pada periode panen kedua, hanya terdokumentasi melalui siaran pers dan pemberitaan media, disalurkan secara manual oleh Bintara Pembina Desa (Babinsa) tanpa basis data terpusat yang dapat diakses maupun dianalisis lebih lanjut @kabarbaikreplikasi2025. Kondisi ini sejalan dengan temuan umum bahwa pencatatan dan pelaporan berbasis komunitas di tingkat desa di Indonesia, termasuk pada program ketahanan pangan dan tata kelola desa berbasis digital, masih menghadapi kendala serupa berupa keterbatasan sistem pendataan terintegrasi @riantis2025jpes.

Ketiadaan sistem pencatatan digital ini berisiko menghambat replikasi program secara terukur. Tanpa data historis hasil panen, populasi ternak, maupun sebaran demplot yang tersimpan secara sistematis, pengambilan keputusan mengenai kecamatan mana yang layak menerima bibit lanjutan, prediksi hasil panen siklus berikutnya, atau evaluasi keberhasilan replikasi di 27 kecamatan sulit dilakukan secara objektif dan hanya bergantung pada laporan manual Babinsa. Pemanfaatan big data dan machine learning untuk mendukung prediksi hasil panen berbasis data historis telah terbukti membantu kelompok tani mengurangi kesalahan estimasi produksi yang selama ini dilakukan secara manual, sebagaimana ditunjukkan pada studi penerapan model prediksi hasil panen berbasis web dengan pendekatan fuzzy logic pada kelompok tani jagung, yang mencapai tingkat akurasi cukup tinggi dengan nilai MAPE 15,92% @lasut2024jteksis. Pendekatan serupa berpotensi diadaptasi untuk mendukung perencanaan dan monitoring hasil panen padi, ternak, dan perikanan pada Kampung Pandu Sakti secara lebih terukur.

Berdasarkan kesenjangan tersebut, proyek ini mengusulkan pengembangan sistem informasi manajemen berbasis web untuk mendukung pencatatan dan pemantauan data operasional Kampung Pandu Sakti, mencakup hasil panen per siklus dan komoditas, inventaris ternak, serta distribusi bibit dan hasil produksi ke kecamatan/dapur MBG penerima, dilengkapi modul analitik prediktif berbasis machine learning sebagai pendukung perencanaan siklus produksi berikutnya. Sistem ini dirancang murni berbasis perangkat lunak (input data manual atau dari laporan yang sudah ada, tanpa pemasangan sensor atau perangkat keras tambahan), sehingga dapat diimplementasikan dengan cepat dan selaras dengan status Kampung Pandu Sakti sebagai model yang harus terukur untuk direplikasi ke daerah lain.

== Rumusan Masalah

Bertolak dari kondisi tersebut, rumusan masalah pokok dalam proyek ini adalah:

- Bagaimana merancang dan membangun sistem informasi/dashboard pemantauan berbasis web yang mampu mencatat, mengelola, dan menyajikan data operasional Kampung Pandu Sakti (hasil panen, inventaris ternak, distribusi bibit dan hasil produksi ke kecamatan/dapur MBG) secara terpusat dan mudah diaudit, menggantikan pencatatan manual yang saat ini dilakukan Babinsa?
- Bagaimana mengembangkan modul analitik/prediksi berbasis machine learning yang memanfaatkan data historis hasil panen untuk mendukung perencanaan siklus produksi berikutnya secara lebih terukur?
- Bagaimana merancang fitur akses informasi tambahan berbasis WhatsApp sebagai kanal pelaporan ringkas bagi Satgas Pandu, sebagai fitur sekunder/opsional yang dikembangkan bila waktu dan koordinasi dengan mitra memungkinkan?

== Tujuan Studi Independen

Berdasarkan rumusan masalah tersebut, tujuan proyek ini adalah:

- Merancang dan membangun sistem informasi manajemen berbasis web yang andal untuk memfasilitasi pencatatan dan monitoring data operasional Kampung Pandu Sakti secara terstruktur, terpusat, dan menggantikan pencatatan manual yang selama ini dilakukan Babinsa.
- Mengembangkan dan menguji modul analitik/prediksi berbasis machine learning yang memanfaatkan data historis hasil panen untuk mendukung perencanaan siklus produksi berikutnya secara lebih terukur dan objektif.
- Merancang purwarupa fitur komunikasi sekunder berbasis WhatsApp sebagai kanal pelaporan ringkas bagi Satgas Pandu, dikembangkan secara opsional sesuai ketersediaan waktu tanpa mengorbankan kualitas dua luaran utama di atas.

== Manfaat Proyek/Studi Independen

Proyek ini dirancang untuk memberi manfaat bagi beberapa pihak, mencakup aspek akademis, mitra dan masyarakat, serta pengembangan kompetensi mahasiswa.

=== Manfaat bagi Pengetahuan Akademis dan Riset

- Memberikan contoh penerapan sistem informasi manajemen berbasis web dan machine learning pada program ketahanan pangan berbasis komando teritorial, konteks yang belum banyak dibahas pada penelitian sejenis.
- Menjadi studi kasus perancangan modul prediksi hasil panen berbasis data historis pada program multikomoditas dan multilokasi replikasi, memperluas cakupan penelitian sebelumnya yang masih terbatas pada satu komoditas dan satu kelompok tani @lasut2024jteksis.
- Menambah referensi mengenai penerapan big data untuk mendukung evaluasi program replikasi ketahanan pangan lintas wilayah.

=== Manfaat bagi Mitra dan Masyarakat

- *Kodim 0812/Satgas Pandu*: mengurangi ketergantungan pada pencatatan manual Babinsa untuk data panen, ternak, dan distribusi bibit/hasil produksi.
- *Pemerintah Desa Jotosanur*: memperoleh dasar data yang lebih kuat untuk mendukung status Kampung Pandu Sakti sebagai model ketahanan pangan yang direplikasi ke daerah lain.
- *Kecamatan-kecamatan penerima replikasi* (27 kecamatan): mempermudah evaluasi efektivitas replikasi program melalui data historis hasil panen dan distribusi yang terpusat.

=== Pengembangan Keterampilan Mahasiswa

- Meningkatkan kemampuan menerapkan ilmu Big Data dan Machine Learning pada persoalan nyata di lapangan, mulai dari analisis kebutuhan data hingga pengembangan modul prediksi.
- Melatih kemampuan merancang sistem informasi yang dapat digunakan oleh pengguna nonteknis, khususnya Satgas Pandu dan Babinsa di lapangan.
- Meningkatkan kemampuan berkoordinasi dan memvalidasi kebutuhan proyek melalui kanal resmi kecamatan tanpa akses langsung ke lokasi.

== Urgensi Studi Independen

Momentum untuk membangun sistem pencatatan Kampung Pandu Sakti saat ini sangat tepat: program telah mendapat sorotan dari Gubernur Jawa Timur dan Kantor Staf Presiden RI, serta tengah aktif direplikasi ke 27 kecamatan lain @kspri2025 @kabarbaikreplikasi2025. Semakin luas replikasi dijalankan tanpa basis data yang terstandardisasi, semakin sulit pula proses ini dievaluasi dan dikoreksi di kemudian hari; setiap siklus panen yang berlalu tanpa pencatatan sistematis adalah data historis yang hilang secara permanen dan tidak dapat direkonstruksi.

Urgensi ini diperkuat oleh konteks kemiskinan yang masih nyata di wilayah sekitar: tingkat kemiskinan Kabupaten Lamongan tercatat 12,42% pada 2023 @jiap2024kemiskinan, dan 268 KPM (Keluarga Penerima Manfaat) di Desa Jotosanur sendiri menerima bantuan beras CPP/Bulog pada Juli 2025 @radarbangsa2025bulog. Data ini menunjukkan bahwa program ketahanan pangan seperti Kampung Pandu Sakti bukan sekadar proyek percontohan simbolis, melainkan inisiatif dengan taruhan nyata bagi kesejahteraan warga sekitar apabila replikasinya berjalan efektif.

== Temuan yang Ditargetkan

Keberhasilan studi independen ini diukur melalui empat capaian konkret. Dashboard web mampu mencatat dan menampilkan data panen, ternak, dan distribusi tanpa kegagalan pada alur inti: input, penyimpanan, hingga tampilan ringkasan dan grafik. Modul machine learning mencapai akurasi yang tervalidasi terhadap data historis, dengan target MAPE di bawah 20%, merujuk pada capaian pembanding sebesar 15,92% @lasut2024jteksis. Panduan operasional selesai disusun dan mencakup seluruh alur penggunaan utama sistem, sehingga Satgas Pandu dapat memakainya tanpa pendampingan berkelanjutan. Bila waktu studi independen memungkinkan, prototipe kanal pelaporan ringkas berbasis WhatsApp turut terhubung ke sistem utama sebagai capaian opsional.

= TINJAUAN PUSTAKA

== Tinjauan Teoritis

Studi ini bertumpu pada dua kerangka konsep utama: *sistem informasi manajemen* dan *big data/machine learning* untuk sektor pertanian.

=== Sistem Informasi Manajemen Berbasis Web

Sistem informasi manajemen berbasis web dipahami sebagai kerangka pencatatan, penyimpanan, dan penyajian data operasional yang menggantikan pencatatan manual agar data dapat diakses, diaudit, dan dianalisis secara konsisten oleh berbagai pemangku kepentingan. Sistem semacam ini umumnya dibangun dengan memisahkan basis data terpusat dari antarmuka penyajian (dashboard), sehingga pembaruan data oleh satu pengguna dapat langsung tercermin pada tampilan yang diakses pengguna lain tanpa proses sinkronisasi manual @prastyo2025bittech.

=== Big Data untuk Sektor Pertanian dan Peternakan

Penerapan big data pada sektor pertanian dan peternakan mencakup pengelolaan data operasional dalam volume dan variasi yang terus bertambah seiring berjalannya siklus produksi, seperti data panen per komoditas, inventaris ternak, dan distribusi hasil produksi ke berbagai lokasi penerima @kustanti2021jpi. Variasi struktur data antar-komoditas ini lazim ditangani melalui basis data NoSQL yang mendukung skema fleksibel tanpa memerlukan definisi ulang struktur tabel setiap kali jenis data baru ditambahkan, pendekatan yang terbukti efektif pada pengelolaan data uji lapangan pertanian skala kecil hingga menengah @wu2024scirep. Sebelum dapat dianalisis, data dari berbagai sumber dan lokasi tersebut perlu melalui alur pemrosesan extract-transform-load (ETL) yang mengekstraksi, membersihkan, dan menstrukturkan data ke penyimpanan terpusat, sebagaimana diterapkan pada pengelolaan data komoditas pertanian Indonesia lintas subsektor @yudhistira2023ilkom. Ekosistem big data pada volume yang jauh lebih besar umumnya mengandalkan kerangka kerja pemrosesan terdistribusi seperti Hadoop dan Spark; pada skala program Kampung Pandu Sakti saat ini, prinsip yang sama diterapkan melalui arsitektur pipeline yang dirancang portabel, sehingga dapat diadaptasi ke platform terdistribusi apabila volume data bertambah seiring perluasan replikasi lintas kecamatan. Dalam konteks program ketahanan pangan berbasis komunitas seperti Kampung Pandu Sakti, data semacam ini berfungsi sebagai basis pengambilan keputusan operasional (misalnya perencanaan siklus tanam berikutnya) maupun keputusan strategis (misalnya evaluasi program replikasi ke berbagai kecamatan).

=== Machine Learning untuk Prediksi Hasil Panen

Prediksi hasil panen berbasis machine learning memanfaatkan data historis (luas lahan, komoditas, hasil panen per siklus) untuk membangun model yang dapat memperkirakan hasil panen mendatang dengan akurasi yang terukur @wijaya2025inti, sebagai pelengkap, bukan pengganti, estimasi manual yang selama ini dilakukan petani atau Babinsa secara berpengalaman.

== Penelitian Sebelumnya

*Penelitian pertama* mengembangkan program bantu perkiraan hasil panen jagung berbasis web menggunakan pendekatan fuzzy Tsukamoto pada Kelompok Tani Mutiara, Desa Maunggal Karya. Variabel bebas pada penelitian ini adalah data historis luas lahan dan hasil panen jagung per siklus, sedangkan variabel terikatnya adalah akurasi prediksi hasil panen, yang tercapai dengan MAPE sebesar 15,92% @lasut2024jteksis. Studi ini menjadi rujukan metodologis utama bagi rancangan modul prediksi pada proyek ini, khususnya dalam hal kelayakan penerapan model prediksi berbasis data historis pada kelompok tani dengan sumber daya teknis terbatas.

*Penelitian kedua* mengkaji model pengabdian terpadu berbasis ketahanan pangan dan digitalisasi gampong (desa) di Gampong Tanjong Hagu, Aceh Utara. Variabel bebas pada penelitian ini adalah intervensi program digitalisasi pendataan dan pelaporan, sedangkan variabel terikatnya adalah kesiapan infrastruktur data desa, yang ditemukan umumnya masih perlu dibangun dari titik nol, sejalan dengan kondisi yang ditemukan pada Kampung Pandu Sakti @riantis2025jpes.

Kedua penelitian tersebut sama-sama berfokus pada satu komoditas atau satu kelompok/wilayah tunggal, belum mencakup skenario multikomoditas (padi, ternak, perikanan) dan multilokasi (replikasi lintas kecamatan) seperti pada Kampung Pandu Sakti @lasut2024jteksis @riantis2025jpes. Diduga sistem pencatatan dan prediksi yang mengakomodasi multikomoditas serta mendukung pemantauan program replikasi lintas wilayah akan memberi nilai tambah yang belum tercakup pada penelitian-penelitian sebelumnya.

=== Variabel yang Diteliti

Variabel utama yang dicatat dan dianalisis dalam sistem ini meliputi: *data panen* (komoditas, luas lahan, tanggal tanam/panen, jumlah hasil per siklus), *data ternak* (jenis, jumlah, perkembangan populasi), dan *data distribusi* (jumlah bibit/hasil produksi, tujuan kecamatan/dapur penerima, tanggal distribusi). Untuk modul prediksi, variabel input utamanya adalah data historis hasil panen per komoditas dan periode, dengan variabel keluaran berupa estimasi hasil panen siklus berikutnya, mengikuti pola variabel yang terbukti relevan pada studi @lasut2024jteksis.

== Luaran Berdampak yang Diusulkan

*Luaran:*
- Sistem Informasi Manajemen Kampung Pandu Sakti (Web): dashboard untuk mencatat dan menampilkan data panen, ternak, serta distribusi bibit/hasil produksi.
- Modul Prediksi Hasil Panen Berbasis Machine Learning: model prediksi hasil panen siklus berikutnya berbasis data historis, terintegrasi dalam dashboard.
- Dokumentasi dan Panduan Operasional Sistem: panduan penggunaan berbahasa sederhana bagi pengguna nonteknis.
- Purwarupa Kanal WhatsApp (Opsional): prototipe kanal pelaporan/permintaan data ringkas, dikembangkan bila waktu memungkinkan.

*Dampak:* Menggantikan pencatatan manual Babinsa, mempermudah evaluasi dan pelaporan capaian program kepada pihak yang meninjau (Gubernur Jawa Timur, Kantor Staf Presiden RI, kecamatan penerima replikasi), mendukung perencanaan produksi yang lebih terukur baik untuk lahan sendiri maupun sebagai referensi kecamatan penerima replikasi, dan menjamin keberlanjutan penggunaan sistem oleh Satgas Pandu setelah masa studi independen berakhir.

*Mitra:* Kodim 0812/Lamongan, Satgas Pandu, Pemerintah Desa Jotosanur.

= METODE

== Waktu dan Tempat Pelaksanaan

Kegiatan studi independen ini dilaksanakan mulai Agustus hingga akhir Desember 2026, dengan objek studi Kampung Pandu Sakti di Desa Jotosanur, Kecamatan Tikung, Kabupaten Lamongan, Jawa Timur. Mengingat karakteristik proyek yang bersifat pengembangan perangkat lunak, sebagian besar pekerjaan pengembangan sistem dilakukan secara remote/daring, dengan koordinasi berkala bersama mitra (Kodim 0812/Satgas Pandu, melalui Kecamatan Tikung sebagai kanal komunikasi resmi) untuk pengumpulan data awal, validasi kebutuhan, dan uji coba sistem.

== Posisi / Kedudukan Kegiatan Proyek/Studi Independen

Mahasiswa berperan sebagai pengembang individu yang bertanggung jawab atas keseluruhan siklus pengembangan sistem informasi manajemen Kampung Pandu Sakti, mulai dari analisis kebutuhan, perancangan basis data dan antarmuka, pengembangan modul pencatatan dan modul prediksi machine learning, hingga pengujian dan penyusunan dokumentasi. Posisi ini berada langsung di bawah koordinasi Dosen Pembimbing Lapangan dan berkoordinasi dengan pihak Kodim 0812/Satgas Pandu selaku pengelola operasional Kampung Pandu Sakti sebagai penerima manfaat utama sistem.

== Metodologi Penyelesaian Tugas

Pengembangan sistem dilakukan dengan pendekatan iteratif melalui empat tahap utama: analisis kebutuhan data, perancangan dan pengembangan sistem, pengembangan modul prediksi, serta pengujian dan validasi.

=== Analisis Kebutuhan Data

Analisis kebutuhan data dilakukan secara berlapis, mengingat akses langsung ke pencatatan operasional mitra belum tersedia pada tahap penyusunan proposal. Data kualitatif diperoleh dari pemberitaan resmi (jumlah panen, luas lahan, jumlah anggota Satgas, cakupan replikasi). Data kuantitatif historis untuk kebutuhan pipeline dan modul prediksi bersumber dari data terbuka pemerintah: luas panen padi bulanan tingkat kecamatan, termasuk Kecamatan Tikung, tersedia dalam format CSV/JSON melalui API terbuka Portal Data Lamongan @datalamongan2024, dilengkapi luas panen, produktivitas, dan produksi padi per kecamatan dari publikasi tahunan Kabupaten Lamongan Dalam Angka @bpslamongan2024. Kedua sumber ini menjadi baseline regional untuk menguji alur ETL dan melatih model prediksi awal, sebelum data operasional Kampung Pandu Sakti secara spesifik diperoleh langsung dari mitra. Rancangan skema basis data awal disusun berdasarkan gabungan sumber tersebut dan disempurnakan lebih lanjut melalui koordinasi dengan mitra.

=== Perancangan dan Pengembangan Sistem

Perancangan dan pengembangan sistem mengikuti pola pengembangan aplikasi web pada umumnya, merujuk pada pendekatan sistem informasi berbasis web yang telah terbukti efektif untuk kelompok tani serupa @lasut2024jteksis. Skema basis data dirancang secara hibrida: struktur relasional untuk data transaksional (distribusi, pengguna) dipadukan komponen NoSQL untuk menampung variasi atribut antar-komoditas seperti panen dan ternak tanpa migrasi skema berulang @wu2024scirep, dengan alur ETL yang mengagregasi data dari pencatatan lapangan menjadi bentuk siap pakai bagi dashboard maupun modul prediksi @yudhistira2023ilkom.

=== Pengembangan Modul Prediksi

Pengembangan modul prediksi mengadopsi metode fuzzy Tsukamoto, pendekatan inferensi fuzzy yang menghasilkan keluaran crisp melalui rata-rata terbobot atas sejumlah aturan IF-THEN dengan fungsi keanggotaan monoton, sebagaimana diterapkan pada prediksi hasil panen jagung dengan MAPE 15,92% @lasut2024jteksis. Metode ini dipilih karena dapat bekerja dengan volume data historis yang relatif kecil pada tahap awal program, berbeda dari pendekatan jaringan saraf tiruan seperti pada @wijaya2025inti yang umumnya membutuhkan data latih dalam jumlah lebih besar.

=== Pengujian dan Validasi

Pengujian dan validasi dilakukan baik secara teknis maupun bersama mitra untuk memastikan sistem sesuai kebutuhan operasional Satgas Pandu.

== Pembelajaran Hal Baru

Melalui studi independen ini, mahasiswa memperoleh pengalaman langsung merancang sistem informasi untuk konteks nyata dengan pengguna nonteknis (Satgas Pandu/Babinsa), termasuk tantangan menerjemahkan kebutuhan lapangan yang tidak selalu terdokumentasi secara formal menjadi rancangan sistem yang jelas. Mahasiswa juga mendapat pengalaman menerapkan model prediksi machine learning pada data riil dengan keterbatasan volume data historis, situasi yang berbeda dari data latih ideal pada tugas kuliah, sehingga melatih kemampuan memilih pendekatan pemodelan yang realistis.


= KORELASI PROGRAM STUDI INDEPENDEN DENGAN KONVERSI MATA KULIAH

== Rencana Studi Independen yang Dikembangkan

Rencana studi independen yang akan dikembangkan difokuskan pada pengembangan sistem informasi manajemen berbasis web disertai modul prediksi machine learning, berkolaborasi dengan Komando Distrik Militer (Kodim) 0812/Lamongan melalui Satuan Tugas (Satgas) Pandu dan Pemerintah Desa Jotosanur selaku pengelola Kampung Pandu Sakti. Studi ini diarahkan untuk menjawab permasalahan nyata di lapangan, yaitu ketiadaan sistem pencatatan digital untuk data panen, ternak, dan distribusi bibit/hasil produksi pada program yang telah direplikasikan ke 27 kecamatan tanpa basis data terpusat. Melalui pendekatan berbasis riset terapan, studi ini mengusulkan pengembangan dashboard pencatatan dan modul prediksi hasil panen guna membantu Satgas Pandu meningkatkan efisiensi pencatatan serta ketepatan perencanaan siklus produksi berikutnya. Kegiatan dijalankan secara terstruktur, dimulai dari analisis kebutuhan, perancangan sistem, pengembangan modul prediksi, hingga uji coba dan serah terima sistem kepada mitra. Dengan demikian, studi independen ini tidak hanya menghasilkan luaran akademik, tetapi juga berdampak langsung pada tata kelola data Kampung Pandu Sakti.

=== Rencana Pengembangan Studi Independen

Rencana pengembangan studi independen ini disusun untuk memberi ruang bagi mahasiswa menerapkan ilmu Big Data dan Machine Learning yang telah diperoleh selama masa studi independen melalui pendekatan berbasis proyek, berkolaborasi dengan Kodim 0812/Satgas Pandu dan Pemerintah Desa Jotosanur, serta menghasilkan luaran yang nyata dan berdampak. Mahasiswa akan fokus pada pengembangan sistem informasi manajemen Kampung Pandu Sakti beserta modul prediksi hasil panen, yang bertujuan menyelesaikan permasalahan ketiadaan basis data terpusat pada program yang telah direplikasikan ke 27 kecamatan.

/ Tujuan Pengembangan:

- Meningkatkan kapasitas mahasiswa dalam menerapkan ilmu Big Data dan Machine Learning pada persoalan nyata di lapangan.
- Menghasilkan sistem pencatatan dan prediksi hasil panen yang menggantikan pencatatan manual Babinsa di Kampung Pandu Sakti.
- Menjadi dasar konversi capaian pembelajaran mata kuliah Big Data dan Machine Learning sesuai skema SKS yang berlaku.

/ Langkah-langkah Pengembangan:

- *Identifikasi Masalah dan Kebutuhan Mitra* \ Mahasiswa melakukan kajian pemberitaan resmi dan koordinasi awal dengan mitra melalui Kecamatan Tikung untuk memahami kebutuhan pencatatan data Kampung Pandu Sakti.
- *Perumusan Gagasan dan Desain Solusi* \ Merancang skema basis data hibrida (relasional dan NoSQL) beserta alur pemrosesan data (ETL), arsitektur sistem, dan antarmuka dashboard sesuai kebutuhan pencatatan panen, ternak, dan distribusi.
- *Pengembangan Sistem dan Modul Prediksi* \ Membangun dashboard pencatatan serta modul prediksi hasil panen berbasis machine learning secara iteratif.
- *Validasi dan Uji Coba bersama Mitra* \ Melibatkan mitra melalui koordinasi daring untuk menguji dan memvalidasi sistem sesuai kebutuhan operasional Satgas Pandu.
- *Evaluasi dan Dokumentasi Hasil* \ Mengevaluasi efektivitas sistem, menyusun panduan operasional, dan menyerahkan sistem kepada mitra sebagai luaran akhir.

#[
  #show figure: set block(breakable: true)
  #figure(
    table(
      columns: 5,
      inset: 6pt,
      stroke: 0.2pt,
      align: (x, y) => if x == 0 or x == 3 { horizon + center } else { horizon + left },

      table.header(
        [*Minggu*], [*Aktivitas*], [*Target*], [*Durasi (jam)*], [*Metode*],
      ),

      [1], [Orientasi dan koordinasi awal dengan DPL serta mitra (Kecamatan Tikung/Kodim 0812), dilanjutkan analisis kebutuhan data panen, ternak, dan distribusi], [Kesepakatan lingkup kerja serta daftar kebutuhan data dan skema awal basis data], [24], [Koordinasi daring, studi dokumen, dan diskusi mitra],
      [2], [Perancangan skema basis data hibrida (relasional dan NoSQL) dan arsitektur sistem, dilanjutkan perancangan antarmuka (UI/UX) dashboard], [Skema basis data hibrida final, rancangan arsitektur, wireframe, dan mockup dashboard], [24], [Perancangan mandiri, ditinjau DPL],

      [3-4], [Pengembangan backend, basis data hibrida, dan alur ETL awal, dilanjutkan pengembangan modul pencatatan panen dan ternak], [Modul backend inti berjalan; alur ETL serta penyimpanan data panen dan ternak berfungsi], [36], [Pemrograman],
      [3-4], [Pengembangan modul pencatatan distribusi bibit/hasil produksi, dilanjutkan integrasi alur ETL ke antarmuka dashboard (ringkasan dan grafik)], [Fitur pencatatan distribusi berfungsi; dashboard menyajikan data hasil ETL dalam bentuk ringkasan dan grafik], [36], [Pemrograman],

      [5], [Pengumpulan dan pra-pemrosesan data historis, dilanjutkan pengembangan model prediksi machine learning], [Dataset historis siap dilatih; model prediksi awal terlatih], [36], [Pengolahan data dan pemodelan machine learning],
      [6], [Validasi dan penyetelan model prediksi (target MAPE di bawah 20%), dilanjutkan integrasi modul prediksi ke dashboard], [Model tervalidasi dengan akurasi terukur dan terintegrasi ke dashboard], [36], [Evaluasi model dan integrasi sistem],

      table.cell(align: center, colspan: 5)[*Evaluasi Program*],
      [7], [Pengujian fungsional sistem secara menyeluruh, dilanjutkan uji coba dan validasi bersama mitra melalui Kecamatan Tikung], [Sistem lolos uji fungsionalitas inti; umpan balik mitra terhadap sistem], [24], [Pengujian teknis, koordinasi daring, dan demo sistem],
      [8], [Penyusunan dokumentasi dan panduan operasional, dilanjutkan perbaikan akhir dan serah terima sistem], [Dokumen panduan penggunaan selesai; sistem siap pakai dan laporan akhir selesai], [24], [Penyusunan dokumen serta serah terima],
    ),
    kind: table,
    caption: [Tabel Rencana Kegiatan]
  )
]

=== Dampak Studi Independen yang Diusulkan

+ *Dampak bagi Mitra (Kodim 0812/Satgas Pandu dan Pemerintah Desa Jotosanur)*:

  - *Efisiensi Pencatatan Operasional* \ Sistem menggantikan pencatatan manual Babinsa untuk data panen, ternak, dan distribusi bibit/hasil produksi.

  - *Kemudahan Evaluasi dan Pelaporan* \ Mempermudah evaluasi dan pelaporan capaian program kepada pihak yang meninjau, termasuk Gubernur Jawa Timur, Kantor Staf Presiden RI, dan kecamatan penerima replikasi.

  - *Perencanaan Produksi yang Lebih Terukur* \ Mendukung perencanaan siklus produksi berikutnya, baik untuk lahan Kampung Pandu Sakti sendiri maupun sebagai referensi bagi 27 kecamatan penerima replikasi.

  - *Keberlanjutan Penggunaan Sistem* \ Menjamin keberlanjutan penggunaan sistem oleh Satgas Pandu setelah masa studi independen berakhir.

+ *Dampak bagi Mitra (Dicoding Indonesia)*:

  - *Studi Kasus Penerapan Kurikulum* \ Proyek ini menjadi contoh penerapan kurikulum Big Data dan Machine Learning Dicoding pada persoalan ketahanan pangan berbasis komunitas, di luar konteks industri teknologi konvensional yang selama ini banyak menjadi mitra program.

  - *Penguatan Portofolio Dampak Sosial* \ Memperkuat portofolio Dicoding sebagai penyelenggara Studi Independen yang berkontribusi pada program pemerintah berskala nasional, mengingat Kampung Pandu Sakti telah ditinjau langsung oleh Gubernur Jawa Timur dan Kantor Staf Presiden RI.

+ *Dampak bagi Mahasiswa*:

  - *Pengalaman Praktik dan Penerapan Ilmu* \ Mahasiswa menerapkan ilmu Big Data dan Machine Learning secara langsung melalui pengembangan sistem informasi dan modul prediksi untuk Kampung Pandu Sakti.

  - *Pengalaman Merancang untuk Pengguna Nonteknis* \ Mahasiswa melatih kemampuan menerjemahkan kebutuhan lapangan Satgas Pandu/Babinsa yang tidak selalu terdokumentasi formal menjadi rancangan sistem yang jelas.

  - *Peningkatan Kemampuan Pemodelan Data Riil* \ Mahasiswa memperoleh pengalaman menerapkan model prediksi pada data historis dengan keterbatasan volume, melatih kemampuan memilih pendekatan pemodelan yang realistis.

  - *Kemampuan Koordinasi Jarak Jauh* \ Mahasiswa melatih kemampuan berkoordinasi dan memvalidasi kebutuhan proyek melalui kanal resmi kecamatan tanpa akses langsung ke lokasi.


== Relevansi dengan Mata Kuliah Konversi

Berdasarkan hasil observasi awal serta kajian pemberitaan resmi dan publikasi terkait Kampung Pandu Sakti, mahasiswa merancang rencana proyek studi independen yang difokuskan pada pengembangan sistem informasi manajemen dan modul prediksi machine learning untuk mendukung pencatatan dan perencanaan produksi. Kegiatan utama dalam studi independen ini meliputi analisis kebutuhan data, perancangan dan pengembangan sistem informasi berbasis web, pengembangan dan validasi modul prediksi berbasis machine learning, serta evaluasi dan dokumentasi hasil. Setiap aktivitas yang dirancang selama studi independen telah dikaitkan secara langsung dengan mata kuliah yang relevan di Program Studi Teknik Informatika, sehingga memungkinkan konversi 10 SKS sesuai skema yang berlaku. Berikut rincian relevansi antara kegiatan studi independen dengan mata kuliah konversi:

+ Perencanaan Program (2 SKS) \ Mahasiswa menyusun desain kegiatan berbasis kebutuhan pencatatan dan prediksi Kampung Pandu Sakti, mencakup studi literatur, analisis kebutuhan data, penetapan tujuan dan indikator keberhasilan, serta perancangan skema basis data dan arsitektur sistem.

+ Konversi Big Data (3 SKS) \ Mencakup analisis kebutuhan data, perancangan skema basis data hibrida (relasional dan NoSQL) untuk menangani variasi data multikomoditas, pengembangan alur pemrosesan data (ETL), serta pengembangan sistem informasi manajemen berbasis web untuk pencatatan dan visualisasi data panen, ternak, dan distribusi bibit/hasil produksi.

+ Konversi Machine Learning (3 SKS) \ Mencakup pengembangan dan validasi modul prediksi hasil panen berbasis machine learning menggunakan data historis, dengan target akurasi MAPE di bawah 20%.

+ Evaluasi Program (2 SKS) \ Meliputi pengujian fungsional dan validasi sistem bersama mitra, penyusunan dokumentasi dan panduan operasional, serta evaluasi capaian terhadap indikator yang ditetapkan pada tahap perencanaan.


= PENUTUP

Proposal Program Mahasiswa Berdampak Studi Independen ini disusun sebagai kerangka acuan pelaksanaan proyek pengembangan sistem informasi manajemen dan monitoring Kampung Pandu Sakti berbasis web disertai modul prediksi machine learning. Kegiatan ini berlokasi di Desa Jotosanur, Kecamatan Tikung, Kabupaten Lamongan, Jawa Timur, berkolaborasi dengan Komando Distrik Militer (Kodim) 0812/Lamongan melalui Satuan Tugas (Satgas) Pandu dan Pemerintah Desa Jotosanur selaku pengelola Kampung Pandu Sakti. Melalui pelaksanaan studi independen ini, target utama yang ingin dicapai meliputi:

+ *Implementasi Sistem* \ Terbangunnya dashboard pencatatan dan modul prediksi hasil panen berbasis machine learning yang siap dioperasikan oleh Satgas Pandu.

+ *Efisiensi Pencatatan Operasional* \ Menggantikan pencatatan manual Babinsa untuk data panen, ternak, dan distribusi bibit/hasil produksi dengan sistem yang terpusat dan mudah diaudit.

+ *Dukungan Evaluasi Replikasi Program* \ Tersedianya basis data historis yang mendukung evaluasi efektivitas replikasi Kampung Pandu Sakti pada 27 kecamatan penerima.

+ *Capaian Akademik dan Konversi SKS* \ Penerapan ilmu Big Data dan Machine Learning pada persoalan nyata di lapangan, sekaligus pemenuhan capaian pembelajaran untuk konversi 10 SKS sesuai skema yang berlaku.

Besar harapan kami agar proposal ini dapat disetujui sehingga seluruh rencana kegiatan yang telah dirancang dapat terlaksana dengan lancar, serta memberikan kontribusi nyata dan berkelanjutan bagi tata kelola data Kampung Pandu Sakti maupun replikasinya di kecamatan-kecamatan lain.


// Daftar Pustaka
// Setiap pustaka yang dirujuk dalam naskah harus muncul dalam daftar pustaka, dan sebaliknya. Format perujukan pustaka mengikuti Harvard style (nama belakang, tahun dan diurutkan berdasar abjad).