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

## Sources

### idn-jawatimur-lamongan-tikung (Kecamatan Tikung, Lamongan)

| `source` | Publication | Tables | Data year |
|---|---|---|---|
| `bps_tikung_2014` | BPS Kabupaten Lamongan, *Kecamatan Tikung Dalam Angka 2014*, catalogue 1102001.3524140 | 5.3, p. 56 | 2013 |
| `bps_tikung_2021` | BPS Kabupaten Lamongan, *Kecamatan Tikung Dalam Angka 2021*, publication 35240, ISSN 2798-7892 | 5.1-5.5, pp. 119-123 | 2020 |

- 2013: rice only. 2020: rice and hybrid maize (`jagung_hibrida`).
- Both years predate Kampung Pandu Sakti (started ~2025), so they are a pre-program
  baseline.
- Editions 2016 and 2022-2024 are cited elsewhere but no download was found
  (searched 2026-09-18); since 2018 BPS estimates rice with the area-sampling survey
  (KSA), so newer editions may not list rice per desa.

Earlier source notes (livestock, fisheries, CIMMYT, news figures on the program) are
kept in `archives/sumber-data/`.
