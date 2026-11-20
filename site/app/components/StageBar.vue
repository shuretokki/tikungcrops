<script setup lang="ts">
import { VisStackedBar, VisXYContainer } from '@unovis/vue'
import { STAGES, formatHa, type Stage } from '~/composables/useArea'

const props = defineProps<{ totals: Record<Stage, number> }>()

const ORDER: Stage[] = ['planted', 'peaked', 'fallow', 'unknown']

// Cloud-hidden cells get a hatch so they never read as a fourth hue.
const FILL: Record<Stage, string> = {
  planted: 'var(--viz-3)',
  peaked: 'var(--viz-2)',
  fallow: 'var(--viz-neutral)',
  unknown: 'url(#stage-hatch)'
}
const SWATCH: Record<Stage, Record<string, string>> = {
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
  ha: props.totals[k]
})))

const colors = ORDER.map(k => FILL[k])
const accessors = computed(() => ORDER.map(k => () => props.totals[k]))
</script>

<template>
  <figure class="flex flex-col gap-3">
    <svg
      width="0"
      height="0"
      class="absolute"
      aria-hidden="true"
    >
      <defs>
        <pattern
          id="stage-hatch"
          width="6"
          height="6"
          patternUnits="userSpaceOnUse"
          patternTransform="rotate(45)"
        >
          <rect
            width="6"
            height="6"
            fill="transparent"
          />
          <rect
            width="2"
            height="6"
            fill="var(--viz-neutral)"
          />
        </pattern>
      </defs>
    </svg>
    <div
      role="img"
      :aria-label="parts.map(p => `${p.label} ${formatHa(p.ha)}`).join(', ')"
    >
      <ClientOnly>
        <VisXYContainer
          :data="[{ row: 0 }]"
          :height="40"
          :margin="{ top: 0, right: 0, bottom: 0, left: 0 }"
          :padding="{ top: 0, right: 0, bottom: 0, left: 0 }"
          :y-domain="[0, sum]"
          class="vis-chart"
        >
          <VisStackedBar
            :x="() => 0"
            :y="accessors"
            :color="colors"
            orientation="horizontal"
            :bar-padding="0"
            :rounded-corners="3"
          />
        </VisXYContainer>
        <template #fallback>
          <div class="h-10 rounded-sm bg-muted" />
        </template>
      </ClientOnly>
    </div>
    <ul class="grid grid-cols-2 gap-x-6 gap-y-2 sm:grid-cols-4">
      <li
        v-for="p in parts"
        :key="p.key"
      >
        <UTooltip
          :text="COPY.stageHelp[p.key]"
          :content="{ side: 'top' }"
        >
          <button
            type="button"
            class="flex cursor-help items-start gap-2 rounded-md text-left focus-visible:outline-2 focus-visible:outline-(--focus-ring)"
          >
            <span
              class="mt-1 size-3 shrink-0 rounded-sm"
              :style="SWATCH[p.key]"
            />
            <span class="flex flex-col">
              <span class="text-sm">{{ p.label }}</span>
              <span class="text-xs text-muted tabular-nums">{{ formatHa(p.ha) }}</span>
            </span>
          </button>
        </UTooltip>
      </li>
    </ul>
    <p class="text-sm text-muted">
      {{ COPY.stageNote }}
    </p>
  </figure>
</template>
