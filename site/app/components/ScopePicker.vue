<script setup lang="ts">
type Option = { value: string, label: string, ready: boolean }

const t = COPY.scope
const region = ref('tikung')
const crop = ref('padi')

// A choice that is not finished stays visible but cannot be picked.
const toItems = (list: Option[]) => list.map(o => ({ label: o.ready ? o.label : `${o.label} (${t.soon})`, value: o.value, disabled: !o.ready }))
</script>

<template>
  <div class="flex flex-col gap-4 rounded-[18px] bg-muted p-5 sm:p-6">
    <p class="font-semibold">
      {{ t.title }}
    </p>
    <div class="grid gap-4 sm:grid-cols-2">
      <UFormField :label="t.region">
        <USelect
          v-model="region"
          :items="toItems(t.regions)"
          size="lg"
          class="w-full"
        />
      </UFormField>
      <UFormField :label="t.crop">
        <USelect
          v-model="crop"
          :items="toItems(t.crops)"
          size="lg"
          class="w-full"
        />
      </UFormField>
    </div>
    <div class="flex flex-wrap items-center gap-3">
      <UButton
        :label="t.go"
        to="/kalender"
        trailing-icon="i-lucide-arrow-right"
        size="lg"
      />
      <UButton
        :label="COPY.site.search"
        to="#desa"
        icon="i-lucide-search"
        variant="outline"
        size="lg"
      />
    </div>
    <p class="text-sm text-muted">
      {{ t.note }}
    </p>
  </div>
</template>
