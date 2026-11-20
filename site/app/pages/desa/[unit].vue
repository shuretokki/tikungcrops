<script setup lang="ts">
import type { FeatureCollection } from 'geojson'
import { AREAS, formatDate, formatHa, useAreaClientFile, useAreaFile, useAreaRainMonths, useAreaSeasons, type Cell, type CurrentRow, type IntensityRow, type Meta, type OutlookRow } from '~/composables/useArea'

const t = COPY.desa
const route = useRoute()
const unit = computed(() => String(route.params.unit))
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: current } = await useAreaFile<CurrentRow[]>(area, 'current.json')
const { data: outlook } = await useAreaFile<OutlookRow[]>(area, 'outlook.json')
const { data: seasons } = await useAreaSeasons(area)
const { data: intensity } = await useAreaFile<IntensityRow[]>(area, 'intensity.json')
const { data: rainMonths } = await useAreaRainMonths(area, unit)
const { data: desa } = await useAreaFile<FeatureCollection>(area, 'boundaries.geojson')
const { data: cells } = useAreaClientFile<Cell[]>(area, 'cells.json')
const { data: kecamatan } = useAreaClientFile<FeatureCollection>(AREAS.lamongan, 'boundaries.geojson')

const info = computed(() => meta.value?.units.find(u => u.unit === unit.value))
const labels = computed(() => (meta.value?.units ?? []).map(u => ({ name: u.unit, lon: u.lon, lat: u.lat })))
const today = computed(() => (meta.value?.as_of ? dayOfYear(meta.value.as_of) : null))
const day = (d: number) => new Date(Date.UTC(2001, 0, 1 + d)).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', timeZone: 'UTC' })

const stages = computed(() => stageTotals((current.value ?? []).filter(r => r.unit === unit.value)))
const mt1 = computed(() => mainSeasonDates((seasons.value ?? []).filter(s => s.unit === unit.value)))
const schedule = computed(() => (mt1.value ? [{ unit: unit.value, plant: mt1.value.plant, harvest: mt1.value.harvest }] : []))
const history = computed(() => seasonHistory((seasons.value ?? []).filter(s => s.unit === unit.value)))
const historyRows = computed(() => history.value.map(h => ({ unit: unit.value, plant: h.plant, harvest: h.harvest, label: COPY.history.label(h.year) })))
const onset = computed(() => onsetShift((seasons.value ?? []).filter(s => s.unit === unit.value)))

// Same eight-week window as the Beranda page, so both pages agree.
const HORIZON_DAYS = 56
const weeks = computed(() => {
  const asOf = meta.value?.as_of ? new Date(meta.value.as_of).getTime() : 0
  return (outlook.value ?? [])
    .filter((o) => {
      const dt = new Date(o.week).getTime() - asOf
      return o.unit === unit.value && o.expected_ha >= 0.5 && dt >= -6 * 86_400_000 && dt <= HORIZON_DAYS * 86_400_000
    })
    .sort((a, b) => a.week.localeCompare(b.week))
})
const weekMax = computed(() => Math.max(1, ...weeks.value.map(w => w.expected_ha)))

// The place of this desa among the desa of Tikung, for the same three measures as the comparison page.
const places = computed(() => {
  const sets: Record<'sawah' | 'intensitas' | 'tumbuh', Entry[]> = {
    sawah: (meta.value?.units ?? []).map(u => ({ unit: u.unit, value: u.paddy_ha })),
    intensitas: latestIntensity(intensity.value ?? []).entries,
    tumbuh: growingShare(current.value ?? [])
  }
  return (Object.keys(sets) as (keyof typeof sets)[]).flatMap((key) => {
    const own = sets[key].find(e => e.unit === unit.value)
    const spot = placeOf(sets[key], unit.value)
    if (!own || !spot) return []
    return [{ key, label: COPY.bandingkan.metrics[key].label, text: COPY.bandingkan.metrics[key].value(own.value), ...spot }]
  })
})

const rainMm = (v: number) => Math.round(v).toLocaleString('id-ID')
const orDash = (v?: number) => (v === undefined ? '-' : rainMm(v))
const monthLabel = (m: RainMonth) => new Date(Date.UTC(m.year, m.month - 1, 1)).toLocaleDateString('id-ID', { month: 'long', year: 'numeric', timeZone: 'UTC' })

definePageMeta({ layout: 'tiles' })
useSeoMeta({ title: () => t.seoTitle(unit.value) })
</script>

<template>
  <div>
    <section class="tile flex flex-col items-start gap-5 pb-12 sm:pb-16">
      <UButton
        :label="t.back"
        to="/#desa"
        icon="i-lucide-arrow-left"
        color="neutral"
        variant="outline"
      />
      <h1 class="text-4xl/[1.07] font-semibold text-balance sm:text-5xl/[1.07]">
        {{ t.title(unit) }}
      </h1>
      <p class="max-w-2xl text-lg text-muted">
        {{ info ? t.description(formatHa(info.paddy_ha), formatDate(meta?.as_of)) : t.notFound }}
      </p>
    </section>
    <template v-if="info">
      <section class="tile tile-parchment flex flex-col gap-8">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.now.title }}
        </h2>
        <div class="tile-box">
          <StageBar :totals="stages" />
        </div>
      </section>

      <section class="tile flex flex-col gap-8">
        <header class="flex flex-col gap-3">
          <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
            {{ t.schedule.title }}
          </h2>
          <p class="text-muted">
            {{ mt1 ? t.schedule.body : t.schedule.none }}
          </p>
        </header>
        <template v-if="mt1">
          <dl class="grid max-w-3xl gap-4 sm:grid-cols-3">
            <div class="flex flex-col-reverse gap-1 rounded-lg bg-muted p-4">
              <dt class="text-sm text-muted">
                {{ t.schedule.plant }}
              </dt>
              <dd class="text-xl font-semibold">
                {{ day(mt1.plant) }}
              </dd>
            </div>
            <div class="flex flex-col-reverse gap-1 rounded-lg bg-muted p-4">
              <dt class="text-sm text-muted">
                {{ t.schedule.harvest }}
              </dt>
              <dd class="text-xl font-semibold">
                {{ day(mt1.harvest) }}
              </dd>
            </div>
            <div
              v-if="onset"
              class="flex flex-col-reverse gap-1 rounded-lg bg-muted p-4"
            >
              <dt class="text-sm text-muted">
                {{ COPY.onset.card(onset.year, day(onset.plant), day(onset.mean)) }}
              </dt>
              <dd class="text-xl font-semibold">
                {{ COPY.onset.value(onset.shift) }}
              </dd>
            </div>
          </dl>
          <DesaSchedule
            :rows="schedule"
            :today="today"
          />
        </template>
      </section>

      <section
        v-if="history.length"
        class="tile tile-parchment flex flex-col gap-8"
      >
        <header class="flex max-w-2xl flex-col gap-3">
          <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
            {{ COPY.history.title }}
          </h2>
          <p class="text-muted">
            {{ COPY.history.body }}
          </p>
        </header>
        <div class="tile-box flex flex-col gap-8">
          <DesaSchedule
            :rows="historyRows"
            :today="today"
            :show-today="false"
            ordered
            :note="COPY.history.note"
          />
          <ChartTable
            :caption="COPY.history.title"
            :columns="[COPY.history.columns.season, COPY.history.columns.plant, COPY.history.columns.harvest, COPY.history.columns.ha]"
            :rows="history.map(h => [COPY.history.label(h.year), day(h.plant), day(h.harvest), formatHa(h.ha)])"
          />
        </div>
      </section>

      <section class="tile flex flex-col gap-8">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.harvest.title }}
        </h2>
        <ul
          v-if="weeks.length"
          class="flex flex-col gap-2"
        >
          <li
            v-for="w in weeks"
            :key="w.week"
            class="grid grid-cols-[1fr_12rem] items-center gap-3 sm:grid-cols-[1fr_16rem]"
          >
            <span class="h-3 rounded-sm bg-muted">
              <span
                class="block h-full rounded-sm bg-(--viz-2)"
                :style="{ width: `${(w.expected_ha / weekMax) * 100}%` }"
              />
            </span>
            <span class="text-sm text-muted tabular-nums">{{ t.harvest.row(formatDate(w.week, { day: 'numeric', month: 'short' }), formatHa(w.expected_ha)) }}</span>
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
          {{ t.harvest.empty }}
        </p>
      </section>

      <section
        v-if="places.length"
        class="tile tile-parchment flex flex-col gap-8"
      >
        <header class="flex flex-col gap-2">
          <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
            {{ t.compare.title }}
          </h2>
          <p class="text-muted">
            {{ t.compare.body }}
          </p>
        </header>
        <div class="tile-box flex flex-col gap-8">
          <dl class="grid gap-4 sm:grid-cols-3">
            <div
              v-for="p in places"
              :key="p.key"
              class="flex flex-col-reverse gap-1 rounded-lg bg-muted p-4"
            >
              <dt class="text-sm text-muted">
                {{ p.label }}: {{ p.text }}
              </dt>
              <dd class="text-3xl/[1.15] font-semibold sm:text-[2.5rem]/[1.1] tabular-nums">
                {{ t.compare.place(p.place, p.total) }}
              </dd>
            </div>
          </dl>
          <div>
            <UButton
              :label="t.compare.link"
              to="/perbandingan"
              trailing-icon="i-lucide-arrow-right"
              variant="outline"
            />
          </div>
        </div>
      </section>

      <section
        v-if="rainMonths?.length"
        class="tile flex flex-col gap-8"
      >
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ COPY.landing.rain.title }}
        </h2>
        <RainBars :months="rainMonths" />
        <ChartTable
          :caption="COPY.landing.rain.title"
          :columns="[COPY.landing.rain.columns.month, COPY.landing.rain.columns.mm, COPY.landing.rain.columns.normal, COPY.landing.rain.columns.lo, COPY.landing.rain.columns.hi]"
          :rows="rainMonths.map(m => [monthLabel(m), rainMm(m.mm), rainMm(rainBaseline(m)), orDash(m.lo), orDash(m.hi)])"
        />
      </section>

      <section class="tile tile-parchment flex flex-col gap-8">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.map.title }}
        </h2>
        <div class="h-[26rem] overflow-hidden rounded-[18px]">
          <ClientOnly>
            <AreaMap
              :outer="kecamatan"
              :inner="desa"
              :cells="cells"
              :labels="labels"
              :selected="unit"
              @select="(u: string) => navigateTo(`/desa/${encodeURIComponent(u)}`)"
            />
            <template #fallback>
              <div class="flex h-full items-center justify-center rounded-md bg-muted text-sm text-muted">
                {{ COPY.landing.mapLoading }}
              </div>
            </template>
          </ClientOnly>
        </div>
      </section>
    </template>
  </div>
</template>
