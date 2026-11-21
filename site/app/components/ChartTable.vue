<script setup lang="ts">
defineProps<{
  caption: string
  columns: string[]
  rows: (string | number)[][]
}>()
</script>

<template>
  <UModal
    :title="caption"
    :ui="{ content: 'max-w-3xl' }"
  >
    <UButton
      :label="COPY.landing.tableToggle"
      icon="i-lucide-table"
      color="neutral"
      variant="link"
      size="xs"
      class="self-start px-0"
    />
    <template #body>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs tabular-nums sm:text-sm">
          <caption class="sr-only">
            {{ caption }}
          </caption>
          <thead class="text-xs text-muted">
            <tr>
              <th
                v-for="c in columns"
                :key="c"
                scope="col"
                class="py-1 pr-3 font-normal sm:pr-4"
              >
                {{ c }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(r, i) in rows"
              :key="i"
              class="border-t border-default"
            >
              <td
                v-for="(v, j) in r"
                :key="j"
                class="py-1 pr-3 sm:pr-4"
              >
                {{ v }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </UModal>
</template>
