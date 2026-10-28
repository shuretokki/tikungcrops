// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// All user-facing text of the site lives here, so a rewrite touches one file.

export const COPY = {
  site: {
    title: 'Tanam Padi Lamongan',
    footer: 'Data diolah dari Copernicus Sentinel-1/2 (ESA), CHIRPS, ESA WorldCover, dan Lahan Baku Sawah (BIG). Batas wilayah: geoBoundaries (OCHA ROAP, BPS 2019), CC BY 3.0 IGO. Peta dasar: OpenFreeMap, © OpenStreetMap.'
  },

  nav: {
    ringkasan: 'Ringkasan',
    perbandingan: 'Perbandingan',
    metode: 'Metode',
    data: 'Data'
  },

  landing: {
    seoTitle: 'Tanam Padi Lamongan',
    eyebrow: 'Kecamatan Tikung, Kabupaten Lamongan',
    headline: 'Musim tanam padi di tiga belas desa, terpantau dari satelit',
    description: 'Situs ini menunjukkan tahap tanam setiap desa, pola musim sejak 2017, dan perkiraan waktu panen. Semua angka berasal dari citra satelit sehingga tidak memerlukan survei lapangan.',
    primaryCta: 'Lihat ringkasan',
    secondaryCta: 'Pelajari metode',
    stats: {
      paddy: 'Luas sawah yang dipantau',
      units: 'Desa',
      since: 'Pengamatan sejak',
      asOf: 'Data terakhir'
    },
    tableToggle: 'Lihat tabel data',

    now: {
      kicker: 'Saat ini',
      title: (pct: string, date: string) => `${pct} sawah sedang bera pada ${date}`,
      body: (month: string) => `Sebagian besar sawah menunggu musim tanam berikutnya. Berdasarkan pola sejak 2017, penanaman musim utama biasanya dimulai pada bulan ${month}.`,
      columns: { stage: 'Tahap', ha: 'Luas', share: 'Bagian' }
    },

    calendar: {
      kicker: 'Pola tahunan',
      title: (start: string, harvest: string) => `Musim utama mulai ditanam pada bulan ${start} dan dipanen pada bulan ${harvest}`,
      body: 'Setiap pita menunjukkan rentang dari awal tanam sampai akhir panen. Waktunya adalah rata-rata semua desa sejak 2017.',
      today: 'Hari ini',
      plant: 'Puncak tanam',
      harvest: 'Puncak panen',
      seasons: { MT1: 'Musim tanam 1', MT2: 'Musim tanam 2', MT3: 'Musim tanam 3' },
      seasonNote: { MT1: 'Musim utama', MT2: 'Musim kedua', MT3: 'Tidak setiap tahun' },
      columns: { season: 'Musim', start: 'Awal tanam', plant: 'Puncak tanam', harvest: 'Puncak panen', end: 'Akhir panen' }
    },

    intensity: {
      kicker: 'Intensitas',
      title: (avg: string) => `Sawah ditanami rata-rata ${avg} kali per tahun`,
      body: 'Angka ini disebut indeks pertanaman dan mencakup padi serta tanaman lain. Angka satelit lebih tinggi daripada angka BPS 2020 (2,18 berbanding 1,62), jadi bacalah sebagai batas atas.',
      average: (v: string) => `Rata-rata ${v}`,
      readout: (year: number, v: string) => `${year}: ${v} kali tanam`,
      columns: { year: 'Tahun', value: 'Kali tanam per tahun' }
    },

    validation: {
      kicker: 'Ketepatan',
      title: (r: string) => `Luas dari satelit sejalan dengan luas panen BPS (korelasi ${r})`,
      body: (ratio: string) => `Perbandingan ini memakai data BPS tahun 2020 untuk tiga belas desa. Satelit mencatat luas sekitar ${ratio} kali luas BPS karena peta lahan pertanian juga mencakup jagung dan lahan kering.`,
      x: 'Luas panen BPS 2020 (ha)',
      y: 'Luas dari satelit (ha)',
      equal: 'Sama dengan BPS',
      readout: (unit: string, ref: string, sat: string) => `${unit}: BPS ${ref}, satelit ${sat}`,
      hint: 'Arahkan kursor ke titik untuk melihat nama desa.',
      columns: { unit: 'Desa', reference: 'BPS 2020', satellite: 'Satelit' }
    },

    steps: {
      kicker: 'Cara kerja',
      title: 'Tiga langkah dari citra satelit ke kalender tanam',
      items: [
        {
          icon: 'i-lucide-satellite',
          title: 'Citra radar dan optik',
          description: 'Sentinel-1 merekam permukaan sawah walaupun langit berawan, sedangkan Sentinel-2 merekam kehijauan tanaman.'
        },
        {
          icon: 'i-lucide-waves',
          title: 'Genangan dan pertumbuhan',
          description: 'Genangan air menandai awal tanam, lalu puncak kehijauan menandai fase menjelang panen.'
        },
        {
          icon: 'i-lucide-calendar-check',
          title: 'Kalender per desa',
          description: 'Hasilnya dirangkum per desa menjadi musim tanam, intensitas, dan perkiraan panen.'
        }
      ]
    },

    limitsTitle: 'Keterbatasan data',
    limits: 'Tanggal tanam dan panen diperoleh dari deteksi satelit dan belum dicocokkan dengan catatan panen petani. Sejak 2022 satelit radar lebih jarang melintas sehingga sebagian musim padi tidak terdeteksi. Perkiraan pada musim hujan juga dapat meleset beberapa minggu.',
    limitsCta: 'Baca metode lengkap',

    desa: {
      title: 'Rincian per desa',
      body: 'Pilih desa untuk melihat kalender tanam dan perkiraan panennya.'
    }
  },

  ringkasan: {
    seoTitle: 'Ringkasan - Tanam Padi Lamongan',
    title: 'Kondisi tanam padi saat ini',
    description: (asOf: string) => `Kecamatan Tikung terdiri atas tiga belas desa. Data citra satelit tersedia hingga ${asOf}. Pilih desa pada peta atau tabel untuk melihat rinciannya.`,
    paddy: 'Luas sawah yang dipantau',
    outlook: 'Perkiraan panen musim ini',
    mapLoading: 'Memuat peta...',
    alertTitle: 'Perkiraan musim hujan belum akurat',
    alert: 'Tanggal tanam dan panen berasal dari deteksi satelit dan belum dicocokkan dengan catatan panen petani. Pada musim hujan, awan menutupi citra pada awal musim sehingga perkiraan dapat meleset tiga hingga lima minggu. Pada musim kemarau, selisihnya sekitar satu hingga dua minggu.',
    columns: {
      unit: 'Desa',
      paddy: 'Luas sawah',
      outlook: 'Perkiraan panen',
      topWeek: 'Minggu panen terbanyak'
    }
  }
}
