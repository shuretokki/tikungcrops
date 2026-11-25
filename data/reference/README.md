# Reference statistics

Official or recorded harvest statistics used to check the satellite results
(`just validate AOI`) and loaded into MongoDB `harvests` for the matching area. They
are optional: an area without a folder here runs the whole pipeline, and its results
are reported as unvalidated.

These files are typed in by hand from publications, so they cannot be regenerated and
are tracked in git. Original documents go in `<aoi>/sources/` (PDFs are not tracked).

## Layout

```
reference/<aoi-slug>/harvested_area.csv
reference/<aoi-slug>/sources/          original publications (not tracked)
```

`<aoi-slug>` is the slug `aoi.resolve` gives the area, e.g.
`idn-jawatimur-lamongan-tikung` for `Lamongan/Tikung`.

## `harvested_area.csv`

| Column | Type | Meaning |
|---|---|---|
| `unit` | text | AOI unit name, exactly as the pipeline names it (GADM name or GeoJSON `name`) |
| `year` | int | Data year (not publication year) |
| `crop` | text | Crop as the source names it; rice is any of `padi`, `padi_sawah`, `rice` |
| `harvested_area_ha` | float | Harvested area in the year, summed over seasons |
| `production_ton` | float, optional | Production; empty if the source has none |
| `source` | text | Short id of the publication, described below |

Harvested area counts each season separately (a field harvested twice counts twice),
which is what the satellite season areas are compared against.

## `harvested_area_monthly.csv` (optional)

Harvested area per calendar month for the whole AOI, used to check harvest timing.

| Column | Type | Meaning |
|---|---|---|
| `year` | int | Data year |
| `month` | int | 1-12 |
| `crop` | text | Crop as the source names it |
| `harvested_area_ha` | float | Harvested area in that month |
| `source` | text | Short id of the publication, described below |

## Sources

### idn-jawatimur-lamongan-tikung (Kecamatan Tikung, Lamongan)

| `source` | Publication | Tables | Data year |
|---|---|---|---|
| `bps_tikung_2014` | BPS Kabupaten Lamongan, *Kecamatan Tikung Dalam Angka 2014*, catalogue 1102001.3524140 | 5.3, p. 56 | 2013 |
| `bps_tikung_2021` | BPS Kabupaten Lamongan, *Kecamatan Tikung Dalam Angka 2021*, publication 35240.2117, ISSN 2798-7892 | 5.1-5.5, pp. 119-123 | 2020 |
| `bps_tikung_2022` | BPS Kabupaten Lamongan, *Kecamatan Tikung Dalam Angka 2022*, released 26 Sep 2022 | 5.3 (rice), 5.4 (maize), pp. 120-121 | 2021 |

- 2013: rice only. 2020 and 2021: rice and hybrid maize (`jagung_hibrida`).
- 2021 rows: production divided by area matches the printed productivity for every row.
  Areas sum to the printed totals (rice 7,402 ha, maize 1,255 ha).
  Printed production totals (53,220 t rice, 9,513 t maize) are 36 t and 83 t below the row sums, which is an inconsistency in the source.
  Rows stay as printed.
- All three years predate Kampung Pandu Sakti (started ~2025), so they are a pre-program
  baseline. 2021 is the first year the rice thresholds were not tuned on (they come from 2020).
- Editions 2023-2026 (downloaded 2026-10-28) give food crops only for the whole kecamatan, sourced from DKPP.
  Rice area is 7,042 ha in 2021, 7,659 in 2022, 7,658 in 2023 and 5,830 in 2024, so these editions cannot validate per desa.
  DKPP's 2021 kecamatan rice area (7,042 ha) differs from the BPS desa table (7,402 ha), so do not mix the two series.

### idn-jawatimur-lamongan (Kabupaten Lamongan)

| `source` | Publication | Tables | Data year |
|---|---|---|---|
| `bps_ksa_lamongan_2020_2022` | BPS Kabupaten Lamongan, *Luas Panen dan Produksi Padi di Kabupaten Lamongan 2020-2022* (released 22 Dec 2023) | Lampiran 1, p. 63 | 2020 |
| `bps_ksa_lamongan_2023` | BPS Kabupaten Lamongan, *Luas Panen dan Produksi Padi di Kabupaten Lamongan 2023*, publication 35240.24045 | Lampiran 1, p. 53 | 2021-2023 |
| `dkpp_lamongan_2021` | Satu Data Kabupaten Lamongan (satudata.lamongankab.go.id), "Luas Panen Tanaman Pangan Menurut Kecamatan dan Jenis Tanaman", producer DKPP | rows 1.1.1-1.1.27 (padi) | 2021 |

- `harvested_area.csv` holds the DKPP kecamatan rice area for 2021, the only year with
  kecamatan figures found. The page lists values and row labels separately, so the
  mapping was checked against five kecamatan named in the Diskominfo news post of
  2 Feb 2022 (Sugio 10,991, Modo 9,345, Laren 9,061, Kembangbahu 8,912, Kedungpring
  8,632 ha). All five match. The 27 rows sum to 154,209 ha, the post gives 154,204 ha
  and a DKPP post gives 154,206 ha.

- Monthly rice harvest from the area-sampling survey (KSA), kabupaten total only. None of
  the four KSA reports (2020-2021, 2020-2022, 2023, 2024) has kecamatan tables.
- 2020 is published in thousand hectares, so its months sum to 148,020 ha against the
  printed total of 148,030 ha.
- The agriculture office (DKPP) reports 154,204 ha for 2021, 11% above KSA's 138,450 ha.
  Do not mix the two series.
