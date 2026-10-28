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
    headline: 'Pemantauan musim tanam padi melalui citra satelit',
    description: 'Situs ini menunjukkan desa yang sedang menanam padi dan perkiraan waktu panennya. Semua data berasal dari citra satelit sehingga tidak memerlukan survei lapangan.',
    primaryCta: 'Lihat ringkasan',
    secondaryCta: 'Pelajari metode',
    stats: {
      paddy: 'Luas sawah yang dipantau',
      units: 'Jumlah desa di Kecamatan Tikung',
      asOf: 'Tanggal data terakhir'
    },
    featuresTitle: 'Informasi yang tersedia',
    features: [
      {
        title: 'Tahap tanam saat ini',
        description: 'Luas sawah yang sedang ditanami dan yang menjelang panen di setiap desa.',
        icon: 'i-lucide-sprout',
        to: '/ringkasan'
      },
      {
        title: 'Perkiraan panen',
        description: 'Minggu dengan luas panen terbesar pada musim berjalan di setiap desa.',
        icon: 'i-lucide-calendar-range',
        to: '/ringkasan'
      },
      {
        title: 'Perbandingan antardesa',
        description: 'Perbandingan luas tanam dan jumlah musim tanam per tahun sejak 2017.',
        icon: 'i-lucide-chart-column',
        to: '/perbandingan'
      },
      {
        title: 'Data terbuka',
        description: 'Tabel dan peta yang digunakan di situs ini dapat diunduh.',
        icon: 'i-lucide-download',
        to: '/data'
      }
    ],
    limitsTitle: 'Keterbatasan data',
    limits: 'Tanggal tanam dan panen diperoleh dari deteksi satelit dan belum dicocokkan dengan catatan panen petani. Hasilnya sudah dibandingkan dengan data BPS dan KSA. Meskipun demikian, perkiraan pada musim hujan masih dapat meleset beberapa minggu.',
    limitsCta: 'Baca metode lengkap'
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
