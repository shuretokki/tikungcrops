<script setup lang="ts">
import type { FeatureCollection } from 'geojson'
import { AREAS, STAGES, formatDate, formatHa, useAreaClientFile, useAreaFile, type Cell, type CurrentRow, type Meta, type OutlookRow, type SeasonRow, type Stage } from '~/composables/useArea'

const t = COPY.ringkasan
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: current } = await useAreaFile<CurrentRow[]>(area, 'current.json')
const { data: outlook } = await useAreaFile<OutlookRow[]>(area, 'outlook.json')
const { data: seasons } = await useAreaFile<SeasonRow[]>(area, 'seasons.json')
const { data: desa } = await useAreaFile<FeatureCollection>(area, 'boundaries.geojson')
const { data: cells } = useAreaClientFile<Cell[]>(area, 'cells.json')
const { data: kecamatan } = useAreaClientFile<FeatureCollection>(AREAS.lamongan, 'boundaries.geojson')

const units = computed(() => meta.value?.units ?? [])
const labels = computed(() => units.value.map(u => ({ name: u.unit, lon: u.lon, lat: u.lat })))
const today = computed(() => (meta.value?.as_of ? dayOfYear(meta.value.as_of) : null))
const day = (d: number) => new Date(Date.UTC(2001, 0, 1 + d)).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', timeZone: 'UTC' })

const stages = computed(() => stageTotals(current.value ?? []))

// Typical main-season dates per desa, from the reliable past seasons of that desa.
const schedule = computed(() => units.value.flatMap((u) => {
  const mt1 = mainSeasonDates((seasons.value ?? []).filter(s => s.unit === u.unit))
  return mt1 ? [{ unit: u.unit, plant: mt1.plant, harvest: mt1.harvest }] : []
}))
const mainHarvest = computed(() => seasonBands(seasons.value ?? []).find(b => b.season === 'MT1')?.harvest)

// Weeks within eight weeks of the data date. Desa with less than one hectare are left out as noise.
const HORIZON_DAYS = 56
const upcoming = computed(() => {
  const asOf = meta.value?.as_of ? new Date(meta.value.as_of).getTime() : 0
  const near = (outlook.value ?? []).filter((o) => {
    const dt = new Date(o.week).getTime() - asOf
    return dt >= -6 * 86_400_000 && dt <= HORIZON_DAYS * 86_400_000
  })
  const byUnit = new Map<string, OutlookRow[]>()
  for (const o of near) byUnit.set(o.unit, [...(byUnit.get(o.unit) ?? []), o])
  const rows = [...byUnit.entries()].map(([unit, weeks]) => {
    const top = weeks.reduce((a, b) => (b.expected_ha > a.expected_ha ? b : a))
    return { unit, total: weeks.reduce((s, w) => s + w.expected_ha, 0), topWeek: top.week }
  }).filter(r => r.total >= 1)
  return rows.sort((a, b) => a.topWeek.localeCompare(b.topWeek))
})
const upcomingMax = computed(() => Math.max(1, ...upcoming.value.map(r => r.total)))

const STAGE_ORDER: Stage[] = ['planted', 'peaked', 'fallow', 'unknown']
const STAGE_FILL: Record<Stage, string> = {
  planted: 'var(--viz-3)',
  peaked: 'var(--viz-2)',
  fallow: 'var(--viz-neutral)',
  unknown: 'repeating-linear-gradient(45deg, var(--viz-neutral) 0 2px, transparent 2px 5px)'
}

const rows = computed(() => units.value.map((u) => {
  const own = stageTotals((current.value ?? []).filter(r => r.unit === u.unit))
  const sum = STAGE_ORDER.reduce((s, k) => s + own[k], 0) || 1
  const sch = schedule.value.find(s => s.unit === u.unit)
  return {
    unit: u.unit,
    paddy: u.paddy_ha,
    mix: STAGE_ORDER.map(k => ({ key: k, share: own[k] / sum })),
    mixTitle: STAGE_ORDER.map(k => `${STAGES[k].label} ${Math.round((own[k] / sum) * 100)}%`).join(', '),
    plant: sch ? day(sch.plant) : '-',
    harvest: sch ? day(sch.harvest) : '-'
  }
}))

const columns = [
  { accessorKey: 'unit', header: t.table.columns.unit },
  { accessorKey: 'paddy', header: t.table.columns.paddy },
  { accessorKey: 'mix', header: t.table.columns.stage },
  { accessorKey: 'plant', header: t.table.columns.plant },
  { accessorKey: 'harvest', header: t.table.columns.harvest }
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
      :description="t.description(units.length, formatDate(meta?.as_of))"
    />
    <UPageBody class="flex flex-col gap-14">
      <section class="flex flex-col gap-4">
        <h2 class="text-xl font-semibold">
          {{ t.now.title }}
        </h2>
        <StageBar :totals="stages" />
      </section>

      <section
        v-if="schedule.length"
        class="flex flex-col gap-4"
      >
        <header class="flex max-w-2xl flex-col gap-2">
          <h2 class="text-xl font-semibold">
            {{ t.schedule.title }}
          </h2>
          <p class="text-muted">
            {{ t.schedule.body }}
          </p>
        </header>
        <DesaSchedule
          :rows="schedule"
          :today="today"
        />
      </section>

      <section class="flex flex-col gap-4">
        <header class="flex max-w-2xl flex-col gap-2">
          <h2 class="text-xl font-semibold">
            {{ t.harvest.title }}
          </h2>
          <p
            v-if="upcoming.length"
            class="text-muted"
          >
            {{ t.harvest.body }}
          </p>
        </header>
        <ul
          v-if="upcoming.length"
          class="flex flex-col gap-2"
        >
          <li
            v-for="r in upcoming"
            :key="r.unit"
          >
            <NuxtLink
              :to="`/desa/${encodeURIComponent(r.unit)}`"
              class="grid grid-cols-[7rem_1fr] items-center gap-x-3 gap-y-1 rounded-md px-2 py-1.5 hover:bg-muted sm:grid-cols-[9rem_1fr_16rem]"
            >
              <span class="font-semibold">{{ r.unit }}</span>
              <span class="h-3 rounded-sm bg-muted">
                <span
                  class="block h-full rounded-sm bg-(--viz-2)"
                  :style="{ width: `${(r.total / upcomingMax) * 100}%` }"
                />
              </span>
              <span class="col-span-2 text-sm text-muted tabular-nums sm:col-span-1">{{ t.harvest.row(formatDate(r.topWeek, { day: 'numeric', month: 'short' }), formatHa(r.total)) }}</span>
            </NuxtLink>
          </li>
        </ul>
        <p
          v-else
          class="flex items-center gap-3 rounded-md bg-muted p-4 text-sm"
        >
          <UIcon
            name="i-lucide-calendar-clock"
            class="size-5 shrink-0 text-(--ui-primary)"
          />
          {{ t.harvest.empty(mainHarvest !== undefined ? monthName(mainHarvest) : '-') }}
        </p>
      </section>

      <section class="flex flex-col gap-4">
        <h2 class="text-xl font-semibold">
          {{ t.map.title }}
        </h2>
        <div class="h-[28rem]">
          <ClientOnly>
            <AreaMap
              :outer="kecamatan"
              :inner="desa"
              :cells="cells"
              :labels="labels"
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
      </section>

      <section class="flex flex-col gap-4">
        <h2 class="text-xl font-semibold">
          {{ t.table.title }}
        </h2>
        <UTable
          :data="rows"
          :columns="columns"
          @select="(_e: unknown, row: { original: { unit: string } }) => open(row.original.unit)"
        >
          <template #unit-cell="{ row }">
            <NuxtLink
              :to="`/desa/${encodeURIComponent(row.original.unit)}`"
              class="font-semibold text-(--ui-primary) hover:underline"
              @mouseenter="selected = row.original.unit"
              @mouseleave="selected = null"
            >
              {{ row.original.unit }}
            </NuxtLink>
          </template>
          <template #paddy-cell="{ row }">
            <span class="tabular-nums">{{ formatHa(row.original.paddy) }}</span>
          </template>
          <template #mix-cell="{ row }">
            <span
              class="flex h-2 w-28 gap-px overflow-hidden rounded-full"
              :title="row.original.mixTitle"
            >
              <span
                v-for="m in row.original.mix.filter(m => m.share > 0)"
                :key="m.key"
                class="h-full"
                :style="{ flexGrow: m.share, background: STAGE_FILL[m.key] }"
              />
            </span>
          </template>
        </UTable>
      </section>
    </UPageBody>
  </UPage>
</template>
