<script setup lang="ts">
import type { DesaOutlines } from '~/utils/landing'

const props = defineProps<{
  outlines: DesaOutlines | null | undefined
  values: Record<string, number>
  format: (v: number) => string
  highlight?: string
  // The low end gets the strongest color, as for the earliest planting.
  invert?: boolean
  minLabel: string
  maxLabel: string
  hint: string
  label: string
}>()

const MIN_SHARE = 18

const range = computed(() => {
  const v = Object.values(props.values)
  return { lo: Math.min(...v), hi: Math.max(...v) }
})

function share(unit: string) {
  const v = props.values[unit]
  if (v === undefined) return null
  const span = range.value.hi - range.value.lo
  const n = span > 0 ? (v - range.value.lo) / span : 0.5
  return Math.round(MIN_SHARE + (props.invert ? 1 - n : n) * (100 - MIN_SHARE))
}

const fill = (unit: string) => {
  const s = share(unit)
  return s === null ? 'var(--ui-bg-accented)' : `color-mix(in srgb, var(--ui-primary) ${s}%, var(--ui-bg))`
}

const hovered = ref<string | null>(null)
const readout = computed(() => {
  const v = hovered.value ? props.values[hovered.value] : undefined
  return hovered.value && v !== undefined ? `${hovered.value}: ${props.format(v)}` : null
})
const ordered = computed(() => [...(props.outlines?.paths ?? [])].sort((a, b) => Number(a.unit === props.highlight) - Number(b.unit === props.highlight)))
const ramp = computed(() => {
  const low = `color-mix(in srgb, var(--ui-primary) ${MIN_SHARE}%, var(--ui-bg))`
  const high = 'var(--ui-primary)'
  return `linear-gradient(to right, ${props.invert ? `${high}, ${low}` : `${low}, ${high}`})`
})
</script>

<template>
  <figure class="flex flex-col gap-4">
    <p
      class="min-h-6 text-sm tabular-nums"
      :class="readout ? 'font-semibold' : 'text-muted'"
    >
      {{ readout ?? hint }}
    </p>
    <svg
      v-if="outlines"
      :viewBox="outlines.viewBox"
      class="max-h-[55svh] w-full"
      role="group"
      :aria-label="label"
    >
      <path
        v-for="p in ordered"
        :key="p.unit"
        :d="p.d"
        :fill="fill(p.unit)"
        :stroke="p.unit === highlight ? 'var(--ui-text-highlighted)' : 'var(--ui-bg)'"
        :stroke-width="p.unit === highlight ? 1.2 : 0.5"
        stroke-linejoin="round"
        role="graphics-symbol"
        tabindex="0"
        :aria-label="values[p.unit] === undefined ? p.unit : `${p.unit}: ${format(values[p.unit]!)}`"
        class="outline-none transition-opacity focus-visible:stroke-(--ui-primary)"
        :class="hovered && hovered !== p.unit ? 'opacity-60' : ''"
        @mouseenter="hovered = p.unit"
        @mouseleave="hovered = null"
        @focus="hovered = p.unit"
        @blur="hovered = null"
      />
    </svg>
    <div
      v-else
      class="aspect-[4/3] rounded-lg bg-muted"
    />
    <div class="flex flex-col gap-1">
      <span
        class="h-2 w-full rounded-full"
        :style="{ background: ramp }"
        aria-hidden="true"
      />
      <span class="flex justify-between text-xs text-muted">
        <span>{{ minLabel }}</span>
        <span>{{ maxLabel }}</span>
      </span>
    </div>
  </figure>
</template>
