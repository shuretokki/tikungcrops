<script setup lang="ts">
import { VisAxis, VisTimeline, VisTooltip, VisXYContainer } from '@unovis/vue'
import { Timeline } from '@unovis/ts'

export interface ScheduleRow { unit: string, plant: number, harvest: number, label?: string }

const props = withDefaults(defineProps<{
  rows: ScheduleRow[]
  today: number | null
  // Keep the order of the rows instead of sorting by planting day.
  ordered?: boolean
  showToday?: boolean
  note?: string
}>(), { ordered: false, showToday: true, note: undefined })
const t = COPY.landing.schedule

interface Item { row: string, start: number, length: number, color: string, tip: string }

// The axis starts at the month of the data date and runs twelve months ahead.
const start = computed(() => {
  if (props.today === null) return 0
  const d = new Date(Date.UTC(2001, 0, 1 + props.today))
  return dayOfYear(`2001-${String(d.getUTCMonth() + 1).padStart(2, '0')}-01`)
})
const rel = (day: number) => (day - start.value + 365) % 365

const months = computed(() => Array.from({ length: 12 }, (_, i) => {
  const d = new Date(Date.UTC(2001, 0, 1 + start.value))
  d.setUTCMonth(d.getUTCMonth() + i)
  const day = dayOfYear(`2001-${String(d.getUTCMonth() + 1).padStart(2, '0')}-01`)
  return { at: rel(day), label: monthName(day, 'short') }
}))

const date = (day: number) => new Date(Date.UTC(2001, 0, 1 + day)).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', timeZone: 'UTC' })

// Rows run in planting order from the data date, so the desa that plants first is on top.
const items = computed<Item[]>(() => {
  const rows = props.ordered ? props.rows : [...props.rows].sort((a, b) => rel(a.plant) - rel(b.plant))
  const out = rows.map((r) => {
    const length = (rel(r.harvest) - rel(r.plant) + 365) % 365
    return {
      row: r.label ?? r.unit,
      start: rel(r.plant),
      length,
      color: 'var(--viz-3)',
      tip: tip({
        title: r.label ?? `Desa ${r.unit}`,
        rows: [
          { label: COPY.tip.plant, value: date(r.plant) },
          { label: COPY.tip.harvest, value: date(r.harvest) },
          { label: COPY.tip.span, value: COPY.tip.days(length) }
        ],
        note: props.note ?? COPY.tip.since
      })
    }
  })
  if (props.today !== null && props.showToday) out.push({ row: t.today, start: rel(props.today), length: 3, color: 'var(--ui-primary)', tip: tip({ title: t.today, subtitle: date(props.today) }) })
  return out
})

const ROW = 30
const height = computed(() => items.value.length * ROW + 36)
const tick = (v: number | Date) => months.value.find(m => m.at === Number(v))?.label ?? ''
const triggers = { [Timeline.selectors.line]: (d: Item) => d.tip }
</script>

<template>
  <figure class="flex flex-col gap-2">
    <p class="text-sm text-muted">
      {{ t.hint }}
    </p>
    <ClientOnly>
      <VisXYContainer
        :data="items"
        :height="height"
        :x-domain="[0, 365]"
        class="vis-chart"
        role="img"
        :aria-label="t.title"
      >
        <VisTimeline
          :x="(d: Item) => d.start"
          :line-duration="(d: Item) => d.length"
          :line-row="(d: Item) => d.row"
          :color="(d: Item) => d.color"
          :row-height="ROW"
          :line-width="12"
          :show-row-labels="true"
          :row-label-width="130"
        />
        <VisAxis
          type="x"
          :tick-values="months.map(m => m.at)"
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
    <p class="flex items-center gap-1.5 text-xs text-muted">
      <span class="size-3 rounded-sm bg-(--viz-3)" />{{ t.legend }}
    </p>
  </figure>
</template>
