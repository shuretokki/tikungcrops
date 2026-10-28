// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// Kecamatan-level facts for the landing page, derived from the per-desa JSON.

import type { CurrentRow, IntensityRow, SeasonRow, Stage } from '~/composables/useArea'

export interface ValidationUnit { unit: string, year: number, measure: string, reference_ha: number, satellite_ha: number }
export interface Validation {
  area: { year: number, measure: string, units: number, r: number, ratio: number }[]
  area_units: ValidationUnit[]
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

export function seasonBands(rows: SeasonRow[]): SeasonBand[] {
  const order: SeasonRow['season'][] = ['MT1', 'MT2', 'MT3']
  return order.flatMap((season) => {
    const own = rows.filter(r => r.season === season && r.rice_area_ha > 0)
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

export interface IntensityYear { year: number, all: number, rice: number }

// Only years where every desa has a full year of images, weighted by paddy area.
export function intensityByYear(rows: IntensityRow[]): IntensityYear[] {
  const years = new Map<number, { all: number, rice: number, w: number, complete: boolean }>()
  for (const r of rows) {
    if (r.ip_all === null) continue
    const y = years.get(r.year) ?? { all: 0, rice: 0, w: 0, complete: true }
    y.all += r.ip_all * r.paddy_ha
    y.rice += (r.ip_rice ?? 0) * r.paddy_ha
    y.w += r.paddy_ha
    y.complete &&= r.complete
    years.set(r.year, y)
  }
  return [...years.entries()]
    .filter(([, y]) => y.complete && y.w > 0)
    .sort(([a], [b]) => a - b)
    .map(([year, y]) => ({ year, all: y.all / y.w, rice: y.rice / y.w }))
}

export function stageTotals(rows: CurrentRow[]) {
  const totals: Record<Stage, number> = { planted: 0, peaked: 0, fallow: 0, unknown: 0 }
  for (const r of rows) totals[r.stage ?? 'unknown'] += r.paddy_ha
  return totals
}

export function monthName(day: number, style: 'long' | 'short' = 'long') {
  return new Date(Date.UTC(2001, 0, 1 + day)).toLocaleDateString('id-ID', { month: style, timeZone: 'UTC' })
}
