<script setup lang="ts">
import type { FeatureCollection } from 'geojson'
import { AREAS, STAGES, formatDate, formatHa, useAreaClientFile, useAreaFile, type Cell, type CurrentRow, type Meta, type OutlookRow, type Stage } from '~/composables/useArea'

const t = COPY.ringkasan
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: current } = await useAreaFile<CurrentRow[]>(area, 'current.json')
const { data: outlook } = await useAreaFile<OutlookRow[]>(area, 'outlook.json')
const { data: desa } = await useAreaFile<FeatureCollection>(area, 'boundaries.geojson')
const { data: cells } = useAreaClientFile<Cell[]>(area, 'cells.json')
const { data: kecamatan } = useAreaClientFile<FeatureCollection>(AREAS.lamongan, 'boundaries.geojson')
const labels = computed(() => (meta.value?.units ?? []).map(u => ({ name: u.unit, lon: u.lon, lat: u.lat })))

const STAGE_ORDER: Stage[] = ['planted', 'peaked', 'fallow', 'unknown']
const STAGE_FILL: Record<Stage, string> = {
  planted: 'var(--viz-3)',
  peaked: 'var(--viz-2)',
  fallow: 'var(--viz-neutral)',
  unknown: 'repeating-linear-gradient(45deg, var(--viz-neutral) 0 2px, transparent 2px 5px)'
}

// Outlook weeks before the data date are already past.
const ahead = computed(() => {
  const from = meta.value?.as_of ? new Date(meta.value.as_of).getTime() - 6 * 86_400_000 : 0
  return (outlook.value ?? []).filter(o => new Date(o.week).getTime() >= from)
})

const rows = computed(() =>
  (meta.value?.units ?? []).map((u) => {
    const own = stageTotals((current.value ?? []).filter(r => r.unit === u.unit))
    const sum = STAGE_ORDER.reduce((s, k) => s + own[k], 0) || 1
    const weeks = ahead.value.filter(o => o.unit === u.unit)
    const top = weeks.reduce<OutlookRow | null>((best, w) => (!best || w.expected_ha > best.expected_ha ? w : best), null)
    return {
      unit: u.unit,
      paddy: u.paddy_ha,
      planted: own.planted,
      peaked: own.peaked,
      mix: STAGE_ORDER.map(k => ({ key: k, share: own[k] / sum })),
      mixTitle: STAGE_ORDER.map(k => `${STAGES[k].label} ${Math.round((own[k] / sum) * 100)}%`).join(', '),
      outlook: weeks.reduce((s, w) => s + w.expected_ha, 0),
      topWeek: top?.week ?? null
    }
  })
)

const totals = computed(() => {
  const all = stageTotals(current.value ?? [])
  return {
    paddy: rows.value.reduce((s, r) => s + r.paddy, 0),
    planted: all.planted,
    peaked: all.peaked,
    outlook: rows.value.reduce((s, r) => s + r.outlook, 0)
  }
})
const stats = computed(() => [
  { label: t.stats.paddy, value: formatHa(totals.value.paddy), color: undefined },
  { label: STAGES.planted.label, value: formatHa(totals.value.planted), color: STAGE_FILL.planted },
  { label: STAGES.peaked.label, value: formatHa(totals.value.peaked), color: STAGE_FILL.peaked },
  { label: t.stats.outlook, value: formatHa(totals.value.outlook), color: undefined }
])

const columns = [
  { accessorKey: 'unit', header: t.columns.unit },
  { accessorKey: 'paddy', header: t.columns.paddy },
  { accessorKey: 'mix', header: COPY.landing.now.columns.stage },
  { accessorKey: 'outlook', header: t.columns.outlook },
  { accessorKey: 'topWeek', header: t.columns.topWeek }
]

// The chosen layout lives in the URL, so a shared link opens the same view.
const LAYOUTS = ['tabel', 'peta', 'kalender'] as const
type Layout = typeof LAYOUTS[number]
const route = useRoute()
const layout = computed<Layout>({
  get: () => (LAYOUTS as readonly string[]).includes(String(route.query.tampilan)) ? route.query.tampilan as Layout : 'tabel',
  set: v => navigateTo({ query: { ...route.query, tampilan: v === 'tabel' ? undefined : v } }, { replace: true })
})
const tabs = [
  { label: t.layouts.table, value: 'tabel', icon: 'i-lucide-table' },
  { label: t.layouts.map, value: 'peta', icon: 'i-lucide-map' },
  { label: t.layouts.calendar, value: 'kalender', icon: 'i-lucide-calendar-days' }
]

const selected = ref<string | null>(null)
function open(unit: string) {
  navigateTo(`/desa/${encodeURIComponent(unit)}`)
}
const shortDate = (iso: string | null) => formatDate(iso, { day: 'numeric', month: 'short' })

useSeoMeta({ title: t.seoTitle })
</script>

<template>
  <UPage>
    <UPageHeader
      :title="t.title"
      :description="t.description(meta?.units.length ?? 0, formatDate(meta?.as_of))"
    />
    <UPageBody>
      <dl class="grid grid-cols-2 gap-x-6 gap-y-4 lg:grid-cols-4">
        <div
          v-for="s in stats"
          :key="s.label"
          class="flex flex-col-reverse justify-end gap-1 border-l-2 pl-3"
          :style="{ borderColor: s.color ?? 'var(--ui-primary)' }"
        >
          <dt class="text-sm text-muted">
            {{ s.label }}
          </dt>
          <dd class="text-2xl font-semibold tabular-nums">
            {{ s.value }}
          </dd>
        </div>
      </dl>

      <UTabs
        v-model="layout"
        :items="tabs"
        :content="false"
        :aria-label="t.layouts.label"
        class="w-full sm:w-auto"
      />

      <template v-if="layout === 'tabel'">
        <div class="h-[26rem]">
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
              class="flex h-2 w-32 gap-px overflow-hidden rounded-full"
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
          <template #outlook-cell="{ row }">
            <span class="tabular-nums">{{ formatHa(row.original.outlook) }}</span>
          </template>
          <template #topWeek-cell="{ row }">
            {{ shortDate(row.original.topWeek) }}
          </template>
        </UTable>
      </template>

      <div
        v-else-if="layout === 'peta'"
        class="grid gap-4 lg:grid-cols-[1fr_22rem]"
      >
        <div class="h-[28rem] lg:sticky lg:top-20 lg:h-[36rem]">
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
        <ul class="flex flex-col divide-y divide-(--ui-border) rounded-md ring ring-default">
          <li
            v-for="r in rows"
            :key="r.unit"
          >
            <NuxtLink
              :to="`/desa/${encodeURIComponent(r.unit)}`"
              class="flex flex-col gap-1.5 px-4 py-3 transition hover:bg-muted focus-visible:outline-2"
              :class="selected === r.unit ? 'bg-muted' : ''"
              @mouseenter="selected = r.unit"
              @mouseleave="selected = null"
              @focus="selected = r.unit"
              @blur="selected = null"
            >
              <span class="flex items-center justify-between gap-2">
                <span class="font-semibold">{{ r.unit }}</span>
                <span class="text-sm text-muted tabular-nums">{{ formatHa(r.paddy) }}</span>
              </span>
              <span
                class="flex h-1.5 w-full gap-px overflow-hidden rounded-full"
                aria-hidden="true"
              >
                <span
                  v-for="m in r.mix.filter(m => m.share > 0)"
                  :key="m.key"
                  class="h-full"
                  :style="{ flexGrow: m.share, background: STAGE_FILL[m.key] }"
                />
              </span>
              <span class="text-xs text-muted">
                {{ r.topWeek ? t.list.topWeek(shortDate(r.topWeek)) : t.list.noHarvest }}
              </span>
            </NuxtLink>
          </li>
        </ul>
      </div>

      <section
        v-else
        class="flex flex-col gap-4"
      >
        <header class="flex max-w-2xl flex-col gap-2">
          <h2 class="text-xl font-semibold">
            {{ t.calendar.title }}
          </h2>
          <p class="text-muted">
            {{ t.calendar.body }}
          </p>
        </header>
        <HarvestCalendar
          :units="rows.map(r => r.unit)"
          :outlook="outlook ?? []"
          :as-of="meta?.as_of"
        />
      </section>
    </UPageBody>
  </UPage>
</template>
