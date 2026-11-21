<script setup lang="ts">
import { AREAS, useAreaFile, useAreaOutlines, useAreaRainMonths, useAreaSeasons, type Meta } from '~/composables/useArea'

const t = COPY.landing
const k = COPY.kalender
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: seasons } = await useAreaSeasons(area)
const { data: rainMonths } = await useAreaRainMonths(area)
const { data: outlines } = await useAreaOutlines(area)

const mm = (v: number) => Math.round(v).toLocaleString('id-ID')
const units = computed(() => meta.value?.units ?? [])
const bands = computed(() => seasonBands(seasons.value ?? []))
const main = computed(() => bands.value.find(b => b.season === 'MT1'))
const today = computed(() => (meta.value?.as_of ? dayOfYear(meta.value.as_of) : null))

// Typical main-season dates per desa, from the reliable past seasons of that desa.
const schedule = computed(() => units.value.flatMap((u) => {
  const mt1 = mainSeasonDates((seasons.value ?? []).filter(s => s.unit === u.unit))
  return mt1 ? [{ unit: u.unit, plant: mt1.plant, harvest: mt1.harvest }] : []
}))

// Desa with the latest planting come first. A desa needs three earlier seasons to have a baseline.
const onsets = computed(() => units.value.flatMap((u) => {
  const s = onsetShift((seasons.value ?? []).filter(r => r.unit === u.unit))
  return s ? [{ unit: u.unit, ...s }] : []
}).sort((a, b) => b.shift - a.shift))
const onsetMax = computed(() => Math.max(1, ...onsets.value.map(o => Math.abs(o.shift))))
const barStyle = (shift: number) => {
  const w = (Math.abs(shift) / onsetMax.value) * 50
  return { width: `${w}%`, left: shift > 0 ? '50%' : `${50 - w}%` }
}

const dayLabel = (d: number) => new Date(Date.UTC(2001, 0, 1 + d)).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', timeZone: 'UTC' })

const SEP1 = dayOfYear('2001-09-01')
// Days since 1 September, so planting in November and in January sort in the right order.
const sinceSep = (d: number) => (d - SEP1 + 365) % 365

type View = 'kalender' | 'peta' | 'tabel'
type Measure = 'plant' | 'harvest'
const view = useQueryChoice<View>('tampilan', ['tabel', 'kalender', 'peta'], 'tabel')
const measure = useQueryChoice<Measure>('ukuran', ['plant', 'harvest'], 'plant')
const viewItems = [
  { label: k.views.tabel, value: 'tabel', icon: 'i-lucide-table' },
  { label: k.views.kalender, value: 'kalender', icon: 'i-lucide-calendar-days' },
  { label: k.views.peta, value: 'peta', icon: 'i-lucide-map' }
]
// A short line under the title, and the long explanation behind an info button, so the header keeps one height.
const sub = computed(() => {
  if (view.value === 'kalender') return { short: t.calendar.short, detail: t.calendar.body }
  if (view.value === 'peta') return { short: k.map.hint, detail: null }
  return { short: k.tableBody, detail: k.tableDetail }
})
const measureItems = [
  { label: k.measures.plant, value: 'plant' },
  { label: k.measures.harvest, value: 'harvest' }
]
const mapValues = computed(() => Object.fromEntries(schedule.value.map(s => [s.unit, sinceSep(s[measure.value])])))

// The table sorts on the clicked column. The date columns sort from 1 September, the same order as the season.
type SortKey = 'unit' | Measure
const sortKey = ref<SortKey>('plant')
const sortDesc = ref(false)
function sortBy(key: SortKey) {
  if (sortKey.value === key) sortDesc.value = !sortDesc.value
  else {
    sortKey.value = key
    sortDesc.value = false
  }
}
const tableRows = computed(() => {
  const dir = sortDesc.value ? -1 : 1
  const key = sortKey.value
  return [...schedule.value].sort((a, b) => key === 'unit'
    ? dir * a.unit.localeCompare(b.unit)
    : dir * (sinceSep(a[key]) - sinceSep(b[key])) || a.unit.localeCompare(b.unit))
})
const ariaSort = (key: SortKey) => (sortKey.value === key ? (sortDesc.value ? 'descending' : 'ascending') : 'none')
const sortIcon = (key: SortKey) => sortKey.value === key ? (sortDesc.value ? 'i-lucide-arrow-down' : 'i-lucide-arrow-up') : 'i-lucide-arrow-up-down'
const query = ref('')
const tableShown = computed(() => {
  const q = query.value.trim().toLowerCase()
  return q ? tableRows.value.filter(r => r.unit.toLowerCase().includes(q)) : tableRows.value
})
// In the table the measure select picks the column that sorts the rows.
watch(measure, (m) => {
  sortKey.value = m
  sortDesc.value = false
})
// A thin bar shows where the season of the desa sits in the year that starts on 1 September.
const barOf = (r: { plant: number, harvest: number }) => {
  const from = sinceSep(r.plant) / 365
  const to = Math.max(from + 0.02, sinceSep(r.harvest) / 365)
  return { left: `${from * 100}%`, width: `${(Math.min(to, 1) - from) * 100}%` }
}

const months = computed(() => rainMonths.value ?? [])
const lastMonth = computed(() => months.value.at(-1))
const monthLabel = (m: RainMonth) => new Date(Date.UTC(m.year, m.month - 1, 1)).toLocaleDateString('id-ID', { month: 'long', year: 'numeric', timeZone: 'UTC' })

definePageMeta({ layout: 'tiles' })
useSeoMeta({ title: k.seoTitle, description: k.description })
</script>

<template>
  <div>
    <section
      data-figure="kalender-tanam"
      class="tile flex flex-col gap-8"
    >
      <header class="flex max-w-3xl flex-col gap-4">
        <ScopeChip />
        <h1 class="text-4xl/[1.07] font-semibold text-balance sm:text-5xl/[1.07] lg:text-[3.5rem]/[1.07]">
          {{ k.title }}
        </h1>
        <p class="text-lg text-muted">
          {{ k.description }}
        </p>
      </header>

      <div class="flex flex-col gap-5">
        <header class="flex max-w-3xl flex-col gap-1">
          <h2 class="text-2xl/[1.2] font-bold text-balance">
            {{ view === 'kalender' && main ? t.calendar.title(monthName(main.start)) : view === 'peta' ? k.mapTitle(k.measures[measure]) : k.tableTitle }}
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
              :placeholder="k.search"
              :aria-label="k.search"
              class="w-52"
            />
            <USelect
              v-if="view === 'peta'"
              v-model="measure"
              :items="measureItems"
              size="sm"
              class="w-52"
              :aria-label="k.measureLabel"
            />
          </div>
        </div>

        <div class="lg:min-h-[48rem]">
          <SeasonCalendar
            v-if="view === 'kalender'"
            :bands="bands"
            :today="today"
          />

          <OutlineMap
            v-else-if="view === 'peta'"
            :outlines="outlines"
            :values="mapValues"
            :format="v => dayLabel((v + SEP1) % 365)"
            invert
            :min-label="k.map.early"
            :max-label="k.map.late"
            :hint="k.map.hint"
            :label="k.mapTitle(k.measures[measure])"
            class="mx-auto w-full max-w-3xl"
          />

          <div
            v-else
            class="overflow-x-auto"
          >
            <table class="w-full text-left sm:min-w-[34rem]">
              <caption class="sr-only">
                {{ k.tableTitle }}
              </caption>
              <thead>
                <tr class="border-b border-default text-sm">
                  <th
                    scope="col"
                    :aria-sort="ariaSort('unit')"
                    class="py-2 pr-4 font-semibold"
                  >
                    <button
                      type="button"
                      class="inline-flex items-center gap-1 rounded-sm focus-visible:outline-2 focus-visible:outline-(--ui-primary)"
                      @click="sortBy('unit')"
                    >
                      {{ t.schedule.columns.unit }}
                      <UIcon
                        :name="sortIcon('unit')"
                        class="size-4 text-muted"
                      />
                    </button>
                  </th>
                  <th
                    v-for="m in (['plant', 'harvest'] as const)"
                    :key="m"
                    scope="col"
                    :aria-sort="ariaSort(m)"
                    class="px-2 py-2 text-right font-semibold"
                  >
                    <button
                      type="button"
                      class="inline-flex items-center gap-1 rounded-sm focus-visible:outline-2 focus-visible:outline-(--ui-primary)"
                      @click="sortBy(m)"
                    >
                      {{ k.measures[m] }}
                      <UIcon
                        :name="sortIcon(m)"
                        class="size-4 text-muted"
                      />
                    </button>
                  </th>
                  <th
                    scope="col"
                    class="hidden w-1/3 px-2 py-2 font-semibold sm:table-cell"
                  >
                    {{ k.trend }}
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
                    class="py-3 pr-4 font-semibold"
                  >
                    <NuxtLink
                      :to="`/desa/${encodeURIComponent(r.unit)}`"
                      class="rounded-sm hover:text-(--ui-primary) focus-visible:outline-2 focus-visible:outline-(--ui-primary)"
                    >
                      {{ r.unit }}
                    </NuxtLink>
                  </th>
                  <td class="px-2 py-3 text-right tabular-nums">
                    {{ dayLabel(r.plant) }}
                  </td>
                  <td class="px-2 py-3 text-right tabular-nums">
                    {{ dayLabel(r.harvest) }}
                  </td>
                  <td
                    class="hidden px-2 py-3 sm:table-cell"
                    aria-hidden="true"
                  >
                    <span class="relative block h-2 rounded-full bg-muted">
                      <span
                        class="absolute inset-y-0 rounded-full bg-(--viz-3)"
                        :style="barOf(r)"
                      />
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
            <p
              v-if="!tableShown.length"
              class="py-6 text-sm text-muted"
            >
              {{ COPY.bandingkan.empty }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <section
      v-if="onsets.length"
      class="tile tile-parchment flex flex-col gap-10"
    >
      <header class="flex max-w-2xl flex-col gap-3">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ COPY.onset.title }}
        </h2>
        <p class="text-muted">
          {{ COPY.onset.body }}
        </p>
      </header>
      <div class="flex flex-col gap-8">
        <ul class="flex flex-col gap-4 sm:gap-2">
          <li
            v-for="o in onsets"
            :key="o.unit"
            class="grid items-center gap-x-4 gap-y-1.5 sm:grid-cols-[8rem_1fr_13rem]"
          >
            <span class="font-semibold">{{ o.unit }}</span>
            <span
              class="relative h-3 rounded-full bg-default"
              aria-hidden="true"
            >
              <span class="absolute inset-y-0 left-1/2 w-px bg-(--ui-border-accented)" />
              <span
                class="absolute inset-y-0 rounded-full"
                :class="o.shift > 0 ? 'bg-(--viz-2)' : 'bg-(--viz-3)'"
                :style="barStyle(o.shift)"
              />
            </span>
            <span
              class="flex items-center gap-1.5 text-sm tabular-nums"
              :class="o.shift >= COPY.onset.lateAfter ? 'font-semibold text-(--ui-warning)' : 'text-muted'"
            >
              <UIcon
                v-if="o.shift >= COPY.onset.lateAfter"
                name="i-lucide-clock-alert"
                class="size-4 shrink-0"
              />
              <span
                v-if="o.shift >= COPY.onset.lateAfter"
                class="sr-only"
              >{{ COPY.onset.late }}:</span>
              {{ COPY.onset.value(o.shift) }}, {{ COPY.onset.seasonOf(o.year) }}
            </span>
          </li>
        </ul>
        <ChartTable
          :caption="COPY.onset.title"
          :columns="[COPY.onset.columns.unit, COPY.onset.columns.plant, COPY.onset.columns.mean, COPY.onset.columns.shift]"
          :rows="onsets.map(o => [o.unit, dayLabel(o.plant), dayLabel(o.mean), o.shift])"
        />
      </div>
    </section>

    <section
      v-if="lastMonth"
      data-figure="hujan-bulanan"
      class="tile flex flex-col gap-10"
    >
      <header class="flex max-w-2xl flex-col gap-3">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.rain.title }}
        </h2>
        <p class="text-muted">
          {{ t.rain.body(monthLabel(lastMonth), mm(lastMonth.mm), mm(rainBaseline(lastMonth))) }}
        </p>
      </header>
      <div class="flex flex-col gap-8">
        <p class="font-semibold">
          {{ rainPlain(lastMonth) }}
        </p>
        <RainBars :months="months" />
        <ChartTable
          :caption="t.rain.title"
          :columns="[t.rain.columns.month, t.rain.columns.mm, t.rain.columns.normal, t.rain.columns.lo, t.rain.columns.hi]"
          :rows="months.map(m => [monthLabel(m), mm(m.mm), mm(rainBaseline(m)), m.lo === undefined ? '-' : mm(m.lo), m.hi === undefined ? '-' : mm(m.hi)])"
        />
        <p class="text-sm text-muted">
          {{ k.notesLink.text }}
          <NuxtLink
            to="/tentang#catatan"
            class="font-semibold text-(--ui-primary) underline-offset-2 hover:underline focus-visible:outline-2 focus-visible:outline-(--focus-ring)"
          >
            {{ k.notesLink.link }}
          </NuxtLink>
        </p>
      </div>
    </section>
  </div>
</template>
