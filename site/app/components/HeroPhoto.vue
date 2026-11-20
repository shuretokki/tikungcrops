<script setup lang="ts">
defineProps<{
  src: string
  alt: string
  author: string
  source: string
}>()
</script>

<template>
  <figure class="flex flex-col gap-3">
    <img
      :src="src"
      :alt="alt"
      width="1920"
      height="1440"
      fetchpriority="high"
      class="aspect-[4/3] max-h-[60svh] w-full rounded-[18px] object-cover"
    >
    <figcaption class="text-xs text-muted">
      {{ COPY.site.photo.prefix }}
      <a
        :href="source"
        rel="noopener"
        class="underline underline-offset-2 hover:text-default focus-visible:outline-2 focus-visible:outline-(--focus-ring)"
      >{{ author }}</a>, {{ COPY.site.photo.license }}
    </figcaption>
  </figure>
</template>
