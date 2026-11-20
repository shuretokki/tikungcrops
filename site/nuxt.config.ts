// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// https://nuxt.com/docs/api/configuration/nuxt-config
import { fileURLToPath } from 'node:url'

export default defineNuxtConfig({
  modules: [
    '@nuxt/eslint',
    '@nuxt/ui'
  ],

  devtools: {
    enabled: true
  },

  app: {
    head: {
      htmlAttrs: { lang: 'id' },
      title: 'Pemantauan Tanam Padi Lamongan',
      meta: [
        {
          name: 'description',
          content: 'Musim tanam, intensitas tanam, dan perkiraan panen padi per desa dari citra satelit Sentinel-1 dan Sentinel-2.'
        }
      ]
    }
  },

  css: ['~/assets/css/main.css', '~/assets/css/viz.css', 'maplibre-gl/dist/maplibre-gl.css'],

  // Light is the default on every device, so the system theme is not followed.
  // To undo, set preference to 'system'.
  colorMode: { preference: 'light', fallback: 'light' },

  ui: {
    // the design has no "secondary" color, a short list stops it showing a stock Tailwind blue
    theme: { colors: ['primary', 'info', 'success', 'warning', 'error'] }
  },

  compatibilityDate: '2026-06-30',

  nitro: {
    // every page is prerendered, so the site needs no server
    prerender: { crawlLinks: true, routes: ['/'] },
    // pages read the exported JSON from data/web through server/api while they prerender
    serverAssets: [{ baseName: 'areas', dir: fileURLToPath(new URL('../data/web', import.meta.url)) }]
  },

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  },

  // inline SVG icons let CSS set the stroke width
  icon: { mode: 'svg' }
})
