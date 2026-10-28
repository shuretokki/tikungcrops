<script setup lang="ts">
const links = [
  { label: COPY.nav.ringkasan, to: '/ringkasan', icon: 'i-lucide-map' },
  { label: COPY.nav.perbandingan, to: '/perbandingan', icon: 'i-lucide-chart-column' },
  { label: COPY.nav.metode, to: '/metode', icon: 'i-lucide-microscope' },
  { label: COPY.nav.data, to: '/data', icon: 'i-lucide-download' }
]
</script>

<template>
  <UApp>
    <UHeader
      :title="COPY.site.title"
      to="/"
    >
      <UNavigationMenu
        :items="links"
        class="hidden md:flex"
      />
      <template #right>
        <UColorModeButton />
      </template>
      <template #body>
        <UNavigationMenu
          :items="links"
          orientation="vertical"
        />
      </template>
    </UHeader>
    <UMain>
      <UContainer>
        <NuxtPage />
      </UContainer>
    </UMain>
    <UFooter>
      <template #left>
        <p class="text-xs text-muted">
          {{ COPY.site.footer }}
        </p>
      </template>
    </UFooter>
  </UApp>
</template>
