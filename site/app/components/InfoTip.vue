<script setup lang="ts">
defineProps<{ text: string }>()
</script>

<template>
  <UPopover :content="{ side: 'bottom', align: 'start' }">
    <UButton
      icon="i-lucide-info"
      color="neutral"
      variant="ghost"
      size="xs"
      :aria-label="COPY.site.detail"
    />
    <template #content>
      <p class="max-w-xs p-3 text-sm text-muted">
        {{ text }}
      </p>
    </template>
  </UPopover>
</template>
