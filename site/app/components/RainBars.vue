<script setup lang="ts">
import { VisAxis, VisGroupedBar, VisLine, VisTooltip, VisXYContainer } from '@unovis/vue'
import { GroupedBar } from '@unovis/ts'

const props = defineProps<{ months: RainMonth[] }>()
const t = COPY.landing.rain

const fmt = (v: number) => Math.round(v).toLocaleString('id-ID')
const label = (m: RainMonth) => new Date(Date.UTC(m.year, m.month - 1, 1)).toLocaleDateString('id-ID', { month: 'long', year: 'numeric', timeZone: 'UTC' })
const short = (m: RainMonth) => new Date(Date.UTC(m.year, m.month - 1, 1)).toLocaleDateString('id-ID', { month: 'short', timeZone: 'UTC' })

const ticks = computed(() => props.months.map((_, i) => i))
const tick = (v: number | Date) => {
  const m = props.months[Number(v)]
  return m ? short(m) : ''
}
const triggers = {
  [GroupedBar.selectors.bar]: (m: RainMonth) => t.readout(label(m), fmt(m.mm), fmt(m.normal))
}
const latest = computed(() => props.months.at(-1))
</script>

<template>
  <figure class="flex flex-col gap-2">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <p class="text-sm tabular-nums">
        <template v-if="latest">
          {{ t.readout(label(latest), fmt(latest.mm), fmt(latest.normal)) }}
        </template>
      </p>
      <div class="flex gap-4 text-xs text-muted">
        <span class="flex items-center gap-1.5"><span class="size-3 rounded-sm bg-(--viz-1)" />{{ t.actual }}</span>
        <span class="flex items-center gap-1.5"><span class="h-0.5 w-4 bg-(--viz-outline)" />{{ t.normal }}</span>
      </div>
    </div>
    <ClientOnly>
      <VisXYContainer
        :data="months"
        :height="192"
        class="vis-chart"
        role="img"
        :aria-label="t.title"
      >
        <VisGroupedBar
          :x="(_: RainMonth, i: number) => i"
          :y="(m: RainMonth) => m.mm"
          color="var(--viz-1)"
          :rounded-corners="2"
        />
        <VisLine
          :x="(_: RainMonth, i: number) => i"
          :y="(m: RainMonth) => m.normal"
          color="var(--viz-outline)"
          :line-width="2"
        />
        <VisAxis
          type="x"
          :tick-values="ticks"
          :tick-format="tick"
          :grid-line="false"
        />
        <VisAxis
          type="y"
          :num-ticks="4"
        />
        <VisTooltip :triggers="triggers" />
      </VisXYContainer>
      <template #fallback>
        <div class="h-48 rounded-md bg-muted" />
      </template>
    </ClientOnly>
  </figure>
</template>
