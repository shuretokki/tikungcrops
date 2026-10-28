<script setup lang="ts">
import type { FeatureCollection } from 'geojson'
import { AREAS, STAGES, formatDate, formatHa, useAreaFile, type Cell, type CurrentRow, type IntensityRow, type Meta, type SeasonRow, type Stage } from '~/composables/useArea'

const t = COPY.landing
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: current } = await useAreaFile<CurrentRow[]>(area, 'current.json')
const { data: seasons } = await useAreaFile<SeasonRow[]>(area, 'seasons.json')
const { data: intensity } = await useAreaFile<IntensityRow[]>(area, 'intensity.json')
const { data: validation } = await useAreaFile<Validation>(area, 'validation.json')
const { data: cells } = await useAreaFile<Cell[]>(area, 'cells.json')
const { data: desa } = await useAreaFile<FeatureCollection>(area, 'boundaries.geojson')
const { data: kecamatan } = await useAreaFile<FeatureCollection>(AREAS.lamongan, 'boundaries.geojson')

const num = (v: number, digits = 1) => v.toLocaleString('id-ID', { minimumFractionDigits: digits, maximumFractionDigits: digits })
const pct = (v: number) => v.toLocaleString('id-ID', { style: 'percent', maximumFractionDigits: 0 })

const units = computed(() => meta.value?.units ?? [])
const paddy = computed(() => units.value.reduce((s, u) => s + u.paddy_ha, 0))
const firstYear = computed(() => Math.min(...(seasons.value ?? []).map(s => s.year)) - 1)

const stages = computed(() => stageTotals(current.value ?? []))
const stageSum = computed(() => Object.values(stages.value).reduce((s, v) => s + v, 0))
const fallowShare = computed(() => (stageSum.value ? stages.value.fallow / stageSum.value : 0))

const bands = computed(() => seasonBands(seasons.value ?? []))
const main = computed(() => bands.value.find(b => b.season === 'MT1'))
const today = computed(() => (meta.value?.as_of ? dayOfYear(meta.value.as_of) : null))

const years = computed(() => intensityByYear(intensity.value ?? []))
const avgIntensity = computed(() => years.value.reduce((s, y) => s + y.all, 0) / (years.value.length || 1))

const allCrops = computed(() => validation.value?.area.find(a => a.measure === 'all_crops'))
const points = computed(() => (validation.value?.area_units ?? []).filter(p => p.measure === 'all_crops' && p.year === allCrops.value?.year))

const stats = computed(() => [
  { label: t.stats.paddy, value: formatHa(paddy.value) },
  { label: t.stats.units, value: String(units.value.length) },
  { label: t.stats.since, value: String(firstYear.value) },
  { label: t.stats.asOf, value: formatDate(meta.value?.as_of) }
])

const STAGE_ORDER: Stage[] = ['planted', 'peaked', 'fallow', 'unknown']
const stageRows = computed(() => STAGE_ORDER.map(k => [
  STAGES[k].label,
  formatHa(stages.value[k]),
  pct(stageSum.value ? stages.value[k] / stageSum.value : 0)
]))

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
            to="/ringkasan"
            icon="i-lucide-map"
            size="lg"
          />
          <UButton
            :label="t.secondaryCta"
            to="/metode"
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
              {{ COPY.ringkasan.mapLoading }}
            </div>
          </template>
        </ClientOnly>
      </div>
    </section>

    <section class="grid gap-8 lg:grid-cols-[1fr_2fr]">
      <header class="flex flex-col gap-3">
        <p class="text-sm font-semibold text-(--ui-primary)">
          {{ t.now.kicker }}
        </p>
        <h2 class="text-2xl font-semibold text-balance">
          {{ t.now.title(pct(fallowShare), formatDate(meta?.as_of, { day: 'numeric', month: 'long' })) }}
        </h2>
        <p
          v-if="main"
          class="text-muted"
        >
          {{ t.now.body(monthName(main.start)) }}
        </p>
      </header>
      <div class="flex flex-col justify-center gap-4">
        <p class="text-6xl font-semibold tabular-nums">
          {{ pct(fallowShare) }}
        </p>
        <StageBar :totals="stages" />
        <ChartTable
          :caption="t.now.kicker"
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
        <p class="text-sm font-semibold text-(--ui-primary)">
          {{ t.calendar.kicker }}
        </p>
        <h2 class="text-2xl font-semibold text-balance">
          {{ t.calendar.title(monthName(main.start), monthName(main.harvest)) }}
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
        :caption="t.calendar.kicker"
        :columns="[t.calendar.columns.season, t.calendar.columns.start, t.calendar.columns.plant, t.calendar.columns.harvest, t.calendar.columns.end]"
        :rows="bands.map(b => [t.calendar.seasons[b.season], monthName(b.start), monthName(b.plant), monthName(b.harvest), monthName(b.end)])"
      />
    </section>

    <section class="grid gap-12 lg:grid-cols-2">
      <div class="flex flex-col gap-6">
        <header class="flex flex-col gap-3">
          <p class="text-sm font-semibold text-(--ui-primary)">
            {{ t.intensity.kicker }}
          </p>
          <h2 class="text-2xl font-semibold text-balance">
            {{ t.intensity.title(num(avgIntensity)) }}
          </h2>
          <p class="text-muted">
            {{ t.intensity.body }}
          </p>
        </header>
        <IntensityBars :years="years" />
        <ChartTable
          :caption="t.intensity.kicker"
          :columns="[t.intensity.columns.year, t.intensity.columns.value]"
          :rows="years.map(y => [y.year, num(y.all, 2)])"
        />
      </div>

      <div
        v-if="allCrops"
        class="flex flex-col gap-6"
      >
        <header class="flex flex-col gap-3">
          <p class="text-sm font-semibold text-(--ui-primary)">
            {{ t.validation.kicker }}
          </p>
          <h2 class="text-2xl font-semibold text-balance">
            {{ t.validation.title(num(allCrops.r, 2)) }}
          </h2>
          <p class="text-muted">
            {{ t.validation.body(num(allCrops.ratio, 2)) }}
          </p>
        </header>
        <ValidationScatter :points="points" />
        <ChartTable
          :caption="t.validation.kicker"
          :columns="[t.validation.columns.unit, t.validation.columns.reference, t.validation.columns.satellite]"
          :rows="points.map(p => [p.unit, formatHa(p.reference_ha), formatHa(p.satellite_ha)])"
        />
      </div>
    </section>

    <section class="flex flex-col gap-8">
      <header class="flex max-w-2xl flex-col gap-3">
        <p class="text-sm font-semibold text-(--ui-primary)">
          {{ t.steps.kicker }}
        </p>
        <h2 class="text-2xl font-semibold text-balance">
          {{ t.steps.title }}
        </h2>
      </header>
      <ol class="grid gap-4 md:grid-cols-3">
        <li
          v-for="(s, i) in t.steps.items"
          :key="s.title"
          class="relative flex flex-col gap-3 rounded-md bg-muted p-5 ring ring-default"
        >
          <div class="flex items-center gap-3">
            <span class="flex size-8 items-center justify-center rounded-full bg-(--ui-primary) text-sm font-semibold text-inverted">
              {{ i + 1 }}
            </span>
            <UIcon
              :name="s.icon"
              class="size-6 text-(--ui-primary)"
            />
          </div>
          <h3 class="font-semibold">
            {{ s.title }}
          </h3>
          <p class="text-sm text-muted">
            {{ s.description }}
          </p>
        </li>
      </ol>
      <UAlert
        color="warning"
        variant="subtle"
        icon="i-lucide-triangle-alert"
        :title="t.limitsTitle"
        :description="t.limits"
        :actions="[{ label: t.limitsCta, to: '/metode', color: 'neutral', variant: 'outline' }]"
      />
    </section>

    <section class="flex flex-col gap-5">
      <header class="flex flex-col gap-2">
        <h2 class="text-2xl font-semibold">
          {{ t.desa.title }}
        </h2>
        <p class="text-muted">
          {{ t.desa.body }}
        </p>
      </header>
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
            trailing-icon="i-lucide-arrow-right"
          />
        </li>
      </ul>
    </section>
  </div>
</template>
