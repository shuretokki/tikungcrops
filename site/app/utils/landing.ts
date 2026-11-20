// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// Kecamatan-level facts for the landing page, derived from the per-desa JSON.

import type { FeatureCollection, Position } from 'geojson'
import type { CurrentRow, RainRow, SeasonRow, Stage } from '~/composables/useArea'

export interface ValidationUnit { unit: string, year: number, measure: string, reference_ha: number, satellite_ha: number }
export interface Validation {
  area: { year: number, measure: string, units: number, r: number, ratio: number, median_abs_diff_pct?: number }[]
  area_units: ValidationUnit[]
}

// The season columns the pages read. The server keeps only these, so the page payload stays small.
export type SeasonSlim = Pick<SeasonRow, 'unit' | 'year' | 'season' | 'rice_area_ha' | 'flood_start' | 'flood_median' | 'harvest_median' | 'harvest_end'>

export function slimSeasons(rows: SeasonRow[]): SeasonSlim[] {
  return rows.map(r => ({
    unit: r.unit,
    year: r.year,
    season: r.season,
    rice_area_ha: r.rice_area_ha,
    flood_start: r.flood_start,
    flood_median: r.flood_median,
    harvest_median: r.harvest_median,
    harvest_end: r.harvest_end
  }))
}

export interface SeasonBand {
  season: SeasonRow['season']
  start: number
  plant: number
  harvest: number
  end: number
  meanHa: number
  years: number
}

const YEAR_DAYS = 365

export function dayOfYear(iso: string) {
  const d = new Date(iso)
  return Math.round((d.getTime() - Date.UTC(d.getUTCFullYear(), 0, 1)) / 86_400_000)
}

// Season dates cross the new year, so an arithmetic mean of day-of-year would land in mid-year.
function circularMean(points: [day: number, weight: number][]) {
  let x = 0
  let y = 0
  for (const [day, w] of points) {
    const a = (2 * Math.PI * day) / YEAR_DAYS
    x += w * Math.cos(a)
    y += w * Math.sin(a)
  }
  const day = (Math.atan2(y, x) * YEAR_DAYS) / (2 * Math.PI)
  return Math.round((day + YEAR_DAYS) % YEAR_DAYS)
}

// MT1 seasons count only when their flooding peak falls in October to January.
// Peaks in February to April come from the partial first year and from radar gaps (F08, F22), not from real planting.
const SEP1 = dayOfYear('2001-09-01')
// The month and day are read in a common non-leap year, so a leap year never shifts a date by one day.
const sinceSep = (iso: string) => (dayOfYear(`2001-${iso.slice(5, 10)}`) - SEP1 + 365) % 365
function isReliable(r: SeasonSlim) {
  if (r.season !== 'MT1') return true
  return !!r.flood_median && sinceSep(r.flood_median) >= 30 && sinceSep(r.flood_median) < 153
}

export function seasonBands(rows: SeasonSlim[]): SeasonBand[] {
  const order: SeasonRow['season'][] = ['MT1', 'MT2', 'MT3']
  return order.flatMap((season) => {
    const own = rows.filter(r => r.season === season && r.rice_area_ha > 0 && isReliable(r))
    if (!own.length) return []
    const at = (key: 'flood_start' | 'flood_median' | 'harvest_median' | 'harvest_end') =>
      circularMean(own.filter(r => r[key]).map(r => [dayOfYear(r[key]!), r.rice_area_ha]))
    const perYear = new Map<number, number>()
    for (const r of own) perYear.set(r.year, (perYear.get(r.year) ?? 0) + r.rice_area_ha)
    const total = [...perYear.values()].reduce((s, v) => s + v, 0)
    return [{
      season,
      start: at('flood_start'),
      plant: at('flood_median'),
      harvest: at('harvest_median'),
      end: at('harvest_end'),
      meanHa: total / perYear.size,
      years: perYear.size
    }]
  })
}

// The band and the five-year mean follow the AGMET plots of GEOGLAM Crop Monitor.
// They use the same calendar month of earlier years only, so the current year never compares with itself.
export interface RainMonth { year: number, month: number, mm: number, normal: number, lo?: number, hi?: number, mean5?: number }

// The baseline of a month is the mean of the last five years, and the long-term normal when fewer years exist.
export const rainBaseline = (m: RainMonth) => m.mean5 ?? m.normal

// Share of a season that has passed on a given day of the year, from its start to its end.
// This is the Progress of Season of FAO ASIS. It is null when the day is outside the season.
export function seasonProgress(band: { start: number, end: number }, today: number): number | null {
  const length = (band.end - band.start + 365) % 365
  if (length === 0) return null
  const passed = (today - band.start + 365) % 365
  return passed <= length ? passed / length : null
}

export interface MainSeasonDates { plant: number, harvest: number, seasons: number }

// Typical main-season (MT1) dates for one desa, as day-of-year.
// The median of the reliable seasons resists the odd year better than a mean.
export function mainSeasonDates(rows: SeasonSlim[], minSeasons = 3): MainSeasonDates | null {
  const ok = rows.filter(r => r.season === 'MT1' && r.rice_area_ha > 0 && r.harvest_median && isReliable(r))
  if (ok.length < minSeasons) return null
  const median = (v: number[]) => {
    const s = [...v].sort((a, b) => a - b)
    const m = Math.floor(s.length / 2)
    return s.length % 2 ? s[m]! : (s[m - 1]! + s[m]!) / 2
  }
  const back = (d: number) => Math.round((d + SEP1) % 365)
  return {
    plant: back(median(ok.map(r => sinceSep(r.flood_median!)))),
    harvest: back(median(ok.map(r => sinceSep(r.harvest_median!)))),
    seasons: ok.length
  }
}

export interface RainVerdict { kind: 'same' | 'wetter' | 'drier' | 'above' | 'below', pct: number }

// A percent of a very small baseline exaggerates, so under minBase millimetres only the direction is reported.
export function rainVerdict(mm: number, base: number, minBase = 20, tolerance = 0.05): RainVerdict {
  if (base < minBase) {
    const gap = mm - base
    return { kind: Math.abs(gap) < 1 ? 'same' : gap > 0 ? 'above' : 'below', pct: 0 }
  }
  const diff = (mm - base) / base
  if (Math.abs(diff) < tolerance) return { kind: 'same', pct: 0 }
  return { kind: diff > 0 ? 'wetter' : 'drier', pct: Math.abs(diff) }
}

export interface SeasonYear { year: number, plant: number, harvest: number, ha: number }

// The MT1 seasons of one desa, oldest first, with plant and harvest days counted in a non-leap year.
export function seasonHistory(rows: SeasonSlim[]): SeasonYear[] {
  const md = (iso: string) => dayOfYear(`2001-${iso.slice(5, 10)}`)
  return rows
    .filter(r => r.season === 'MT1' && r.rice_area_ha > 0 && r.flood_median && r.harvest_median && isReliable(r))
    .sort((a, b) => a.year - b.year)
    .map(r => ({ year: r.year, plant: md(r.flood_median!), harvest: md(r.harvest_median!), ha: r.rice_area_ha }))
}

export interface OnsetShift { year: number, plant: number, mean: number, shift: number, priorSeasons: number }

// How much later or earlier the newest MT1 planting peak came than the mean of up to five earlier MT1 seasons.
// This is the Delayed Onset driver of GEOGLAM Crop Monitor. A positive shift means later, in days.
export function onsetShift(rows: SeasonSlim[], baselineSeasons = 5, minPrior = 3): OnsetShift | null {
  const ok = rows
    .filter(r => r.season === 'MT1' && r.rice_area_ha > 0 && r.flood_median && isReliable(r))
    .sort((a, b) => a.year - b.year)
  const latest = ok.at(-1)
  if (!latest) return null
  const prior = ok.slice(0, -1).slice(-baselineSeasons)
  if (prior.length < minPrior) return null
  const mean = prior.reduce((s, r) => s + sinceSep(r.flood_median!), 0) / prior.length
  const own = sinceSep(latest.flood_median!)
  const back = (d: number) => Math.round((d + SEP1) % 365)
  return { year: latest.year, plant: back(own), mean: back(mean), shift: Math.round(own - mean), priorSeasons: prior.length }
}

export interface DesaOutlines { viewBox: string, paths: { unit: string, d: string }[] }

// SVG outlines of every desa in one shared frame, so a tile can highlight its own desa.
// An equirectangular projection scaled by cos(latitude) is exact enough at kecamatan size.
export function desaOutlines(fc: FeatureCollection | null | undefined, width = 100): DesaOutlines | null {
  if (!fc?.features.length) return null
  const rings: { unit: string, rings: Position[][] }[] = fc.features.map((f) => {
    const g = f.geometry
    const polys = g.type === 'MultiPolygon' ? g.coordinates : g.type === 'Polygon' ? [g.coordinates] : []
    return { unit: String(f.properties?.unit ?? ''), rings: polys.flat() }
  })
  const all = rings.flatMap(r => r.rings.flat())
  const lons = all.map(p => p[0]!)
  const lats = all.map(p => p[1]!)
  const [minX, maxX, minY, maxY] = [Math.min(...lons), Math.max(...lons), Math.min(...lats), Math.max(...lats)]
  const k = Math.cos(((minY + maxY) / 2) * Math.PI / 180)
  const scale = width / ((maxX - minX) * k)
  const height = (maxY - minY) * scale
  const pt = (p: Position) => `${((p[0]! - minX) * k * scale).toFixed(1)},${((maxY - p[1]!) * scale).toFixed(1)}`
  return {
    viewBox: `0 0 ${width} ${height.toFixed(1)}`,
    paths: rings.map(r => ({ unit: r.unit, d: r.rings.map(ring => `M${ring.map(pt).join('L')}Z`).join('') }))
  }
}

// BPS Provinsi Jawa Timur, "Luas Panen dan Produksi Padi di Provinsi Jawa Timur 2025" (released 3 Sep 2026), Lampiran 3, 6 and 8.
// Production is tons of GKG.
// Harvested area is the 2024 value plus the published 2025 change, because the 2025 column is unreadable in the PDF text.
// Update once a year when BPS releases the next edition.
export const JATIM_RICE = {
  year: 2025,
  top: [
    { name: 'Lamongan', tons: 879_993.80 },
    { name: 'Bojonegoro', tons: 879_685.13 },
    { name: 'Ngawi', tons: 772_570.76 },
    { name: 'Jember', tons: 679_513.67 },
    { name: 'Tuban', tons: 577_963.77 }
  ],
  province: 10_438_360.58,
  lamonganRiceTons: 508_126.15,
  lamonganHarvestHa: 152_564
}

// Mean over desa for the most recent months in the export.
export function rainByMonth(rows: RainRow[], months = 12): RainMonth[] {
  const byMonth = new Map<string, { year: number, month: number, mm: number, normal: number, n: number }>()
  for (const r of rows) {
    const key = `${r.year}-${r.month}`
    const m = byMonth.get(key) ?? { year: r.year, month: r.month, mm: 0, normal: 0, n: 0 }
    m.mm += r.precip_mm
    m.normal += r.normal_mm
    m.n += 1
    byMonth.set(key, m)
  }
  const all = [...byMonth.values()]
    .sort((a, b) => a.year - b.year || a.month - b.month)
    .map(m => ({ year: m.year, month: m.month, mm: m.mm / m.n, normal: m.normal / m.n }))
  return all.slice(-months).map((m): RainMonth => {
    const prior = all.filter(o => o.month === m.month && o.year < m.year).sort((a, b) => b.year - a.year)
    if (!prior.length) return m
    const last5 = prior.slice(0, 5)
    return {
      ...m,
      lo: Math.min(...prior.map(p => p.mm)),
      hi: Math.max(...prior.map(p => p.mm)),
      mean5: last5.reduce((s, p) => s + p.mm, 0) / last5.length
    }
  })
}

export function stageTotals(rows: CurrentRow[]) {
  const totals: Record<Stage, number> = { planted: 0, peaked: 0, fallow: 0, unknown: 0 }
  for (const r of rows) totals[r.stage ?? 'unknown'] += r.paddy_ha
  return totals
}

export function monthName(day: number, style: 'long' | 'short' = 'long') {
  return new Date(Date.UTC(2001, 0, 1 + day)).toLocaleDateString('id-ID', { month: style, timeZone: 'UTC' })
}
