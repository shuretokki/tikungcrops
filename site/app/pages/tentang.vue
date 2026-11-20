<script setup lang="ts">
const t = COPY.tentang

definePageMeta({ layout: 'tiles' })
useSeoMeta({ title: t.seoTitle, description: t.purpose[0] })
</script>

<template>
  <div>
    <section class="tile flex flex-col gap-10">
      <header class="flex max-w-3xl flex-col gap-4">
        <p class="text-sm font-semibold text-(--ui-primary)">
          {{ t.eyebrow }}
        </p>
        <h1 class="text-4xl/[1.07] font-semibold text-balance sm:text-5xl/[1.07] lg:text-[3.5rem]/[1.07]">
          {{ t.title }}
        </h1>
        <p
          v-for="p in t.purpose"
          :key="p"
          class="text-lg text-muted"
        >
          {{ p }}
        </p>
      </header>
      <div class="flex flex-col gap-4">
        <h2 class="text-xl font-semibold">
          {{ t.helps.title }}
        </h2>
        <ul class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <li
            v-for="h in t.helps.items"
            :key="h.title"
            class="flex flex-col gap-2 rounded-[18px] bg-muted p-5"
          >
            <UIcon
              :name="h.icon"
              class="size-6 text-(--ui-primary)"
            />
            <p class="font-semibold">
              {{ h.title }}
            </p>
            <p class="text-sm text-muted">
              {{ h.body }}
            </p>
          </li>
        </ul>
      </div>
    </section>

    <section class="tile tile-parchment grid items-start gap-10 lg:grid-cols-2">
      <div class="tile-box flex flex-col gap-6">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.how.title }}
        </h2>
        <ol class="flex flex-col gap-4">
          <li
            v-for="(s, i) in t.how.steps"
            :key="s"
            class="grid grid-cols-[2.5rem_1fr] items-start gap-4"
          >
            <span class="flex size-10 items-center justify-center rounded-full bg-(--ui-primary) font-semibold text-(--ui-on-primary) tabular-nums">{{ i + 1 }}</span>
            <span class="pt-2">{{ s }}</span>
          </li>
        </ol>
        <UButton
          :label="t.faqLink"
          to="/faq"
          trailing-icon="i-lucide-arrow-right"
          variant="outline"
          class="self-start"
        />
      </div>
      <div class="tile-box flex flex-col gap-6">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.coverage.title }}
        </h2>
        <ul class="flex flex-col divide-y divide-default">
          <li
            v-for="r in t.coverage.rows"
            :key="r.item"
            class="flex flex-col gap-1 py-4 first:pt-0 last:pb-0"
          >
            <div class="flex flex-wrap items-center justify-between gap-2">
              <span class="font-semibold">{{ r.item }}</span>
              <UBadge
                :label="r.ready ? t.coverage.ready : t.coverage.planned"
                :color="r.ready ? 'success' : 'neutral'"
                variant="subtle"
              />
            </div>
            <span class="text-sm text-muted">{{ r.note }}</span>
          </li>
        </ul>
      </div>
    </section>

    <section
      id="sumber"
      class="tile flex scroll-mt-20 flex-col gap-10"
    >
      <header class="flex max-w-3xl flex-col gap-3">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.sources.title }}
        </h2>
      </header>
      <ul class="grid gap-4 sm:grid-cols-2">
        <li
          v-for="s in t.sources.items"
          :key="s.name"
        >
          <a
            :href="s.href"
            rel="noopener"
            class="flex h-full items-center justify-between gap-3 rounded-[18px] bg-muted p-5 font-semibold transition hover:ring-2 hover:ring-(--ui-primary) focus-visible:outline-2 focus-visible:outline-(--focus-ring)"
          >
            {{ s.name }}
            <UIcon
              name="i-lucide-arrow-up-right"
              class="size-4 shrink-0 text-muted"
            />
          </a>
        </li>
      </ul>
    </section>

    <section
      id="catatan"
      class="tile tile-parchment flex scroll-mt-20 flex-col gap-10"
    >
      <header class="flex max-w-3xl flex-col gap-3">
        <h2 class="text-3xl/[1.15] font-semibold text-balance sm:text-[2.5rem]/[1.1]">
          {{ t.notes.title }}
        </h2>
        <p class="text-muted">
          {{ t.notes.body }}
        </p>
      </header>
      <div class="tile-box flex flex-col gap-4">
        <UAlert
          v-for="item in t.notes.items"
          :key="item"
          color="warning"
          variant="subtle"
          icon="i-lucide-circle-alert"
          :description="item"
        />
      </div>
    </section>
  </div>
</template>
