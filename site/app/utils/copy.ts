// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// All user-facing text of the site lives here, so a rewrite touches one file.
// The site talks to local residents in a casual "kamu" register.
// Headings, buttons and chart titles use Title Case, while labels, body text and placeholders use sentence case.
// Text never names a colour, because colours come from the theme and can change.

export const COPY = {
  site: {
    title: 'Tanam Padi Lamongan',
    footer: 'Data diolah dari Copernicus Sentinel-1/2 (ESA), CHIRPS, ESA WorldCover, dan Lahan Baku Sawah (BIG). Batas wilayah: geoBoundaries (OCHA ROAP, BPS 2019), CC BY 3.0 IGO. Peta dasar: OpenFreeMap, © OpenStreetMap.'
  },

  nav: {
    ringkasan: 'Ringkasan',
    tentang: 'Tentang Data'
  },

  stages: {
    planted: 'Sedang ditanam',
    peaked: 'Menjelang panen',
    fallow: 'Bera',
    unknown: 'Tidak terbaca (awan)'
  },

  landing: {
    seoTitle: 'Tanam Padi Lamongan',
    eyebrow: 'Kecamatan Tikung, Lamongan',
    headline: 'Kapan Sawah di Desamu Mulai Ditanami?',
    description: (units: number) => `Lihat kondisi sawah di ${units} desa Tikung, kalender tanam tiap musim, dan hujan beberapa bulan terakhir.`,
    primaryCta: 'Cari Desamu',
    secondaryCta: 'Lihat Ringkasan',
    stats: {
      paddy: 'Luas sawah',
      units: 'Desa',
      season: 'Awal musim tanam 1',
      asOf: 'Data terakhir'
    },
    tableToggle: 'Lihat Tabel',
    mapLoading: 'Memuat peta...',

    pride: {
      title: 'Lamongan, Lumbung Padi Jawa Timur',
      body: (units: number, year: number) => `Pada ${year}, Lamongan jadi penghasil padi terbesar di Jawa Timur, tipis di atas Bojonegoro. Sawah di ${units} desa Tikung ikut menyumbang panen itu.`,
      chartTitle: (year: number) => `Produksi Padi ${year}, Lima Kabupaten Teratas`,
      unit: 'ribu ton gabah kering giling',
      rank: 'Peringkat 1',
      stats: {
        share: 'dari seluruh padi Jawa Timur',
        rice: 'beras dari Lamongan',
        harvest: 'sawah yang dipanen'
      },
      source: (year: number) => `Sumber: BPS Provinsi Jawa Timur, Luas Panen dan Produksi Padi di Provinsi Jawa Timur ${year}.`
    },

    now: {
      title: (resting: boolean) => (resting ? 'Sawah Menunggu Musim Tanam' : 'Musim Tanam Sedang Berjalan'),
      body: (resting: boolean, pct: string, date: string) => resting
        ? `Pada ${date}, ${pct} sawah sedang bera. Biasanya sawah mulai ditanami lagi setelah hujan turun.`
        : `Pada ${date}, ${pct} sawah sedang bera, sementara sisanya sedang ditanami atau menjelang panen.`,
      columns: { stage: 'Tahap', ha: 'Luas', share: 'Persen' }
    },

    calendar: {
      title: (month: string) => `Musim Tanam Utama Biasanya Mulai ${month}`,
      body: 'Tiap pita menunjukkan masa tanam sampai panen. Garis tegak menandai hari ini.',
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
      body: 'Ketik nama desamu, lalu pilih desa untuk melihat jadwal tanam dan perkiraan panen.',
      search: 'Ketik nama desa',
      empty: 'Desa tidak ditemukan. Coba ejaan lain.',
      paddy: (ha: string) => `${ha} sawah`
    }
  },

  tentang: {
    seoTitle: 'Tentang Data - Tanam Padi Lamongan',
    title: 'Tentang Data',
    description: 'Dari mana angka di situs ini berasal, seberapa tepat, dan apa saja batasnya.',
    facts: {
      units: 'desa dipantau',
      since: 'awal data citra',
      sinceValue: 'Okt 2017',
      match: 'selisih luas padi dengan BPS'
    },
    steps: {
      title: 'Cara Kerja',
      items: [
        {
          icon: 'i-lucide-satellite',
          title: 'Citra Radar dan Optik',
          description: 'Sentinel-2 merekam kehijauan tanaman. Sentinel-1 memakai radar, sehingga tetap bisa merekam sawah saat langit berawan.'
        },
        {
          icon: 'i-lucide-waves',
          title: 'Genangan dan Pertumbuhan',
          description: 'Sawah yang baru digenangi menandai awal tanam. Saat tanaman paling hijau, panen biasanya tinggal beberapa minggu lagi.'
        },
        {
          icon: 'i-lucide-calendar-check',
          title: 'Jadwal per Desa',
          description: 'Hasil dari tiap petak dijumlahkan per desa menjadi jadwal tanam dan perkiraan panen.'
        }
      ]
    },
    accuracy: {
      title: 'Seberapa Tepat?',
      body: (years: string, units: number) => `Luas sawah dari satelit dibandingkan dengan luas panen BPS di ${units} desa pada ${years}. Untuk padi, kedua angka hampir sama.`,
      crops: 'Luas semua tanaman dari satelit lebih besar, karena peta lahan pertanian juga memuat jagung dan tegalan.',
      rNote: 'Kecocokan antardesa bernilai 0 sampai 1. Makin dekat ke 1, makin mirip urutan desa dari satelit dengan urutan desa dari BPS.',
      scatterNote: (year: number) => `Titik di bawah adalah padi tahun ${year}. Data tahun tersebut tidak dipakai saat aturan deteksi padi dibuat.`,
      x: 'Luas panen padi BPS (ha)',
      y: 'Luas padi dari satelit (ha)',
      equal: 'Sama dengan BPS',
      readout: (unit: string, ref: string, sat: string) => `${unit}: BPS ${ref}, satelit ${sat}`,
      hint: 'Ketuk atau arahkan kursor ke titik untuk melihat nama desa.',
      cropNames: { rice: 'Padi', all_crops: 'Semua tanaman' } as Record<string, string>,
      summaryColumns: { year: 'Tahun', crop: 'Tanaman', r: 'Kecocokan antardesa', ratio: 'Luas satelit dibanding BPS' },
      columns: { unit: 'Desa', reference: 'BPS', satellite: 'Satelit' }
    },
    sources: {
      title: 'Sumber Data',
      items: [
        { name: 'Sentinel-2 (ESA)', role: 'Kehijauan tanaman' },
        { name: 'Sentinel-1 (ESA)', role: 'Genangan air, tembus awan' },
        { name: 'CHIRPS', role: 'Curah hujan bulanan' },
        { name: 'ESA WorldCover', role: 'Batas lahan pertanian' },
        { name: 'Lahan Baku Sawah (BIG)', role: 'Peta sawah resmi' },
        { name: 'BPS Kabupaten Lamongan', role: 'Luas panen pembanding' }
      ]
    },
    limits: {
      title: 'Batas Data Ini',
      items: [
        'Tanggal tanam dan panen belum dicocokkan dengan catatan petani.',
        'Saat musim hujan, awan sering menutupi awal musim, sehingga perkiraan bisa meleset tiga sampai lima minggu. Pada kemarau, selisihnya sekitar satu sampai dua minggu.',
        'Sejak 2022, satelit radar lebih jarang melintas. Akibatnya, sebagian musim padi tidak terdeteksi.'
      ]
    }
  },

  ringkasan: {
    seoTitle: 'Ringkasan - Tanam Padi Lamongan',
    title: 'Ringkasan Sawah Tikung',
    description: (units: number, asOf: string) => `Kondisi sawah, jadwal tanam, dan perkiraan panen di ${units} desa. Data terakhir: ${asOf}.`,
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
      hint: 'Ketuk atau arahkan kursor ke baris untuk melihat tanggal.'
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
  },

  desa: {
    seoTitle: (unit: string) => `Desa ${unit} - Tanam Padi Lamongan`,
    title: (unit: string) => `Desa ${unit}`,
    description: (ha: string, asOf: string) => `Luas sawah sekitar ${ha}. Data terakhir: ${asOf}.`,
    back: 'Semua Desa',
    notFound: 'Desa tidak ditemukan.',
    now: {
      title: 'Kondisi Sekarang'
    },
    schedule: {
      title: 'Jadwal Musim Tanam 1',
      body: 'Tanggal biasa berdasarkan pola sejak 2017.',
      plant: 'Puncak tanam',
      harvest: 'Puncak panen',
      none: 'Data musim lalu di desa ini belum cukup untuk membuat jadwal.'
    },
    harvest: {
      title: 'Panen 8 Minggu ke Depan',
      row: (week: string, ha: string) => `Minggu ${week}: sekitar ${ha}`,
      empty: 'Belum ada perkiraan panen dalam 8 minggu ke depan.'
    },
    map: {
      title: 'Letak Sawah'
    }
  }
}
