// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest'
import { growingShare, latestIntensity, placeOf, rank } from '../app/utils/compare'
import type { CurrentRow, IntensityRow } from '../app/composables/useArea'

const row = (over: Partial<IntensityRow>): IntensityRow => ({
  unit: 'A', year: 2024, paddy_ha: 100, ip_all: 2, ip_rice: 1.5, share_3plus: 0, complete: true, ...over
})

describe('latestIntensity', () => {
  it('uses the newest complete year and skips partial years', () => {
    const rows = [
      row({ unit: 'A', year: 2023, ip_all: 1.2 }),
      row({ unit: 'A', year: 2024, ip_all: 1.6 }),
      row({ unit: 'A', year: 2025, ip_all: 0.4, complete: false })
    ]
    expect(latestIntensity(rows)).toEqual({ year: 2024, entries: [{ unit: 'A', value: 1.6 }] })
  })

  it('returns no year when nothing is complete', () => {
    expect(latestIntensity([row({ complete: false })])).toEqual({ year: null, entries: [] })
  })

  it('skips a unit with no intensity', () => {
    expect(latestIntensity([row({ ip_all: null })]).entries).toEqual([])
  })

  it('ignores the rice-only column, so a weak rice flag cannot lower a unit', () => {
    const entries = latestIntensity([row({ ip_all: 1.8, ip_rice: 0.3 })]).entries
    expect(entries).toEqual([{ unit: 'A', value: 1.8 }])
  })
})

describe('growingShare', () => {
  const cur = (unit: string, stage: CurrentRow['stage'], paddy_ha: number) => ({ unit, stage, paddy_ha }) as CurrentRow

  it('counts planted and peaked paddy against all readable paddy', () => {
    const rows = [cur('A', 'planted', 30), cur('A', 'peaked', 10), cur('A', 'fallow', 60)]
    expect(growingShare(rows)).toEqual([{ unit: 'A', value: 0.4 }])
  })

  it('ignores cells hidden by cloud', () => {
    const rows = [cur('A', 'planted', 10), cur('A', 'unknown', 500), cur('A', null, 500)]
    expect(growingShare(rows)).toEqual([{ unit: 'A', value: 1 }])
  })

  it('drops a unit with no readable paddy', () => {
    expect(growingShare([cur('A', 'unknown', 50)])).toEqual([])
  })
})

describe('placeOf', () => {
  const entries = [{ unit: 'A', value: 1 }, { unit: 'B', value: 3 }, { unit: 'C', value: 2 }]

  it('gives the position and the number of ranked units', () => {
    expect(placeOf(entries, 'C')).toEqual({ place: 2, total: 3 })
    expect(placeOf(entries, 'B')).toEqual({ place: 1, total: 3 })
  })

  it('is null for a unit that has no value', () => {
    expect(placeOf(entries, 'Z')).toBeNull()
  })
})

describe('rank', () => {
  it('sorts from high to low and breaks ties by name', () => {
    const out = rank([{ unit: 'B', value: 1 }, { unit: 'C', value: 3 }, { unit: 'A', value: 1 }])
    expect(out.map(e => e.unit)).toEqual(['C', 'A', 'B'])
  })

  it('does not change the input array', () => {
    const input = [{ unit: 'B', value: 1 }, { unit: 'A', value: 2 }]
    rank(input)
    expect(input[0]!.unit).toBe('B')
  })
})
