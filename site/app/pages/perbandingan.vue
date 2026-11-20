<script setup lang="ts">
import { AREAS, useAreaFile, type CurrentRow, type IntensityRow, type Meta } from '~/composables/useArea'

type Level = 'desa' | 'kecamatan'
type Metric = 'sawah' | 'intensitas' | 'tumbuh'

const t = COPY.bandingkan

const NuxtLink = resolveComponent('NuxtLink')

const route = useRoute()
const router = useRouter()

// The tabs live in the address, so a comparison can be shared and the back button works.
function fromQuery<T extends string>(key: string, allowed: readonly T[], fallback: T) {
  return computed<T>({
    get: () => {
      const v = String(route.query[key] ?? '')
      return (allowed as readonly string[]).includes(v) ? v as T : fallback
    },
    set: (v) => {
      router.replace({ query: { ...route.query, [key]: v === fallback ? undefined : v } })
    }
  })
}
const level = fromQuery<Level>('tingkat', ['desa', 'kecamatan'], 'desa')
const metric = fromQuery<Metric>('ukuran', ['sawah', 'intensitas', 'tumbuh'], 'sawah')

const sources = {
  desa: AREAS.tikung,
  kecamatan: AREAS.lamongan
}

async function load(level: Level) {
  const area = sources[level]
  const [{ data: meta }, { data: current }, { data: intensity }] = await Promise.all([
    useAreaFile<Meta>(area, 'meta.json'),
    useAreaFile<CurrentRow[]>(area, 'current.json'),
    useAreaFile<IntensityRow[]>(area, 'intensity.json')
  ])
  return { meta, current, intensity }
}
const data = { desa: await load('desa'), kecamatan: await load('kecamatan') }
const { data: validation } = await useAreaFile<Validation>(AREAS.lamongan, 'validation.json')

const { data: tikungCheck } = await useAreaFile<Validation>(AREAS.tikung, 'validation.json')

const num = (v: number) => v.toLocaleString('id-ID', { maximumFractionDigits: 2 })
const pctOf = (v: number) => `${Math.round(v * 100).toLocaleString('id-ID')}%`
const summary = computed(() => [...(tikungCheck.value?.area ?? [])].sort((a, b) => a.year - b.year || a.measure.localeCompare(b.measure)))
const years = computed(() => [...new Set(summary.value.map(a => a.year))])
// The scatter shows rice in the newest year, because the rice thresholds were tuned on the oldest one.
const latestYear = computed(() => years.value.at(-1))
const points = computed(() => (tikungCheck.value?.area_units ?? []).filter(p => p.measure === 'rice' && p.year === latestYear.value))
const checkedUnits = computed(() => Math.max(0, ...summary.value.map(a => a.units)))

const intensity = computed(() => latestIntensity(data[level.value].intensity.value ?? []))

const entries = computed<Entry[]>(() => {
  const d = data[level.value]
  if (metric.value === 'sawah') return (d.meta.value?.units ?? []).map(u => ({ unit: u.unit, value: u.paddy_ha }))
  if (metric.value === 'intensitas') return intensity.value.entries
  return growingShare(d.current.value ?? [])
})

const ranked = computed(() => rank(entries.value))
const top = computed(() => Math.max(1e-9, ...ranked.value.map(e => e.value)))

const rows = computed(() => ranked.value.map((e, i) => ({
  ...e,
  place: i + 1,
  text: t.metrics[metric.value].value(e.value),
  to: level.value === 'desa' ? `/desa/${encodeURIComponent(e.unit)}` : null,
  here: level.value === 'kecamatan' && e.unit === 'Tikung'
})))
const tikung = computed(() => rows.value.find(r => r.here))

const heading = computed(() => {
  const m = t.metrics[metric.value]
  return metric.value === 'intensitas' ? t.metrics.intensitas.title(intensity.value.year) : (m.title as string)
})

// The frequency ranking counts every season on the paddy map, so its check is the all-crops area and not the rice flag.
const seasonCheck = computed(() => validation.value?.area.find(a => a.measure === 'all_crops'))
const note = computed(() => {
  const c = seasonCheck.value
  if (level.value !== 'kecamatan' || metric.value !== 'intensitas' || !c || c.median_abs_diff_pct === undefined) return null
  return t.kecamatanNote(`${Math.round(c.median_abs_diff_pct)}%`, c.year)
})

const levelItems = [
  { label: t.levels.desa, value: 'desa' },
  { label: t.levels.kecamatan, value: 'kecamatan' }
]
const metricItems = (Object.keys(t.metrics) as Metric[]).map(k => ({ label: t.metrics[k].label, value: k }))

definePageMeta({ layout: 'tiles' })
useSeoMeta({ title: t.seoTitle, description: t.description })
</script>

<template>
  <div>
    <section class="tile flex flex-col gap-4 pb-12 sm:pb-16">
      <h1 class="max-w-3xl text-4xl/[1.07] font-semibold text-balance sm:text-5xl/[1.07]">
        {{ t.title }}
      </h1>
      <p class="max-w-2xl text-lg text-muted">
        {{ t.description }}
      </p>
    </section>

    <section class="tile tile-parchment flex flex-col gap-12">
      <div class="flex flex-col gap-4">
        <UTabs
          v-model="level"
          :items="levelItems"
          :content="false"
          class="w-full max-w-md"
        />
        <div class="flex flex-col gap-2">
          <p class="text-sm text-muted">
            {{ t.metricLabel }}
          </p>
          <UTabs
            v-model="metric"
            :items="metricItems"
            :content="false"
            size="sm"
            variant="link"
            class="w-full max-w-md"
          />
        </div>
      </div>

      <div class="flex flex-col gap-8">
        <header class="flex max-w-2xl flex-col gap-3">
          <h2 class="text-3xl/[1.15] font-semibold sm:text-[2.125rem]/[1.15] text-balance">
            {{ heading }}
          </h2>
          <p class="text-muted">
            {{ t.metrics[metric].body }}
          </p>
          <p
            v-if="tikung"
            class="font-semibold text-(--ui-primary)"
          >
            {{ t.tikungRank(tikung.place, rows.length) }}
          </p>
        </header>

        <ol
          v-if="rows.length"
          class="flex flex-col gap-2"
        >
          <li
            v-for="r in rows"
            :key="r.unit"
          >
            <component
              :is="r.to ? NuxtLink : 'div'"
              :to="r.to ?? undefined"
              class="grid grid-cols-[2rem_7rem_1fr] items-center gap-x-3 gap-y-1 rounded-md px-3 py-3 sm:grid-cols-[2rem_9rem_1fr_6rem]"
              :class="[r.to ? 'hover:bg-muted focus-visible:outline-2 focus-visible:outline-(--ui-primary)' : '', r.here ? 'bg-muted' : '']"
            >
              <span class="text-sm text-muted tabular-nums">{{ t.rank(r.place) }}</span>
              <span
                class="truncate"
                :class="r.here ? 'font-semibold text-(--ui-primary)' : 'font-semibold'"
              >{{ r.unit }}</span>
              <UProgress
                :model-value="r.value"
                :max="top"
                :color="r.here ? 'primary' : 'neutral'"
                size="md"
                :aria-label="`${r.unit}: ${r.text}`"
                class="col-span-2 col-start-2 sm:col-span-1 sm:col-start-auto"
              />
              <span class="col-start-3 text-sm text-muted tabular-nums sm:col-start-auto sm:text-right">{{ r.text }}</span>
            </component>
          </li>
        </ol>
        <p
          v-else
          class="rounded-md bg-muted p-4 text-sm"
        >
          {{ t.empty }}
        </p>

        <UAlert
          v-if="note"
          color="warning"
          variant="subtle"
          icon="i-lucide-circle-alert"
          :description="note"
          class="max-w-2xl"
        />
      </div>
    </section>

    <section
      v-if="summary.length && latestYear"
      id="ketepatan"
      data-figure="validasi-bps"
      class="tile grid scroll-mt-20 gap-12 lg:grid-cols-[2fr_3fr]"
    >
      <div class="flex flex-col gap-4">
        <h2 class="text-3xl/[1.15] font-semibold sm:text-[2.125rem]/[1.15] text-balance">
          {{ t.accuracy.title }}
        </h2>
        <p>{{ t.accuracy.body(years.join(' dan '), checkedUnits) }}</p>
        <p class="text-muted">
          {{ t.accuracy.crops }}
        </p>
        <UTable
          :data="summary.map(a => ({ year: a.year, crop: t.accuracy.cropNames[a.measure] ?? a.measure, r: num(a.r), ratio: pctOf(a.ratio) }))"
          :columns="[
            { accessorKey: 'year', header: t.accuracy.summaryColumns.year },
            { accessorKey: 'crop', header: t.accuracy.summaryColumns.crop },
            { accessorKey: 'r', header: t.accuracy.summaryColumns.r },
            { accessorKey: 'ratio', header: t.accuracy.summaryColumns.ratio }
          ]"
        />
        <p class="text-sm text-muted">
          {{ t.accuracy.rNote }}
        </p>
      </div>
      <figure class="flex flex-col gap-3">
        <figcaption class="text-sm text-muted">
          {{ t.accuracy.scatterNote(latestYear) }}
        </figcaption>
        <ValidationScatter :points="points" />
        <ChartTable
          :caption="t.accuracy.title"
          :columns="[t.accuracy.columns.unit, t.accuracy.columns.reference, t.accuracy.columns.satellite]"
          :rows="points.map(p => [p.unit, Math.round(p.reference_ha), Math.round(p.satellite_ha)])"
        />
      </figure>
    </section>
  </div>
</template>
