// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest'
import { mainSeasonDates, seasonBands, slimSeasons } from '../app/utils/landing'
import type { SeasonRow } from '../app/composables/useArea'

const full = (year: number): SeasonRow => ({
  unit: 'Jotosanur',
  year,
  season: 'MT1',
  area_ha: 120,
  rice_area_ha: 100,
  rice_unknown_ha: 5,
  flood_start: `${year - 1}-11-10`,
  flood_median: `${year - 1}-11-25`,
  flood_end: `${year - 1}-12-10`,
  harvest_start: `${year}-03-01`,
  harvest_median: `${year}-03-10`,
  harvest_end: `${year}-03-25`
})

describe('slimSeasons', () => {
  it('keeps only the columns the pages read', () => {
    const [row] = slimSeasons([full(2024)])
    expect(Object.keys(row!).sort()).toEqual(['flood_median', 'flood_start', 'harvest_end', 'harvest_median', 'rice_area_ha', 'season', 'unit', 'year'])
  })

  it('gives the same bands and dates as the full rows', () => {
    const rows = [2021, 2022, 2023, 2024].map(full)
    expect(seasonBands(slimSeasons(rows))).toEqual(seasonBands(rows))
    expect(mainSeasonDates(slimSeasons(rows))).toEqual(mainSeasonDates(rows))
  })
})
