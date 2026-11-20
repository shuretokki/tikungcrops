// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// Values the comparison page ranks, one number per desa or kecamatan.

import type { CurrentRow, IntensityRow } from '~/composables/useArea'

export interface Entry { unit: string, value: number }

// Rice cropping intensity of the newest year that has a full set of scenes.
export function latestIntensity(rows: IntensityRow[]): { year: number | null, entries: Entry[] } {
  const ok = rows.filter(r => r.complete && r.ip_rice !== null)
  if (!ok.length) return { year: null, entries: [] }
  const year = Math.max(...ok.map(r => r.year))
  return { year, entries: ok.filter(r => r.year === year).map(r => ({ unit: r.unit, value: r.ip_rice! })) }
}

// Share of the readable paddy that is planted or close to harvest.
// Cells hidden by cloud are left out, so a cloudy week does not look like a resting field.
export function growingShare(rows: CurrentRow[]): Entry[] {
  const sums = new Map<string, { growing: number, known: number }>()
  for (const r of rows) {
    if (!r.stage || r.stage === 'unknown') continue
    const s = sums.get(r.unit) ?? { growing: 0, known: 0 }
    s.known += r.paddy_ha
    if (r.stage === 'planted' || r.stage === 'peaked') s.growing += r.paddy_ha
    sums.set(r.unit, s)
  }
  return [...sums.entries()].filter(([, s]) => s.known > 0).map(([unit, s]) => ({ unit, value: s.growing / s.known }))
}

export function rank(entries: Entry[]): Entry[] {
  return [...entries].sort((a, b) => b.value - a.value || a.unit.localeCompare(b.unit))
}

// Position of one unit in the ranking, with the number of ranked units. Null when the unit has no value.
export function placeOf(entries: Entry[], unit: string): { place: number, total: number } | null {
  const ranked = rank(entries)
  const i = ranked.findIndex(e => e.unit === unit)
  return i < 0 ? null : { place: i + 1, total: ranked.length }
}
