<script setup lang="ts">
const props = defineProps<{ bands: SeasonBand[], today: number | null }>()
const t = COPY.landing.calendar

const MONTHS = Array.from({ length: 12 }, (_, m) => {
  const start = dayOfYear(`2001-${String(m + 1).padStart(2, '0')}-01`)
  return { start, label: monthName(start, 'short') }
})

const pos = (day: number) => `${(day / 365) * 100}%`

// A season that crosses the new year is drawn as two pieces.
function pieces(b: SeasonBand) {
  return b.end >= b.start
    ? [{ left: b.start, width: b.end - b.start }]
    : [{ left: b.start, width: 365 - b.start }, { left: 0, width: b.end }]
}

const rows = computed(() => props.bands.map(b => ({
  ...b,
  main: b.season === 'MT1',
  label: COPY.seasons[b.season],
  pieces: pieces(b)
})))
</script>

<template>
  <figure class="flex flex-col gap-1">
    <div class="grid grid-cols-[4.5rem_1fr] items-end gap-x-3 sm:grid-cols-[5rem_1fr]">
      <span />
      <div class="relative h-5 text-xs text-muted">
        <span
          v-for="m in MONTHS"
          :key="m.start"
          class="absolute top-0"
          :style="{ left: pos(m.start) }"
        >
          <span class="hidden sm:inline">{{ m.label }}</span>
          <span class="sm:hidden">{{ m.label.slice(0, 1) }}</span>
        </span>
      </div>
    </div>

    <div
      v-for="r in rows"
      :key="r.season"
      class="grid grid-cols-[4.5rem_1fr] items-center gap-x-3 sm:grid-cols-[5rem_1fr]"
    >
      <span
        class="text-sm"
        :class="r.main ? 'font-semibold' : ''"
      >{{ r.label }}</span>
      <div
        class="relative h-10"
        role="img"
        :aria-label="`${r.label}: ${monthName(r.start)} sampai ${monthName(r.end)}, ${t.plant.toLowerCase()} ${monthName(r.plant)}, ${t.harvest.toLowerCase()} ${monthName(r.harvest)}`"
      >
        <span
          v-for="m in MONTHS"
          :key="m.start"
          class="absolute inset-y-0 w-px bg-(--ui-border)"
          :style="{ left: pos(m.start) }"
        />
        <span
          v-for="(p, i) in r.pieces"
          :key="i"
          class="absolute top-1/2 h-4 -translate-y-1/2 rounded-sm"
          :class="r.main ? 'bg-(--viz-3)' : 'bg-(--viz-neutral)'"
          :style="{ left: pos(p.left), width: pos(p.width) }"
        />
        <span
          v-if="today !== null"
          class="absolute inset-y-0 w-0.5 -translate-x-1/2 bg-(--ui-primary)"
          :style="{ left: pos(today) }"
        />
        <span
          class="absolute top-1/2 size-3 -translate-1/2 rounded-full border-2 border-(--viz-outline) bg-(--ui-bg)"
          :style="{ left: pos(r.plant) }"
          :title="`${t.plant}: ${monthName(r.plant)}`"
        />
        <span
          class="absolute top-1/2 size-3 -translate-1/2 rounded-full border-2 border-(--ui-bg) bg-(--viz-outline)"
          :style="{ left: pos(r.harvest) }"
          :title="`${t.harvest}: ${monthName(r.harvest)}`"
        />
      </div>
    </div>

    <div class="grid grid-cols-[4.5rem_1fr] gap-x-3 sm:grid-cols-[5rem_1fr]">
      <span />
      <div class="relative h-6">
        <span
          v-if="today !== null"
          class="absolute top-0 -translate-x-1/2 text-xs font-semibold text-(--ui-primary)"
          :style="{ left: pos(today) }"
        >▲ {{ t.today }}</span>
      </div>
    </div>

    <figcaption class="flex flex-wrap gap-x-5 gap-y-1 text-xs text-muted">
      <span class="flex items-center gap-1.5">
        <span class="size-3 rounded-full border-2 border-(--viz-outline)" />{{ t.plant }}
      </span>
      <span class="flex items-center gap-1.5">
        <span class="size-3 rounded-full bg-(--viz-outline)" />{{ t.harvest }}
      </span>
    </figcaption>
  </figure>
</template>
