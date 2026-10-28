<script setup lang="ts">
const props = defineProps<{ years: IntensityYear[] }>()
const t = COPY.landing.intensity

const fmt = (v: number) => v.toLocaleString('id-ID', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
const top = computed(() => Math.max(3, Math.ceil(Math.max(...props.years.map(y => y.all)))))
const avg = computed(() => props.years.reduce((s, y) => s + y.all, 0) / (props.years.length || 1))
const height = (v: number) => `${(v / top.value) * 100}%`

const hovered = ref<number | null>(null)
const shown = computed(() => props.years.find(y => y.year === hovered.value) ?? props.years.at(-1))
const ticks = computed(() => Array.from({ length: top.value + 1 }, (_, i) => i))
</script>

<template>
  <figure class="flex flex-col gap-2">
    <p
      class="h-5 text-sm tabular-nums"
      aria-live="polite"
    >
      <template v-if="shown">
        {{ t.readout(shown.year, fmt(shown.all)) }}
      </template>
    </p>
    <div class="relative ml-6 h-56">
      <div
        v-for="tick in ticks"
        :key="tick"
        class="absolute inset-x-0 border-t border-(--ui-border)"
        :style="{ bottom: height(tick) }"
      >
        <span class="absolute -left-6 -translate-y-1/2 text-xs text-muted tabular-nums">{{ tick }}</span>
      </div>
      <div
        class="absolute inset-x-0 z-10 border-t-2 border-dashed border-(--viz-outline)"
        :style="{ bottom: height(avg) }"
      >
        <span class="absolute right-0 -translate-y-full bg-(--ui-bg) px-1 text-xs">{{ t.average(fmt(avg)) }}</span>
      </div>
      <div class="absolute inset-0 flex items-end gap-2 sm:gap-4">
        <button
          v-for="(y, i) in years"
          :key="y.year"
          type="button"
          class="group flex h-full flex-1 items-end focus-visible:outline-2"
          :aria-label="t.readout(y.year, fmt(y.all))"
          @mouseenter="hovered = y.year"
          @mouseleave="hovered = null"
          @focus="hovered = y.year"
          @blur="hovered = null"
        >
          <span
            class="w-full rounded-t-sm transition-opacity group-hover:opacity-80"
            :class="i === years.length - 1 ? 'bg-(--viz-3)' : 'bg-(--viz-neutral)'"
            :style="{ height: height(y.all) }"
          />
        </button>
      </div>
    </div>
    <div class="ml-6 flex gap-2 sm:gap-4">
      <span
        v-for="y in years"
        :key="y.year"
        class="flex-1 text-center text-xs text-muted tabular-nums"
      >{{ y.year }}</span>
    </div>
  </figure>
</template>
