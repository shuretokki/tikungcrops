// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// All user-facing text of the site lives here, so a rewrite touches one file.

export const COPY = {
  site: {
    title: 'Tanam Padi Lamongan',
    footer: 'Data turunan Copernicus Sentinel-1/2 (ESA), CHIRPS, ESA WorldCover, Lahan Baku Sawah (BIG). Batas wilayah: geoBoundaries (OCHA ROAP, BPS 2019), CC BY 3.0 IGO. Peta dasar: OpenFreeMap, © OpenStreetMap.'
  },

  nav: {
    ringkasan: 'Ringkasan',
    perbandingan: 'Perbandingan',
    metode: 'Metode',
    data: 'Data'
  },

  landing: {
    seoTitle: 'Tanam Padi Lamongan',
    headline: 'Pantau musim tanam padi dari satelit',
    description: 'Lihat desa mana yang sedang menanam dan kapan panen diperkirakan tiba. Data diperbarui dari citra satelit, tanpa survei lapangan.',
    primaryCta: 'Lihat ringkasan',
    secondaryCta: 'Baca cara kerjanya',
    stats: {
      paddy: 'Sawah dipantau',
      units: 'Desa di Kecamatan Tikung',
      asOf: 'Data terakhir'
    },
    featuresTitle: 'Yang bisa Anda lihat',
    features: [
      {
        title: 'Tahap tanam hari ini',
        description: 'Luas sawah yang sedang ditanam dan yang menjelang panen, per desa.',
        icon: 'i-lucide-sprout',
        to: '/ringkasan'
      },
      {
        title: 'Perkiraan panen',
        description: 'Minggu dengan panen terbanyak di musim berjalan, untuk tiap desa.',
        icon: 'i-lucide-calendar-range',
        to: '/ringkasan'
      },
      {
        title: 'Perbandingan antardesa',
        description: 'Bandingkan luas tanam dan jumlah musim per tahun sejak 2017.',
        icon: 'i-lucide-chart-column',
        to: '/perbandingan'
      },
      {
        title: 'Data terbuka',
        description: 'Unduh tabel dan peta yang dipakai di situs ini.',
        icon: 'i-lucide-download',
        to: '/data'
      }
    ],
    limitsTitle: 'Batas data ini',
    limits: 'Tanggal tanam dan panen berasal dari deteksi satelit, belum dicek dengan catatan panen petani. Hasilnya sudah dibandingkan dengan data BPS dan KSA, tetapi tetap bisa meleset beberapa minggu saat musim hujan.',
    limitsCta: 'Baca metode'
  },

  ringkasan: {
    seoTitle: 'Ringkasan - Tanam Padi Lamongan',
    title: 'Musim tanam padi hari ini',
    description: (asOf: string) => `Kecamatan Tikung, 13 desa, dari citra satelit sampai ${asOf}. Klik desa di peta atau tabel untuk rinciannya.`,
    paddy: 'Sawah dipantau',
    outlook: 'Perkiraan panen, musim berjalan',
    mapLoading: 'Memuat peta...',
    alertTitle: 'Perkiraan musim hujan masih kasar',
    alert: 'Tanggal berasal dari deteksi satelit, belum dicek dengan catatan panen petani. Pada musim hujan awan menutupi awal musim, jadi perkiraan bisa meleset 3-5 minggu. Musim kemarau meleset sekitar 1-2 minggu.',
    columns: {
      unit: 'Desa',
      paddy: 'Sawah',
      outlook: 'Perkiraan panen',
      topWeek: 'Minggu terbanyak'
    }
  }
}
