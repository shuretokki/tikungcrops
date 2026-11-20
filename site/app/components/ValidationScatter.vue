<script setup lang="ts">
import { VisAxis, VisLine, VisScatter, VisTooltip, VisXYContainer } from '@unovis/vue'
import { Scatter } from '@unovis/ts'
import { formatHa } from '~/composables/useArea'

const props = defineProps<{ points: ValidationUnit[] }>()
const t = COPY.bandingkan.accuracy

const max = computed(() => Math.ceil(Math.max(...props.points.flatMap(p => [p.reference_ha, p.satellite_ha])) / 500) * 500)
const diagonal = computed(() => [0, max.value])
const triggers = {
  [Scatter.selectors.point]: (p: ValidationUnit) => tip({
    title: `Desa ${p.unit}`,
    rows: [
      { label: COPY.tip.reference, value: formatHa(p.reference_ha) },
      { label: COPY.tip.satellite, value: formatHa(p.satellite_ha), color: 'var(--viz-1)' },
      { label: COPY.tip.diff, value: p.reference_ha > 0 ? signedPercent((p.satellite_ha - p.reference_ha) / p.reference_ha) : '-' }
    ]
  })
}
const grid = (v: number | Date) => Number(v).toLocaleString('id-ID')
</script>

<template>
  <figure class="flex flex-col gap-2">
    <p class="text-sm text-muted">
      {{ t.hint }}
    </p>
    <ClientOnly>
      <VisXYContainer
        :data="points"
        :height="320"
        :x-domain="[0, max]"
        :y-domain="[0, max]"
        :scale-by-domain="true"
        class="vis-chart max-w-xl"
        role="img"
        :aria-label="`${t.y} / ${t.x}`"
      >
        <VisLine
          :data="diagonal"
          :x="(v: number) => v"
          :y="(v: number) => v"
          color="var(--viz-outline)"
          :line-width="1.5"
          :line-dash-array="[4, 4]"
        />
        <VisScatter
          :x="(p: ValidationUnit) => p.reference_ha"
          :y="(p: ValidationUnit) => p.satellite_ha"
          :size="12"
          color="var(--viz-1)"
          :stroke-color="'var(--ui-bg)'"
        />
        <VisAxis
          type="x"
          :label="t.x"
          :tick-format="grid"
          :grid-line="false"
        />
        <VisAxis
          type="y"
          :label="t.y"
          :tick-format="grid"
        />
        <VisTooltip :triggers="triggers" />
      </VisXYContainer>
      <template #fallback>
        <div class="h-80 max-w-xl rounded-md bg-muted" />
      </template>
    </ClientOnly>
    <p class="text-xs text-muted">
      {{ t.equalNote }}
    </p>
  </figure>
</template>
