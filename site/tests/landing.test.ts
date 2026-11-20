// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest'
import { dayOfYear, mainSeasonDates, rainByMonth, seasonBands, stageTotals } from '../app/utils/landing'
import type { CurrentRow, RainRow, SeasonRow } from '../app/composables/useArea'

function season(over: Partial<SeasonRow>): SeasonRow {
  return {
    unit: 'Jotosanur',
    year: 2024,
    season: 'MT1',
    rice_area_ha: 100,
    flood_start: '2023-11-10',
    flood_median: '2023-11-25',
    harvest_median: '2024-03-10',
    harvest_end: '2024-03-25',
    ...over
  } as SeasonRow
}

describe('dayOfYear', () => {
  it('counts from 1 January as day 0', () => {
    expect(dayOfYear('2024-01-01')).toBe(0)
    expect(dayOfYear('2024-03-01')).toBe(60)
  })
})

describe('seasonBands', () => {
  it('keeps a season that crosses the new year near its real dates', () => {
    const rows = [season({ year: 2023 }), season({ year: 2024, flood_median: '2024-11-27' })]
    const [band] = seasonBands(rows)
    expect(band?.season).toBe('MT1')
    expect(band?.plant).toBeGreaterThan(320)
    expect(band?.plant).toBeLessThan(340)
  })

  it('ignores a main season whose flooding peak falls in the unreliable months', () => {
    const rows = [season({ flood_median: '2024-03-01' })]
    expect(seasonBands(rows)).toEqual([])
  })

  it('skips seasons without rice', () => {
    expect(seasonBands([season({ rice_area_ha: 0 })])).toEqual([])
  })
})

describe('mainSeasonDates', () => {
  it('needs at least three reliable seasons', () => {
    const rows = [season({ year: 2022 }), season({ year: 2023 })]
    expect(mainSeasonDates(rows)).toBeNull()
  })

  it('returns the median plant and harvest days', () => {
    const rows = [2021, 2022, 2023].map(year => season({ year }))
    const dates = mainSeasonDates(rows)
    expect(dates?.seasons).toBe(3)
    expect(dates?.plant).toBe(dayOfYear('2023-11-25'))
    expect(dates?.harvest).toBe(dayOfYear('2024-03-10'))
  })
})

describe('rainByMonth', () => {
  it('averages over desa and keeps the newest months', () => {
    const rows = [
      { unit: 'A', year: 2026, month: 1, precip_mm: 100, normal_mm: 200 },
      { unit: 'B', year: 2026, month: 1, precip_mm: 300, normal_mm: 200 },
      { unit: 'A', year: 2026, month: 2, precip_mm: 50, normal_mm: 150 }
    ] as RainRow[]
    expect(rainByMonth(rows, 1)).toEqual([{ year: 2026, month: 2, mm: 50, normal: 150 }])
    expect(rainByMonth(rows)[0]).toEqual({ year: 2026, month: 1, mm: 200, normal: 200 })
  })
})

describe('stageTotals', () => {
  it('sums paddy hectares per stage and counts a missing stage as unknown', () => {
    const rows = [
      { unit: 'A', stage: 'planted', paddy_ha: 10 },
      { unit: 'B', stage: 'planted', paddy_ha: 5 },
      { unit: 'C', stage: null, paddy_ha: 2 }
    ] as unknown as CurrentRow[]
    expect(stageTotals(rows)).toEqual({ planted: 15, peaked: 0, fallow: 0, unknown: 2 })
  })
})
