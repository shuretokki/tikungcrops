// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from 'vitest'
import { seasonSegments } from '../app/utils/timeline'

describe('seasonSegments', () => {
  it('splits a season inside one year into three phases', () => {
    expect(seasonSegments({ start: 100, plant: 120, harvest: 200, end: 220 })).toEqual([
      { phase: 'sow', start: 100, length: 20 },
      { phase: 'grow', start: 120, length: 80 },
      { phase: 'harvest', start: 200, length: 20 }
    ])
  })

  it('wraps a phase that crosses the new year into two pieces', () => {
    const parts = seasonSegments({ start: 300, plant: 330, harvest: 60, end: 80 })
    const grow = parts.filter(p => p.phase === 'grow')
    expect(grow).toEqual([
      { phase: 'grow', start: 330, length: 35 },
      { phase: 'grow', start: 0, length: 60 }
    ])
  })

  it('keeps the total length equal to the season length', () => {
    const parts = seasonSegments({ start: 300, plant: 330, harvest: 60, end: 80 })
    expect(parts.reduce((s, p) => s + p.length, 0)).toBe(365 - 300 + 80)
  })

  it('moves a phase that starts after the new year back to the start of the year', () => {
    const parts = seasonSegments({ start: 350, plant: 10, harvest: 90, end: 120 })
    expect(parts.find(p => p.phase === 'harvest')).toEqual({ phase: 'harvest', start: 90, length: 30 })
  })
})
