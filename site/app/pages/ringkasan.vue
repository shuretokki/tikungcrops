<script setup lang="ts">
import type { FeatureCollection } from 'geojson'
import { AREAS, STAGES, formatDate, formatHa, useAreaFile, type Cell, type CurrentRow, type Meta, type OutlookRow, type Stage } from '~/composables/useArea'

const t = COPY.ringkasan
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: current } = await useAreaFile<CurrentRow[]>(area, 'current.json')
const { data: outlook } = await useAreaFile<OutlookRow[]>(area, 'outlook.json')
const { data: cells } = await useAreaFile<Cell[]>(area, 'cells.json')
const { data: desa } = await useAreaFile<FeatureCollection>(area, 'boundaries.geojson')
const { data: kecamatan } = await useAreaFile<FeatureCollection>(AREAS.lamongan, 'boundaries.geojson')

function haBy(unit: string | null, stage: Stage) {
  return (current.value ?? []).filter(r => (unit === null || r.unit === unit) && r.stage === stage).reduce((s, r) => s + r.paddy_ha, 0)
}

const rows = computed(() =>
  (meta.value?.units ?? []).map((u) => {
    const weeks = (outlook.value ?? []).filter(o => o.unit === u.unit)
    const top = weeks.reduce<OutlookRow | null>((best, w) => (!best || w.expected_ha > best.expected_ha ? w : best), null)
    return {
      unit: u.unit,
      paddy: u.paddy_ha,
      planted: haBy(u.unit, 'planted'),
      peaked: haBy(u.unit, 'peaked'),
      outlook: weeks.reduce((s, w) => s + w.expected_ha, 0),
      topWeek: top?.week ?? null
    }
  })
)

const totals = computed(() => ({
  paddy: rows.value.reduce((s, r) => s + r.paddy, 0),
  planted: haBy(null, 'planted'),
  peaked: haBy(null, 'peaked'),
  outlook: rows.value.reduce((s, r) => s + r.outlook, 0)
}))

const columns = [
  { accessorKey: 'unit', header: t.columns.unit },
  { accessorKey: 'paddy', header: t.columns.paddy },
  { accessorKey: 'planted', header: STAGES.planted.label },
  { accessorKey: 'peaked', header: STAGES.peaked.label },
  { accessorKey: 'outlook', header: t.columns.outlook },
  { accessorKey: 'topWeek', header: t.columns.topWeek }
]

const selected = ref<string | null>(null)
function open(unit: string) {
  navigateTo(`/desa/${encodeURIComponent(unit)}`)
}

useSeoMeta({ title: t.seoTitle })
</script>

<template>
  <UPage>
    <UPageHeader
      :title="t.title"
      :description="t.description(formatDate(meta?.as_of))"
    />
    <UPageBody>
      <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <UCard>
          <p class="text-xs text-muted">
            {{ t.paddy }}
          </p>
          <p class="text-xl font-semibold">
            {{ formatHa(totals.paddy) }}
          </p>
        </UCard>
        <UCard>
          <p class="text-xs text-muted">
            {{ STAGES.planted.label }}
          </p>
          <p class="text-xl font-semibold">
            {{ formatHa(totals.planted) }}
          </p>
        </UCard>
        <UCard>
          <p class="text-xs text-muted">
            {{ STAGES.peaked.label }}
          </p>
          <p class="text-xl font-semibold">
            {{ formatHa(totals.peaked) }}
          </p>
        </UCard>
        <UCard>
          <p class="text-xs text-muted">
            {{ t.outlook }}
          </p>
          <p class="text-xl font-semibold">
            {{ formatHa(totals.outlook) }}
          </p>
        </UCard>
      </div>

      <div class="h-[28rem]">
        <ClientOnly>
          <AreaMap
            :outer="kecamatan"
            :inner="desa"
            :cells="cells"
            :selected="selected"
            @select="open"
          />
          <template #fallback>
            <div class="flex h-full items-center justify-center rounded-md bg-muted text-sm text-muted">
              {{ t.mapLoading }}
            </div>
          </template>
        </ClientOnly>
      </div>

      <UAlert
        color="warning"
        icon="i-lucide-cloud-rain"
        :title="t.alertTitle"
        :description="t.alert"
      />

      <UTable
        :data="rows"
        :columns="columns"
        @select="(_e: unknown, row: { original: { unit: string } }) => open(row.original.unit)"
      >
        <template #paddy-cell="{ row }">
          {{ formatHa(row.original.paddy) }}
        </template>
        <template #planted-cell="{ row }">
          {{ formatHa(row.original.planted) }}
        </template>
        <template #peaked-cell="{ row }">
          {{ formatHa(row.original.peaked) }}
        </template>
        <template #outlook-cell="{ row }">
          {{ formatHa(row.original.outlook) }}
        </template>
        <template #topWeek-cell="{ row }">
          {{ formatDate(row.original.topWeek, { day: 'numeric', month: 'short' }) }}
        </template>
        <template #unit-cell="{ row }">
          <NuxtLink
            :to="`/desa/${encodeURIComponent(row.original.unit)}`"
            class="text-primary hover:underline"
            @mouseenter="selected = row.original.unit"
            @mouseleave="selected = null"
          >
            {{ row.original.unit }}
          </NuxtLink>
        </template>
      </UTable>
    </UPageBody>
  </UPage>
</template>
