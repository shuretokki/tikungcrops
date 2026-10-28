<script setup lang="ts">
const props = defineProps<{
  units: string[]
  outlook: OutlookRow[]
  asOf: string | null | undefined
}>()
const t = COPY.ringkasan.calendar

const week = (iso: string) => new Date(iso).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })

// Weeks from the one that holds the data date onwards, because past weeks are already harvested.
const weeks = computed(() => {
  const from = props.asOf ? new Date(props.asOf).getTime() - 6 * 86_400_000 : 0
  return [...new Set(props.outlook.map(o => o.week))].filter(w => new Date(w).getTime() >= from).sort()
})
const value = computed(() => {
  const m = new Map<string, number>()
  for (const o of props.outlook) m.set(`${o.unit}|${o.week}`, (m.get(`${o.unit}|${o.week}`) ?? 0) + o.expected_ha)
  return m
})
const max = computed(() => Math.max(0, ...weeks.value.flatMap(w => props.units.map(u => value.value.get(`${u}|${w}`) ?? 0))))

// A square-root scale keeps small harvests visible next to the largest one.
function fill(v: number) {
  if (v <= 0 || max.value <= 0) return undefined
  const p = Math.round(20 + 80 * Math.sqrt(v / max.value))
  return `color-mix(in oklab, var(--viz-2) ${p}%, var(--ui-bg))`
}

// Label a column only when a new month starts, so the header stays readable.
const headers = computed(() => weeks.value.map((w, i) => {
  const d = new Date(w)
  const prev = i > 0 ? new Date(weeks.value[i - 1]!) : null
  return i === 0 || d.getMonth() !== prev?.getMonth() ? d.toLocaleDateString('id-ID', { month: 'short' }) : ''
}))

const hovered = ref<{ unit: string, week: string } | null>(null)
const readout = computed(() => {
  if (!hovered.value) return null
  const v = value.value.get(`${hovered.value.unit}|${hovered.value.week}`) ?? 0
  return t.readout(hovered.value.unit, week(hovered.value.week), formatHa(v))
})
const formatHa = (ha: number) => `${ha < 1 && ha > 0 ? ha.toLocaleString('id-ID', { maximumFractionDigits: 1 }) : Math.round(ha).toLocaleString('id-ID')} ha`
</script>

<template>
  <figure
    v-if="weeks.length && max > 0"
    class="flex flex-col gap-3"
  >
    <div class="flex flex-wrap items-center justify-between gap-3">
      <p
        class="text-sm tabular-nums"
        :class="readout ? '' : 'text-muted'"
        aria-live="polite"
      >
        {{ readout ?? t.hint }}
      </p>
      <div class="flex items-center gap-2 text-xs text-muted">
        {{ t.less }}
        <span class="h-2.5 w-24 rounded-full bg-linear-to-r from-[color-mix(in_oklab,var(--viz-2)_20%,var(--ui-bg))] to-(--viz-2)" />
        {{ t.more }}
      </div>
    </div>
    <div class="overflow-x-auto">
      <div
        class="grid min-w-max gap-0.5"
        :style="{ gridTemplateColumns: `8.5rem repeat(${weeks.length}, 1.5rem)` }"
        role="table"
        :aria-label="t.title"
      >
        <span role="columnheader" />
        <span
          v-for="(h, i) in headers"
          :key="weeks[i]"
          role="columnheader"
          class="h-5 text-xs whitespace-nowrap text-muted"
          :class="i === 0 ? 'font-semibold text-(--ui-primary)' : ''"
        >{{ i === 0 ? t.today : h }}</span>
        <template
          v-for="u in units"
          :key="u"
        >
          <span
            role="rowheader"
            class="truncate pr-2 text-sm leading-6"
          >{{ u }}</span>
          <span
            v-for="w in weeks"
            :key="w"
            role="cell"
            tabindex="0"
            class="h-6 rounded-xs bg-muted outline-offset-1 focus-visible:outline-2"
            :class="hovered?.unit === u && hovered?.week === w ? 'ring-2 ring-(--ui-text-highlighted)' : ''"
            :style="{ background: fill(value.get(`${u}|${w}`) ?? 0) }"
            :aria-label="t.readout(u, week(w), formatHa(value.get(`${u}|${w}`) ?? 0))"
            @mouseenter="hovered = { unit: u, week: w }"
            @mouseleave="hovered = null"
            @focus="hovered = { unit: u, week: w }"
            @blur="hovered = null"
          />
        </template>
      </div>
    </div>
  </figure>
  <p
    v-else
    class="rounded-md bg-muted p-4 text-sm text-muted"
  >
    {{ t.empty }}
  </p>
</template>
