<script setup lang="ts">
import type { FeatureCollection } from 'geojson'
import { AREAS, STAGES, formatDate, formatHa, useAreaClientFile, useAreaFile, type Cell, type CurrentRow, type Meta, type RainRow, type SeasonRow, type Stage } from '~/composables/useArea'

const t = COPY.landing
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: current } = await useAreaFile<CurrentRow[]>(area, 'current.json')
const { data: seasons } = await useAreaFile<SeasonRow[]>(area, 'seasons.json')
const { data: rain } = await useAreaFile<RainRow[]>(area, 'rain.json')
const { data: desa } = await useAreaFile<FeatureCollection>(area, 'boundaries.geojson')
const { data: cells } = useAreaClientFile<Cell[]>(area, 'cells.json')
const { data: kecamatan } = useAreaClientFile<FeatureCollection>(AREAS.lamongan, 'boundaries.geojson')

const pct = (v: number) => v.toLocaleString('id-ID', { style: 'percent', maximumFractionDigits: 0 })
const mm = (v: number) => Math.round(v).toLocaleString('id-ID')

const units = computed(() => meta.value?.units ?? [])
const paddy = computed(() => units.value.reduce((s, u) => s + u.paddy_ha, 0))

const stages = computed(() => stageTotals(current.value ?? []))
const stageSum = computed(() => Object.values(stages.value).reduce((s, v) => s + v, 0))
const fallowShare = computed(() => (stageSum.value ? stages.value.fallow / stageSum.value : 0))
const resting = computed(() => fallowShare.value >= 0.5)
const STAGE_ORDER: Stage[] = ['planted', 'peaked', 'fallow', 'unknown']
const stageRows = computed(() => STAGE_ORDER.map(k => [
  STAGES[k].label,
  formatHa(stages.value[k]),
  pct(stageSum.value ? stages.value[k] / stageSum.value : 0)
]))

const bands = computed(() => seasonBands(seasons.value ?? []))
const main = computed(() => bands.value.find(b => b.season === 'MT1'))
const today = computed(() => (meta.value?.as_of ? dayOfYear(meta.value.as_of) : null))

const months = computed(() => rainByMonth(rain.value ?? []))
const lastMonth = computed(() => months.value.at(-1))
const monthLabel = (m: RainMonth) => new Date(Date.UTC(m.year, m.month - 1, 1)).toLocaleDateString('id-ID', { month: 'long', year: 'numeric', timeZone: 'UTC' })

// Each desa tile shows its stage mix today and its place in the kecamatan.
const desaCards = computed(() => units.value.map((u) => {
  const own = stageTotals((current.value ?? []).filter(r => r.unit === u.unit))
  const sum = STAGE_ORDER.reduce((s, k) => s + own[k], 0) || 1
  const known = STAGE_ORDER.filter(k => k !== 'unknown')
  const top = known.reduce((best, k) => (own[k] > own[best] ? k : best), known[0]!)
  return { unit: u.unit, paddy: u.paddy_ha, stage: top, mix: STAGE_ORDER.map(k => ({ key: k, share: own[k] / sum })) }
}))
const outlines = computed(() => desaOutlines(desa.value))
const labels = computed(() => units.value.map(u => ({ name: u.unit, lon: u.lon, lat: u.lat })))
const query = ref('')
const shownDesa = computed(() => {
  const q = query.value.trim().toLowerCase()
  return q ? desaCards.value.filter(d => d.unit.toLowerCase().includes(q)) : desaCards.value
})
const STAGE_FILL: Record<Stage, string> = {
  planted: 'var(--viz-3)',
  peaked: 'var(--viz-2)',
  fallow: 'var(--viz-neutral)',
  unknown: 'repeating-linear-gradient(45deg, var(--viz-neutral) 0 2px, transparent 2px 5px)'
}

const thousand = (v: number) => Math.round(v / 1000).toLocaleString('id-ID')
const prideTop = JATIM_RICE_2024.top[0]!.tons
const prideStats = [
  { value: (JATIM_RICE_2024.top[0]!.tons / JATIM_RICE_2024.province).toLocaleString('id-ID', { style: 'percent', maximumFractionDigits: 1 }), label: t.pride.stats.share },
  { value: `${thousand(JATIM_RICE_2024.lamonganRiceTons)} ribu ton`, label: t.pride.stats.rice },
  { value: `${thousand(JATIM_RICE_2024.lamonganHarvestHa)} ribu ha`, label: t.pride.stats.harvest }
]

const stats = computed(() => [
  { label: t.stats.paddy, value: formatHa(paddy.value) },
  { label: t.stats.units, value: String(units.value.length) },
  { label: t.stats.season, value: main.value ? monthName(main.value.start) : '-' },
  { label: t.stats.asOf, value: formatDate(meta.value?.as_of) }
])

useSeoMeta({ title: t.seoTitle, description: () => t.description(units.value.length) })
</script>

<template>
  <div class="flex flex-col gap-20 pb-16">
    <section class="grid items-center gap-8 pt-10 lg:grid-cols-[5fr_6fr] lg:pt-16">
      <div class="flex flex-col gap-5">
        <p class="text-sm font-semibold text-(--ui-primary)">
          {{ t.eyebrow }}
        </p>
        <h1 class="text-3xl font-semibold text-balance sm:text-4xl">
          {{ t.headline }}
        </h1>
        <p class="text-lg text-muted">
          {{ t.description(units.length) }}
        </p>
        <div class="flex flex-wrap gap-3">
          <UButton
            :label="t.primaryCta"
            to="#desa"
            icon="i-lucide-search"
            size="lg"
          />
          <UButton
            :label="t.secondaryCta"
            to="/ringkasan"
            color="neutral"
            variant="subtle"
            size="lg"
          />
        </div>
        <dl class="mt-2 grid grid-cols-2 gap-x-6 gap-y-4 border-t border-default pt-5 sm:grid-cols-4">
          <div
            v-for="s in stats"
            :key="s.label"
            class="flex flex-col-reverse"
          >
            <dt class="text-xs text-muted">
              {{ s.label }}
            </dt>
            <dd class="text-xl font-semibold tabular-nums">
              {{ s.value }}
            </dd>
          </div>
        </dl>
      </div>
      <div class="h-[26rem] lg:h-[32rem]">
        <ClientOnly>
          <AreaMap
            :outer="kecamatan"
            :inner="desa"
            :cells="cells"
            :labels="labels"
            :selected="null"
            @select="(u: string) => navigateTo(`/desa/${encodeURIComponent(u)}`)"
          />
          <template #fallback>
            <div class="flex h-full items-center justify-center rounded-md bg-muted text-sm text-muted">
              {{ t.mapLoading }}
            </div>
          </template>
        </ClientOnly>
      </div>
    </section>

    <section class="overflow-hidden rounded-lg ring ring-default">
      <div class="grid lg:grid-cols-[2fr_3fr]">
        <div class="flex flex-col justify-between gap-6 bg-(--ui-primary) p-6 text-inverted sm:p-10">
          <div class="flex flex-col gap-3">
            <p class="text-6xl font-semibold sm:text-7xl">
              {{ t.pride.rank }}
            </p>
            <h2 class="text-2xl font-semibold text-balance">
              {{ t.pride.title }}
            </h2>
            <p class="opacity-90">
              {{ t.pride.body(units.length) }}
            </p>
          </div>
          <dl class="grid grid-cols-3 items-start gap-4 border-t border-current/30 pt-5">
            <div
              v-for="s in prideStats"
              :key="s.label"
              class="flex flex-col-reverse justify-end gap-1"
            >
              <dt class="text-xs opacity-80">
                {{ s.label }}
              </dt>
              <dd class="text-lg font-semibold tabular-nums sm:text-xl">
                {{ s.value }}
              </dd>
            </div>
          </dl>
        </div>
        <figure class="flex flex-col gap-4 bg-muted p-6 sm:p-10">
          <figcaption class="flex flex-col gap-1">
            <span class="font-semibold">{{ t.pride.chartTitle }}</span>
            <span class="text-xs text-muted">{{ t.pride.unit }}</span>
          </figcaption>
          <ol class="flex flex-col gap-3">
            <li
              v-for="(k, i) in JATIM_RICE_2024.top"
              :key="k.name"
              class="grid grid-cols-[6.5rem_1fr_3rem] items-center gap-3 text-sm"
            >
              <span :class="i === 0 ? 'font-semibold' : 'text-muted'">{{ i + 1 }}. {{ k.name }}</span>
              <span class="h-6 rounded-sm bg-(--ui-bg)">
                <span
                  class="block h-full rounded-sm"
                  :class="i === 0 ? 'bg-(--ui-primary)' : 'bg-(--viz-neutral)'"
                  :style="{ width: `${(k.tons / prideTop) * 100}%` }"
                />
              </span>
              <span
                class="text-right tabular-nums"
                :class="i === 0 ? 'font-semibold' : 'text-muted'"
              >{{ thousand(k.tons) }}</span>
            </li>
          </ol>
          <p class="mt-auto text-xs text-muted">
            {{ t.pride.source }}
          </p>
        </figure>
      </div>
    </section>

    <section class="grid gap-8 lg:grid-cols-[1fr_2fr]">
      <header class="flex flex-col gap-3">
        <h2 class="text-2xl font-semibold text-balance">
          {{ t.now.title(resting) }}
        </h2>
        <p class="text-muted">
          {{ t.now.body(resting, pct(fallowShare), formatDate(meta?.as_of, { day: 'numeric', month: 'long' })) }}
        </p>
      </header>
      <div class="flex flex-col justify-center gap-4">
        <StageBar :totals="stages" />
        <ChartTable
          :caption="t.now.title(resting)"
          :columns="[t.now.columns.stage, t.now.columns.ha, t.now.columns.share]"
          :rows="stageRows"
        />
      </div>
    </section>

    <section
      v-if="main"
      class="flex flex-col gap-6"
    >
      <header class="flex max-w-2xl flex-col gap-3">
        <h2 class="text-2xl font-semibold text-balance">
          {{ t.calendar.title(monthName(main.start)) }}
        </h2>
        <p class="text-muted">
          {{ t.calendar.body }}
        </p>
      </header>
      <SeasonCalendar
        :bands="bands"
        :today="today"
      />
      <ChartTable
        :caption="t.calendar.title(monthName(main.start))"
        :columns="[t.calendar.columns.season, t.calendar.columns.start, t.calendar.columns.plant, t.calendar.columns.harvest, t.calendar.columns.end]"
        :rows="bands.map(b => [t.calendar.seasons[b.season], monthName(b.start), monthName(b.plant), monthName(b.harvest), monthName(b.end)])"
      />
    </section>

    <section
      v-if="lastMonth"
      class="flex flex-col gap-6"
    >
      <header class="flex max-w-2xl flex-col gap-3">
        <h2 class="text-2xl font-semibold">
          {{ t.rain.title }}
        </h2>
        <p class="text-muted">
          {{ t.rain.body(monthLabel(lastMonth), mm(lastMonth.mm), mm(lastMonth.normal)) }}
        </p>
      </header>
      <RainBars :months="months" />
      <ChartTable
        :caption="t.rain.title"
        :columns="[t.rain.columns.month, t.rain.columns.mm, t.rain.columns.normal]"
        :rows="months.map(m => [monthLabel(m), mm(m.mm), mm(m.normal)])"
      />
    </section>

    <section
      id="desa"
      class="flex scroll-mt-20 flex-col gap-6"
    >
      <header class="flex flex-wrap items-end justify-between gap-4">
        <div class="flex flex-col gap-2">
          <h2 class="text-2xl font-semibold">
            {{ t.desa.title }}
          </h2>
          <p class="text-muted">
            {{ t.desa.body }}
          </p>
        </div>
        <UInput
          v-model="query"
          icon="i-lucide-search"
          :placeholder="t.desa.search"
          :aria-label="t.desa.search"
          size="lg"
          class="w-full sm:w-72"
        />
      </header>
      <ul
        v-if="shownDesa.length"
        class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4"
      >
        <li
          v-for="d in shownDesa"
          :key="d.unit"
        >
          <NuxtLink
            :to="`/desa/${encodeURIComponent(d.unit)}`"
            class="group flex h-full flex-col overflow-hidden rounded-md bg-muted ring ring-default transition hover:ring-2 hover:ring-(--ui-primary) focus-visible:outline-2"
          >
            <svg
              v-if="outlines"
              :viewBox="outlines.viewBox"
              class="h-28 w-full bg-(--ui-bg) p-3"
              aria-hidden="true"
            >
              <path
                v-for="p in outlines.paths"
                :key="p.unit"
                :d="p.d"
                :fill="p.unit === d.unit ? 'var(--ui-primary)' : 'var(--ui-bg-accented)'"
                stroke="var(--ui-bg)"
                stroke-width="0.6"
              />
            </svg>
            <span class="flex flex-1 flex-col gap-2 p-3">
              <span class="flex items-center justify-between gap-2 font-semibold">
                {{ d.unit }}
                <UIcon
                  name="i-lucide-arrow-right"
                  class="size-4 text-muted transition group-hover:translate-x-0.5 group-hover:text-(--ui-primary)"
                />
              </span>
              <span class="text-sm text-muted tabular-nums">{{ t.desa.paddy(formatHa(d.paddy)) }}</span>
              <span
                class="flex h-1.5 w-full gap-px overflow-hidden rounded-full"
                aria-hidden="true"
              >
                <span
                  v-for="m in d.mix.filter(m => m.share > 0)"
                  :key="m.key"
                  class="h-full"
                  :style="{ flexGrow: m.share, background: STAGE_FILL[m.key] }"
                />
              </span>
              <span class="flex items-center gap-1.5 text-xs">
                <span
                  class="size-2 rounded-full"
                  :style="{ background: STAGE_FILL[d.stage] }"
                />
                {{ STAGES[d.stage].label }}
              </span>
            </span>
          </NuxtLink>
        </li>
      </ul>
      <p
        v-else
        class="rounded-md bg-muted p-4 text-sm text-muted"
      >
        {{ t.desa.empty }}
      </p>
    </section>
  </div>
</template>
