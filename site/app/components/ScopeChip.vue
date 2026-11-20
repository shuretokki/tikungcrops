<script setup lang="ts">
defineProps<{ light?: boolean }>()
const { label } = useScope()
</script>

<template>
  <p class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
    <span
      class="font-semibold"
      :class="light ? 'text-white' : 'text-(--ui-primary)'"
    >{{ label }}</span>
    <NuxtLink
      to="/#pilih"
      class="rounded-sm underline-offset-2 hover:underline focus-visible:outline-2 focus-visible:outline-(--ui-primary)"
      :class="light ? 'text-white/80 hover:text-white' : 'text-muted hover:text-default'"
    >
      {{ COPY.scope.change }}
    </NuxtLink>
  </p>
</template>
