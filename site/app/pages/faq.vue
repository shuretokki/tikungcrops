<script setup lang="ts">
const t = COPY.faq

// Questions are numbered Q01, Q02 and so on, as on the FAQ page of ASEAN AFSIS.
const items = t.items.map((it, i) => ({
  label: `Q${String(i + 1).padStart(2, '0')}. ${it.q}`,
  value: String(i),
  paragraphs: it.a
}))

definePageMeta({ layout: 'tiles' })
useSeoMeta({ title: t.seoTitle, description: t.description })
</script>

<template>
  <div>
    <section class="tile flex flex-col gap-10">
      <header class="flex max-w-3xl flex-col gap-4">
        <h1 class="text-4xl/[1.07] font-semibold text-balance sm:text-5xl/[1.07] lg:text-[3.5rem]/[1.07]">
          {{ t.title }}
        </h1>
        <p class="text-lg text-muted">
          {{ t.description }}
        </p>
      </header>
      <UAccordion
        :items="items"
        type="multiple"
        class="max-w-3xl"
      >
        <template #body="{ item }">
          <div class="flex flex-col gap-3 pb-2 text-muted">
            <p
              v-for="p in item.paragraphs"
              :key="p"
            >
              {{ p }}
            </p>
          </div>
        </template>
      </UAccordion>
    </section>
  </div>
</template>
