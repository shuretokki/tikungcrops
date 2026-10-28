<script setup lang="ts">
defineProps<{
  caption: string
  columns: string[]
  rows: (string | number)[][]
}>()
</script>

<template>
  <details class="text-sm">
    <summary class="cursor-pointer text-muted hover:text-default">
      {{ COPY.common.tableToggle }}
    </summary>
    <table class="mt-2 w-full text-left tabular-nums">
      <caption class="sr-only">
        {{ caption }}
      </caption>
      <thead class="text-xs text-muted">
        <tr>
          <th
            v-for="c in columns"
            :key="c"
            scope="col"
            class="py-1 pr-4 font-normal"
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
            class="py-1 pr-4"
          >
            {{ v }}
          </td>
        </tr>
      </tbody>
    </table>
  </details>
</template>
