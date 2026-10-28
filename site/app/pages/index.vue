<script setup lang="ts">
import type { FeatureCollection } from 'geojson'
import { AREAS, STAGES, formatDate, formatHa, useAreaFile, type Cell, type CurrentRow, type Meta, type RainRow, type SeasonRow, type Stage } from '~/composables/useArea'

const t = COPY.landing
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: current } = await useAreaFile<CurrentRow[]>(area, 'current.json')
const { data: seasons } = await useAreaFile<SeasonRow[]>(area, 'seasons.json')
const { data: rain } = await useAreaFile<RainRow[]>(area, 'rain.json')
const { data: cells } = await useAreaFile<Cell[]>(area, 'cells.json')
const { data: desa } = await useAreaFile<FeatureCollection>(area, 'boundaries.geojson')
const { data: kecamatan } = await useAreaFile<FeatureCollection>(AREAS.lamongan, 'boundaries.geojson')

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

// Each desa card shows the stage that covers most of its sawah today.
const desaCards = computed(() => units.value.map((u) => {
  const own = (current.value ?? []).filter(r => r.unit === u.unit && r.stage !== null && r.stage !== 'unknown')
  const top = own.reduce<CurrentRow | null>((best, r) => (!best || r.paddy_ha > best.paddy_ha ? r : best), null)
  return { unit: u.unit, paddy: u.paddy_ha, stage: (top?.stage ?? 'unknown') as Stage }
}))

const stats = computed(() => [
  { label: t.stats.paddy, value: formatHa(paddy.value) },
  { label: t.stats.units, value: String(units.value.length) },
  { label: t.stats.season, value: main.value ? monthName(main.value.start) : '-' },
  { label: t.stats.asOf, value: formatDate(meta.value?.as_of) }
])

useSeoMeta({ title: t.seoTitle, description: t.description })
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
          {{ t.description }}
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

    <section class="grid gap-8 rounded-lg bg-muted p-6 ring ring-default sm:p-10 lg:grid-cols-[2fr_3fr]">
      <header class="flex flex-col gap-3">
        <h2 class="text-2xl font-semibold text-balance">
          {{ t.pride.title }}
        </h2>
        <p class="text-muted">
          {{ t.pride.body }}
        </p>
      </header>
      <div class="flex flex-col gap-4">
        <dl class="grid gap-6 sm:grid-cols-3">
          <div
            v-for="s in t.pride.stats"
            :key="s.label"
            class="flex flex-col-reverse gap-1"
          >
            <dt class="text-sm text-muted">
              {{ s.label }}
            </dt>
            <dd class="text-3xl font-semibold text-(--ui-primary) tabular-nums">
              {{ s.value }}
            </dd>
          </div>
        </dl>
        <p class="text-xs text-muted">
          {{ t.pride.source }}
        </p>
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
      <header class="flex flex-col gap-2">
        <h2 class="text-2xl font-semibold">
          {{ t.desa.title }}
        </h2>
        <p class="text-muted">
          {{ t.desa.body }}
        </p>
      </header>
      <ul class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <li
          v-for="d in desaCards"
          :key="d.unit"
        >
          <NuxtLink
            :to="`/desa/${encodeURIComponent(d.unit)}`"
            class="flex h-full flex-col gap-2 rounded-md bg-muted p-4 ring ring-default transition hover:ring-(--ui-primary) focus-visible:outline-2"
          >
            <span class="flex items-center justify-between gap-2 font-semibold">
              {{ d.unit }}
              <UIcon
                name="i-lucide-arrow-right"
                class="size-4 text-muted"
              />
            </span>
            <span class="text-sm text-muted tabular-nums">{{ t.desa.paddy(formatHa(d.paddy)) }}</span>
            <span class="flex items-center gap-1.5 text-sm">
              <span
                class="size-2.5 rounded-full"
                :style="{ background: STAGES[d.stage].color === 'transparent' ? 'var(--viz-neutral)' : STAGES[d.stage].color }"
              />
              {{ STAGES[d.stage].label }}
            </span>
          </NuxtLink>
        </li>
      </ul>
    </section>
  </div>
</template>
