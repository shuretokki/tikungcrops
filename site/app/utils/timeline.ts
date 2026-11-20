// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// Day numbers run from 0 to 364. A season that crosses the new year keeps counting past 365 and wraps back to 0.

export type Phase = 'sow' | 'grow' | 'harvest'

export interface Segment { phase: Phase, start: number, length: number }

const YEAR = 365

function unwrap(prev: number, day: number) {
  return day < prev ? day + YEAR : day
}

function wrapSpan(from: number, to: number): { start: number, length: number }[] {
  if (to <= YEAR) return [{ start: from, length: to - from }]
  if (from >= YEAR) return [{ start: from - YEAR, length: to - from }]
  return [{ start: from, length: YEAR - from }, { start: 0, length: to - YEAR }]
}

// A season splits into sowing, growing and harvesting, with the plant and harvest peaks as the boundaries.
export function seasonSegments(s: { start: number, plant: number, harvest: number, end: number }): Segment[] {
  const plant = unwrap(s.start, s.plant)
  const harvest = unwrap(plant, s.harvest)
  const end = unwrap(harvest, s.end)
  const spans: [Phase, number, number][] = [['sow', s.start, plant], ['grow', plant, harvest], ['harvest', harvest, end]]
  return spans.flatMap(([phase, from, to]) => wrapSpan(from, to).map(p => ({ phase, ...p })))
}
