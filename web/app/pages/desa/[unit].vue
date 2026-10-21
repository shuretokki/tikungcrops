<script setup lang="ts">
const route = useRoute()
</script>

<template>
  <UPage>
    <UPageHeader :title="String(route.params.unit)" description="Rincian desa menyusul." />
  </UPage>
</template>
