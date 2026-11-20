// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// Areas the site shows, and loaders for the JSON that `just web` exports per area, copied to public/json.

export interface Area {
  slug: string
  name: string
  unitLabel: string
}

export const AREAS = {
  lamongan: { slug: 'idn-jawatimur-lamongan', name: 'Kabupaten Lamongan', unitLabel: 'kecamatan' },
  tikung: { slug: 'idn-jawatimur-lamongan-tikung', name: 'Kecamatan Tikung', unitLabel: 'desa' }
} satisfies Record<string, Area>

export const STAGES = {
  planted: { label: COPY.stages.planted, color: 'var(--viz-3)' },
  peaked: { label: COPY.stages.peaked, color: 'var(--viz-2)' },
  fallow: { label: COPY.stages.fallow, color: 'var(--viz-neutral)' },
  unknown: { label: COPY.stages.unknown, color: 'transparent' }
} as const

export type Stage = keyof typeof STAGES

export interface Meta {
  aoi: string
  as_of: string
  generated_at: string
  units: { unit: string, cells: number, paddy_ha: number, lon: number, lat: number }[]
  files: string[]
}
export interface Cell { cell_id: number, unit: string, lon: number, lat: number, paddy_frac: number, stage: Stage | null }
export interface CurrentRow { unit: string, stage: Stage | null, paddy_ha: number }
export interface OutlookRow { unit: string, week: string, expected_ha: number, cells: number }
export interface SeasonRow {
  unit: string
  year: number
  season: 'MT1' | 'MT2' | 'MT3'
  area_ha: number
  rice_area_ha: number
  rice_unknown_ha: number
  flood_start: string | null
  flood_median: string | null
  flood_end: string | null
  harvest_start: string | null
  harvest_median: string | null
  harvest_end: string | null
}
export interface IntensityRow { unit: string, year: number, paddy_ha: number, ip_all: number | null, ip_rice: number | null, share_3plus: number | null, complete: boolean }
export interface RainRow { unit: string, year: number, month: number, precip_mm: number, normal_mm: number, anomaly_pct: number | null }

// read through the server route at build time, so the data lands in each page payload
// a missing file (an area without that output) is null, not an error
export function useAreaFile<T>(area: Area, file: string) {
  return useAsyncData(`${area.slug}/${file}`, () =>
    $fetch<T>(`/api/area/${area.slug}/${file}`).catch(() => null)
  )
}

// Seasons and rain are large, so the server trims them before they enter a page payload.
export function useAreaSeasons(area: Area) {
  return useAsyncData(`${area.slug}/seasons.slim`, async () => {
    const rows = await $fetch<SeasonRow[]>(`/api/area/${area.slug}/seasons.json`).catch(() => null)
    return rows ? slimSeasons(rows) : null
  })
}

// Without a unit the months average over every unit of the area.
export function useAreaRainMonths(area: Area, unit?: MaybeRefOrGetter<string>) {
  return useAsyncData(`${area.slug}/rain.months/${toValue(unit) ?? 'all'}`, async () => {
    const rows = await $fetch<RainRow[]>(`/api/area/${area.slug}/rain.json`).catch(() => null)
    const only = toValue(unit)
    return rows ? rainByMonth(only ? rows.filter(r => r.unit === only) : rows) : null
  })
}

// Large map-only files load in the browser from the static copy in public/json.
// They stay out of the page payload, and every page shares one cached download.
export function useAreaClientFile<T>(area: Area, file: string) {
  return useAsyncData(`client:${area.slug}/${file}`, () =>
    $fetch<T>(`/json/${area.slug}/${file}`).catch(() => null),
  { server: false, lazy: true }
  )
}

export function formatDate(iso: string | null | undefined, opts: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short', year: 'numeric' }) {
  return iso ? new Date(iso).toLocaleDateString('id-ID', opts) : '-'
}

export function formatHa(ha: number) {
  return `${Math.round(ha).toLocaleString('id-ID')} ha`
}
