// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

import { fileURLToPath } from 'node:url'

export default defineNuxtConfig({
  modules: ['@nuxt/ui'],
  css: ['~/assets/css/main.css', '~/assets/css/viz.css', 'maplibre-gl/dist/maplibre-gl.css'],
  ui: {
    // the design has no "secondary" color, a short list stops it showing a stock Tailwind blue
    theme: { colors: ['primary', 'info', 'success', 'warning', 'error'] }
  },
  // inline SVG icons let CSS set the stroke width
  icon: { mode: 'svg' },
  // the design is dark first
  colorMode: { preference: 'dark', fallback: 'dark' },
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
  // every page is prerendered from the JSON in public/data, so the site needs no server
  nitro: {
    prerender: { crawlLinks: true, routes: ['/'] },
    serverAssets: [{ baseName: 'areas', dir: fileURLToPath(new URL('../data/web', import.meta.url)) }]
  },
  compatibilityDate: '2026-10-01'
})
