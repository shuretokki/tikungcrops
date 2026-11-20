<script setup lang="ts">
import { AREAS, formatDate, useAreaFile, type Meta } from '~/composables/useArea'

const route = useRoute()
const { data: meta } = await useAreaFile<Meta>(AREAS.tikung, 'meta.json')
const long = { day: 'numeric', month: 'long', year: 'numeric' } as const

const footerLinks = computed(() => [
  { label: COPY.nav.beranda, to: '/' },
  { label: COPY.nav.kalender, to: '/kalender' },
  { label: COPY.nav.bandingkan, to: '/perbandingan' },
  { label: COPY.site.search, to: '/#desa' }
])

const links = computed(() => [
  { label: COPY.nav.beranda, to: '/', icon: 'i-lucide-house', active: route.path === '/' },
  { label: COPY.nav.kalender, to: '/kalender', icon: 'i-lucide-calendar-days' },
  { label: COPY.nav.bandingkan, to: '/perbandingan', icon: 'i-lucide-chart-bar' },
  { label: COPY.nav.faq, to: '/faq', icon: 'i-lucide-circle-help' }
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
      <NuxtLayout>
        <NuxtPage />
      </NuxtLayout>
    </UMain>
    <footer class="tile tile-parchment tile-slim border-t border-default">
      <div class="grid gap-10 sm:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr_1.2fr]">
        <div class="flex flex-col gap-2">
          <p class="font-semibold">
            {{ COPY.site.title }}
          </p>
          <p class="text-sm text-muted">
            {{ COPY.site.subtitle }}
          </p>
          <p class="mt-2 text-sm text-muted">
            {{ COPY.site.updated(formatDate(meta?.generated_at, long), formatDate(meta?.as_of, long)) }}
          </p>
        </div>
        <nav
          :aria-label="COPY.site.footer.pages"
          class="flex flex-col"
        >
          <p class="mb-2 text-sm font-semibold">
            {{ COPY.site.footer.pages }}
          </p>
          <NuxtLink
            v-for="l in footerLinks"
            :key="l.to"
            :to="l.to"
            class="rounded-sm py-1 text-sm text-muted hover:text-default focus-visible:outline-2 focus-visible:outline-(--focus-ring)"
          >
            {{ l.label }}
          </NuxtLink>
        </nav>
        <nav
          :aria-label="COPY.site.footer.data"
          class="flex flex-col"
        >
          <p class="mb-2 text-sm font-semibold">
            {{ COPY.site.footer.data }}
          </p>
          <a
            v-for="f in COPY.site.download.files"
            :key="f.file"
            :href="`/json/${AREAS.tikung.slug}/${f.file}`"
            :download="f.file"
            class="rounded-sm py-1 text-sm text-muted hover:text-default focus-visible:outline-2 focus-visible:outline-(--focus-ring)"
          >{{ f.label }}</a>
        </nav>
        <nav
          :aria-label="COPY.site.footer.info"
          class="flex flex-col"
        >
          <p class="mb-2 text-sm font-semibold">
            {{ COPY.site.footer.info }}
          </p>
          <NuxtLink
            v-for="l in COPY.site.footer.infoLinks"
            :key="l.to"
            :to="l.to"
            class="rounded-sm py-1 text-sm text-muted hover:text-default focus-visible:outline-2 focus-visible:outline-(--focus-ring)"
          >
            {{ l.label }}
          </NuxtLink>
        </nav>
      </div>
      <p class="mt-10 border-t border-default pt-6 text-xs text-muted">
        {{ COPY.site.footer.copyright }}
      </p>
    </footer>
  </UApp>
</template>
