<script setup lang="ts">
import { AREAS, formatDate, useAreaFile, useAreaRainMonths, useAreaSeasons, type Meta } from '~/composables/useArea'

const t = COPY.landing
const k = COPY.kalender
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: seasons } = await useAreaSeasons(area)
const { data: rainMonths } = await useAreaRainMonths(area)

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

const dayLabel = (d: number) => new Date(Date.UTC(2001, 0, 1 + d)).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', timeZone: 'UTC' })

const months = computed(() => rainMonths.value ?? [])
const lastMonth = computed(() => months.value.at(-1))
const monthLabel = (m: RainMonth) => new Date(Date.UTC(m.year, m.month - 1, 1)).toLocaleDateString('id-ID', { month: 'long', year: 'numeric', timeZone: 'UTC' })

useSeoMeta({ title: k.seoTitle, description: k.description })
</script>

<template>
  <UPage>
    <UPageHeader
      :title="k.title"
      :description="`${k.description} Data terakhir: ${formatDate(meta?.as_of)}.`"
    />
    <UPageBody class="flex flex-col gap-16">
      <section
        v-if="main"
        data-figure="kalender-tanam"
        class="flex flex-col gap-6"
      >
        <header class="flex max-w-2xl flex-col gap-3">
          <h2 class="text-3xl/[1.15] font-semibold sm:text-[2.125rem]/[1.15] text-balance">
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
        v-if="schedule.length"
        data-figure="jadwal-per-desa"
        class="flex flex-col gap-6"
      >
        <header class="flex max-w-2xl flex-col gap-2">
          <h2 class="text-3xl/[1.15] font-semibold sm:text-[2.125rem]/[1.15] text-balance">
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
        v-if="lastMonth"
        data-figure="hujan-bulanan"
        class="flex flex-col gap-6"
      >
        <header class="flex max-w-2xl flex-col gap-3">
          <h2 class="text-3xl/[1.15] font-semibold sm:text-[2.125rem]/[1.15] text-balance">
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

      <section class="flex max-w-2xl flex-col gap-4">
        <header class="flex flex-col gap-2">
          <h2 class="text-3xl/[1.15] font-semibold sm:text-[2.125rem]/[1.15] text-balance">
            {{ k.notes.title }}
          </h2>
          <p class="text-muted">
            {{ k.notes.body }}
          </p>
        </header>
        <UAlert
          v-for="item in k.notes.items"
          :key="item"
          color="warning"
          variant="subtle"
          icon="i-lucide-circle-alert"
          :description="item"
        />
      </section>
    </UPageBody>
  </UPage>
</template>
