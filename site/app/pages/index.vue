<script setup lang="ts">
import { AREAS, formatDate, formatHa, useAreaFile, type Meta } from '~/composables/useArea'

const t = COPY.landing
const { data: meta } = await useAreaFile<Meta>(AREAS.tikung, 'meta.json')

const stats = computed(() => [
  { label: t.stats.paddy, value: formatHa((meta.value?.units ?? []).reduce((s, u) => s + u.paddy_ha, 0)) },
  { label: t.stats.units, value: String(meta.value?.units.length ?? '-') },
  { label: t.stats.asOf, value: formatDate(meta.value?.as_of) }
])

useSeoMeta({ title: t.seoTitle, description: t.description })
</script>

<template>
  <div>
    <UPageHero
      :title="t.headline"
      :description="t.description"
      :links="[
        { label: t.primaryCta, to: '/ringkasan', icon: 'i-lucide-map', size: 'lg' },
        { label: t.secondaryCta, to: '/metode', color: 'neutral', variant: 'subtle', size: 'lg' }
      ]"
    />

    <dl class="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <UCard
        v-for="s in stats"
        :key="s.label"
      >
        <dt class="text-xs text-muted">
          {{ s.label }}
        </dt>
        <dd class="text-xl font-semibold">
          {{ s.value }}
        </dd>
      </UCard>
    </dl>

    <UPageSection
      :title="t.featuresTitle"
      :features="t.features"
    />

    <UPageCTA
      :title="t.limitsTitle"
      :description="t.limits"
      variant="subtle"
      :links="[{ label: t.limitsCta, to: '/metode', color: 'neutral', variant: 'outline' }]"
      class="mb-12"
    />
  </div>
</template>
