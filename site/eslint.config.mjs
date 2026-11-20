// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'
import betterTailwindcss from 'eslint-plugin-better-tailwindcss'
import { getDefaultAttributes } from 'eslint-plugin-better-tailwindcss/api/defaults'
import vuejsAccessibility from 'eslint-plugin-vuejs-accessibility'

export default withNuxt(
  betterTailwindcss.configs['correctness-error'],
  ...vuejsAccessibility.configs['flat/recommended'],
  {
    rules: {
      'better-tailwindcss/no-unknown-classes': ['error', { ignore: ['^vis-chart$', '^tile(-parchment|-slim|-box)?$', '^font-brand$'] }]
    },
    settings: {
      'better-tailwindcss': {
        entryPoint: 'app/assets/css/main.css',
        attributes: [
          ...getDefaultAttributes(),
          ['^v-bind:ui$', [{ match: 'objectValues' }]]
        ]
      }
    }
  },
  {
    // The map regions are focusable and labelled, and their hover and focus handlers only show a readout line.
    // The ranking list on the same page is the full keyboard path.
    // To undo, delete this block and give each region a real link.
    files: ['app/components/OutlineMap.vue'],
    rules: { 'vuejs-accessibility/no-static-element-interactions': 'off' }
  }
)
