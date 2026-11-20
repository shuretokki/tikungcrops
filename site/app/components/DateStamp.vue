<script setup lang="ts">
defineProps<{ date: string }>()
</script>

<template>
  <p class="flex items-center gap-2 self-start rounded-full bg-default px-5 py-2.5 text-lg font-semibold tabular-nums ring ring-default">
    <UIcon
      name="i-lucide-calendar-check"
      class="size-5 text-(--ui-primary)"
    />
    {{ COPY.site.asOf(date) }}
  </p>
</template>
