<script setup lang="ts">
import { VisAxis, VisTimeline, VisTooltip, VisXYContainer } from '@unovis/vue'
import { Timeline } from '@unovis/ts'

const props = defineProps<{ bands: SeasonBand[], today: number | null }>()
const t = COPY.landing.calendar

interface Item { row: string, start: number, length: number, color: string, tip: string }

const PHASE_COLOR: Record<Phase, string> = {
  sow: 'color-mix(in srgb, var(--viz-3) 45%, transparent)',
  grow: 'var(--viz-3)',
  harvest: 'var(--viz-2)'
}
const MUTED: Record<Phase, string> = {
  sow: 'color-mix(in srgb, var(--viz-neutral) 45%, transparent)',
  grow: 'var(--viz-neutral)',
  harvest: 'color-mix(in srgb, var(--viz-neutral) 70%, transparent)'
}

const MONTH_STARTS = Array.from({ length: 12 }, (_, m) => dayOfYear(`2001-${String(m + 1).padStart(2, '0')}-01`))

const items = computed<Item[]>(() => {
  const out = props.bands.flatMap((b) => {
    const row = t.seasons[b.season]
    return seasonSegments(b).map(s => ({
      row,
      start: s.start,
      length: s.length,
      color: (b.season === 'MT1' ? PHASE_COLOR : MUTED)[s.phase],
      tip: tip({
        title: row,
        subtitle: t.phases[s.phase],
        rows: [
          { label: COPY.tip.start, value: monthName(b.start) },
          { label: COPY.tip.plant, value: monthName(b.plant) },
          { label: COPY.tip.harvest, value: monthName(b.harvest) },
          { label: COPY.tip.end, value: monthName(b.end) }
        ],
        note: t.seasonNote[b.season]
      })
    }))
  })
  if (props.today !== null) {
    const date = new Date(Date.UTC(2001, 0, 1 + props.today)).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', timeZone: 'UTC' })
    out.push({ row: t.today, start: props.today, length: 3, color: 'var(--ui-primary)', tip: tip({ title: t.today, subtitle: date }) })
  }
  return out
})

const narrow = ref(false)
onMounted(() => {
  const query = window.matchMedia('(max-width: 639px)')
  narrow.value = query.matches
  query.addEventListener('change', (e) => {
    narrow.value = e.matches
  })
})
const ticks = computed(() => narrow.value ? MONTH_STARTS.filter((_, m) => m % 3 === 0) : MONTH_STARTS)

const ROW = 40
const height = computed(() => (props.bands.length + (props.today === null ? 0 : 1)) * ROW + 36)
const tick = (v: number | Date) => monthName(Number(v), 'short')
const triggers = { [Timeline.selectors.line]: (d: Item) => d.tip }

const legend = [
  { key: 'sow', label: t.phases.sow, color: PHASE_COLOR.sow },
  { key: 'grow', label: t.phases.grow, color: PHASE_COLOR.grow },
  { key: 'harvest', label: t.phases.harvest, color: PHASE_COLOR.harvest }
]
</script>

<template>
  <figure class="flex flex-col gap-2">
    <ClientOnly>
      <VisXYContainer
        :data="items"
        :height="height"
        :x-domain="[0, 365]"
        class="vis-chart"
        role="img"
        :aria-label="t.body"
      >
        <VisTimeline
          :x="(d: Item) => d.start"
          :line-duration="(d: Item) => d.length"
          :line-row="(d: Item) => d.row"
          :color="(d: Item) => d.color"
          :row-height="ROW"
          :line-width="16"
          :show-row-labels="true"
          :row-label-width="narrow ? 104 : 140"
        />
        <VisAxis
          type="x"
          :tick-values="ticks"
          :tick-format="tick"
          :grid-line="true"
        />
        <VisTooltip :triggers="triggers" />
      </VisXYContainer>
      <template #fallback>
        <div
          class="rounded-md bg-muted"
          :style="{ height: `${height}px` }"
        />
      </template>
    </ClientOnly>
    <figcaption class="flex flex-wrap gap-x-5 gap-y-1 text-xs text-muted">
      <span
        v-for="l in legend"
        :key="l.key"
        class="flex items-center gap-1.5"
      >
        <span
          class="size-3 rounded-sm"
          :style="{ background: l.color }"
        />{{ l.label }}
      </span>
    </figcaption>
  </figure>
</template>
