// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// All user-facing text of the site lives here, so a rewrite touches one file.
// The landing page talks to local residents in a casual "kamu" register, with headings in Title Case.
// Sources, method and limits stay on the Metode page.

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
    eyebrow: 'Kecamatan Tikung, Lamongan',
    headline: 'Kapan Sawah di Desamu Mulai Tanam?',
    description: (units: number) => `Lihat kondisi sawah di ${units} desa Tikung, kalender tanam tiap musim, dan hujan beberapa bulan terakhir.`,
    primaryCta: 'Cari Desamu',
    secondaryCta: 'Lihat Ringkasan',
    stats: {
      paddy: 'Luas sawah',
      units: 'Desa',
      season: 'Musim tanam 1 mulai',
      asOf: 'Data terakhir'
    },
    tableToggle: 'Lihat Tabel',
    mapLoading: 'Memuat peta...',

    pride: {
      title: 'Lamongan, Lumbung Padi Jawa Timur',
      body: (units: number) => `Pada 2024, Lamongan jadi penghasil padi terbesar di Jawa Timur. Sawah di ${units} desa Tikung ikut menyumbang panen itu.`,
      chartTitle: 'Produksi padi 2024, lima kabupaten teratas',
      unit: 'ribu ton gabah kering giling',
      rank: '#1',
      stats: {
        share: 'dari seluruh padi Jawa Timur',
        rice: 'beras dari Lamongan',
        harvest: 'sawah yang dipanen'
      },
      source: 'Sumber: BPS Provinsi Jawa Timur dan BPS Kabupaten Lamongan, 2024.'
    },

    now: {
      title: (resting: boolean) => (resting ? 'Sawah Menunggu Musim Tanam' : 'Musim Tanam Sedang Berjalan'),
      body: (resting: boolean, pct: string, date: string) => resting
        ? `Per ${date}, ${pct} sawah sedang bera. Biasanya sawah mulai ditanami lagi setelah hujan turun.`
        : `Per ${date}, ${pct} sawah sedang bera. Sisanya sedang ditanami atau menjelang panen.`,
      columns: { stage: 'Tahap', ha: 'Luas', share: 'Bagian' }
    },

    calendar: {
      title: (month: string) => `Musim Tanam Utama Biasanya Mulai ${month}`,
      body: 'Tiap pita menunjukkan masa tanam sampai panen. Garis hijau menunjukkan posisi hari ini.',
      today: 'Hari ini',
      plant: 'Puncak tanam',
      harvest: 'Puncak panen',
      seasons: { MT1: 'Musim Tanam 1', MT2: 'Musim Tanam 2', MT3: 'Musim Tanam 3' },
      seasonNote: { MT1: 'Musim utama', MT2: 'Musim kedua', MT3: 'Tidak tiap tahun' },
      columns: { season: 'Musim', start: 'Awal tanam', plant: 'Puncak tanam', harvest: 'Puncak panen', end: 'Akhir panen' }
    },

    rain: {
      title: 'Hujan 12 Bulan Terakhir',
      body: (month: string, mm: string, normal: string) => `Hujan ${month}: ${mm} mm. Biasanya sekitar ${normal} mm.`,
      actual: 'Hujan',
      normal: 'Biasanya',
      readout: (label: string, mm: string, normal: string) => `${label}: ${mm} mm, biasanya ${normal} mm`,
      columns: { month: 'Bulan', mm: 'Hujan (mm)', normal: 'Biasanya (mm)' }
    },

    desa: {
      title: 'Cari Desamu',
      body: 'Ketik nama desamu, lalu pilih untuk melihat kalender tanam dan perkiraan panennya.',
      search: 'Ketik nama desa',
      empty: 'Desa tidak ditemukan. Coba ejaan lain.',
      paddy: (ha: string) => `${ha} sawah`
    }
  },

  metode: {
    seoTitle: 'Metode - Tanam Padi Lamongan',
    title: 'Metode',
    description: 'Dari mana data di situs ini berasal, dan seberapa tepat hasilnya.',
    steps: {
      title: 'Dari Citra Satelit ke Kalender Tanam',
      items: [
        {
          icon: 'i-lucide-satellite',
          title: 'Citra Radar dan Optik',
          description: 'Sentinel-1 merekam permukaan sawah walaupun langit berawan, sedangkan Sentinel-2 merekam kehijauan tanaman.'
        },
        {
          icon: 'i-lucide-waves',
          title: 'Genangan dan Pertumbuhan',
          description: 'Genangan air menandai awal tanam, lalu puncak kehijauan menandai fase menjelang panen.'
        },
        {
          icon: 'i-lucide-calendar-check',
          title: 'Kalender per Desa',
          description: 'Hasilnya dirangkum per desa menjadi musim tanam dan perkiraan panen.'
        }
      ]
    },
    validation: {
      title: 'Seberapa Tepat Datanya',
      body: (r: string, ratio: string, units: number) => `Luas dari satelit dibandingkan dengan luas panen BPS 2020 untuk ${units} desa, dengan korelasi ${r}. Satelit mencatat luas sekitar ${ratio} kali luas BPS, karena peta lahan pertanian juga mencakup jagung dan lahan kering.`,
      x: 'Luas panen BPS 2020 (ha)',
      y: 'Luas dari satelit (ha)',
      equal: 'Sama dengan BPS',
      readout: (unit: string, ref: string, sat: string) => `${unit}: BPS ${ref}, satelit ${sat}`,
      hint: 'Arahkan kursor ke titik untuk melihat nama desa.',
      columns: { unit: 'Desa', reference: 'BPS 2020', satellite: 'Satelit' }
    },
    limits: {
      title: 'Batas Data Ini',
      items: [
        'Tanggal tanam dan panen belum dicocokkan dengan catatan panen petani.',
        'Saat musim hujan, awan menutupi citra di awal musim, jadi perkiraan bisa meleset tiga sampai lima minggu. Saat kemarau, selisihnya sekitar satu sampai dua minggu.',
        'Sejak 2022 satelit radar lebih jarang melintas, jadi sebagian musim padi tidak terdeteksi.'
      ]
    }
  },

  ringkasan: {
    seoTitle: 'Ringkasan - Tanam Padi Lamongan',
    title: 'Ringkasan Sawah Tikung',
    description: (units: number, asOf: string) => `Kondisi sawah, jadwal tanam, dan perkiraan panen di ${units} desa. Data per ${asOf}.`,
    mapLoading: 'Memuat peta...',
    now: {
      title: 'Kondisi Sekarang'
    },
    schedule: {
      title: 'Jadwal Musim Tanam 1 Tiap Desa',
      body: 'Berdasarkan pola sejak 2017. Desa paling atas biasanya mulai tanam paling dulu.',
      plant: 'Puncak tanam',
      harvest: 'Puncak panen',
      today: 'Hari ini',
      readout: (unit: string, plant: string, harvest: string) => `${unit}: puncak tanam ${plant}, puncak panen ${harvest}`,
      hint: 'Arahkan kursor ke baris untuk melihat tanggalnya.'
    },
    harvest: {
      title: 'Panen 8 Minggu ke Depan',
      body: 'Desa dengan perkiraan panen paling cepat ada di atas.',
      row: (week: string, ha: string) => `Paling banyak minggu ${week}, total sekitar ${ha}`,
      empty: (month: string) => `Belum ada panen besar dalam 8 minggu ke depan. Panen musim berikutnya biasanya memuncak bulan ${month}.`
    },
    map: {
      title: 'Peta Sawah'
    },
    table: {
      title: 'Semua Desa',
      columns: {
        unit: 'Desa',
        paddy: 'Luas sawah',
        stage: 'Tahap sekarang',
        plant: 'Puncak tanam',
        harvest: 'Puncak panen'
      }
    }
  }
}
