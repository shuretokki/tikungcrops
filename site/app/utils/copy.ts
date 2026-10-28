// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// All user-facing text of the site lives here, so a rewrite touches one file.
// Data pages show data only. Sources, method and limits belong on the Tentang page.

export const COPY = {
  site: {
    title: 'Tanam Padi Lamongan',
    footer: 'Data diolah dari Copernicus Sentinel-1/2 (ESA), CHIRPS, ESA WorldCover, dan Lahan Baku Sawah (BIG). Batas wilayah: geoBoundaries (OCHA ROAP, BPS 2019), CC BY 3.0 IGO. Peta dasar: OpenFreeMap, © OpenStreetMap.'
  },

  nav: {
    ringkasan: 'Ringkasan',
    perbandingan: 'Perbandingan',
    data: 'Data',
    tentang: 'Tentang'
  },

  stages: {
    planted: 'Ditanami',
    peaked: 'Menjelang panen',
    fallow: 'Bera',
    unknown: 'Tertutup awan'
  },

  seasons: { MT1: 'Musim 1', MT2: 'Musim 2', MT3: 'Musim 3' },

  common: {
    asOf: (date: string) => `Data per ${date}`,
    tableToggle: 'Tampilkan tabel',
    mapLoading: 'Memuat peta...'
  },

  landing: {
    seoTitle: 'Tanam Padi Lamongan',
    title: 'Sawah Kecamatan Tikung',
    cta: 'Buka ringkasan',
    stats: {
      paddy: 'Luas sawah',
      units: 'Desa',
      fallow: 'Bera',
      next: 'Musim 1 dimulai'
    },
    stage: {
      title: 'Tahap tanam',
      columns: { stage: 'Tahap', ha: 'Luas', share: 'Bagian' }
    },
    calendar: {
      title: 'Kalender tanam',
      plant: 'Puncak tanam',
      harvest: 'Puncak panen',
      today: 'Hari ini',
      columns: { season: 'Musim', start: 'Awal tanam', plant: 'Puncak tanam', harvest: 'Puncak panen', end: 'Akhir panen' }
    },
    intensity: {
      title: 'Musim tanam per tahun',
      average: (v: string) => `Rata-rata ${v}`,
      readout: (year: number, v: string) => `${year}: ${v} musim`,
      columns: { year: 'Tahun', value: 'Musim per tahun' }
    },
    desa: { title: 'Desa' }
  },

  ringkasan: {
    seoTitle: 'Ringkasan - Tanam Padi Lamongan',
    title: 'Ringkasan',
    paddy: 'Luas sawah',
    outlook: 'Perkiraan panen',
    columns: {
      unit: 'Desa',
      paddy: 'Luas sawah',
      outlook: 'Perkiraan panen',
      topWeek: 'Puncak panen'
    }
  },

  tentang: {
    seoTitle: 'Tentang - Tanam Padi Lamongan',
    title: 'Tentang',
    description: 'Sumber data, cara kerja, ketepatan, dan keterbatasan situs ini.',
    sources: {
      title: 'Sumber data',
      body: 'Situs ini memakai citra satelit Sentinel-1 dan Sentinel-2 dari program Copernicus. Data hujan berasal dari CHIRPS, sedangkan peta sawah berasal dari Lahan Baku Sawah (BIG). Pengamatan dimulai pada Oktober 2017 dan diperbarui setiap bulan.'
    },
    steps: {
      title: 'Cara kerja',
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
          description: 'Hasilnya dirangkum per desa menjadi musim tanam, jumlah musim per tahun, dan perkiraan panen.'
        }
      ]
    },
    validation: {
      title: 'Ketepatan',
      body: (r: string, ratio: string) => `Luas dari satelit dibandingkan dengan luas panen BPS tahun 2020 untuk tiga belas desa. Korelasinya ${r}. Satelit mencatat luas sekitar ${ratio} kali luas BPS karena peta lahan pertanian juga mencakup jagung dan lahan kering.`,
      x: 'Luas panen BPS 2020 (ha)',
      y: 'Luas dari satelit (ha)',
      equal: 'Sama dengan BPS',
      readout: (unit: string, ref: string, sat: string) => `${unit}: BPS ${ref}, satelit ${sat}`,
      hint: 'Arahkan kursor ke titik untuk melihat nama desa.',
      columns: { unit: 'Desa', reference: 'BPS 2020', satellite: 'Satelit' }
    },
    limits: {
      title: 'Keterbatasan',
      items: [
        'Tanggal tanam dan panen belum dicocokkan dengan catatan panen petani.',
        'Pada musim hujan, awan menutupi citra pada awal musim sehingga perkiraan dapat meleset tiga hingga lima minggu. Pada musim kemarau, selisihnya sekitar satu hingga dua minggu.',
        'Sejak 2022 satelit radar lebih jarang melintas sehingga sebagian musim padi tidak terdeteksi.',
        'Jumlah musim per tahun dari satelit lebih tinggi daripada angka BPS 2020 (2,18 berbanding 1,62), jadi angka ini sebaiknya dibaca sebagai batas atas.'
      ]
    }
  }
}
