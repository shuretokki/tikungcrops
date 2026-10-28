<script setup lang="ts">
const props = defineProps<{ months: RainMonth[] }>()
const t = COPY.landing.rain

const fmt = (v: number) => Math.round(v).toLocaleString('id-ID')
const label = (m: RainMonth) => new Date(Date.UTC(m.year, m.month - 1, 1)).toLocaleDateString('id-ID', { month: 'long', year: 'numeric', timeZone: 'UTC' })
const short = (m: RainMonth) => new Date(Date.UTC(m.year, m.month - 1, 1)).toLocaleDateString('id-ID', { month: 'short', timeZone: 'UTC' })

const top = computed(() => Math.max(100, ...props.months.flatMap(m => [m.mm, m.normal])) * 1.05)
const height = (v: number) => `${(v / top.value) * 100}%`

const hovered = ref<number | null>(null)
const shown = computed(() => props.months[hovered.value ?? props.months.length - 1])
</script>

<template>
  <figure class="flex flex-col gap-2">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <p
        class="text-sm tabular-nums"
        aria-live="polite"
      >
        <template v-if="shown">
          {{ t.readout(label(shown), fmt(shown.mm), fmt(shown.normal)) }}
        </template>
      </p>
      <div class="flex gap-4 text-xs text-muted">
        <span class="flex items-center gap-1.5"><span class="size-3 rounded-sm bg-(--viz-1)" />{{ t.actual }}</span>
        <span class="flex items-center gap-1.5"><span class="h-0.5 w-4 bg-(--viz-outline)" />{{ t.normal }}</span>
      </div>
    </div>
    <div class="relative flex h-48 items-end gap-1 border-b border-(--ui-border) sm:gap-2">
      <button
        v-for="(m, i) in months"
        :key="`${m.year}-${m.month}`"
        type="button"
        class="relative flex h-full flex-1 items-end focus-visible:outline-2"
        :aria-label="t.readout(label(m), fmt(m.mm), fmt(m.normal))"
        @mouseenter="hovered = i"
        @mouseleave="hovered = null"
        @focus="hovered = i"
        @blur="hovered = null"
      >
        <span
          class="w-full rounded-t-sm bg-(--viz-1)"
          :class="hovered === i ? 'opacity-80' : ''"
          :style="{ height: height(m.mm) }"
        />
        <span
          class="absolute inset-x-0 h-0.5 bg-(--viz-outline)"
          :style="{ bottom: height(m.normal) }"
        />
      </button>
    </div>
    <div class="flex gap-1 sm:gap-2">
      <span
        v-for="m in months"
        :key="`${m.year}-${m.month}`"
        class="flex-1 text-center text-xs text-muted"
      >
        <span class="hidden sm:inline">{{ short(m) }}</span>
        <span class="sm:hidden">{{ short(m).slice(0, 1) }}</span>
      </span>
    </div>
  </figure>
</template>
