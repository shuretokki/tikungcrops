<script setup lang="ts">
import type { FeatureCollection } from 'geojson'
import { AREAS, STAGES, formatDate, formatHa, useAreaClientFile, useAreaFile, useAreaRainMonths, useAreaSeasons, type Cell, type CurrentRow, type Meta, type Stage } from '~/composables/useArea'

const t = COPY.landing
const mine = useMyDesa()
const area = AREAS.tikung
const { data: meta } = await useAreaFile<Meta>(area, 'meta.json')
const { data: current } = await useAreaFile<CurrentRow[]>(area, 'current.json')
const { data: seasons } = await useAreaSeasons(area)
const { data: rainMonths } = await useAreaRainMonths(area)
const { data: desa } = await useAreaFile<FeatureCollection>(area, 'boundaries.geojson')
const { data: cells } = useAreaClientFile<Cell[]>(area, 'cells.json')

const pct = (v: number) => v.toLocaleString('id-ID', { style: 'percent', maximumFractionDigits: 0 })

const units = computed(() => meta.value?.units ?? [])

const stages = computed(() => stageTotals(current.value ?? []))
const stageSum = computed(() => Object.values(stages.value).reduce((s, v) => s + v, 0))
const STAGE_ORDER: Stage[] = ['planted', 'peaked', 'fallow', 'unknown']
const stageRows = computed(() => STAGE_ORDER.map(k => [
  STAGES[k].label,
  formatHa(stages.value[k]),
  pct(stageSum.value ? stages.value[k] / stageSum.value : 0)
]))

const bands = computed(() => seasonBands(seasons.value ?? []))
const main = computed(() => bands.value.find(b => b.season === 'MT1'))
const todayDay = useToday()
const progress = computed(() => (main.value && todayDay.value !== null ? seasonProgress(main.value, todayDay.value) : null))

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

// Three headlines in the shape of a FAO GIEWS country brief: season, land, rain.
// Each has one large figure, so the tile reads at a glance.
const snapshot = computed(() => {
  const s = t.snapshot
  const items: { key: 'season' | 'fallow' | 'rain', value: string, valueLabel: string, title: string, body: string }[] = []
  if (main.value) {
    items.push(progress.value === null
      ? { key: 'season', value: monthName(main.value.start, 'short'), valueLabel: s.labels.seasonOutside, title: s.season.outside, body: s.season.outsideBody(monthName(main.value.start)) }
      : { key: 'season', value: pct(progress.value), valueLabel: s.labels.seasonDuring, title: s.season.during(pct(progress.value)), body: s.season.duringBody(monthName(main.value.end)) })
  }
  // Cloud-hidden land is left out of the share, because a cloudy wet season would otherwise look greener or barer than it is.
  const hidden = stages.value.unknown
  const readable = stageSum.value - hidden
  if (readable > 0) {
    const share = pct(stages.value.fallow / readable)
    const offSeason = progress.value === null
    items.push({ key: 'fallow', value: share, valueLabel: s.labels.fallow(formatHa(readable)), title: offSeason ? s.fallow.offSeason(formatDate(meta.value?.as_of, { day: 'numeric', month: 'long', year: 'numeric' })) : s.fallow.title(share), body: s.fallow.body(formatHa(stages.value.fallow), formatHa(readable), formatHa(hidden)) })
  }
  const last = rainMonths.value?.at(-1)
  if (last) {
    const base = rainBaseline(last)
    const v = rainVerdict(last.mm, base)
    const p = signedPercent(v.pct).replace('+', '')
    const word = v.kind === 'wetter' ? s.rain.wetter(p) : v.kind === 'drier' ? s.rain.drier(p) : s.rain[v.kind]
    const month = new Date(Date.UTC(last.year, last.month - 1, 1)).toLocaleDateString('id-ID', { month: 'long', year: 'numeric', timeZone: 'UTC' })
    const mm = Math.round(last.mm).toLocaleString('id-ID')
    const baseText = Math.round(base).toLocaleString('id-ID')
    const veryDry = v.kind === 'drier' && v.pct >= 0.9
    const hasPct = (v.kind === 'wetter' || v.kind === 'drier') && !veryDry
    items.push({
      key: 'rain',
      value: hasPct ? `${v.kind === 'drier' ? '-' : '+'}${p}` : `${mm} mm`,
      valueLabel: hasPct ? s.labels.rainPct : s.labels.rainMm(baseText),
      title: veryDry ? s.rain.veryDry(month) : s.rain.title(month, word),
      body: s.rain.body(mm, baseText)
    })
  }
  return items
})

definePageMeta({ layout: 'tiles' })

useSeoMeta({ title: t.seoTitle, description: () => t.description(units.value.length) })
</script>

<template>
  <div class="flex flex-col">
    <section class="tile flex flex-col items-center justify-center gap-10 text-center">
      <div class="flex max-w-3xl flex-col items-center gap-5">
        <p class="text-sm font-semibold text-(--ui-primary)">
          {{ t.eyebrow }}
        </p>
        <h1 class="text-4xl/[1.07] font-semibold text-balance sm:text-5xl/[1.07] lg:text-[3.5rem]/[1.07]">
          {{ t.headline }}
        </h1>
        <p class="text-lg text-muted">
          {{ t.description(units.length) }}
        </p>
        <ClientOnly>
          <UButton
            v-if="mine"
            :to="`/desa/${encodeURIComponent(mine)}`"
            :label="COPY.desa.mineOpen(mine)"
            icon="i-lucide-map-pin"
            color="neutral"
            variant="subtle"
            size="lg"
          />
        </ClientOnly>
      </div>
      <ScopePicker class="w-full max-w-3xl text-left" />
      <ol class="grid w-full max-w-5xl gap-4 text-left sm:grid-cols-3">
        <li
          v-for="(s, i) in t.steps"
          :key="s.title"
          class="flex flex-col gap-2 border-t border-default pt-5"
        >
          <span class="text-sm font-semibold text-(--ui-primary) tabular-nums">{{ i + 1 }}</span>
          <span class="font-semibold">{{ s.title }}</span>
          <span class="text-sm text-muted">{{ s.body }}</span>
        </li>
      </ol>
    </section>

    <section
      class="tile tile-parchment flex flex-col gap-12"
      data-figure="ringkasan-singkat"
    >
      <header class="flex max-w-2xl flex-col gap-3">
        <p class="text-sm font-semibold text-(--ui-primary)">
          {{ t.snapshot.eyebrow }}
        </p>
        <h2 class="text-3xl/[1.1] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.snapshot.title }}
        </h2>
        <p class="text-sm text-muted">
          {{ COPY.desa.now.asOf(formatDate(meta?.as_of, { day: 'numeric', month: 'long', year: 'numeric' })) }}
        </p>
      </header>
      <ol class="grid gap-12 lg:grid-cols-3 lg:gap-0">
        <li
          v-for="item in snapshot"
          :key="item.key"
          class="flex flex-col gap-5 border-t border-default pt-6 lg:border-t-0 lg:border-l lg:px-8 lg:first:border-l-0 lg:first:ps-0 lg:last:pe-0"
        >
          <div class="flex flex-col gap-2">
            <p class="text-6xl/none font-bold tracking-tight text-(--ui-primary) tabular-nums sm:text-7xl/none">
              {{ item.value }}
            </p>
            <p class="text-sm text-muted">
              {{ item.valueLabel }}
            </p>
          </div>
          <p class="text-xl/[1.3] font-semibold text-balance">
            {{ item.title }}
          </p>
          <p class="text-muted">
            {{ item.body }}
          </p>
          <UProgress
            v-if="item.key === 'season' && progress !== null"
            :model-value="progress * 100"
            :max="100"
            size="lg"
            :aria-label="t.progress.label(pct(progress))"
          />
          <template v-if="item.key === 'fallow'">
            <StageBar :totals="stages" />
            <ChartTable
              :caption="item.title"
              :columns="[t.now.columns.stage, t.now.columns.ha, t.now.columns.share]"
              :rows="stageRows"
            />
          </template>
        </li>
      </ol>
    </section>

    <section
      v-if="main"
      class="tile flex flex-col gap-8"
    >
      <header class="flex flex-wrap items-end justify-between gap-4">
        <div class="flex max-w-2xl flex-col gap-3">
          <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
            {{ t.calendar.title(monthName(main.start)) }}
          </h2>
          <p class="text-muted">
            {{ t.calendar.body }}
          </p>
        </div>
      </header>
      <SeasonCalendar
        :bands="bands"
        :today="todayDay"
      />
      <UButton
        :label="t.calendar.link"
        to="/kalender"
        trailing-icon="i-lucide-arrow-right"
        variant="outline"
        size="lg"
        class="self-start"
      />
    </section>

    <section
      id="desa"
      data-figure="cari-desamu"
      class="tile tile-parchment flex scroll-mt-20 flex-col gap-6"
    >
      <header class="flex flex-wrap items-end justify-between gap-4">
        <div class="flex flex-col gap-2">
          <h2 class="text-3xl/[1.15] font-semibold sm:text-[2.5rem]/[1.1]">
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
          name="cari-desa"
          type="search"
          autocomplete="off"
          size="lg"
          class="w-full sm:w-72"
        />
      </header>
      <div
        class="h-[26rem] overflow-hidden rounded-[18px] lg:h-[32rem]"
        data-figure="peta-beranda"
      >
        <ClientOnly>
          <AreaMap
            :outer="null"
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
            class="group flex h-full flex-col overflow-hidden rounded-md bg-default ring ring-default transition hover:ring-2 hover:ring-(--ui-primary) focus-visible:outline-2"
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
