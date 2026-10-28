<script setup lang="ts">
export interface ScheduleRow { unit: string, plant: number, harvest: number }

const props = defineProps<{ rows: ScheduleRow[], today: number | null }>()
const t = COPY.ringkasan.schedule

// The axis starts at the month of the data date and runs twelve months ahead.
const start = computed(() => {
  if (props.today === null) return 0
  const d = new Date(Date.UTC(2001, 0, 1 + props.today))
  return dayOfYear(`2001-${String(d.getUTCMonth() + 1).padStart(2, '0')}-01`)
})
const rel = (day: number) => (day - start.value + 365) % 365
const pos = (day: number) => `${(rel(day) / 365) * 100}%`

const months = computed(() => Array.from({ length: 12 }, (_, i) => {
  const d = new Date(Date.UTC(2001, 0, 1 + start.value))
  d.setUTCMonth(d.getUTCMonth() + i)
  const day = dayOfYear(`2001-${String(d.getUTCMonth() + 1).padStart(2, '0')}-01`)
  return { day, label: monthName(day, 'short') }
}))

const date = (day: number) => new Date(Date.UTC(2001, 0, 1 + day)).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', timeZone: 'UTC' })

// Rows run in planting order from the data date, so the desa that plants first is on top.
const sorted = computed(() => [...props.rows].sort((a, b) => rel(a.plant) - rel(b.plant)).map(r => ({
  ...r,
  from: rel(r.plant),
  span: (rel(r.harvest) - rel(r.plant) + 365) % 365
})))

const hovered = ref<string | null>(null)
const shown = computed(() => sorted.value.find(r => r.unit === hovered.value))
</script>

<template>
  <figure class="flex flex-col gap-2">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <p
        class="text-sm tabular-nums"
        :class="shown ? '' : 'text-muted'"
        aria-live="polite"
      >
        {{ shown ? t.readout(shown.unit, date(shown.plant), date(shown.harvest)) : t.hint }}
      </p>
      <div class="flex gap-4 text-xs text-muted">
        <span class="flex items-center gap-1.5"><span class="size-3 rounded-full border-2 border-(--viz-3) bg-(--ui-bg)" />{{ t.plant }}</span>
        <span class="flex items-center gap-1.5"><span class="size-3 rounded-full bg-(--viz-2)" />{{ t.harvest }}</span>
      </div>
    </div>

    <div class="grid grid-cols-[7rem_1fr] gap-x-3 sm:grid-cols-[9rem_1fr]">
      <span />
      <div class="relative h-5 text-xs text-muted">
        <span
          v-for="m in months"
          :key="m.day"
          class="absolute"
          :style="{ left: pos(m.day) }"
        >
          <span class="hidden sm:inline">{{ m.label }}</span>
          <span class="sm:hidden">{{ m.label.slice(0, 1) }}</span>
        </span>
      </div>

      <template
        v-for="r in sorted"
        :key="r.unit"
      >
        <span
          class="truncate text-sm leading-8"
          :class="hovered === r.unit ? 'font-semibold' : ''"
        >{{ r.unit }}</span>
        <div
          class="relative h-8 cursor-default"
          tabindex="0"
          role="img"
          :aria-label="t.readout(r.unit, date(r.plant), date(r.harvest))"
          @mouseenter="hovered = r.unit"
          @mouseleave="hovered = null"
          @focus="hovered = r.unit"
          @blur="hovered = null"
        >
          <span
            v-for="m in months"
            :key="m.day"
            class="absolute inset-y-0 w-px bg-(--ui-border)"
            :style="{ left: pos(m.day) }"
          />
          <span
            v-if="today !== null"
            class="absolute inset-y-0 w-0.5 bg-(--ui-primary)"
            :style="{ left: pos(today) }"
          />
          <span
            class="absolute top-1/2 h-1.5 -translate-y-1/2 rounded-full"
            :class="hovered === r.unit ? 'bg-(--viz-outline)' : 'bg-(--viz-neutral)'"
            :style="{ left: `${(r.from / 365) * 100}%`, width: `${(r.span / 365) * 100}%` }"
          />
          <span
            class="absolute top-1/2 size-3.5 -translate-1/2 rounded-full border-2 border-(--viz-3) bg-(--ui-bg)"
            :style="{ left: pos(r.plant) }"
          />
          <span
            class="absolute top-1/2 size-3.5 -translate-1/2 rounded-full border-2 border-(--ui-bg) bg-(--viz-2)"
            :style="{ left: pos(r.harvest) }"
          />
        </div>
      </template>

      <span />
      <div class="relative h-5">
        <span
          v-if="today !== null"
          class="absolute -translate-x-1/2 text-xs font-semibold whitespace-nowrap text-(--ui-primary)"
          :style="{ left: pos(today) }"
        >▲ {{ t.today }}</span>
      </div>
    </div>
  </figure>
</template>
