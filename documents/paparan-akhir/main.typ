// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: CC-BY-4.0

#import "@preview/calmly-touying:0.2.0": *
#import "@preview/touying:0.6.1": appendix, config-common
#import "@preview/cetz:0.3.4"
#import "@preview/fletcher:0.5.8": diagram, edge, node

#let gambar(nama) = "../laporan-akhir/gambar/" + nama

#show: calmly.with(
  colortheme: "paper",
  config-common(handout: true),
  config-info(
    title: [Pemantauan Musim Tanam Padi Berbasis Citra Satelit di Kecamatan Tikung],
    subtitle: [Paparan Akhir Program Mahasiswa Berdampak, Studi Independen],
    author: [Tri Rianto Utomo (24051204104)],
    institution: [Teknik Informatika, Universitas Negeri Surabaya · Mitra Dicoding Indonesia],
  ),
)

#set text(lang: "id")

#title-slide()

== Lamongan menjadi penghasil padi terbesar di Jawa Timur pada 2025

#v(1fr)
#three-col(
  [
    #align(center)[
      #text(size: size-display, weight: "bold")[880 ribu]
      #muted[ton gabah kering giling]
    ]
  ],
  [
    #align(center)[
      #text(size: size-display, weight: "bold")[152,6 ribu]
      #muted[hektare luas panen]
    ]
  ],
  [
    #align(center)[
      #text(size: size-display, weight: "bold")[309 ton]
      #muted[di atas Bojonegoro]
    ]
  ],
)
#v(1fr)

Kecamatan Tikung: 13 desa, sekitar 4.420 hektare sawah.

#cite-box("bpsjatim2026padi", display-label: "BPS Jawa Timur 2026", position: "bottom-right")

== Warga belum punya jadwal tanam per desa yang selalu baru

#two-col(
  [
    *Siapa yang butuh?*
    - Petani: giliran air dan pengendalian hama
    - Buruh tani dan penebas: jadwal kerja panen
    - Pemerintah desa: perencanaan musim
  ],
  [
    *Apa yang tersedia?*
    - Statistik resmi per kecamatan atau kabupaten
    - Terbit setelah musim berlalu
    - Data program Kampung Pandu Sakti tidak tersedia
  ],
)

#v(1fr)
#highlight-box(title: "Jalan keluar")[
  Citra satelit terbuka memotret setiap sawah tiap beberapa hari, tanpa survei lapangan.
]

== Studi ini menjawab tiga pertanyaan

+ Bagaimana mengubah citra Sentinel-1 dan Sentinel-2 menjadi tahap tanam per desa secara otomatis?
+ Seberapa sesuai luas dan waktu panen dari satelit dengan data resmi BPS?
+ Bagaimana memprakirakan waktu panen dan menyajikannya dalam situs yang mudah dipahami warga?

#v(1fr)
#muted[Wilayah: 13 desa di Kecamatan Tikung, data Oktober 2017 sampai September 2026.]

#section-slide[Metode]

== Semua data terbuka dan dapat diambil tanpa biaya

#align(center)[
  #table(
    columns: (auto, 1fr, auto),
    stroke: none,
    inset: 7pt,
    align: (left, left, center),
    table.hline(stroke: 1.2pt),
    table.header([*Data*], [*Sumber*], [*Resolusi*]),
    table.hline(stroke: 0.6pt),
    [Citra optik], [Sentinel-2 Level-2A, ESA], [10 m],
    [Citra radar VV dan VH], [Sentinel-1 RTC, ESA], [10 m],
    [Lahan pertanian], [ESA WorldCover 2021], [10 m],
    [Peta sawah], [Lahan Baku Sawah, BIG], [poligon],
    [Curah hujan bulanan], [CHIRPS], [0,05°],
    [Pembanding], [BPS per desa dan KSA bulanan], [desa, kabupaten],
    table.hline(stroke: 0.6pt),
  )
]

#v(1fr)
#muted[Unit analisis: sel 100 × 100 m. Kecamatan Tikung terbagi menjadi 4.954 sel.]

== Citra diolah bertahap dari data mentah sampai situs

#v(1fr)
#align(center)[
  #diagram(
    spacing: (10mm, 9mm),
    node-stroke: 0.8pt,
    node-corner-radius: 4pt,
    node-inset: 8pt,
    node((0, 0), [Citra Sentinel-1 \ dan Sentinel-2]),
    node((0, 1), [Hujan CHIRPS]),
    node((0, 2), [Peta sawah LBS]),
    node((1, 1), [Data mentah \ per sel]),
    node((2, 1), [Deret waktu \ bersih, 5 hari]),
    node((3, 1), [Musim tanam \ dan prakiraan]),
    node((4, 1), [Situs web], fill: rgb("#0173B2").lighten(80%)),
    node((3, 2.3), [Data BPS], stroke: (dash: "dashed")),
    edge((0, 0), (1, 1), "-|>"),
    edge((0, 1), (1, 1), "-|>"),
    edge((0, 2), (1, 1), "-|>"),
    edge((1, 1), (2, 1), "-|>", label: [buang awan]),
    edge((2, 1), (3, 1), "-|>", label: [deteksi]),
    edge((3, 1), (4, 1), "-|>"),
    edge((3, 2.3), (3, 1), "<|-|>", stroke: (dash: "dashed"), label: [validasi], label-side: left),
  )
]
#v(1fr)
#muted[Pengambilan data bulanan setiap tanggal 25 sudah disiapkan, belum aktif. Benar tidaknya alur diperiksa dengan 64 uji otomatis.]

== Musim tanam terbaca dari naik turunnya kehijauan sawah

#let ndvi(t) = 0.2 + 0.6 * calc.exp(-calc.pow((t - 75) / 28, 2))
#let sx(t) = t * 0.085
#let sy(v) = v * 5
#let t-tumbuh = 75 - 28 * calc.sqrt(-calc.ln(0.2))
#let t-panen = 75 + 28 * calc.sqrt(calc.ln(2))
#let t-tanam = 22

#slide(composer: (3fr, 2fr))[
  #align(center + horizon)[
    #cetz.canvas({
      import cetz.draw: *
      line((0, 0), (sx(150), 0), mark: (end: "stealth"), stroke: 1pt)
      line((0, 0), (0, sy(1)), mark: (end: "stealth"), stroke: 1pt)
      content((sx(150), -0.4), text(size: size-caption)[hari])
      content((-0.2, sy(1)), anchor: "east", text(size: size-caption)[NDVI])
      line((0, sy(0.6)), (sx(145), sy(0.6)), stroke: (paint: luma(150), dash: "dashed", thickness: 0.8pt))
      content((sx(145), sy(0.6) + 0.25), anchor: "east", text(size: size-caption, fill: luma(110))[ambang puncak 0,6])
      merge-path(
        {
          for i in range(0, 151, step: 2) {
            line((sx(i), sy(ndvi(i))), (sx(i + 2), sy(ndvi(i + 2))))
          }
        },
        stroke: rgb("#029E73") + 2pt,
      )
      let tanda(t, label, warna) = {
        line((sx(t), 0), (sx(t), sy(ndvi(t))), stroke: (paint: warna, dash: "dotted", thickness: 1pt))
        circle((sx(t), sy(ndvi(t))), radius: 0.09, fill: warna, stroke: none)
        content((sx(t), -0.45), text(size: size-caption, fill: warna)[#label])
      }
      tanda(t-tanam, [tanam], rgb("#0173B2"))
      tanda(t-tumbuh, [tumbuh], rgb("#0173B2"))
      tanda(75, [puncak], rgb("#029E73"))
      tanda(t-panen, [panen], rgb("#DE8F05"))
    })
  ]
][
  #v(1fr)
  - *Tanam*: sawah tergenang, pantulan radar VH paling rendah
  - *Tumbuh*: NDVI naik 20% dari dasar ke puncak
  - *Puncak*: NDVI di atas 0,6
  - *Panen*: NDVI turun 50% sesudah puncak
  #v(1fr)
  #muted[Kurva contoh, bukan data asli.]
]

#section-slide[Hasil]

== Luas padi dari satelit hampir sama dengan data BPS

#align(center)[
  #table(
    columns: (auto, auto, auto, auto),
    stroke: none,
    inset: 8pt,
    align: (left, left, center, center),
    table.hline(stroke: 1.2pt),
    table.header([*Tahun*], [*Tanaman*], [*Korelasi per desa*], [*Satelit / BPS*]),
    table.hline(stroke: 0.6pt),
    [2020], [Padi], [0,77], [1,01],
    [2020], [Semua tanaman], [0,91], [1,14],
    [*2021*], [*Padi*], [*0,88*], [*1,01*],
    [2021], [Semua tanaman], [0,89], [1,46],
    table.hline(stroke: 0.6pt),
  )
]

#v(1fr)
#highlight-box(title: "Uji yang independen")[
  Ambang padi disetel dengan data 2020, sehingga tahun 2021 menjadi uji yang tidak ikut dipakai.
]

#cite-box(("bpslamongan2021tikung", "bpslamongan2022tikung"), display-label: "BPS Lamongan 2021; 2022", position: "bottom-right")

== Musim tanam 1 dimulai November dan panen terbanyak pada April

#v(1fr)
#align(center)[#image(gambar("kalender-tanam.png"), width: 100%)]
#v(1fr)

- Musim tanam 2: mulai Maret, panen terbanyak Juli
- Musim tanam 3: Oktober sampai Januari, tidak muncul setiap tahun

== Jadwal tanam antardesa berselisih sampai lima minggu

#align(center)[#image(gambar("jadwal-per-desa.png"), height: 290pt)]

#muted[Puncak tanam paling awal di Takeranklating (20 November), paling akhir di Tambakrigadung (24 Desember).]

== Prakiraan panen lebih tepat daripada perkiraan sederhana

#align(center)[
  #table(
    columns: (auto, auto, auto, auto, auto),
    stroke: none,
    inset: 8pt,
    align: (left, center, center, center, center),
    table.hline(stroke: 1.2pt),
    table.header([*Galat rata-rata*], [*Median*], [*Ridge*], [*Random forest*], [*Gradient boosting*]),
    table.hline(stroke: 0.6pt),
    [Dari tanam], [15,2 hari], [13,7 hari], [12,1 hari], [*11,9 hari*],
    [Dari puncak], [10,1 hari], [9,8 hari], [9,7 hari], [*9,3 hari*],
    table.hline(stroke: 0.6pt),
  )
]

#v(1fr)
- Diuji per tahun: satu tahun panen ditahan sebagai data uji, sembilan kali
- Rentang 80% mencakup tanggal panen sebenarnya pada 72 sampai 73% musim

#cite-box(("Kallenberg_2026", "Romano_2019"), display-label: "Kallenberg 2026; Romano 2019", position: "bottom-right")

== Jenis model hampir tidak mengubah galat prakiraan

#slide(composer: (3fr, 2fr))[
  #text(size: size-small)[
    #table(
      columns: (auto, auto, auto),
      stroke: none,
      inset: 4.5pt,
      align: (left, center, center),
      table.hline(stroke: 1.2pt),
      table.header([*Model, pengaturan bawaan*], [*Dari tanam*], [*Dari puncak*]),
      table.hline(stroke: 0.6pt),
      [*Gradient boosting*], [*11,7*], [9,4],
      [XGBoost, voting], [12,0], [10,0; 9,3],
      [LightGBM, spline], [12,1], [9,4; *9,2*],
      [CatBoost, stacking], [12,2], [9,3],
      [Tanpa interaksi fitur], [12,8], [10,3],
      [Regresi linear], [13,8], [9,7],
      [Perkiraan median], [15,2], [10,1],
      table.hline(stroke: 0.6pt),
    )
  ]
][
  #v(1fr)
  - Sembilan model, galat dalam hari
  - Yang membantu: pola tidak lurus dan interaksi antarfitur
  - Model gabungan tidak menambah ketepatan
  #v(1fr)
  #highlight-box(title: "Keputusan")[Gradient boosting di situs dipertahankan.]
]

== Situs menampilkan peta tahap tanam dan daftar desa

#slide(composer: (1fr, 1fr))[
  #align(center + horizon)[#image(gambar("peta-beranda.png"), width: 100%)]
][
  #align(center + horizon)[#image(gambar("cari-desamu.png"), width: 100%)]
]

== Pada 29 September 2026, 95% sawah Tikung menunggu musim tanam

#v(1fr)
#three-col(
  [#align(center)[#text(size: size-display, weight: "bold")[4.216 ha] \ #muted[bera]]],
  [#align(center)[#text(size: size-display, weight: "bold")[74 ha] \ #muted[sedang ditanami]]],
  [#align(center)[#text(size: size-display, weight: "bold")[22 ha] \ #muted[menjelang panen]]],
)
#v(1fr)

- Sekitar 108 ha tertutup awan pada tanggal itu
- Perkiraan panen delapan minggu: Jotosanur sekitar 10 ha, puncak minggu 12 Oktober

== Prakiraan musim hujan dan data lapangan masih menjadi kelemahan

#two-col(
  [
    *Keterbatasan*
    - Tanggal belum dicocokkan dengan catatan petani
    - Prakiraan Januari meleset sampai 41 hari
    - Lintasan radar berkurang sejak 2022
    - Petak Kampung Pandu Sakti belum diketahui
  ],
  [
    *Tindak lanjut*
    - Publikasi situs dan demo daring untuk desa
    - Pembaruan bulanan otomatis
    - Deteksi awal musim yang tahan awan
    - Perluasan ke 27 kecamatan Lamongan
  ],
)

== Satelit terbuka cukup untuk jadwal tanam per desa

+ Alur otomatis mengubah citra 2017 sampai 2026 menjadi tahap tanam di 13 desa.
+ Luas padi satelit sesuai dengan BPS: rasio 1,01 dan korelasi 0,88 pada 2021.
+ Prakiraan panen meleset sekitar 12 hari dari tanam, dan situs sudah berfungsi.

#v(1fr)
#highlight-box(title: "Langkah berikutnya")[
  Menguji situs bersama warga dan pemerintah Desa Jotosanur.
]

#show: appendix

#bibliography-slide(
  title: [Referensi],
  bib-content: bibliography("../laporan-akhir/refs.bib", title: none, style: "harvard-cite-them-right"),
)

== Cadangan: prakiraan Juni jauh lebih tepat daripada Januari

#align(center)[
  #table(
    columns: (auto, auto, auto),
    stroke: none,
    inset: 8pt,
    align: (left, center, center),
    table.hline(stroke: 1.2pt),
    table.header([*Tanggal prakiraan*], [*Galat dari tanam*], [*Galat dari puncak*]),
    table.hline(stroke: 0.6pt),
    [Juni 2022, 2024, 2025], [11 sampai 20 hari], [9 sampai 13 hari],
    [Januari 2022, 2024, 2025], [21 sampai 41 hari], [40 sampai 47 hari],
    table.hline(stroke: 0.6pt),
  )
]

#v(1fr)
#muted[Uji ulang: data dipotong pada tanggal prakiraan, model hanya belajar dari musim yang sudah panen.]

== Cadangan: waktu panen sesuai KSA, kecuali bulan Maret

- Porsi panen Januari sampai Mei berselisih 0,01 sampai 0,08 dari KSA, 2020 sampai 2023
- Korelasi porsi bulanan turun dari 0,61 (2020) menjadi 0,05 (2023)
- KSA: 20 sampai 29% panen tahunan pada Maret
- Satelit: hanya 1 sampai 11% pada Maret 2021 sampai 2023
- Penyebab: awan musim hujan menutupi citra optik di akhir musim tanam 1

#cite-box(("bpslamongan2023ksa", "bpslamongan2024ksa"), display-label: "BPS Lamongan 2023; 2024", position: "bottom-right")
