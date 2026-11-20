// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// All user-facing text of the site lives here, so a text change touches one file.
// The register follows the website of Kementerian Pertanian (pertanian.go.id).
// Text is formal and impersonal, and it never addresses the reader as "Anda".
// Headings and menu labels use Title Case, and body text uses sentence case.
// Abbreviations are written out in full, and numbers use the Indonesian format.
// Text never names a colour, because colours come from the theme and can change.

export const COPY = {
  site: {
    title: 'Kalender Tanam Padi',
    subtitle: 'Kecamatan Tikung, Kabupaten Lamongan',
    skip: 'Lewati ke Konten Utama',
    search: 'Cari Desa',
    updated: (generated: string, asOf: string) => `Diperbarui pada ${generated}. Citra satelit terakhir tanggal ${asOf}.`,
    footer: 'Data diolah dari Copernicus Sentinel-1/2 (ESA), CHIRPS, ESA WorldCover, dan Lahan Baku Sawah (BIG). Batas wilayah: geoBoundaries (OCHA ROAP, BPS 2019), CC BY 3.0 IGO. Peta dasar: OpenFreeMap, © OpenStreetMap.'
  },

  nav: {
    beranda: 'Beranda',
    kalender: 'Kalender Tanam',
    bandingkan: 'Perbandingan'
  },

  stages: {
    planted: 'Sedang Ditanami',
    peaked: 'Menjelang Panen',
    fallow: 'Bera',
    unknown: 'Tidak Terbaca (Tertutup Awan)'
  },

  onset: {
    title: 'Awal Tanam Dibanding Rata-rata 5 Musim',
    body: (year: number, n: number) => `Puncak tanam musim tanam 1 tahun ${year} dibandingkan dengan rata-rata ${n} musim sebelumnya. Batang ke kanan berarti lebih lambat, dan batang ke kiri berarti lebih awal.`,
    value: (d: number) => (d === 0 ? 'Sama dengan rata-rata' : d > 0 ? `${d} hari lebih lambat` : `${-d} hari lebih awal`),
    card: (year: number, plant: string, mean: string) => `Awal tanam musim tanam 1 tahun ${year}: ${plant}. Rata-rata sebelumnya: ${mean}.`,
    note: 'Selisih dihitung dari puncak penggenangan sawah yang terbaca radar, sehingga dapat meleset beberapa minggu. Tanda terlambat muncul pada selisih 14 hari atau lebih.',
    late: 'Terlambat',
    lateAfter: 14,
    columns: { unit: 'Desa', plant: 'Puncak Tanam', mean: 'Rata-rata Sebelumnya', shift: 'Selisih (hari)' }
  },

  stageHelp: {
    planted: 'Padi sudah ditanam dan sedang tumbuh.',
    peaked: 'Tanaman berada pada puncak kehijauan. Panen biasanya tinggal beberapa minggu lagi.',
    fallow: 'Lahan setelah panen dan belum ditanami kembali.',
    unknown: 'Awan menutupi lahan sehingga satelit tidak dapat membaca kondisinya.'
  },

  tip: {
    wetter: (p: string) => `${p} lebih basah dari rata-rata`,
    drier: (p: string) => `${p} lebih kering dari rata-rata`,
    average: 'Sama dengan rata-rata',
    plant: 'Puncak tanam',
    harvest: 'Puncak panen',
    start: 'Awal tanam',
    end: 'Akhir panen',
    days: (n: number) => `${n} hari`,
    span: 'Lama dari tanam sampai panen',
    since: 'Berdasarkan pola musim tanam sejak tahun 2017.',
    reference: 'BPS',
    satellite: 'Satelit',
    diff: 'Selisih',
    mapHint: 'Pilih untuk melihat jadwal desa.',
    today: (date: string) => `Per ${date}`,
    range: 'Rentang sejak 2017'
  },

  landing: {
    seoTitle: 'Kalender Tanam Padi Kecamatan Tikung',
    eyebrow: 'Kecamatan Tikung, Kabupaten Lamongan',
    headline: 'Informasi Musim Tanam Padi di Kecamatan Tikung',
    description: (units: number) => `Informasi kondisi sawah, jadwal tanam, dan perkiraan panen di ${units} desa Kecamatan Tikung berdasarkan pemantauan citra satelit.`,
    primaryCta: 'Cari Desa',
    secondaryCta: 'Lihat Kalender Tanam',
    stats: {
      paddy: 'Luas Sawah',
      units: 'Jumlah Desa',
      season: 'Awal Musim Tanam 1',
      asOf: 'Tanggal Acuan'
    },
    tableToggle: 'Tampilkan Tabel',
    mapLoading: 'Memuat peta…',
    mapLabel: 'Peta petak sawah dan batas wilayah',
    mapFailed: 'Peta tidak dapat ditampilkan pada perangkat ini. Seluruh angka tetap tersedia pada halaman ini.',

    pride: {
      title: 'Lamongan, Lumbung Padi Jawa Timur',
      body: (units: number, year: number) => `Pada tahun ${year}, Kabupaten Lamongan menjadi penghasil padi terbesar di Provinsi Jawa Timur, unggul tipis dari Kabupaten Bojonegoro. Sawah di ${units} desa Kecamatan Tikung turut berkontribusi terhadap capaian tersebut.`,
      chartTitle: (year: number) => `Produksi Padi Tahun ${year}, Lima Kabupaten Teratas`,
      unit: 'ribu ton gabah kering giling',
      rank: '#1',
      stats: {
        share: 'dari seluruh produksi padi Jawa Timur',
        rice: 'produksi beras Kabupaten Lamongan',
        harvest: 'luas panen padi'
      },
      source: (year: number) => `Sumber: BPS Provinsi Jawa Timur, Luas Panen dan Produksi Padi di Provinsi Jawa Timur ${year}.`
    },

    now: {
      title: (resting: boolean) => (resting ? 'Lahan Sawah Menunggu Musim Tanam' : 'Musim Tanam Sedang Berlangsung'),
      body: (resting: boolean, pct: string, date: string) => resting
        ? `Per ${date}, sebanyak ${pct} lahan sawah berstatus bera. Penanaman umumnya dimulai kembali setelah hujan turun.`
        : `Per ${date}, sebanyak ${pct} lahan sawah berstatus bera, sedangkan sisanya sedang ditanami atau menjelang panen.`,
      columns: { stage: 'Tahap', ha: 'Luas', share: 'Persentase' }
    },

    calendar: {
      title: (month: string) => `Musim Tanam Utama Umumnya Dimulai pada Bulan ${month}`,
      body: 'Setiap baris menunjukkan satu musim tanam, yang terbagi atas tahap tanam, tumbuh, dan panen. Baris paling bawah menandai tanggal hari ini.',
      today: 'Hari ini',
      plant: 'Puncak Tanam',
      harvest: 'Puncak Panen',
      phases: { sow: 'Tanam', grow: 'Tumbuh', harvest: 'Panen' },
      readout: (season: string, from: string, to: string, plant: string, harvest: string) => `${season}: ${from} sampai ${to}. Puncak tanam ${plant}, puncak panen ${harvest}.`,
      seasons: { MT1: 'Musim Tanam 1', MT2: 'Musim Tanam 2', MT3: 'Musim Tanam 3' },
      seasonNote: { MT1: 'Musim utama', MT2: 'Musim kedua', MT3: 'Tidak setiap tahun' },
      columns: { season: 'Musim', start: 'Awal Tanam', plant: 'Puncak Tanam', harvest: 'Puncak Panen', end: 'Akhir Panen' }
    },

    rain: {
      title: 'Curah Hujan 12 Bulan Terakhir',
      body: (month: string, mm: string, normal: string) => `Curah hujan bulan ${month} tercatat ${mm} mm, sedangkan rata-rata bulan tersebut sekitar ${normal} mm.`,
      actual: 'Curah hujan',
      normal: 'Rata-rata 5 tahun',
      band: 'Rentang sejak 2017',
      readout: (label: string, mm: string, normal: string) => `${label}: ${mm} mm, rata-rata ${normal} mm`,
      columns: { month: 'Bulan', mm: 'Curah Hujan (mm)', normal: 'Rata-rata 5 Tahun (mm)', lo: 'Terendah (mm)', hi: 'Tertinggi (mm)' }
    },

    progress: {
      title: 'Kemajuan Musim Tanam 1',
      inSeason: (pct: string, from: string, to: string) => `${pct} dari musim tanam 1 telah berjalan, dengan rentang ${from} sampai ${to}.`,
      outside: (from: string) => `Musim tanam 1 belum dimulai. Awal tanam umumnya pada bulan ${from}.`,
      label: (pct: string) => `Kemajuan musim ${pct}`
    },

    schedule: {
      title: 'Jadwal Tanam dan Panen Setiap Desa',
      body: 'Jadwal disusun dari pola musim tanam sejak tahun 2017. Desa yang berada paling atas umumnya memulai tanam lebih awal.',
      today: 'Hari ini',
      readout: (unit: string, plant: string, harvest: string) => `${unit}: puncak tanam ${plant}, puncak panen ${harvest}`,
      hint: 'Pilih atau arahkan kursor ke batang untuk melihat tanggal.',
      legend: 'Rentang dari puncak tanam sampai puncak panen.',
      columns: { unit: 'Desa', plant: 'Puncak Tanam', harvest: 'Puncak Panen' }
    },

    harvest: {
      title: 'Perkiraan Panen 8 Minggu ke Depan',
      body: 'Desa dengan perkiraan panen paling awal berada di urutan teratas.',
      row: (week: string, ha: string) => `Panen terbanyak minggu ${week}, total sekitar ${ha}`,
      empty: (month: string) => `Belum terdapat panen besar dalam 8 minggu ke depan. Panen musim berikutnya umumnya mencapai puncak pada bulan ${month}.`
    },

    desa: {
      title: 'Cari Desa',
      body: 'Masukkan nama desa, kemudian pilih desa untuk melihat jadwal tanam dan perkiraan panen.',
      search: 'Masukkan nama desa, misalnya Jotosanur…',
      empty: 'Desa tidak ditemukan. Periksa kembali penulisan nama desa.',
      paddy: (ha: string) => `Luas sawah ${ha}`
    },

    more: {
      title: 'Informasi Lainnya',
      items: [
        { to: '/kalender', icon: 'i-lucide-calendar-days', title: 'Kalender Tanam', description: 'Jadwal tanam dan panen setiap desa, curah hujan, serta catatan penggunaan data.' },
        { to: '/perbandingan', icon: 'i-lucide-chart-bar', title: 'Perbandingan Wilayah', description: 'Peringkat desa di Kecamatan Tikung dan kecamatan di Kabupaten Lamongan, beserta ketepatan data.' }
      ]
    }
  },

  kalender: {
    seoTitle: 'Jadwal Tanam dan Panen Desa - Kalender Tanam Padi',
    title: 'Kalender Tanam',
    description: 'Jadwal tanam dan panen setiap desa di Kecamatan Tikung, disertai curah hujan dan catatan penggunaan data.',
    notes: {
      title: 'Catatan Penggunaan Data',
      body: 'Jadwal merupakan perkiraan dari citra satelit dan bukan pengganti informasi dari penyuluh pertanian.',
      items: [
        'Tanggal tanam dan panen belum dicocokkan dengan catatan petani.',
        'Pada musim hujan, awan sering menutupi awal musim sehingga perkiraan dapat meleset tiga sampai lima minggu. Pada musim kemarau, selisihnya sekitar satu sampai dua minggu.',
        'Sejak tahun 2022, satelit radar lebih jarang melintas sehingga sebagian musim tanam padi tidak terdeteksi.'
      ]
    }
  },

  bandingkan: {
    seoTitle: 'Perbandingan Wilayah - Kalender Tanam Padi',
    title: 'Perbandingan Wilayah',
    description: 'Peringkat desa dan kecamatan menurut luas sawah, frekuensi tanam padi, dan lahan sawah yang sedang hijau.',
    levels: { desa: 'Desa di Kecamatan Tikung', kecamatan: 'Kecamatan di Kabupaten Lamongan' },
    metricLabel: 'Dibandingkan berdasarkan',
    metrics: {
      sawah: {
        label: 'Luas Sawah',
        title: 'Peringkat Menurut Luas Sawah',
        body: 'Luas sawah menurut peta Lahan Baku Sawah.',
        value: (v: number) => `${Math.round(v).toLocaleString('id-ID')} ha`
      },
      intensitas: {
        label: 'Frekuensi Tanam',
        title: (year: number | null) => `Peringkat Menurut Frekuensi Tanam Padi Tahun ${year ?? '-'}`,
        body: 'Rata-rata frekuensi tanam padi dalam satu tahun. Angka 2 berarti sawah ditanami dua kali dalam setahun.',
        value: (v: number) => `${v.toLocaleString('id-ID', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} kali`
      },
      tumbuh: {
        label: 'Sawah Hijau',
        title: 'Peringkat Menurut Sawah yang Sedang Hijau',
        body: 'Bagian sawah yang sedang ditanami atau menjelang panen. Sawah yang tertutup awan tidak diperhitungkan.',
        value: (v: number) => v.toLocaleString('id-ID', { style: 'percent', maximumFractionDigits: 0 })
      }
    },
    rank: (n: number) => `${n}.`,
    here: 'Tikung',
    tikungRank: (i: number, n: number) => `Kecamatan Tikung berada pada urutan ${i} dari ${n} kecamatan.`,
    kecamatanNote: (ratio: string, year: number) => `Untuk kecamatan lain, satelit membaca sekitar ${ratio} dari luas padi menurut dinas pertanian pada tahun ${year}. Urutan masih dapat digunakan, tetapi angka belum dapat dijadikan acuan.`,
    empty: 'Data untuk perbandingan ini belum tersedia.',

    accuracy: {
      title: 'Ketepatan Data',
      body: (years: string, units: number) => `Luas sawah hasil pemantauan satelit dibandingkan dengan luas panen BPS di ${units} desa pada tahun ${years}. Untuk tanaman padi, kedua angka hampir sama.`,
      crops: 'Luas seluruh tanaman dari satelit lebih besar karena peta lahan pertanian juga memuat jagung dan tegalan.',
      rNote: 'Kecocokan antardesa bernilai 0 sampai 1. Semakin mendekati 1, semakin mirip urutan desa dari satelit dengan urutan desa dari BPS.',
      scatterNote: (year: number) => `Titik pada grafik menunjukkan luas padi tahun ${year}. Data tahun tersebut tidak digunakan saat aturan deteksi padi disusun.`,
      x: 'Luas panen padi BPS (ha)',
      y: 'Luas padi dari satelit (ha)',
      equalNote: 'Garis putus-putus menunjukkan luas satelit sama dengan luas BPS.',
      readout: (unit: string, ref: string, sat: string) => `${unit}: BPS ${ref}, satelit ${sat}`,
      hint: 'Pilih atau arahkan kursor ke titik untuk melihat nama desa.',
      cropNames: { rice: 'Padi', all_crops: 'Seluruh Tanaman' } as Record<string, string>,
      summaryColumns: { year: 'Tahun', crop: 'Tanaman', r: 'Kecocokan Antardesa', ratio: 'Luas Satelit terhadap BPS' },
      columns: { unit: 'Desa', reference: 'BPS', satellite: 'Satelit' }
    }
  },

  desa: {
    seoTitle: (unit: string) => `Desa ${unit} - Kalender Tanam Padi`,
    title: (unit: string) => `Desa ${unit}`,
    description: (ha: string, asOf: string) => `Luas sawah sekitar ${ha}. Data terakhir: ${asOf}.`,
    back: 'Daftar Desa',
    notFound: 'Desa tidak ditemukan.',
    now: {
      title: 'Kondisi Terkini'
    },
    schedule: {
      title: 'Jadwal Musim Tanam 1',
      body: 'Tanggal umum berdasarkan pola musim tanam sejak tahun 2017.',
      plant: 'Puncak Tanam',
      harvest: 'Puncak Panen',
      none: 'Data musim tanam sebelumnya di desa ini belum cukup untuk menyusun jadwal.'
    },
    harvest: {
      title: 'Perkiraan Panen 8 Minggu ke Depan',
      row: (week: string, ha: string) => `Minggu ${week}: sekitar ${ha}`,
      empty: 'Belum terdapat perkiraan panen dalam 8 minggu ke depan.'
    },
    compare: {
      title: 'Perbandingan dengan Desa Lain',
      body: 'Urutan desa ini di antara desa di Kecamatan Tikung. Urutan 1 berarti yang tertinggi.',
      place: (place: number, total: number) => `${place} dari ${total}`,
      link: 'Lihat Perbandingan Seluruh Desa'
    },
    map: {
      title: 'Letak Sawah'
    }
  }
}
