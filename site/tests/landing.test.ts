// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest'
import { dayOfYear, mainSeasonDates, rainBaseline, rainByMonth, seasonBands, seasonProgress, stageTotals } from '../app/utils/landing'
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

describe('rain band', () => {
  const january = (year: number, mm: number) => ({ unit: 'A', year, month: 1, precip_mm: mm, normal_mm: 100 }) as RainRow
  const rows = [january(2018, 50), january(2019, 400), january(2020, 100), january(2021, 100), january(2022, 100), january(2023, 100), january(2024, 100), january(2025, 300)]

  it('takes the minimum and maximum of earlier years in the same calendar month', () => {
    const m = rainByMonth(rows, 1)[0]!
    expect(m.year).toBe(2025)
    expect(m.lo).toBe(50)
    expect(m.hi).toBe(400)
  })

  it('averages only the five latest earlier years, so 2018 and 2019 drop out', () => {
    expect(rainByMonth(rows, 1)[0]!.mean5).toBe(100)
  })

  it('has no band for the first year and falls back to the normal', () => {
    const first = rainByMonth([january(2018, 50)], 1)[0]!
    expect(first.lo).toBeUndefined()
    expect(rainBaseline(first)).toBe(100)
    expect(rainBaseline({ ...first, mean5: 80 })).toBe(80)
  })
})

describe('seasonProgress', () => {
  const season1 = { start: 315, end: 125 }

  it('runs from 0 at the start to 1 at the end, across the new year', () => {
    expect(seasonProgress(season1, 315)).toBe(0)
    expect(seasonProgress(season1, 125)).toBe(1)
    expect(seasonProgress(season1, 20)).toBeCloseTo((20 + 365 - 315) / 175)
  })

  it('is null outside the season', () => {
    expect(seasonProgress(season1, 200)).toBeNull()
    expect(seasonProgress({ start: 10, end: 10 }, 10)).toBeNull()
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
