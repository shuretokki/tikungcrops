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
const plantValues = computed(() => Object.fromEntries(schedule.value.map(s => [s.unit, sinceSep(s.plant)])))

const months = computed(() => rainMonths.value ?? [])
const lastMonth = computed(() => months.value.at(-1))
const monthLabel = (m: RainMonth) => new Date(Date.UTC(m.year, m.month - 1, 1)).toLocaleDateString('id-ID', { month: 'long', year: 'numeric', timeZone: 'UTC' })

definePageMeta({ layout: 'tiles' })
useSeoMeta({ title: k.seoTitle, description: k.description })
</script>

<template>
  <div>
    <section class="tile grid items-center gap-10 lg:grid-cols-[1fr_1fr]">
      <div class="flex flex-col gap-5">
        <h1 class="text-4xl/[1.07] font-semibold text-balance sm:text-5xl/[1.07] lg:text-[3.5rem]/[1.07]">
          {{ k.title }}
        </h1>
        <p class="max-w-xl text-lg text-muted">
          {{ k.description }}
        </p>
      </div>
      <OutlineMap
        :outlines="outlines"
        :values="plantValues"
        :format="v => dayLabel((v + SEP1) % 365)"
        invert
        :min-label="k.map.early"
        :max-label="k.map.late"
        :hint="k.map.hint"
        :label="k.map.label"
      />
    </section>

    <section
      v-if="main"
      data-figure="kalender-tanam"
      class="tile tile-parchment flex flex-col gap-10"
    >
      <header class="flex max-w-2xl flex-col gap-3">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.calendar.title(monthName(main.start)) }}
        </h2>
        <p class="text-muted">
          {{ t.calendar.body }}
        </p>
      </header>
      <div class="tile-box flex flex-col gap-8">
        <SeasonCalendar
          :bands="bands"
          :today="today"
        />
        <ChartTable
          :caption="t.calendar.title(monthName(main.start))"
          :columns="[t.calendar.columns.season, t.calendar.columns.start, t.calendar.columns.plant, t.calendar.columns.harvest, t.calendar.columns.end]"
          :rows="bands.map(b => [t.calendar.seasons[b.season], monthName(b.start), monthName(b.plant), monthName(b.harvest), monthName(b.end)])"
        />
      </div>
    </section>

    <section
      v-if="schedule.length"
      data-figure="jadwal-per-desa"
      class="tile flex flex-col gap-10"
    >
      <header class="flex max-w-2xl flex-col gap-3">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
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
      <ChartTable
        :caption="t.schedule.title"
        :columns="[t.schedule.columns.unit, t.schedule.columns.plant, t.schedule.columns.harvest]"
        :rows="[...schedule].sort((a, b) => a.plant - b.plant).map(r => [r.unit, dayLabel(r.plant), dayLabel(r.harvest)])"
      />
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
          {{ COPY.onset.body(onsets[0]!.year, onsets[0]!.priorSeasons) }}
        </p>
      </header>
      <div class="tile-box flex flex-col gap-8">
        <ul class="flex flex-col gap-2">
          <li
            v-for="o in onsets"
            :key="o.unit"
            class="grid grid-cols-[6.5rem_1fr] items-center gap-x-4 gap-y-1 sm:grid-cols-[8rem_1fr_13rem]"
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
            <span class="col-span-2 flex items-center gap-2 text-sm text-muted tabular-nums sm:col-span-1">
              {{ COPY.onset.value(o.shift) }}
              <UBadge
                v-if="o.shift >= COPY.onset.lateAfter"
                :label="COPY.onset.late"
                color="warning"
                variant="subtle"
                size="xs"
              />
            </span>
          </li>
        </ul>
        <p class="max-w-2xl text-sm text-muted">
          {{ COPY.onset.note }}
        </p>
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
    </section>
  </div>
</template>
