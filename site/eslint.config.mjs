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
      'better-tailwindcss/no-unknown-classes': ['error', { ignore: ['^vis-chart$', '^tile(-parchment|-slim|-box)?$'] }]
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
  }
)
