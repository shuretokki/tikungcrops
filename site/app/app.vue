<script setup lang="ts">
const links = [
  { label: 'Ringkasan', to: '/', icon: 'i-lucide-map' },
  { label: 'Perbandingan', to: '/perbandingan', icon: 'i-lucide-chart-column' },
  { label: 'Metode', to: '/metode', icon: 'i-lucide-microscope' },
  { label: 'Data', to: '/data', icon: 'i-lucide-download' }
]
</script>

<template>
  <UApp>
    <UHeader
      title="Tanam Padi Lamongan"
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
          Data turunan Copernicus Sentinel-1/2 (ESA), CHIRPS, ESA WorldCover, Lahan Baku Sawah (BIG).
          Batas wilayah: geoBoundaries (OCHA ROAP, BPS 2019), CC BY 3.0 IGO. Peta dasar: OpenFreeMap, © OpenStreetMap.
        </p>
      </template>
    </UFooter>
  </UApp>
</template>
