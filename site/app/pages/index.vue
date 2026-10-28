<script setup lang="ts">
import type { FeatureCollection } from 'geojson'
import { AREAS, STAGES, formatDate, formatHa, useAreaFile, type Cell, type CurrentRow, type IntensityRow, type Meta, type SeasonRow, type Stage } from '~/composables/useArea'

const t = COPY.landing
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: current } = await useAreaFile<CurrentRow[]>(area, 'current.json')
const { data: seasons } = await useAreaFile<SeasonRow[]>(area, 'seasons.json')
const { data: intensity } = await useAreaFile<IntensityRow[]>(area, 'intensity.json')
const { data: cells } = await useAreaFile<Cell[]>(area, 'cells.json')
const { data: desa } = await useAreaFile<FeatureCollection>(area, 'boundaries.geojson')
const { data: kecamatan } = await useAreaFile<FeatureCollection>(AREAS.lamongan, 'boundaries.geojson')

const num = (v: number, digits = 1) => v.toLocaleString('id-ID', { minimumFractionDigits: digits, maximumFractionDigits: digits })
const pct = (v: number) => v.toLocaleString('id-ID', { style: 'percent', maximumFractionDigits: 0 })

const units = computed(() => meta.value?.units ?? [])
const paddy = computed(() => units.value.reduce((s, u) => s + u.paddy_ha, 0))

const stages = computed(() => stageTotals(current.value ?? []))
const stageSum = computed(() => Object.values(stages.value).reduce((s, v) => s + v, 0))
const STAGE_ORDER: Stage[] = ['planted', 'peaked', 'fallow', 'unknown']
const stageRows = computed(() => STAGE_ORDER.map(k => [
  STAGES[k].label,
  formatHa(stages.value[k]),
  pct(stageSum.value ? stages.value[k] / stageSum.value : 0)
]))

const bands = computed(() => seasonBands(seasons.value ?? []))
const today = computed(() => (meta.value?.as_of ? dayOfYear(meta.value.as_of) : null))
const main = computed(() => bands.value.find(b => b.season === 'MT1'))

const years = computed(() => intensityByYear(intensity.value ?? []))

const stats = computed(() => [
  { label: t.stats.paddy, value: formatHa(paddy.value) },
  { label: t.stats.units, value: String(units.value.length) },
  { label: t.stats.fallow, value: pct(stageSum.value ? stages.value.fallow / stageSum.value : 0) },
  { label: t.stats.next, value: main.value ? monthName(main.value.start) : '-' }
])

useSeoMeta({ title: t.seoTitle })
</script>

<template>
  <div class="flex flex-col gap-16 pt-10 pb-16">
    <section class="flex flex-col gap-6">
      <div class="flex flex-wrap items-end justify-between gap-4">
        <div class="flex flex-col gap-1">
          <h1 class="text-3xl font-semibold">
            {{ t.title }}
          </h1>
          <p class="text-muted">
            {{ COPY.common.asOf(formatDate(meta?.as_of)) }}
          </p>
        </div>
        <UButton
          :label="t.cta"
          to="/ringkasan"
          trailing-icon="i-lucide-arrow-right"
        />
      </div>
      <dl class="grid grid-cols-2 gap-x-6 gap-y-4 lg:grid-cols-4">
        <div
          v-for="s in stats"
          :key="s.label"
          class="flex flex-col-reverse gap-1 border-l-2 border-(--ui-primary) pl-3"
        >
          <dt class="text-sm text-muted">
            {{ s.label }}
          </dt>
          <dd class="text-2xl font-semibold tabular-nums">
            {{ s.value }}
          </dd>
        </div>
      </dl>
      <div class="h-[26rem] lg:h-[30rem]">
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
              {{ COPY.common.mapLoading }}
            </div>
          </template>
        </ClientOnly>
      </div>
    </section>

    <section class="flex flex-col gap-4">
      <h2 class="text-xl font-semibold">
        {{ t.stage.title }}
      </h2>
      <StageBar :totals="stages" />
      <ChartTable
        :caption="t.stage.title"
        :columns="[t.stage.columns.stage, t.stage.columns.ha, t.stage.columns.share]"
        :rows="stageRows"
      />
    </section>

    <section
      v-if="bands.length"
      class="flex flex-col gap-4"
    >
      <h2 class="text-xl font-semibold">
        {{ t.calendar.title }}
      </h2>
      <SeasonCalendar
        :bands="bands"
        :today="today"
      />
      <ChartTable
        :caption="t.calendar.title"
        :columns="[t.calendar.columns.season, t.calendar.columns.start, t.calendar.columns.plant, t.calendar.columns.harvest, t.calendar.columns.end]"
        :rows="bands.map(b => [COPY.seasons[b.season], monthName(b.start), monthName(b.plant), monthName(b.harvest), monthName(b.end)])"
      />
    </section>

    <section
      v-if="years.length"
      class="flex flex-col gap-4"
    >
      <h2 class="text-xl font-semibold">
        {{ t.intensity.title }}
      </h2>
      <IntensityBars :years="years" />
      <ChartTable
        :caption="t.intensity.title"
        :columns="[t.intensity.columns.year, t.intensity.columns.value]"
        :rows="years.map(y => [y.year, num(y.all, 2)])"
      />
    </section>

    <section class="flex flex-col gap-4">
      <h2 class="text-xl font-semibold">
        {{ t.desa.title }}
      </h2>
      <ul class="flex flex-wrap gap-2">
        <li
          v-for="u in units"
          :key="u.unit"
        >
          <UButton
            :label="u.unit"
            :to="`/desa/${encodeURIComponent(u.unit)}`"
            color="neutral"
            variant="subtle"
          />
        </li>
      </ul>
    </section>
  </div>
</template>
