<script setup lang="ts">
const props = defineProps<{ asOf?: string, label: string }>()

// The age is read in the browser, because a built page would freeze it at build time.
const days = ref<number | null>(null)
onMounted(() => {
  if (props.asOf) days.value = Math.floor((Date.now() - new Date(props.asOf).getTime()) / 86_400_000)
})
const old = computed(() => days.value !== null && days.value > 30)
</script>

<template>
  <div
    v-if="old"
    role="status"
    class="border-b border-default bg-(--ui-warning)/15 py-2 text-sm"
  >
    <UContainer class="flex items-center gap-2">
      <UIcon
        name="i-lucide-clock-alert"
        class="size-4 shrink-0 text-(--ui-warning)"
      />
      <span>{{ COPY.site.stale(label) }}</span>
    </UContainer>
  </div>
</template>
