<script setup lang="ts">
import { AREAS, useAreaFile } from '~/composables/useArea'

const t = COPY.metode
const { data: validation } = await useAreaFile<Validation>(AREAS.tikung, 'validation.json')

const num = (v: number) => v.toLocaleString('id-ID', { maximumFractionDigits: 2 })
const summary = computed(() => [...(validation.value?.area ?? [])].sort((a, b) => a.year - b.year || a.measure.localeCompare(b.measure)))
const years = computed(() => [...new Set(summary.value.map(a => a.year))])
// The scatter shows rice in the newest year, because the rice thresholds were tuned on the oldest one.
const latestYear = computed(() => years.value.at(-1))
const points = computed(() => (validation.value?.area_units ?? []).filter(p => p.measure === 'rice' && p.year === latestYear.value))
const units = computed(() => Math.max(0, ...summary.value.map(a => a.units)))

useSeoMeta({ title: t.seoTitle })
</script>

<template>
  <UPage>
    <UPageHeader
      :title="t.title"
      :description="t.description"
    />
    <UPageBody class="flex max-w-3xl flex-col gap-12">
      <section class="flex flex-col gap-4">
        <h2 class="text-xl font-semibold">
          {{ t.steps.title }}
        </h2>
        <ol class="grid gap-4 md:grid-cols-3">
          <li
            v-for="(s, i) in t.steps.items"
            :key="s.title"
            class="flex flex-col gap-2 rounded-md bg-muted p-4 ring ring-default"
          >
            <span class="flex items-center gap-2 text-(--ui-primary)">
              <span class="text-sm font-semibold">{{ i + 1 }}</span>
              <UIcon
                :name="s.icon"
                class="size-5"
              />
            </span>
            <h3 class="font-semibold">
              {{ s.title }}
            </h3>
            <p class="text-sm text-muted">
              {{ s.description }}
            </p>
          </li>
        </ol>
      </section>

      <section
        v-if="summary.length && latestYear"
        class="flex flex-col gap-4"
      >
        <h2 class="text-xl font-semibold">
          {{ t.validation.title }}
        </h2>
        <p>{{ t.validation.body(years.join(' dan '), units) }}</p>
        <UTable
          :data="summary.map(a => ({ year: a.year, crop: t.validation.crops[a.measure] ?? a.measure, r: num(a.r), ratio: num(a.ratio) }))"
          :columns="[
            { accessorKey: 'year', header: t.validation.summaryColumns.year },
            { accessorKey: 'crop', header: t.validation.summaryColumns.crop },
            { accessorKey: 'r', header: t.validation.summaryColumns.r },
            { accessorKey: 'ratio', header: t.validation.summaryColumns.ratio }
          ]"
        />
        <p class="text-sm text-muted">
          {{ t.validation.scatterNote(latestYear) }}
        </p>
        <ValidationScatter :points="points" />
        <ChartTable
          :caption="t.validation.title"
          :columns="[t.validation.columns.unit, t.validation.columns.reference, t.validation.columns.satellite]"
          :rows="points.map(p => [p.unit, Math.round(p.reference_ha), Math.round(p.satellite_ha)])"
        />
      </section>

      <section class="flex flex-col gap-3">
        <h2 class="text-xl font-semibold">
          {{ t.limits.title }}
        </h2>
        <ul class="flex list-disc flex-col gap-2 pl-5">
          <li
            v-for="item in t.limits.items"
            :key="item"
          >
            {{ item }}
          </li>
        </ul>
      </section>
    </UPageBody>
  </UPage>
</template>
