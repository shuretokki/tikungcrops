<script setup lang="ts">
import type { FeatureCollection } from 'geojson'
import { AREAS, formatDate, formatHa, useAreaClientFile, useAreaFile, useAreaRainMonths, useAreaSeasons, type Cell, type CurrentRow, type IntensityRow, type Meta, type OutlookRow } from '~/composables/useArea'
import desaImages from '~/data/desa-images.json'

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

type DesaImage = { file: string, width: number, height: number, outline: string, date: string }
const images: Record<string, DesaImage> = desaImages
const info = computed(() => meta.value?.units.find(u => u.unit === unit.value))
const photo = computed(() => images[unit.value])
const labels = computed(() => (meta.value?.units ?? []).map(u => ({ name: u.unit, lon: u.lon, lat: u.lat })))
const today = computed(() => (meta.value?.as_of ? dayOfYear(meta.value.as_of) : null))
const day = (d: number) => new Date(Date.UTC(2001, 0, 1 + d)).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', timeZone: 'UTC' })

const stages = computed(() => stageTotals((current.value ?? []).filter(r => r.unit === unit.value)))
const mt1 = computed(() => mainSeasonDates((seasons.value ?? []).filter(s => s.unit === unit.value)))
const schedule = computed(() => (mt1.value ? [{ unit: unit.value, plant: mt1.value.plant, harvest: mt1.value.harvest }] : []))
const history = computed(() => seasonHistory((seasons.value ?? []).filter(s => s.unit === unit.value)))
const historyRows = computed(() => history.value.map(h => ({ unit: unit.value, plant: h.plant, harvest: h.harvest, label: COPY.history.label(h.year) })))
const onset = computed(() => onsetShift((seasons.value ?? []).filter(s => s.unit === unit.value)))
const summary = computed(() => (mt1.value ? [t.summary.usual(day(mt1.value.plant), day(mt1.value.harvest)), ...(onset.value ? [t.summary.onset(onset.value.shift, onset.value.year)] : [])].join(' ') : null))
const lastRain = computed(() => rainMonths.value?.at(-1))
// The percentage of growing sawah says how many hectares it is out of, so a small number of hectares is not mistaken for a large desa.
function basisOf(key: string) {
  if (key !== 'tumbuh') return ''
  const known = stages.value.planted + stages.value.peaked + stages.value.fallow
  return t.compare.basisTumbuh(formatHa(stages.value.planted + stages.value.peaked), formatHa(known))
}
// The harvest weeks and the timing line depend on today's date, so they are set in the browser once the page has loaded.
const todayMs = ref<number | null>(null)
onMounted(() => {
  todayMs.value = Date.now()
})
// The rain advice only shows when planting is within 30 days and the rain data is not older than about six weeks, so old dry months never decide the advice.
const adviceOn = computed(() => {
  if (todayMs.value === null || !mt1.value || !lastRain.value) return false
  const now = dayOfYear(`2001-${new Date(todayMs.value).toISOString().slice(5, 10)}`)
  const ahead = (mt1.value.plant - now + 365) % 365
  const monthEnd = Date.UTC(lastRain.value.year, lastRain.value.month, 1)
  return ahead <= 30 && todayMs.value - monthEnd <= 45 * 86_400_000
})
const timing = computed(() => {
  if (todayMs.value === null || !mt1.value) return null
  const now = dayOfYear(`2001-${new Date(todayMs.value).toISOString().slice(5, 10)}`)
  const { plant, harvest } = mt1.value
  const sincePlant = (now - plant + 365) % 365
  const length = (harvest - plant + 365) % 365
  const ahead = (plant - now + 365) % 365
  const r = t.timing
  if (sincePlant <= length) return length - sincePlant <= 30 ? r.harvestSoon(day(harvest)) : r.during
  return ahead <= 30 ? r.near(ahead, day(plant)) : r.before(day(plant))
})
const mine = useMyDesa()
const isMine = computed(() => mine.value === unit.value)
function toggleMine() {
  mine.value = isMine.value ? null : unit.value
}
function share() {
  const text = `${t.shareText(unit.value, summary.value ?? '')} ${window.location.href}`
  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank', 'noopener')
}

// Same eight-week window as the Beranda page, so both pages agree.
const HORIZON_DAYS = 56
const weeks = computed(() => {
  const asOf = meta.value?.as_of ? new Date(meta.value.as_of).getTime() : 0
  return (outlook.value ?? [])
    .filter((o) => {
      const dt = new Date(o.week).getTime() - asOf
      const notPast = todayMs.value === null || new Date(o.week).getTime() >= todayMs.value - 6 * 86_400_000
      return o.unit === unit.value && o.expected_ha >= 0.5 && notPast && dt >= -6 * 86_400_000 && dt <= HORIZON_DAYS * 86_400_000
    })
    .sort((a, b) => a.week.localeCompare(b.week))
})
const weekMax = computed(() => Math.max(1, ...weeks.value.map(w => w.expected_ha)))

// The place of this desa among the desa of Tikung, for the same three measures as the comparison page.
const places = computed(() => {
  const sets: Record<'intensitas' | 'tumbuh', Entry[]> = {
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
    <section class="tile relative isolate grid items-center gap-10 overflow-hidden text-white lg:grid-cols-[1fr_1fr]">
      <img
        v-if="photo"
        :src="photo.file"
        :width="photo.width"
        :height="photo.height"
        alt=""
        fetchpriority="high"
        class="absolute inset-0 -z-20 size-full scale-110 object-cover blur-2xl"
      >
      <div
        class="absolute inset-0 -z-10 bg-black/60"
        aria-hidden="true"
      />
      <div class="flex flex-col items-start gap-5">
        <UButton
          :label="t.back"
          to="/#desa"
          icon="i-lucide-arrow-left"
          color="neutral"
          variant="subtle"
        />
        <ScopeChip light />
        <h1 class="text-4xl/[1.07] font-semibold text-balance sm:text-5xl/[1.07] lg:text-[3.5rem]/[1.07]">
          {{ t.title(unit) }}
        </h1>
        <p class="max-w-xl text-lg text-white/85">
          {{ info ? t.description(unit) : t.notFound }}
        </p>
        <p
          v-if="summary"
          class="max-w-xl text-xl/[1.35] font-semibold"
        >
          {{ summary }}
        </p>
        <p
          v-if="timing"
          class="max-w-xl text-lg text-white/90"
        >
          {{ timing }}
        </p>
        <p
          v-if="lastRain && adviceOn"
          class="max-w-xl text-lg text-white/90"
        >
          {{ rainAdvice(lastRain) }}
        </p>
        <div class="flex flex-wrap gap-3">
          <ClientOnly>
            <UButton
              :label="isMine ? t.isMine : t.mine"
              :icon="isMine ? 'i-lucide-map-pin-check' : 'i-lucide-map-pin-plus'"
              :color="isMine ? 'primary' : 'neutral'"
              :variant="isMine ? 'solid' : 'outline'"
              :class="isMine ? '' : 'text-white ring-white/70 hover:bg-white/10'"
              :aria-pressed="isMine"
              @click="toggleMine"
            />
          </ClientOnly>
          <UButton
            :label="t.share"
            icon="i-lucide-share-2"
            color="neutral"
            variant="subtle"
            @click="share"
          />
        </div>
        <p class="max-w-xl text-sm text-white/70">
          {{ t.mineHelp }}
        </p>
        <p class="max-w-xl text-sm text-white/70">
          {{ COPY.site.advice }}
        </p>
      </div>
      <svg
        v-if="photo"
        :viewBox="`0 0 ${photo.width} ${photo.height}`"
        class="h-auto max-h-[58svh] w-full"
        role="img"
        :aria-label="t.photo.alt(unit)"
      >
        <path
          :d="photo.outline"
          fill="white"
          fill-opacity="0.22"
          stroke="white"
          stroke-width="5"
          stroke-linejoin="round"
        />
      </svg>
    </section>

    <template v-if="info">
      <section class="tile tile-parchment flex flex-col gap-10">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.groups.conditions }}
        </h2>
        <div class="grid gap-6 lg:grid-cols-2">
          <div class="tile-box flex flex-col gap-6">
            <h3 class="text-xl font-semibold">
              {{ t.now.title }}
              <span class="block text-sm font-normal text-muted">{{ t.now.asOf(formatDate(meta?.as_of, { day: 'numeric', month: 'long', year: 'numeric' })) }}</span>
            </h3>
            <StageBar :totals="stages" />
          </div>
          <div class="tile-box flex flex-col gap-6">
            <h3 class="text-xl font-semibold">
              {{ t.schedule.title }}
            </h3>
            <p class="text-muted">
              {{ mt1 ? t.schedule.body : t.schedule.none }}
            </p>
            <template v-if="mt1">
              <dl class="grid gap-3 sm:grid-cols-3">
                <div class="flex min-h-22 flex-col-reverse gap-1 rounded-lg bg-default p-4">
                  <dt class="text-sm text-muted">
                    {{ t.schedule.plant }}
                  </dt>
                  <dd class="text-xl font-semibold">
                    {{ day(mt1.plant) }}
                  </dd>
                </div>
                <div class="flex min-h-22 flex-col-reverse gap-1 rounded-lg bg-default p-4">
                  <dt class="text-sm text-muted">
                    {{ t.schedule.harvest }}
                  </dt>
                  <dd class="text-xl font-semibold">
                    {{ day(mt1.harvest) }}
                  </dd>
                </div>
                <div
                  v-if="onset"
                  class="flex min-h-22 flex-col-reverse gap-1 rounded-lg bg-default p-4"
                >
                  <dt class="text-sm text-muted">
                    {{ COPY.onset.card }}
                  </dt>
                  <dd class="flex items-center gap-1 text-xl font-semibold whitespace-nowrap">
                    {{ COPY.onset.short(onset.shift) }}
                    <InfoTip :text="COPY.onset.cardDetail(onset.year, onset.shift, day(onset.plant), day(onset.mean))" />
                  </dd>
                </div>
              </dl>
              <DesaSchedule
                :rows="schedule"
                :today="today"
              />
            </template>
          </div>
        </div>
      </section>

      <section class="tile flex flex-col gap-10">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.groups.history }}
        </h2>
        <div class="grid gap-10 lg:grid-cols-[3fr_2fr]">
          <div
            v-if="history.length"
            class="flex flex-col gap-6"
          >
            <div class="flex flex-col gap-2">
              <h3 class="text-xl font-semibold">
                {{ COPY.history.title }}
              </h3>
              <p class="text-muted">
                {{ COPY.history.body }}
              </p>
            </div>
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
          <div class="flex flex-col gap-6">
            <h3 class="text-xl font-semibold">
              {{ t.harvest.title }}
            </h3>
            <ul
              v-if="weeks.length"
              class="flex flex-col gap-3"
            >
              <li
                v-for="w in weeks"
                :key="w.week"
                class="grid grid-cols-[1fr_12rem] items-center gap-3"
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
              {{ t.harvest.empty(mt1 ? day(mt1.harvest) : null) }}
            </p>
          </div>
        </div>
      </section>

      <section class="tile tile-parchment flex flex-col gap-10">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.groups.context }}
        </h2>
        <div class="grid gap-6 lg:grid-cols-2">
          <div
            v-if="places.length"
            class="tile-box flex flex-col gap-6"
          >
            <div class="flex flex-col gap-2">
              <h3 class="text-xl font-semibold">
                {{ t.compare.title }}
              </h3>
              <p class="text-muted">
                {{ t.compare.body }}
              </p>
            </div>
            <dl class="grid gap-3">
              <div
                v-for="p in places"
                :key="p.key"
                class="flex min-h-22 flex-col-reverse gap-1 rounded-lg bg-default p-4"
              >
                <dt class="text-sm text-muted">
                  {{ p.label }}: {{ p.text }}{{ basisOf(p.key) }}
                </dt>
                <dd class="text-3xl/[1.15] font-semibold tabular-nums">
                  {{ t.compare.place(p.place, p.total) }}
                </dd>
              </div>
            </dl>
            <UButton
              :label="t.compare.link"
              to="/perbandingan"
              trailing-icon="i-lucide-arrow-right"
              variant="outline"
              class="self-start"
            />
          </div>
          <div
            v-if="rainMonths?.length"
            class="tile-box flex flex-col gap-6"
          >
            <h3 class="text-xl font-semibold">
              {{ COPY.landing.rain.title }}
            </h3>
            <p
              v-if="lastRain"
              class="font-semibold"
            >
              {{ rainPlain(lastRain) }}
            </p>
            <p
              v-if="lastRain"
              class="text-sm text-muted"
            >
              {{ t.rainOwn(rainMm(rainBaseline(lastRain))) }}
            </p>
            <RainBars :months="rainMonths" />
            <ChartTable
              :caption="COPY.landing.rain.title"
              :columns="[COPY.landing.rain.columns.month, COPY.landing.rain.columns.mm, COPY.landing.rain.columns.normal, COPY.landing.rain.columns.lo, COPY.landing.rain.columns.hi]"
              :rows="rainMonths.map(m => [monthLabel(m), rainMm(m.mm), rainMm(rainBaseline(m)), orDash(m.lo), orDash(m.hi)])"
            />
          </div>
        </div>
      </section>

      <section class="tile flex flex-col gap-8">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.map.title }}
        </h2>
        <div class="h-[62svh] overflow-hidden rounded-[18px]">
          <ClientOnly>
            <AreaMap
              :outer="null"
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
