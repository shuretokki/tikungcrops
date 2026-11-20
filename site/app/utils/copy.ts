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
    title: 'Kalender Tanam Lamongan',
    subtitle: 'Pemantauan musim tanam dari satelit',
    skip: 'Lewati ke Konten Utama',
    search: 'Cari Desa',
    download: {
      label: 'Unduh data (JSON)',
      files: [
        { label: 'Ringkasan desa', file: 'meta.json' },
        { label: 'Kondisi sawah', file: 'current.json' },
        { label: 'Prakiraan panen', file: 'outlook.json' },
        { label: 'Musim tanam', file: 'seasons.json' },
        { label: 'Curah hujan', file: 'rain.json' },
        { label: 'Kali tanam', file: 'intensity.json' },
        { label: 'Ketepatan data', file: 'validation.json' },
        { label: 'Batas desa', file: 'boundaries.geojson' }
      ]
    },
    updated: (generated: string, asOf: string) => `Diperbarui pada ${generated}. Data per ${asOf}.`,
    footer: {
      pages: 'Halaman',
      data: 'Unduh Data',
      info: 'Informasi',
      infoLinks: [
        { label: 'Tentang Situs', to: '/tentang' },
        { label: 'Sumber Data', to: '/tentang#sumber' },
        { label: 'Catatan Penggunaan Data', to: '/tentang#catatan' },
        { label: 'Tanya Jawab (FAQ)', to: '/faq' }
      ],
      copyright: 'Copyright © 2026 Tri Rianto Utomo'
    }
  },

  nav: {
    beranda: 'Beranda',
    kalender: 'Kalender Tanam',
    bandingkan: 'Perbandingan',
    tentang: 'Tentang',
    faq: 'FAQ'
  },

  // The pick lists follow the entry steps of the FAO Crop Calendar: choose the place, choose the crop, then search.
  // Only rice in Kecamatan Tikung is finished. The other choices are listed so the site is ready for them.
  // Crops follow KATAM Terpadu (padi, jagung, kedelai) and the five crops of ASEAN AFSIS (padi, jagung, tebu, kedelai, singkong).
  scope: {
    title: 'Pilih Wilayah dan Tanaman',
    region: 'Wilayah',
    crop: 'Tanaman',
    soon: 'segera',
    regions: [
      { value: 'tikung', label: 'Kecamatan Tikung', ready: true },
      { value: 'kecamatan', label: 'Kecamatan lain di Lamongan', ready: false },
      { value: 'lamongan', label: 'Seluruh Kabupaten Lamongan', ready: false }
    ],
    crops: [
      { value: 'padi', label: 'Padi', ready: true },
      { value: 'jagung', label: 'Jagung', ready: false },
      { value: 'kedelai', label: 'Kedelai', ready: false },
      { value: 'tebu', label: 'Tebu', ready: false },
      { value: 'singkong', label: 'Singkong', ready: false }
    ],
    note: 'Pilihan bertanda segera sedang disiapkan.',
    go: 'Lihat Kalender Tanam'
  },

  tentang: {
    seoTitle: 'Tentang Situs - Kalender Tanam Lamongan',
    eyebrow: 'Tentang',
    title: 'Untuk Apa Situs Ini?',
    purpose: [
      'Kalender Tanam Lamongan menampilkan kondisi sawah, jadwal tanam, dan perkiraan panen dari citra satelit, sampai tingkat desa. Informasi ini membantu petani, penyuluh pertanian, dan dinas merencanakan tanam, menyiapkan benih dan pupuk, serta memperkirakan kapan panen datang.',
      'Situs ini hasil penelitian mahasiswa dan belum menggantikan layanan resmi, seperti Kalender Tanam Terpadu (KATAM) milik Kementerian Pertanian.'
    ],
    helps: {
      title: 'Siapa yang Terbantu',
      items: [
        { icon: 'i-lucide-sprout', title: 'Petani', body: 'Melihat kapan desa mulai menanam dan kapan panen biasanya datang.' },
        { icon: 'i-lucide-users', title: 'Penyuluh pertanian', body: 'Memantau kondisi dan awal tanam setiap desa binaan.' },
        { icon: 'i-lucide-landmark', title: 'Dinas pertanian', body: 'Membandingkan desa dan kecamatan untuk perencanaan benih, pupuk, dan panen.' },
        { icon: 'i-lucide-microscope', title: 'Peneliti', body: 'Mengunduh data dan memeriksa ketepatannya terhadap data BPS.' }
      ]
    },
    how: {
      title: 'Cara Memakai',
      steps: [
        'Pilih wilayah dan tanaman pada halaman Beranda.',
        'Buka Kalender Tanam untuk melihat musim tanam utama, jadwal setiap desa, awal tanam, dan curah hujan.',
        'Buka halaman desa untuk melihat kondisi, jadwal, riwayat musim, dan perkiraan panen desa tersebut.',
        'Bandingkan desa atau kecamatan pada halaman Perbandingan.',
        'Unduh data dalam bentuk JSON dari bagian bawah halaman.'
      ]
    },
    coverage: {
      title: 'Cakupan Saat Ini dan Rencana',
      columns: { item: 'Cakupan', status: 'Status', note: 'Keterangan' },
      ready: 'Tersedia',
      planned: 'Disiapkan',
      rows: [
        { item: 'Padi di Kecamatan Tikung', ready: true, note: '13 desa, data citra sejak Oktober 2017.' },
        { item: 'Padi di kecamatan lain di Lamongan', ready: false, note: 'Data 27 kecamatan sudah diolah dan baru tampil pada halaman Perbandingan.' },
        { item: 'Jagung, kedelai, tebu, dan singkong', ready: false, note: 'Belum diolah. Aturan deteksi saat ini khusus padi.' }
      ]
    },
    sources: {
      title: 'Sumber Data',
      items: [
        { name: 'Copernicus Sentinel-1 (ESA)', href: 'https://sentiwiki.copernicus.eu/web/s1-mission' },
        { name: 'Copernicus Sentinel-2 (ESA)', href: 'https://sentiwiki.copernicus.eu/web/s2-mission' },
        { name: 'CHIRPS', href: 'https://www.chc.ucsb.edu/data/chirps' },
        { name: 'ESA WorldCover', href: 'https://esa-worldcover.org' },
        { name: 'Lahan Baku Sawah (BIG)', href: 'https://www.big.go.id' },
        { name: 'BPS dan Dinas Pertanian Kabupaten Lamongan', href: 'https://lamongankab.bps.go.id' },
        { name: 'geoBoundaries (OCHA ROAP, BPS 2019), CC BY 3.0 IGO', href: 'https://www.geoboundaries.org' },
        { name: 'OpenFreeMap, © OpenStreetMap contributors', href: 'https://openfreemap.org' }
      ]
    },
    notes: {
      title: 'Catatan Penggunaan Data',
      body: 'Jadwal merupakan perkiraan dari citra satelit dan bukan pengganti informasi dari penyuluh pertanian.',
      items: [
        'Tanggal tanam dan panen belum dicocokkan dengan catatan petani.',
        'Pada musim hujan, awan sering menutupi awal musim sehingga perkiraan dapat meleset tiga sampai lima minggu. Pada musim kemarau, selisihnya sekitar satu sampai dua minggu.',
        'Sejak tahun 2022, satelit radar lebih jarang melintas sehingga sebagian musim tanam padi tidak terdeteksi.'
      ]
    },
    faqLink: 'Baca Tanya Jawab (FAQ)'
  },

  faq: {
    seoTitle: 'Tanya Jawab - Kalender Tanam Lamongan',
    title: 'Tanya Jawab',
    description: 'Jawaban singkat untuk pertanyaan yang sering muncul tentang Kalender Tanam Lamongan.',
    items: [
      { q: 'Apa itu Kalender Tanam Lamongan?', a: ['Situs yang menampilkan kondisi sawah, jadwal tanam, dan perkiraan panen dari citra satelit Sentinel-1 dan Sentinel-2, sampai tingkat desa. Saat ini tersedia untuk padi di Kecamatan Tikung.'] },
      { q: 'Untuk siapa situs ini?', a: ['Untuk petani, penyuluh pertanian, dinas pertanian, dan peneliti. Penjelasan lengkap ada pada halaman Tentang.'] },
      { q: 'Wilayah dan tanaman apa yang tersedia?', a: ['Padi di 13 desa Kecamatan Tikung. Data kecamatan lain di Kabupaten Lamongan sudah diolah dan baru tampil pada halaman Perbandingan. Jagung, kedelai, tebu, dan singkong sedang disiapkan dan belum dapat dipilih.'] },
      { q: 'Dari mana datanya?', a: ['Dari citra satelit Sentinel-1 dan Sentinel-2 milik Badan Antariksa Eropa, curah hujan CHIRPS, peta Lahan Baku Sawah dari Badan Informasi Geospasial, dan data panen pembanding dari BPS serta dinas pertanian. Daftar lengkap ada pada bagian Sumber Data di halaman Tentang.'] },
      { q: 'Seberapa sering data diperbarui?', a: ['Pengambilan citra dijadwalkan setiap bulan. Tanggal citra terakhir tertera pada penanda tanggal di halaman dan pada bagian bawah setiap halaman.'] },
      { q: 'Mengapa citra terakhir lebih lama dari hari ini?', a: ['Satelit melintas pada selang waktu tertentu, awan sering menutupi citra optik, dan pengolahan memerlukan waktu. Karena itu data selalu tertinggal dari hari ini.'] },
      { q: 'Bagaimana tahap sedang ditanami, menjelang panen, dan bera ditentukan?', a: ['Radar Sentinel-1 mendeteksi genangan saat penanaman, dan citra optik Sentinel-2 mengukur kehijauan tanaman. Tanaman yang paling hijau berarti panen biasanya tinggal beberapa minggu lagi. Lahan tanpa tanaman setelah panen disebut bera.'] },
      { q: 'Mengapa sebagian sawah tidak terbaca?', a: ['Awan menutupi lahan sehingga satelit optik tidak dapat membaca kondisinya. Luas yang tertutup awan tidak dihitung dalam persentase.'] },
      { q: 'Seberapa tepat jadwal tanam dan panen?', a: ['Jadwal merupakan perkiraan dari pola musim tanam sejak tahun 2017. Pada musim hujan, awan dapat menggeser perkiraan tiga sampai lima minggu, dan pada musim kemarau sekitar satu sampai dua minggu. Tanggal belum dicocokkan dengan catatan petani.'] },
      { q: 'Seberapa tepat luas sawah dan padi?', a: ['Di Kecamatan Tikung, luas padi dari satelit mendekati data BPS per desa. Hasilnya dapat dilihat pada bagian Ketepatan Data di halaman Perbandingan.', 'Untuk kecamatan lain, luas semua tanaman dari satelit berbeda sekitar 17 persen (median) dari luas panen menurut dinas pertanian pada tahun 2021. Penanda padi masih melewatkan sebagian padi tadah hujan dan padi tabur benih.'] },
      { q: 'Apa arti awal tanam lebih lambat dari rata-rata?', a: ['Puncak tanam musim tanam 1 terakhir dibandingkan dengan rata-rata lima musim sebelumnya, dengan syarat minimal tiga musim. Selisih 14 hari atau lebih diberi tanda terlambat. Selisih dihitung dari radar sehingga dapat meleset beberapa minggu.'] },
      { q: 'Mengapa frekuensi tanam tidak sama dengan jumlah panen padi?', a: ['Frekuensi tanam menghitung semua musim tanam yang terbaca pada peta sawah, tidak hanya padi. Cara ini dipilih karena penanda padi melewatkan sebagian padi di beberapa kecamatan.'] },
      { q: 'Bolehkah data diunduh dan dipakai?', a: ['Berkas JSON dapat diunduh dari bagian bawah setiap halaman. Cantumkan sumber data saat memakainya. Lisensi setiap sumber berbeda, jadi periksa daftar pada halaman Tentang.'] },
      { q: 'Apakah situs ini menggantikan penyuluh pertanian?', a: ['Tidak. Informasi di sini perkiraan dari citra satelit. Untuk keputusan tanam, tanyakan juga kepada penyuluh pertanian setempat.'] },
      { q: 'Bagaimana menghubungi pengelola?', a: ['Informasi kontak akan dicantumkan saat situs diterbitkan.'] }
    ]
  },

  stages: {
    planted: 'Sedang Ditanami',
    peaked: 'Menjelang Panen',
    fallow: 'Bera',
    unknown: 'Tidak Terbaca (Tertutup Awan)'
  },

  history: {
    title: 'Riwayat Musim Tanam 1',
    body: 'Puncak tanam sampai puncak panen pada setiap musim tanam 1 yang terbaca sejak tahun 2017. Musim ditulis dengan tahun tanam dan tahun panen.',
    label: (year: number) => `${year - 1}/${String(year).slice(2)}`,
    note: 'Tanggal diperkirakan dari citra satelit.',
    columns: { season: 'Musim', plant: 'Puncak Tanam', harvest: 'Puncak Panen', ha: 'Luas Padi' }
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
    seoTitle: 'Kalender Tanam Lamongan',
    eyebrow: 'Kabupaten Lamongan',
    headline: 'Informasi Musim Tanam di Kabupaten Lamongan',
    description: (units: number) => `Saat ini tersedia untuk padi di Kecamatan Tikung, ${units} desa, dari pemantauan citra satelit. Kecamatan dan tanaman lain sedang disiapkan.`,
    primaryCta: 'Cari Desa',
    secondaryCta: 'Lihat Kalender Tanam',
    stats: {
      paddy: 'Luas Sawah',
      units: 'Jumlah Desa',
      season: 'Awal Musim Tanam 1'
    },
    tableToggle: 'Tampilkan Tabel',
    mapLoading: 'Memuat peta…',
    mapLabel: 'Peta petak sawah dan batas wilayah',
    mapFailed: 'Peta tidak dapat ditampilkan pada perangkat ini. Seluruh angka tetap tersedia pada halaman ini.',

    snapshot: {
      eyebrow: 'Ringkasan',
      title: 'Kondisi Kecamatan Tikung',
      labels: {
        seasonOutside: 'awal tanam berikutnya',
        seasonDuring: 'dari musim tanam 1',
        fallow: 'bera dari sawah yang terbaca',
        rainPct: 'dibanding rata-rata 5 tahun',
        rainMm: (base: string) => `rata-rata 5 tahun ${base} mm`
      },
      season: {
        outside: 'Saat ini di luar musim tanam 1',
        during: (pct: string) => `Musim tanam 1 berada pada ${pct} dari rentang biasanya`,
        outsideBody: (month: string) => `Menurut pola sejak tahun 2017, awal tanam berikutnya pada bulan ${month}.`,
        duringBody: (to: string) => `Menurut pola sejak tahun 2017, panen terakhir selesai pada bulan ${to}. Ini posisi pada kalender, bukan pengamatan lapangan.`
      },
      fallow: {
        title: (pct: string) => `${pct} sawah yang terbaca berstatus bera`,
        body: (bera: string, readable: string, hidden: string) => `Sebanyak ${bera} dari ${readable} sawah yang terbaca belum ditanami kembali. Sawah seluas ${hidden} tertutup awan dan tidak dihitung.`
      },
      rain: {
        title: (month: string, word: string) => `Curah hujan ${month} ${word}`,
        body: (mm: string, base: string) => `Tercatat ${mm} mm, sedangkan rata-rata 5 tahun ${base} mm.`,
        wetter: (p: string) => `${p} lebih basah dari rata-rata`,
        drier: (p: string) => `${p} lebih kering dari rata-rata`,
        above: 'di atas rata-rata',
        below: 'di bawah rata-rata',
        same: 'sama dengan rata-rata'
      }
    },

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
      empty: (month: string) => `Belum terdapat panen besar dalam 8 minggu ke depan. Panen musim berikutnya umumnya mencapai puncak pada bulan ${month}.`,
      emptyTitle: 'Belum ada panen besar dalam 8 minggu ke depan',
      emptyBody: (month: string) => `Panen musim berikutnya umumnya mencapai puncak pada bulan ${month}.`
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
    map: {
      label: 'Peta desa di Kecamatan Tikung menurut waktu puncak tanam',
      hint: 'Arahkan kursor ke desa untuk melihat tanggal puncak tanam.',
      early: 'Lebih awal',
      late: 'Lebih akhir'
    },
    seoTitle: 'Jadwal Tanam dan Panen Desa - Kalender Tanam Lamongan',
    title: 'Kalender Tanam',
    description: 'Jadwal tanam dan panen setiap desa di Kecamatan Tikung, disertai awal tanam dan curah hujan.',
    notesLink: { text: 'Jadwal merupakan perkiraan dari citra satelit.', link: 'Baca catatan penggunaan data' }
  },

  bandingkan: {
    seoTitle: 'Perbandingan Wilayah - Kalender Tanam Lamongan',
    title: 'Perbandingan Wilayah',
    description: 'Peringkat desa dan kecamatan menurut luas sawah, frekuensi tanam padi, dan lahan sawah yang sedang hijau.',
    levels: { desa: 'Desa di Kecamatan Tikung', kecamatan: 'Kecamatan di Kabupaten Lamongan' },
    map: {
      label: (level: string, metric: string) => `Peta ${level} menurut ${metric}`,
      hint: 'Arahkan kursor ke wilayah untuk melihat nilainya.',
      low: 'Lebih rendah',
      high: 'Lebih tinggi'
    },
    podium: { label: (metric: string) => `Tiga teratas menurut ${metric.toLowerCase()}` },
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
        title: (year: number | null) => `Peringkat Menurut Frekuensi Tanam Sawah Tahun ${year ?? '-'}`,
        body: 'Rata-rata jumlah musim tanam yang terbaca satelit pada satu hektare sawah dalam setahun. Angka 2 berarti sawah ditanami dua kali. Semua tanaman dihitung, tidak hanya padi.',
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
    kecamatanNote: (diff: string, year: number) => `Frekuensi tanam kecamatan lain dihitung dari semua musim pada peta sawah. Pada tahun ${year}, luas dari satelit berbeda sekitar ${diff} (median) dari luas panen menurut dinas pertanian. Urutan dapat dipakai, tetapi angka belum pasti.`,
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
    seoTitle: (unit: string) => `Desa ${unit} - Kalender Tanam Lamongan`,
    title: (unit: string) => `Desa ${unit}`,
    description: (ha: string) => `Luas sawah sekitar ${ha}.`,
    groups: { conditions: 'Kondisi dan Jadwal', history: 'Riwayat dan Panen', context: 'Perbandingan dan Hujan' },
    shape: { label: (unit: string) => `Letak Desa ${unit} di Kecamatan Tikung` },
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
