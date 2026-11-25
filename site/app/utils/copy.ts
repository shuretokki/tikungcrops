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
    title: "tikungcrops",
    subtitle: "Kalender Tanam Kecamatan Tikung",
    detail: "Lihat penjelasan",
    skip: "Lewati ke Konten Utama",
    stale: (date: string) => `Data per ${date}. Perkiraan dapat berubah.`,
    advice:
      "Untuk keputusan tanam, tanyakan juga kepada penyuluh pertanian di kantor kecamatan. Informasi dalam web ini merupakan perkiraan dari foto satelit.",
    search: "Cari Desa",
    download: {
      label: "Unduh Data",
      files: [
        { label: "Ringkasan desa", file: "meta.json" },
        { label: "Kondisi sawah", file: "current.json" },
        { label: "Prakiraan panen", file: "outlook.json" },
        { label: "Musim tanam", file: "seasons.json" },
        { label: "Curah hujan", file: "rain.json" },
        { label: "Berapa kali tanam", file: "intensity.json" },
        { label: "Ketepatan data", file: "validation.json" },
        { label: "Batas desa", file: "boundaries.geojson" },
      ],
    },
    updated: (asOf: string) => `Data per ${asOf}.`,
    footer: {
      pages: "Halaman",
      data: "Unduh Data",
      info: "Informasi",
      infoLinks: [
        { label: "Tentang Situs", to: "/tentang" },
        { label: "Sumber Data", to: "/tentang#sumber" },
        { label: "Penggunaan Data", to: "/tentang#catatan" },
        { label: "Tanya Jawab (FAQ)", to: "/faq" },
      ],
      copyright: "Copyright © 2026 Tri Rianto Utomo",
    },
  },

  nav: {
    beranda: "Beranda",
    kalender: "Kalender Tanam",
    bandingkan: "Perbandingan Wilayah",
    tentang: "Tentang",
    faq: "FAQ",
  },

  // The pick lists follow the entry steps of the FAO Crop Calendar: choose the place, choose the crop, then search.
  // Only rice in Kecamatan Tikung is finished. The other choices are listed so the site is ready for them.
  // Crops follow KATAM Terpadu (padi, jagung, kedelai) and the five crops of ASEAN AFSIS (padi, jagung, tebu, kedelai, singkong).
  scope: {
    title: "Pilih Tanaman",
    place: "Data tersedia untuk Kecamatan Tikung.",
    region: "Wilayah",
    crop: "Tanaman",
    soon: "segera",
    regions: [{ value: "tikung", label: "Kecamatan Tikung", ready: true }],
    crops: [
      { value: "padi", label: "Padi", image: "/crops/padi.jpg", ready: true },
      {
        value: "jagung",
        label: "Jagung",
        image: "/crops/jagung.jpg",
        ready: false,
      },
      {
        value: "kedelai",
        label: "Kedelai",
        image: "/crops/kedelai.jpg",
        ready: false,
      },
      { value: "tebu", label: "Tebu", image: "/crops/tebu.jpg", ready: false },
      {
        value: "singkong",
        label: "Singkong",
        image: "/crops/singkong.jpg",
        ready: false,
      },
    ],
    note: "Pilihan bertanda segera sedang disiapkan.",
    summary: (crop: string, region: string) => `${crop} di ${region}`,
    change: "Ganti",
    go: "Lihat Kalender Tanam",
  },

  tentang: {
    seoTitle: "Tentang Situs - tikungcrops",
    eyebrow: "Tentang",
    title: "Untuk Apa Situs Ini?",
    purpose: [
      "tikungcrops menampilkan kondisi sawah, jadwal tanam, dan perkiraan panen dari foto satelit, sampai tingkat desa. Informasi ini membantu petani, penyuluh pertanian, dan dinas merencanakan tanam, menyiapkan benih dan pupuk, serta memperkirakan kapan panen datang.",
      "Situs ini dibuat sebagai penelitian mahasiswa dan belum menggantikan layanan resmi dari Kementerian Pertanian.",
    ],
    helps: {
      title: "Siapa yang Terbantu",
      items: [
        {
          icon: "i-lucide-sprout",
          title: "Petani",
          body: "Melihat kapan desa mulai menanam dan kapan panen biasanya datang.",
        },
        {
          icon: "i-lucide-users",
          title: "Penyuluh pertanian",
          body: "Memantau kondisi dan mulai tanam setiap desa binaan.",
        },
        {
          icon: "i-lucide-landmark",
          title: "Dinas pertanian",
          body: "Membandingkan desa dan kecamatan untuk perencanaan benih, pupuk, dan panen.",
        },
        {
          icon: "i-lucide-microscope",
          title: "Peneliti",
          body: "Mengunduh data dan memeriksa ketepatannya terhadap data BPS.",
        },
      ],
    },
    how: {
      title: "Cara Memakai",
      steps: [
        "Pilih wilayah dan tanaman pada halaman Beranda.",
        "Buka Kalender Tanam untuk melihat musim tanam utama, jadwal setiap desa, mulai tanam, dan curah hujan.",
        "Buka halaman desa untuk melihat kondisi, jadwal, riwayat musim, dan perkiraan panen desa tersebut.",
        "Bandingkan desa atau kecamatan pada halaman Perbandingan.",
        "Unduh data dalam bentuk berkas dari bagian bawah halaman.",
      ],
    },
    coverage: {
      title: "Cakupan Saat Ini dan Rencana",
      columns: { item: "Cakupan", status: "Status", note: "Keterangan" },
      ready: "Tersedia",
      planned: "Disiapkan",
      rows: [
        {
          item: "Padi di Kecamatan Tikung",
          ready: true,
          note: "13 desa, data foto satelit sejak Oktober 2017.",
        },
        {
          item: "Jagung, kedelai, tebu, dan singkong",
          ready: false,
          note: "Belum diolah. Perhitungan saat ini khusus padi.",
        },
      ],
    },
    sources: {
      title: "Sumber Data",
      items: [
        {
          name: "Copernicus Sentinel-1 (ESA)",
          href: "https://sentiwiki.copernicus.eu/web/s1-mission",
        },
        {
          name: "Copernicus Sentinel-2 (ESA). Contains modified Copernicus Sentinel data 2026",
          href: "https://sentiwiki.copernicus.eu/web/s2-mission",
        },
        { name: "CHIRPS", href: "https://www.chc.ucsb.edu/data/chirps" },
        { name: "ESA WorldCover", href: "https://esa-worldcover.org" },
        { name: "Lahan Baku Sawah (BIG)", href: "https://www.big.go.id" },
        {
          name: "BPS dan Dinas Pertanian",
          href: "https://lamongankab.bps.go.id",
        },
        {
          name: "geoBoundaries (OCHA ROAP, BPS 2019), CC BY 3.0 IGO",
          href: "https://www.geoboundaries.org",
        },
        {
          name: "OpenFreeMap, © OpenStreetMap contributors",
          href: "https://openfreemap.org",
        },
        {
          name: "Foto tanaman, Wikimedia Commons. Kedelai: United Soybean Board, CC BY 2.0. Tebu: Sarah and Jason, CC BY-SA 2.0",
          href: "https://commons.wikimedia.org",
        },
      ],
    },
    notes: {
      title: "Penggunaan Data",
      body: "Jadwal merupakan perkiraan dari foto satelit dan bukan pengganti informasi dari penyuluh pertanian.",
      items: [
        "Pada musim hujan, awan sering menutupi awal musim sehingga perkiraan dapat meleset tiga sampai lima minggu. Pada musim kemarau, bedanya sekitar satu sampai dua minggu.",
        "Sejak tahun 2022, satelit yang dipakai lebih jarang melintas sehingga sebagian musim tanam padi tidak terlihat.",
      ],
    },
    researcher: "Untuk Peneliti",
    faqLink: "Baca Tanya Jawab (FAQ)",
  },

  faq: {
    seoTitle: "Tanya Jawab - tikungcrops",
    title: "Tanya Jawab",
    description:
      "Jawaban singkat untuk pertanyaan yang sering muncul tentang tikungcrops.",
    items: [
      {
        q: "Apa itu tikungcrops?",
        a: [
          "Situs yang menunjukkan kapan sawah di desa biasanya mulai ditanami dan dipanen, serta kondisi sawahnya, dari foto yang diambil satelit. Saat ini hanya untuk padi di Kecamatan Tikung.",
        ],
      },
      {
        q: "Untuk siapa situs ini?",
        a: [
          "Untuk petani, penyuluh pertanian, dinas pertanian, dan peneliti. Penjelasan lengkap ada pada halaman Tentang.",
        ],
      },
      {
        q: "Wilayah dan tanaman apa yang tersedia?",
        a: [
          "Padi di 13 desa Kecamatan Tikung. Jagung, kedelai, tebu, dan singkong sedang disiapkan dan belum dapat dipilih.",
        ],
      },
      {
        q: "Dari mana datanya?",
        a: [
          "Dari foto satelit milik Badan Antariksa Eropa, data curah hujan, peta sawah dari pemerintah, dan data panen resmi dari Badan Pusat Statistik dan dinas pertanian. Nama lengkapnya ada di bagian Sumber Data pada halaman Tentang.",
        ],
      },
      {
        q: "Seberapa sering data diperbarui?",
        a: [
          "Data diperbarui jika ada foto satelit baru yang sudah diolah. Tanggal data terakhir tertera di bagian bawah setiap halaman.",
        ],
      },
      {
        q: "Mengapa data lebih lama dari hari ini?",
        a: [
          "Satelit hanya lewat beberapa hari sekali, awan sering menutupi sawah, dan pengolahan memerlukan waktu. Karena itu data selalu tertinggal dari hari ini.",
        ],
      },
      {
        q: "Bagaimana tahap sawah ditentukan?",
        a: [
          "Satelit melihat air yang menggenang saat sawah ditanami, lalu melihat warna hijau tanaman yang makin tua. Tanaman yang paling hijau berarti panen tinggal beberapa minggu lagi. Sawah yang kosong setelah panen disebut belum ditanami.",
        ],
      },
      {
        q: "Mengapa sebagian sawah tidak diketahui?",
        a: [
          "Awan menutupi sawah sehingga satelit tidak dapat melihatnya. Sawah itu tidak dihitung dalam angka persen.",
        ],
      },
      {
        q: "Seberapa tepat jadwal tanam dan panen?",
        a: [
          "Jadwal adalah perkiraan dari pola sejak tahun 2017. Pada musim hujan perkiraan bisa meleset tiga sampai lima minggu, dan pada musim kemarau satu sampai dua minggu. Tanggalnya belum dicocokkan dengan catatan petani.",
        ],
      },
      {
        q: "Seberapa tepat luas sawah dan padi?",
        a: [
          "Di Kecamatan Tikung, luas padi dari satelit mendekati data BPS untuk setiap desa. Hasil pemeriksaan ada di bagian Ketepatan Data pada halaman Tentang.",
        ],
      },
      {
        q: "Apa arti mulai tanam lebih lambat dari rata-rata?",
        a: [
          "Mulai tanam musim terakhir dibandingkan dengan rata-rata lima musim sebelumnya. Jika beda harinya 7 hari atau lebih, desa diberi tanda lebih lambat. Angka ini perkiraan dan bisa meleset beberapa minggu.",
        ],
      },
      {
        q: "Mengapa angka berapa kali tanam berbeda dengan jumlah panen padi?",
        a: [
          "Angka itu menghitung semua tanaman di sawah, tidak hanya padi, karena cara satelit mengenali padi kadang melewatkan sebagian padi.",
        ],
      },
      {
        q: "Bolehkah data diunduh dan dipakai?",
        a: [
          "Boleh. Data dapat diunduh dari bagian bawah setiap halaman. Sebutkan sumber datanya saat memakainya, dan periksa izin setiap sumber di halaman Tentang.",
        ],
      },
      {
        q: "Apakah situs ini menggantikan penyuluh pertanian?",
        a: [
          "Tidak. Informasi di sini hanya perkiraan dari foto satelit. Untuk keputusan tanam, tanyakan juga kepada penyuluh pertanian di kantor kecamatan.",
        ],
      },
      {
        q: "Bagaimana menghubungi pengelola?",
        a: ["Informasi kontak akan dicantumkan saat situs diterbitkan."],
      },
    ],
  },

  stages: {
    planted: "Sedang Ditanami",
    peaked: "Menjelang Panen",
    fallow: "Belum Ditanami",
    unknown: "Belum Diketahui",
  },

  history: {
    title: "Musim Tanam Sebelumnya",
    body: "Mulai tanam sampai panen pada setiap musim tanam utama yang tercatat sejak tahun 2017. Musim ditulis dengan tahun tanam dan tahun panen.",
    label: (year: number) => `${year - 1}/${String(year).slice(2)}`,
    note: "Tanggal diperkirakan dari foto satelit.",
    columns: {
      season: "Musim",
      plant: "Mulai Tanam",
      harvest: "Panen",
      ha: "Luas Padi",
    },
  },

  onset: {
    title: "Mulai Tanam Dibanding Rata-rata 5 Musim",
    body: "Mulai tanam musim tanam utama terakhir yang tercatat di setiap desa, dibandingkan dengan rata-rata musim-musim sebelumnya di desa itu.",
    value: (d: number) =>
      d === 0
        ? "Sama dengan rata-rata"
        : d > 0
          ? `${d} hari lebih lambat`
          : `${-d} hari lebih awal`,
    card: "Mulai Tanam",
    seasonOf: (year: number) => `musim ${year}`,
    short: (d: number) =>
      d >= 7 ? "Lebih Lambat" : d <= -7 ? "Lebih Awal" : "Sama Saja",
    cardDetail: (year: number, shift: number, plant: string, mean: string) =>
      `Dibandingkan musim-musim sebelumnya di desa ini, bukan dengan desa lain. Tahun ${year}: ${shift === 0 ? "sama dengan rata-rata" : shift > 0 ? `${shift} hari lebih lambat dari rata-rata` : `${-shift} hari lebih awal dari rata-rata`}. Mulai tanam ${plant}, rata-rata sebelumnya ${mean}.`,
    late: "Lebih Lambat",
    lateAfter: 7,
    columns: {
      unit: "Desa",
      plant: "Mulai Tanam",
      mean: "Rata-rata Sebelumnya",
      shift: "Beda (hari)",
    },
  },

  stageNote: "",

  stageHelp: {
    planted: "Padi sudah ditanam dan sedang tumbuh.",
    peaked:
      "Tanaman berada pada hijau terbanyak. Panen biasanya tinggal beberapa minggu lagi.",
    fallow: "Lahan setelah panen dan belum ditanami kembali.",
    unknown: "Satelit tidak dapat membaca kondisi lahan.",
  },

  tip: {
    wetter: (p: string) => `${p} lebih basah dari rata-rata`,
    drier: (p: string) => `${p} lebih kering dari rata-rata`,
    average: "Sama dengan rata-rata",
    plant: "Mulai tanam",
    harvest: "Panen",
    start: "Mulai musim",
    end: "Akhir panen",
    days: (n: number) => `${n} hari`,
    span: "Lama dari tanam sampai panen",
    since: "Berdasarkan pola musim tanam sejak tahun 2017.",
    reference: "BPS",
    satellite: "Satelit",
    diff: "Beda",
    mapHint: "Pilih untuk melihat jadwal desa.",
    today: (date: string) => `Per ${date}`,
    range: "Hujan paling sedikit dan paling banyak sejak 2017",
  },

  landing: {
    seoTitle: "tikungcrops",
    eyebrow: "Kabupaten Lamongan",
    steps: [
      {
        title: "Pilih Wilayah dan Tanaman",
        body: "Tentukan wilayah dan tanaman yang ingin dilihat.",
      },
      {
        title: "Lihat Kalender Tanam",
        body: "Baca musim tanam utama, jadwal setiap desa, dan curah hujan.",
      },
      {
        title: "Buka Halaman Desa",
        body: "Periksa kondisi sawah, jadwal, dan perkiraan panen desa.",
      },
    ],
    headline: "Informasi Musim Tanam di Kecamatan Tikung",
    description: (units: number) =>
      `Padi menjadi tanaman pertama yang tersedia, lengkap dengan jadwal tanam, kondisi sawah, dan perkiraan panen ${units} desa di Kecamatan Tikung dari foto satelit. Jagung, kedelai, tebu, dan singkong menyusul.`,
    primaryCta: "Cari Desa",
    secondaryCta: "Lihat Kalender Tanam",
    tableToggle: "Lihat Tabel",
    mapLoading: "Memuat peta…",
    mapLabel: "Peta petak sawah dan batas wilayah",
    mapFailed:
      "Peta tidak dapat ditampilkan pada perangkat ini. Seluruh angka tetap tersedia pada halaman ini.",

    snapshot: {
      eyebrow: "Ringkasan",
      title: "Kondisi Kecamatan Tikung",
      labels: {
        seasonOutside: "mulai tanam berikutnya, rata-rata semua desa",
        seasonDuring: "dari musim tanam utama",
        fallow: (ha: string) =>
          `sawah belum ditanami, dari ${ha} sawah yang diketahui`,
        rainPct: "dibanding rata-rata 5 tahun",
        rainMm: (base: string) => `rata-rata 5 tahun di kecamatan ${base} mm`,
      },
      season: {
        outside: "Saat ini di luar musim tanam utama",
        during: (pct: string) =>
          `Musim tanam 1 berada pada ${pct} dari masa biasanya`,
        outsideBody: (month: string) =>
          `Menurut pola sejak tahun 2017, mulai tanam berikutnya pada bulan ${month}.`,
        duringBody: (to: string) =>
          `Menurut pola sejak tahun 2017, panen terakhir selesai pada bulan ${to}. Ini posisi pada kalender, bukan pengamatan lapangan.`,
      },
      fallow: {
        title: (pct: string) => `${pct} sawah belum ditanami`,
        offSeason: (date: string) =>
          `Pada ${date} belum musim tanam, jadi sawah belum ditanami.`,
        body: (bera: string, readable: string, unknown: string) =>
          `Sebanyak ${bera} dari ${readable} sawah belum ditanami. Sawah seluas ${unknown} belum diketahui.`,
      },
      rain: {
        title: (month: string, word: string) => `Curah hujan ${month} ${word}`,
        body: (mm: string, base: string) =>
          `Tercatat ${mm} mm, sedangkan rata-rata 5 tahun di kecamatan ${base} mm.`,
        wetter: (p: string) => `${p} lebih basah dari rata-rata`,
        drier: (p: string) => `${p} lebih kering dari rata-rata`,
        above: "di atas rata-rata",
        below: "di bawah rata-rata",
        same: "sama dengan rata-rata",
        veryDry: (month: string) => `Hujan ${month} hampir tidak ada`,
      },
    },

    now: {
      title: (resting: boolean) =>
        resting
          ? "Lahan Sawah Menunggu Musim Tanam"
          : "Musim Tanam Sedang Berlangsung",
      body: (resting: boolean, pct: string, date: string) =>
        resting
          ? `Per ${date}, sebanyak ${pct} lahan sawah belum ditanami. Penanaman umumnya dimulai kembali setelah hujan turun.`
          : `Per ${date}, sebanyak ${pct} lahan sawah belum ditanami, sedangkan sisanya sedang ditanami atau menjelang panen.`,
      columns: { stage: "Tahap", ha: "Luas", share: "Persentase" },
    },

    calendar: {
      short: "Satu baris untuk satu musim tanam.",
      link: "Buka Kalender Tanam",
      title: (month: string) =>
        `Musim Tanam Utama Umumnya Dimulai pada Bulan ${month}`,
      body: "Setiap baris menunjukkan satu musim tanam, yang terbagi atas tahap tanam, tumbuh, dan panen. Baris paling bawah menandai tanggal hari ini.",
      today: "Hari ini",
      plant: "Mulai Tanam",
      harvest: "Panen",
      phases: { sow: "Tanam", grow: "Tumbuh", harvest: "Panen" },
      readout: (
        season: string,
        from: string,
        to: string,
        plant: string,
        harvest: string,
      ) =>
        `${season}: ${from} sampai ${to}. Mulai tanam ${plant}, panen ${harvest}.`,
      seasons: {
        MT1: "Musim Tanam Utama",
        MT2: "Musim Tanam 2",
        MT3: "Musim Tanam 3",
      },
      seasonNote: {
        MT1: "Musim utama",
        MT2: "Musim kedua",
        MT3: "Tidak setiap tahun",
      },
      columns: {
        season: "Musim",
        start: "Mulai Musim",
        plant: "Tanam",
        harvest: "Panen",
        end: "Selesai",
      },
    },

    rain: {
      title: "Curah Hujan 12 Bulan Terakhir",
      body: (month: string, mm: string, normal: string) =>
        `Curah hujan bulan ${month} tercatat ${mm} mm, sedangkan rata-rata bulan tersebut di kecamatan sekitar ${normal} mm.`,
      advice: {
        dry: (m: string) =>
          `Hujan ${m} kurang dari biasanya, jadi tunggu hujan turun sebelum mulai tanam.`,
        ok: (m: string) => `Hujan ${m} tidak kurang dari biasanya.`,
      },
      plain: {
        wetter: (m: string, p: string) =>
          `Hujan ${m} lebih banyak dari biasanya (${p}).`,
        drier: (m: string, p: string) =>
          `Hujan ${m} lebih sedikit dari biasanya (${p}).`,
        veryDry: (m: string) => `Hujan ${m} hampir tidak ada.`,
        above: (m: string) => `Hujan ${m} di atas rata-rata.`,
        below: (m: string) => `Hujan ${m} di bawah rata-rata.`,
        same: (m: string) => `Hujan ${m} sama dengan biasanya.`,
      },
      actual: "Curah hujan",
      normal: "Rata-rata 5 tahun",
      band: "Hujan paling sedikit dan paling banyak sejak 2017",
      readout: (label: string, mm: string, normal: string) =>
        `${label}: ${mm} mm, rata-rata ${normal} mm`,
      columns: {
        month: "Bulan",
        mm: "Curah Hujan (mm)",
        normal: "Rata-rata 5 Tahun (mm)",
        lo: "Terendah (mm)",
        hi: "Tertinggi (mm)",
      },
    },

    progress: {
      title: "Kemajuan Musim Tanam Utama",
      inSeason: (pct: string, from: string, to: string) =>
        `${pct} dari musim tanam utama telah berjalan, yaitu ${from} sampai ${to}.`,
      outside: (from: string) =>
        `Musim tanam 1 belum dimulai. Mulai tanam umumnya pada bulan ${from}.`,
      label: (pct: string) => `Kemajuan musim ${pct}`,
    },

    schedule: {
      title: "Jadwal Tanam dan Panen Setiap Desa",
      body: "Jadwal disusun dari pola musim tanam sejak tahun 2017. Desa yang berada paling atas umumnya memulai tanam lebih awal.",
      today: "Hari ini",
      readout: (unit: string, plant: string, harvest: string) =>
        `${unit}: mulai tanam ${plant}, panen ${harvest}`,
      hint: "Sentuh garis warna untuk melihat tanggal.",
      legend: "Garis warna menunjukkan masa dari mulai tanam sampai panen.",
      columns: { unit: "Desa", plant: "Mulai Tanam", harvest: "Panen" },
    },

    harvest: {
      title: "Perkiraan Panen 8 Minggu ke Depan",
      body: "Desa dengan perkiraan panen paling awal berada di urutan teratas.",
      row: (week: string, ha: string) =>
        `Panen terbanyak minggu ${week}, total sekitar ${ha}`,
      empty: (month: string) =>
        `Belum terdapat panen besar dalam 8 minggu ke depan. Panen musim berikutnya umumnya paling banyak pada bulan ${month}.`,
      emptyTitle: "Belum ada panen besar dalam 8 minggu ke depan",
      emptyBody: (month: string) =>
        `Panen musim berikutnya umumnya paling banyak pada bulan ${month}.`,
    },

    desa: {
      title: "Cari Desa",
      body: "Masukkan nama desa, kemudian pilih desa untuk melihat jadwal tanam dan perkiraan panen.",
      search: "Masukkan nama desa, misalnya Jotosanur…",
      empty: "Desa tidak ditemukan. Periksa kembali penulisan nama desa.",
      paddy: (ha: string) => `Luas sawah ${ha}`,
    },

    more: {
      title: "Informasi Lainnya",
      items: [
        {
          to: "/kalender",
          icon: "i-lucide-calendar-days",
          title: "Kalender Tanam",
          description: "Jadwal tanam dan panen setiap desa, curah hujan.",
        },
        {
          to: "/perbandingan",
          icon: "i-lucide-chart-bar",
          title: "Perbandingan Wilayah",
          description:
            "Perbandingan desa di Kecamatan Tikung, beserta ketepatan data.",
        },
      ],
    },
  },

  kalender: {
    map: {
      label: "Peta desa di Kecamatan Tikung menurut waktu mulai tanam",
      hint: "Sentuh desa untuk melihat tanggal mulai tanam.",
      early: "Lebih awal",
      late: "Lebih akhir",
    },
    seoTitle: "Jadwal Tanam dan Panen Desa - tikungcrops",
    title: "Kalender Tanam",
    description:
      "Jadwal tanam dan panen setiap desa di Kecamatan Tikung, disertai mulai tanam dan curah hujan.",
    views: { kalender: "Kalender", peta: "Peta", tabel: "Tabel" },
    measureLabel: "Ukuran",
    measures: { plant: "Mulai Tanam", harvest: "Panen" },
    mapTitle: (measure: string) => `Peta Desa Menurut ${measure}`,
    tableTitle: "Jadwal Tanam dan Panen Setiap Desa",
    tableBody: "Klik judul kolom untuk mengurutkan.",
    tableDetail: "Garis warna menunjukkan musim tanam sejak 1 September.",
    trend: "Musim",
    search: "Cari desa…",
    notesLink: {
      text: "Jadwal merupakan perkiraan dari foto satelit.",
      link: "Baca penggunaan data",
    },
  },

  bandingkan: {
    seoTitle: "Perbandingan Wilayah - tikungcrops",
    title: "Perbandingan Wilayah",
    description:
      "Perbandingan desa di Kecamatan Tikung menurut luas sawah, berapa kali tanam padi, dan sawah yang ada tanamannya.",
    map: {
      label: (metric: string) => `Peta desa menurut ${metric}`,
      hint: "Sentuh wilayah untuk melihat nilainya.",
      low: "Lebih rendah",
      high: "Lebih tinggi",
    },
    views: { peta: "Peta", tabel: "Tabel" },
    tableTitle: "Tabel Desa di Kecamatan Tikung",
    tableUnit: "Desa",
    trend: {
      title: "Berapa Kali Tanam dari Tahun ke Tahun",
      body: (from: number, to: number) =>
        `Rata-rata jumlah musim tanam setiap desa pada tahun ${from} sampai ${to}. Garis yang naik berarti sawah makin sering ditanami.`,
      value: (last: string, delta: number) =>
        `${last} kali setahun, ${delta > 0.05 ? "naik" : delta < -0.05 ? "turun" : "tetap"}`,
      label: (unit: string, last: string, delta: number) =>
        `Berapa kali tanam Desa ${unit}: ${last} kali setahun, ${delta > 0.05 ? "naik" : delta < -0.05 ? "turun" : "tetap"}`,
    },
    tableBody: "Klik judul kolom untuk mengurutkan.",
    tableDetail:
      "Garis tipis di bawah angka menunjukkan besarnya dibanding desa lain.",
    search: "Cari desa…",
    metricLabel: "Ukuran",
    metrics: {
      sawah: {
        label: "Luas Sawah",
        title: "Luas Sawah Setiap Desa",
        short: "Luas sawah menurut peta Lahan Baku Sawah.",
        body: "Luas sawah menurut peta Lahan Baku Sawah.",
        value: (v: number) => `${Math.round(v).toLocaleString("id-ID")} ha`,
      },
      intensitas: {
        label: "Berapa Kali Tanam",
        title: (year: number | null) =>
          `Berapa Kali Sawah Ditanami Setahun, Tahun ${year ?? "-"}`,
        short: "Jumlah musim tanam per hektare dalam setahun.",
        body: "Rata-rata jumlah musim tanam yang tercatat satelit pada satu hektare sawah dalam setahun. Angka 2 berarti sawah ditanami dua kali. Semua tanaman dihitung, tidak hanya padi.",
        value: (v: number) =>
          `${v.toLocaleString("id-ID", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} kali setahun`,
      },
      tumbuh: {
        label: "Sawah yang Ada Tanamannya",
        title: "Sawah yang Ada Tanamannya Setiap Desa",
        short: "Sawah yang sedang ditanami atau menjelang panen.",
        body: "Bagian sawah yang sedang ditanami atau menjelang panen.",
        value: (v: number) =>
          v.toLocaleString("id-ID", {
            style: "percent",
            maximumFractionDigits: 0,
          }),
      },
    },
    rank: (n: number) => `${n}.`,
    here: "Tikung",
    empty: "Data untuk perbandingan ini belum tersedia.",

    accuracy: {
      title: "Ketepatan Data",
      short: (years: string, units: number) =>
        `Luas padi dari satelit dibandingkan dengan luas panen BPS di ${units} desa pada tahun ${years}.`,
      detail:
        "Luas seluruh tanaman dari satelit lebih besar karena peta lahan pertanian juga memuat jagung dan tegalan. Kemiripan urutan bernilai 0 sampai 1, dan semakin mendekati 1 semakin mirip urutan desa dari satelit dengan urutan dari BPS.",
      statRatio: (year: number) =>
        `Luas padi dari satelit dibanding data BPS, tahun ${year}`,
      statR: "Kemiripan urutan desa dengan BPS (0 sampai 1)",
      scatterNote: (year: number) =>
        `Titik pada grafik menunjukkan luas padi tahun ${year}. Data tahun tersebut tidak dipakai saat cara mengenali padi disusun.`,
      x: "Luas panen padi BPS (ha)",
      y: "Luas padi dari satelit (ha)",
      equalNote:
        "Garis putus-putus menunjukkan luas satelit sama dengan luas BPS.",
      readout: (unit: string, ref: string, sat: string) =>
        `${unit}: BPS ${ref}, satelit ${sat}`,
      hint: "Sentuh titik untuk melihat nama desa.",
      cropNames: { rice: "Padi", all_crops: "Seluruh Tanaman" } as Record<
        string,
        string
      >,
      summaryColumns: {
        year: "Tahun",
        crop: "Tanaman",
        r: "Kemiripan Urutan",
        ratio: "Luas Satelit terhadap BPS",
      },
      columns: { unit: "Desa", reference: "BPS", satellite: "Satelit" },
    },
  },

  desa: {
    seoTitle: (unit: string) => `Desa ${unit} - tikungcrops`,
    title: (unit: string) => `Desa ${unit}`,
    description: (unit: string) =>
      `Kondisi sawah padi, jadwal tanam, dan perkiraan panen Desa ${unit}.`,
    summary: {
      usual: (plant: string, harvest: string) =>
        `Biasanya mulai tanam sekitar ${plant} dan panen sekitar ${harvest}.`,
      onset: (d: number, year: number) =>
        d >= 7
          ? `Pada musim tanam terakhir yang tercatat (${year}), mulai tanamnya ${d} hari lebih lambat dari rata-rata.`
          : d <= -7
            ? `Pada musim tanam terakhir yang tercatat (${year}), mulai tanamnya ${-d} hari lebih awal dari rata-rata.`
            : `Pada musim tanam terakhir yang tercatat (${year}), mulai tanamnya sama dengan rata-rata.`,
    },
    groups: {
      conditions: "Kondisi dan Jadwal",
      history: "Riwayat dan Panen",
      context: "Perbandingan dan Hujan",
    },
    photo: {
      alt: (unit: string) => `Garis batas Desa ${unit}`,
    },
    back: "Daftar Desa",
    rainOwn: (mm: string) => `Rata-rata 5 tahun di desa ini ${mm} mm.`,
    timing: {
      before: (plant: string) =>
        `Belum waktunya tanam. Biasanya mulai sekitar ${plant}.`,
      near: (days: number, plant: string) =>
        `Mulai tanam sudah dekat, sekitar ${plant} (${days} hari lagi).`,
      during: "Musim tanam sedang berjalan.",
      harvestSoon: (harvest: string) => `Mendekati panen, sekitar ${harvest}.`,
    },
    mine: "Jadikan Desa Saya",
    isMine: "Desa Saya",
    mineHelp:
      "Desa Saya menyimpan desa ini di perangkat ini, supaya mudah dibuka dari halaman depan.",
    mineOpen: (unit: string) => `Buka Desa Saya: ${unit}`,
    share: "Bagikan lewat WhatsApp",
    shareText: (unit: string, summary: string) =>
      `Desa ${unit}. ${summary}`.trim(),
    notFound: "Desa tidak ditemukan.",
    now: {
      title: "Kondisi Terkini",
      asOf: (date: string) => `Data per ${date}`,
    },
    schedule: {
      title: "Jadwal Musim Tanam Utama",
      body: "Tanggal umum berdasarkan pola musim tanam sejak tahun 2017.",
      plant: "Mulai Tanam",
      harvest: "Panen",
      none: "Data musim tanam sebelumnya di desa ini belum cukup untuk menyusun jadwal.",
    },
    harvest: {
      title: "Perkiraan Panen 8 Minggu ke Depan",
      row: (week: string, ha: string) => `Minggu ${week}: sekitar ${ha}`,
      summary: (peak: string, first: string, last: string) =>
        `Panen paling banyak diperkirakan pada minggu ${peak}. Panen berlangsung kira-kira dari minggu ${first} sampai minggu ${last}.`,
      empty: (date: string | null) =>
        date
          ? `Belum terdapat perkiraan panen dalam 8 minggu ke depan. Panen musim tanam utama umumnya paling banyak sekitar ${date}.`
          : "Belum terdapat perkiraan panen dalam 8 minggu ke depan.",
    },
    compare: {
      title: "Perbandingan dengan Desa Lain",
      body: "Nomor desa ini di antara 13 desa di Kecamatan Tikung. Nomor 1 berarti angkanya paling besar, belum tentu paling baik. Berapa Kali Tanam adalah rata-rata berapa kali satu petak sawah ditanami dalam setahun.",
      place: (place: number, total: number) =>
        `Nomor ${place} dari ${total} desa`,
      basisTumbuh: (growing: string, known: string) =>
        ` (${growing} dari ${known} sawah yang diketahui)`,
      link: "Lihat Perbandingan Seluruh Desa",
    },
    map: {
      title: "Letak Sawah",
    },
  },
};
