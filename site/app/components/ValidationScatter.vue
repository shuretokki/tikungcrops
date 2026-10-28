<script setup lang="ts">
import { formatHa } from '~/composables/useArea'

const props = defineProps<{ points: ValidationUnit[] }>()
const t = COPY.tentang.validation

const W = 420
const H = 320
const PAD = { l: 48, r: 12, t: 12, b: 40 }
const max = computed(() => Math.ceil(Math.max(...props.points.flatMap(p => [p.reference_ha, p.satellite_ha])) / 500) * 500)
const x = (v: number) => PAD.l + (v / max.value) * (W - PAD.l - PAD.r)
const y = (v: number) => H - PAD.b - (v / max.value) * (H - PAD.t - PAD.b)
const ticks = computed(() => Array.from({ length: max.value / 500 + 1 }, (_, i) => i * 500))

const hovered = ref<string | null>(null)
const shown = computed(() => props.points.find(p => p.unit === hovered.value))
</script>

<template>
  <figure class="flex flex-col gap-2">
    <p
      class="h-5 text-sm tabular-nums"
      aria-live="polite"
    >
      <template v-if="shown">
        {{ t.readout(shown.unit, formatHa(shown.reference_ha), formatHa(shown.satellite_ha)) }}
      </template>
      <span
        v-else
        class="text-muted"
      >{{ t.hint }}</span>
    </p>
    <svg
      :viewBox="`0 0 ${W} ${H}`"
      class="w-full max-w-xl overflow-visible"
      role="img"
      :aria-label="`${t.y} / ${t.x}`"
    >
      <g class="text-(--ui-text-muted)">
        <template
          v-for="v in ticks"
          :key="v"
        >
          <line
            :x1="x(0)"
            :x2="x(max)"
            :y1="y(v)"
            :y2="y(v)"
            stroke="var(--ui-border)"
          />
          <text
            :x="x(0) - 6"
            :y="y(v)"
            text-anchor="end"
            dominant-baseline="middle"
            font-size="11"
            fill="currentColor"
          >{{ v.toLocaleString('id-ID') }}</text>
          <text
            :x="x(v)"
            :y="H - PAD.b + 16"
            text-anchor="middle"
            font-size="11"
            fill="currentColor"
          >{{ v.toLocaleString('id-ID') }}</text>
        </template>
        <text
          :x="(x(0) + x(max)) / 2"
          :y="H - 4"
          text-anchor="middle"
          font-size="12"
          fill="currentColor"
        >{{ t.x }}</text>
        <text
          :transform="`translate(12 ${(y(0) + y(max)) / 2}) rotate(-90)`"
          text-anchor="middle"
          font-size="12"
          fill="currentColor"
        >{{ t.y }}</text>
      </g>
      <line
        :x1="x(0)"
        :y1="y(0)"
        :x2="x(max)"
        :y2="y(max)"
        stroke="var(--viz-outline)"
        stroke-width="1.5"
        stroke-dasharray="4 4"
      />
      <text
        :x="x(max) - 4"
        :y="y(max) + 16"
        text-anchor="end"
        font-size="11"
        fill="var(--ui-text-muted)"
      >{{ t.equal }}</text>
      <circle
        v-for="p in points"
        :key="p.unit"
        :cx="x(p.reference_ha)"
        :cy="y(p.satellite_ha)"
        :r="hovered === p.unit ? 8 : 6"
        fill="var(--viz-1)"
        stroke="var(--ui-bg)"
        stroke-width="2"
        tabindex="0"
        class="cursor-pointer outline-none"
        @mouseenter="hovered = p.unit"
        @mouseleave="hovered = null"
        @focus="hovered = p.unit"
        @blur="hovered = null"
      >
        <title>{{ t.readout(p.unit, formatHa(p.reference_ha), formatHa(p.satellite_ha)) }}</title>
      </circle>
    </svg>
  </figure>
</template>
