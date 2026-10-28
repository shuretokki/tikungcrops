<script setup lang="ts">
import { STAGES, formatHa, type Stage } from '~/composables/useArea'

const props = defineProps<{ totals: Record<Stage, number> }>()

const ORDER: Stage[] = ['planted', 'peaked', 'fallow', 'unknown']

// Cloud-hidden cells get a hatch so they never read as a fourth hue.
const FILL: Record<Stage, Record<string, string>> = {
  planted: { background: 'var(--viz-3)' },
  peaked: { background: 'var(--viz-2)' },
  fallow: { background: 'var(--viz-neutral)' },
  unknown: {
    background: 'repeating-linear-gradient(45deg, var(--viz-neutral) 0 2px, transparent 2px 6px)',
    boxShadow: 'inset 0 0 0 1px var(--viz-neutral)'
  }
}

const sum = computed(() => ORDER.reduce((s, k) => s + props.totals[k], 0))
const parts = computed(() => ORDER.map(k => ({
  key: k,
  label: STAGES[k].label,
  ha: props.totals[k],
  share: sum.value ? props.totals[k] / sum.value : 0
})))

function pct(v: number) {
  return v.toLocaleString('id-ID', { style: 'percent', maximumFractionDigits: v < 0.1 ? 1 : 0 })
}
</script>

<template>
  <figure class="flex flex-col gap-3">
    <div
      class="flex h-10 w-full gap-0.5"
      role="img"
      :aria-label="parts.map(p => `${p.label} ${pct(p.share)}`).join(', ')"
    >
      <div
        v-for="p in parts.filter(p => p.share > 0)"
        :key="p.key"
        class="h-full min-w-1 first:rounded-l-sm last:rounded-r-sm"
        :style="{ ...FILL[p.key], flexGrow: p.share }"
        :title="`${p.label}: ${formatHa(p.ha)} (${pct(p.share)})`"
      />
    </div>
    <ul class="grid grid-cols-2 gap-x-6 gap-y-2 sm:grid-cols-4">
      <li
        v-for="p in parts"
        :key="p.key"
        class="flex items-start gap-2"
      >
        <span
          class="mt-1 size-3 shrink-0 rounded-sm"
          :style="FILL[p.key]"
        />
        <span class="flex flex-col">
          <span class="text-sm">{{ p.label }}</span>
          <span class="text-xs text-muted tabular-nums">{{ formatHa(p.ha) }} · {{ pct(p.share) }}</span>
        </span>
      </li>
    </ul>
  </figure>
</template>
