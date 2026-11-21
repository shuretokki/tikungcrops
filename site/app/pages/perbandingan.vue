<script setup lang="ts">
import { AREAS, useAreaFile, useAreaOutlines, type CurrentRow, type IntensityRow, type Meta } from '~/composables/useArea'

type Metric = 'sawah' | 'intensitas' | 'tumbuh'
type View = 'peta' | 'tabel'

const t = COPY.bandingkan

const metric = useQueryChoice<Metric>('ukuran', ['sawah', 'intensitas', 'tumbuh'], 'sawah')
const view = useQueryChoice<View>('tampilan', ['tabel', 'peta'], 'tabel')

const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: current } = await useAreaFile<CurrentRow[]>(area, 'current.json')
const { data: intensityRows } = await useAreaFile<IntensityRow[]>(area, 'intensity.json')
const { data: outlines } = await useAreaOutlines(area)

const intensity = computed(() => latestIntensity(intensityRows.value ?? []))

function entriesFor(m: Metric): Entry[] {
  if (m === 'sawah') return (meta.value?.units ?? []).map(u => ({ unit: u.unit, value: u.paddy_ha }))
  if (m === 'intensitas') return intensity.value.entries
  return growingShare(current.value ?? [])
}
const entries = computed<Entry[]>(() => entriesFor(metric.value))

// The table shows every measure side by side and sorts on the column that is clicked, as the table view of Our World in Data does.
type SortKey = 'unit' | Metric
const sortKey = ref<SortKey>('sawah')
const sortDesc = ref(true)
function sortBy(key: SortKey) {
  if (sortKey.value === key) sortDesc.value = !sortDesc.value
  else {
    sortKey.value = key
    sortDesc.value = key !== 'unit'
  }
}
const metricKeys = Object.keys(t.metrics) as Metric[]
const tableRows = computed(() => {
  const byUnit = new Map<string, { unit: string } & Partial<Record<Metric, number>>>()
  for (const m of metricKeys) {
    for (const e of entriesFor(m)) {
      const row = byUnit.get(e.unit) ?? { unit: e.unit }
      row[m] = e.value
      byUnit.set(e.unit, row)
    }
  }
  const dir = sortDesc.value ? -1 : 1
  const key = sortKey.value
  return [...byUnit.values()].sort((a, b) => {
    if (key === 'unit') return dir * a.unit.localeCompare(b.unit)
    return dir * ((a[key] ?? -Infinity) - (b[key] ?? -Infinity)) || a.unit.localeCompare(b.unit)
  })
})
const ariaSort = (key: SortKey) => (sortKey.value === key ? (sortDesc.value ? 'descending' : 'ascending') : 'none')
const sortIcon = (key: SortKey) => sortKey.value === key ? (sortDesc.value ? 'i-lucide-arrow-down' : 'i-lucide-arrow-up') : 'i-lucide-arrow-up-down'
const query = ref('')
const tableShown = computed(() => {
  const q = query.value.trim().toLowerCase()
  return q ? tableRows.value.filter(r => r.unit.toLowerCase().includes(q)) : tableRows.value
})
// The thin bar under each value is scaled to the largest value of its own column.
const maxOf = computed(() => Object.fromEntries(metricKeys.map(m => [m, Math.max(1e-9, ...tableRows.value.map(r => r[m] ?? 0))])) as Record<Metric, number>)

const ranked = computed(() => rank(entries.value))
const values = computed(() => Object.fromEntries(ranked.value.map(e => [e.unit, e.value])))

// In the table the measure select picks the column that sorts the rows.
watch(metric, (m) => {
  sortKey.value = m
  sortDesc.value = true
})
// One small line per desa of the yearly planting frequency, all on the same scale so the lines can be compared.
const TREND_W = 180
const TREND_H = 40
const trend = computed(() => {
  const rows = (intensityRows.value ?? []).filter(r => r.complete && r.ip_all !== null)
  const years = [...new Set(rows.map(r => r.year))].sort((a, b) => a - b)
  const values = rows.map(r => r.ip_all!)
  const lo = Math.min(...values)
  const hi = Math.max(...values)
  const span = hi - lo || 1
  const items = [...new Set(rows.map(r => r.unit))].flatMap((unit) => {
    const own = rows.filter(r => r.unit === unit).sort((a, b) => a.year - b.year)
    const first = own[0]
    const last = own.at(-1)
    if (!first || !last || own.length < 2) return []
    const points = own.map(r => `${(years.indexOf(r.year) / Math.max(1, years.length - 1)) * TREND_W},${TREND_H - 4 - ((r.ip_all! - lo) / span) * (TREND_H - 8)}`).join(' ')
    return [{ unit, points, last: last.ip_all!, delta: last.ip_all! - first.ip_all!, fromYear: first.year, toYear: last.year }]
  }).sort((a, b) => b.last - a.last)
  return { items, from: years[0], to: years.at(-1) }
})
const freq = (v: number) => v.toLocaleString('id-ID', { minimumFractionDigits: 1, maximumFractionDigits: 1 })

const heading = computed(() => {
  const m = t.metrics[metric.value]
  return metric.value === 'intensitas' ? t.metrics.intensitas.title(intensity.value.year) : (m.title as string)
})

// A short line under the title, and the long explanation behind an info button, so the header keeps one height.
const sub = computed(() => {
  if (view.value === 'tabel') return { short: t.tableBody, detail: t.tableDetail }
  const m = t.metrics[metric.value]
  return { short: m.short, detail: m.body === m.short ? null : m.body }
})
const metricItems = metricKeys.map(k => ({ label: t.metrics[k].label, value: k }))
const viewItems = [
  { label: t.views.tabel, value: 'tabel', icon: 'i-lucide-table' },
  { label: t.views.peta, value: 'peta', icon: 'i-lucide-map' }
]

definePageMeta({ layout: 'tiles' })
useSeoMeta({ title: t.seoTitle, description: t.description })
</script>

<template>
  <div>
    <section class="tile flex flex-col gap-8">
      <header class="flex max-w-3xl flex-col gap-4">
        <ScopeChip />
        <h1 class="text-4xl/[1.07] font-semibold text-balance sm:text-5xl/[1.07] lg:text-[3.5rem]/[1.07]">
          {{ t.title }}
        </h1>
        <p class="text-lg text-muted">
          {{ t.description }}
        </p>
      </header>

      <div class="flex flex-col gap-5">
        <header class="flex max-w-3xl flex-col gap-1">
          <h2 class="text-2xl/[1.2] font-bold text-balance">
            {{ view === 'tabel' ? t.tableTitle : heading }}
          </h2>
          <p class="flex h-8 items-center gap-1 text-sm text-muted">
            {{ sub.short }}
            <InfoTip
              v-if="sub.detail"
              :text="sub.detail"
            />
          </p>
        </header>

        <div class="flex min-h-12 flex-wrap items-end justify-between gap-x-6 gap-y-2 border-b border-default">
          <UTabs
            v-model="view"
            :items="viewItems"
            :content="false"
            size="sm"
            variant="link"
            class="-mb-px w-auto"
          />
          <div class="mb-2 flex flex-wrap gap-2">
            <UInput
              v-if="view === 'tabel'"
              v-model="query"
              icon="i-lucide-search"
              name="cari-desa"
              type="search"
              autocomplete="off"
              size="sm"
              :placeholder="t.search"
              :aria-label="t.search"
              class="w-52"
            />
            <USelect
              v-if="view === 'peta'"
              v-model="metric"
              :items="metricItems"
              size="sm"
              class="w-52"
              :aria-label="t.metricLabel"
            />
          </div>
        </div>

        <div class="lg:min-h-[52rem]">
          <OutlineMap
            v-if="view === 'peta'"
            :outlines="outlines"
            :values="values"
            :format="v => t.metrics[metric].value(v)"
            :min-label="t.map.low"
            :max-label="t.map.high"
            :hint="t.map.hint"
            :label="t.map.label(t.metrics[metric].label)"
            class="mx-auto w-full max-w-3xl"
          />

          <div
            v-else
            class="overflow-x-auto"
          >
            <table class="w-full text-left sm:min-w-[34rem]">
              <caption class="sr-only">
                {{ t.tableTitle }}
              </caption>
              <thead>
                <tr class="border-b border-default text-xs sm:text-sm">
                  <th
                    scope="col"
                    :aria-sort="ariaSort('unit')"
                    class="py-2 pr-2 sm:pr-4 font-semibold"
                  >
                    <button
                      type="button"
                      class="inline-flex items-center gap-1 rounded-sm focus-visible:outline-2 focus-visible:outline-(--ui-primary)"
                      @click="sortBy('unit')"
                    >
                      {{ t.tableUnit }}
                      <UIcon
                        :name="sortIcon('unit')"
                        class="size-3 shrink-0 text-muted sm:size-4"
                      />
                    </button>
                  </th>
                  <th
                    v-for="m in metricKeys"
                    :key="m"
                    scope="col"
                    :aria-sort="ariaSort(m)"
                    class="px-1 sm:px-2 py-2 text-right font-semibold"
                  >
                    <button
                      type="button"
                      class="inline-flex items-center gap-1 rounded-sm focus-visible:outline-2 focus-visible:outline-(--ui-primary)"
                      @click="sortBy(m)"
                    >
                      {{ t.metrics[m].label }}
                      <UIcon
                        :name="sortIcon(m)"
                        class="size-3 shrink-0 text-muted sm:size-4"
                      />
                    </button>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="r in tableShown"
                  :key="r.unit"
                  class="border-b border-default"
                >
                  <th
                    scope="row"
                    class="py-3 pr-2 sm:pr-4 font-semibold"
                  >
                    <NuxtLink
                      :to="`/desa/${encodeURIComponent(r.unit)}`"
                      class="rounded-sm hover:text-(--ui-primary) focus-visible:outline-2 focus-visible:outline-(--ui-primary)"
                    >
                      {{ r.unit }}
                    </NuxtLink>
                  </th>
                  <td
                    v-for="m in metricKeys"
                    :key="m"
                    class="px-1 sm:px-2 py-3 text-right tabular-nums"
                  >
                    <template v-if="r[m] !== undefined">
                      {{ t.metrics[m].value(r[m]) }}
                      <span
                        class="mt-1 ml-auto block h-1 rounded-full bg-(--ui-primary)/60"
                        :style="{ width: `${Math.max(3, (r[m] / maxOf[m]) * 100)}%`, maxWidth: '6rem' }"
                        aria-hidden="true"
                      />
                    </template>
                    <template v-else>
                      -
                    </template>
                  </td>
                </tr>
              </tbody>
            </table>
            <p
              v-if="!tableShown.length"
              class="py-6 text-sm text-muted"
            >
              {{ t.empty }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <section
      v-if="trend.items.length"
      class="tile tile-parchment flex flex-col gap-8"
    >
      <header class="flex max-w-2xl flex-col gap-3">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.trend.title }}
        </h2>
        <p class="text-muted">
          {{ t.trend.body(trend.from!, trend.to!) }}
        </p>
      </header>
      <ul class="flex flex-col divide-y divide-default border-y border-default">
        <li
          v-for="r in trend.items"
          :key="r.unit"
        >
          <NuxtLink
            :to="`/desa/${encodeURIComponent(r.unit)}`"
            class="grid grid-cols-[7rem_1fr] items-center gap-x-4 gap-y-1 px-2 py-3 hover:bg-default focus-visible:outline-2 focus-visible:outline-(--ui-primary) sm:grid-cols-[9rem_12rem_1fr]"
          >
            <span class="font-semibold">{{ r.unit }}</span>
            <svg
              :viewBox="`0 0 ${TREND_W} ${TREND_H}`"
              class="h-10 w-full max-w-[12rem] text-(--ui-primary)"
              role="img"
              :aria-label="t.trend.label(r.unit, freq(r.last), r.delta)"
            >
              <polyline
                :points="r.points"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <span class="col-span-2 text-sm text-muted tabular-nums sm:col-span-1">{{ t.trend.value(freq(r.last), r.delta) }}</span>
          </NuxtLink>
        </li>
      </ul>
    </section>
  </div>
</template>
