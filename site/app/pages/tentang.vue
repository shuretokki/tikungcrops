<script setup lang="ts">
import { AREAS, useAreaFile } from '~/composables/useArea'

const t = COPY.tentang
const { data: validation } = await useAreaFile<Validation>(AREAS.tikung, 'validation.json')

const num = (v: number) => v.toLocaleString('id-ID', { maximumFractionDigits: 2 })
const pctOf = (v: number) => `${Math.round(v * 100).toLocaleString('id-ID')}%`
const summary = computed(() => [...(validation.value?.area ?? [])].sort((a, b) => a.year - b.year || a.measure.localeCompare(b.measure)))
const years = computed(() => [...new Set(summary.value.map(a => a.year))])
// The scatter shows rice in the newest year, because the rice thresholds were tuned on the oldest one.
const latestYear = computed(() => years.value.at(-1))
const points = computed(() => (validation.value?.area_units ?? []).filter(p => p.measure === 'rice' && p.year === latestYear.value))
const units = computed(() => Math.max(0, ...summary.value.map(a => a.units)))
const riceLatest = computed(() => summary.value.find(a => a.measure === 'rice' && a.year === latestYear.value))

const facts = computed(() => [
  { value: String(units.value), label: t.facts.units },
  { value: t.facts.sinceValue, label: t.facts.since },
  { value: riceLatest.value ? pctOf(Math.abs(riceLatest.value.ratio - 1)) : '-', label: t.facts.match }
])

useSeoMeta({ title: t.seoTitle })
</script>

<template>
  <UPage>
    <UPageHeader
      :title="t.title"
      :description="t.description"
    />
    <UPageBody class="flex flex-col gap-16">
      <dl class="grid gap-4 sm:grid-cols-3">
        <div
          v-for="f in facts"
          :key="f.label"
          class="flex flex-col-reverse gap-1 rounded-lg bg-muted p-5"
        >
          <dt class="text-sm text-muted">
            {{ f.label }}
          </dt>
          <dd class="text-4xl font-semibold tabular-nums">
            {{ f.value }}
          </dd>
        </div>
      </dl>

      <section class="flex flex-col gap-6">
        <h2 class="text-2xl font-semibold">
          {{ t.steps.title }}
        </h2>
        <ol class="grid gap-6 md:grid-cols-3">
          <li
            v-for="(s, i) in t.steps.items"
            :key="s.title"
            class="flex gap-4"
          >
            <span class="flex size-9 shrink-0 items-center justify-center rounded-full bg-(--ui-primary) font-semibold text-inverted">
              {{ i + 1 }}
            </span>
            <div class="flex flex-col gap-1">
              <h3 class="flex items-center gap-2 font-semibold">
                <UIcon
                  :name="s.icon"
                  class="size-4 text-(--ui-primary)"
                />
                {{ s.title }}
              </h3>
              <p class="text-sm text-muted">
                {{ s.description }}
              </p>
            </div>
          </li>
        </ol>
      </section>

      <section
        v-if="summary.length && latestYear"
        data-figure="validasi-bps"
        class="grid gap-8 lg:grid-cols-[2fr_3fr]"
      >
        <div class="flex flex-col gap-4">
          <h2 class="text-2xl font-semibold">
            {{ t.accuracy.title }}
          </h2>
          <p>{{ t.accuracy.body(years.join(' dan '), units) }}</p>
          <p class="text-muted">
            {{ t.accuracy.crops }}
          </p>
          <UTable
            :data="summary.map(a => ({ year: a.year, crop: t.accuracy.cropNames[a.measure] ?? a.measure, r: num(a.r), ratio: pctOf(a.ratio) }))"
            :columns="[
              { accessorKey: 'year', header: t.accuracy.summaryColumns.year },
              { accessorKey: 'crop', header: t.accuracy.summaryColumns.crop },
              { accessorKey: 'r', header: t.accuracy.summaryColumns.r },
              { accessorKey: 'ratio', header: t.accuracy.summaryColumns.ratio }
            ]"
          />
          <p class="text-sm text-muted">
            {{ t.accuracy.rNote }}
          </p>
        </div>
        <figure class="flex flex-col gap-3">
          <figcaption class="text-sm text-muted">
            {{ t.accuracy.scatterNote(latestYear) }}
          </figcaption>
          <ValidationScatter :points="points" />
          <ChartTable
            :caption="t.accuracy.title"
            :columns="[t.accuracy.columns.unit, t.accuracy.columns.reference, t.accuracy.columns.satellite]"
            :rows="points.map(p => [p.unit, Math.round(p.reference_ha), Math.round(p.satellite_ha)])"
          />
        </figure>
      </section>

      <div class="grid gap-10 md:grid-cols-2">
        <section class="flex flex-col gap-4">
          <h2 class="text-2xl font-semibold">
            {{ t.sources.title }}
          </h2>
          <dl class="flex flex-col divide-y divide-default">
            <div
              v-for="s in t.sources.items"
              :key="s.name"
              class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 py-2.5"
            >
              <dt class="font-semibold">
                {{ s.name }}
              </dt>
              <dd class="text-sm text-muted">
                {{ s.role }}
              </dd>
            </div>
          </dl>
        </section>

        <section class="flex flex-col gap-4">
          <h2 class="text-2xl font-semibold">
            {{ t.limits.title }}
          </h2>
          <ul class="flex flex-col gap-3">
            <li
              v-for="item in t.limits.items"
              :key="item"
              class="flex gap-3"
            >
              <UIcon
                name="i-lucide-circle-alert"
                class="mt-0.5 size-5 shrink-0 text-(--ui-warning)"
              />
              <span>{{ item }}</span>
            </li>
          </ul>
        </section>
      </div>
    </UPageBody>
  </UPage>
</template>
