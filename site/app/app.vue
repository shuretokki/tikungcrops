<script setup lang="ts">
import { AREAS, formatDate, useAreaFile, type Meta } from '~/composables/useArea'

const route = useRoute()
const { data: meta } = await useAreaFile<Meta>(AREAS.tikung, 'meta.json')
const long = { day: 'numeric', month: 'long', year: 'numeric' } as const

const links = computed(() => [
  { label: COPY.nav.beranda, to: '/', icon: 'i-lucide-house', active: route.path === '/' },
  { label: COPY.nav.kalender, to: '/kalender', icon: 'i-lucide-calendar-days' },
  { label: COPY.nav.bandingkan, to: '/perbandingan', icon: 'i-lucide-chart-bar' }
])
</script>

<template>
  <UApp>
    <a
      href="#isi"
      class="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:bg-default focus:px-3 focus:py-2"
    >{{ COPY.site.skip }}</a>
    <UHeader to="/">
      <template #title>
        <span class="flex flex-col leading-tight">
          <span class="text-sm font-bold tracking-wide uppercase">{{ COPY.site.title }}</span>
          <span class="text-xs font-normal text-muted">{{ COPY.site.subtitle }}</span>
        </span>
      </template>
      <UNavigationMenu
        :items="links"
        class="hidden lg:flex"
      />
      <template #right>
        <UButton
          :label="COPY.site.search"
          to="/#desa"
          icon="i-lucide-search"
          size="sm"
          class="hidden sm:inline-flex"
        />
        <UColorModeButton />
      </template>
      <template #body>
        <UNavigationMenu
          :items="[...links, { label: COPY.site.search, to: '/#desa', icon: 'i-lucide-search' }]"
          orientation="vertical"
        />
      </template>
    </UHeader>
    <UMain id="isi">
      <UContainer>
        <NuxtPage />
      </UContainer>
    </UMain>
    <UFooter>
      <template #left>
        <div class="flex flex-col gap-1">
          <p class="text-sm text-default">
            {{ COPY.site.updated(formatDate(meta?.generated_at, long), formatDate(meta?.as_of, long)) }}
          </p>
          <p class="text-xs text-muted">
            {{ COPY.site.footer }}
          </p>
        </div>
      </template>
    </UFooter>
  </UApp>
</template>
