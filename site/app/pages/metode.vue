<script setup lang="ts">
import { AREAS, useAreaFile } from '~/composables/useArea'

const t = COPY.metode
const { data: validation } = await useAreaFile<Validation>(AREAS.tikung, 'validation.json')

const num = (v: number) => v.toLocaleString('id-ID', { maximumFractionDigits: 2 })
const allCrops = computed(() => validation.value?.area.find(a => a.measure === 'all_crops'))
const points = computed(() => (validation.value?.area_units ?? []).filter(p => p.measure === 'all_crops' && p.year === allCrops.value?.year))

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
        v-if="allCrops"
        class="flex flex-col gap-4"
      >
        <h2 class="text-xl font-semibold">
          {{ t.validation.title }}
        </h2>
        <p>{{ t.validation.body(num(allCrops.r), num(allCrops.ratio), points.length) }}</p>
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
