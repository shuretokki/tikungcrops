<script setup lang="ts">
const t = COPY.scope
const { crop } = useScope()
</script>

<template>
  <div
    id="pilih"
    class="flex scroll-mt-24 flex-col gap-6 text-left"
  >
    <div class="flex flex-wrap items-end justify-between gap-x-6 gap-y-4">
      <div class="flex flex-col gap-1">
        <p
          id="scope-crop"
          class="text-xl font-semibold"
        >
          {{ t.title }}
        </p>
        <p class="text-sm text-muted">
          {{ t.place }}
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <UButton
          :label="COPY.site.search"
          to="#desa"
          icon="i-lucide-search"
          variant="outline"
          size="lg"
        />
        <UButton
          :label="t.go"
          to="/kalender"
          trailing-icon="i-lucide-arrow-right"
          size="lg"
        />
      </div>
    </div>
    <div
      role="radiogroup"
      aria-labelledby="scope-crop"
      class="grid grid-cols-2 gap-3 sm:grid-cols-5"
    >
      <button
        v-for="o in t.crops"
        :key="o.value"
        type="button"
        role="radio"
        :aria-checked="crop === o.value"
        :disabled="!o.ready"
        class="group relative isolate flex aspect-[4/5] flex-col justify-end overflow-hidden rounded-[18px] p-4 text-left text-white outline-offset-2 transition focus-visible:outline-2 focus-visible:outline-(--ui-primary) disabled:cursor-not-allowed"
        :class="crop === o.value ? 'ring-4 ring-(--ui-primary)' : ''"
        @click="crop = o.value"
      >
        <img
          :src="o.image"
          alt=""
          width="320"
          height="400"
          loading="lazy"
          class="absolute inset-0 -z-20 size-full object-cover transition duration-300 group-enabled:group-hover:scale-105"
          :class="o.ready ? '' : 'grayscale'"
        >
        <span
          class="absolute inset-0 -z-10 bg-linear-to-t from-black/85 via-black/35 to-black/5"
          aria-hidden="true"
        />
        <UIcon
          v-if="crop === o.value"
          name="i-lucide-circle-check"
          class="absolute top-3 right-3 size-6 text-white"
        />
        <span class="text-lg font-semibold">{{ o.label }}</span>
        <span class="min-h-5 text-xs text-white/80">{{ o.ready ? '' : t.soon }}</span>
      </button>
    </div>
  </div>
</template>
