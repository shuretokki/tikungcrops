// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// https://nuxt.com/docs/api/configuration/nuxt-config
import { fileURLToPath } from 'node:url'

export default defineNuxtConfig({
  modules: [
    '@nuxt/eslint',
    '@nuxt/ui',
    '@nuxt/image',
    '@nuxtjs/sitemap',
    '@nuxtjs/robots',
    'nuxt-schema-org',
    'nuxt-seo-utils'
  ],

  devtools: {
    enabled: true
  },

  app: {
    head: {
      htmlAttrs: { lang: 'id' },
      title: 'Pemantauan Tanam Padi Lamongan',
      // Each page title already ends with the site name, so the SEO module must not add it again.
      // To undo, remove this line.
      titleTemplate: '%s',
      meta: [
        {
          name: 'description',
          content: 'Musim tanam, intensitas tanam, dan perkiraan panen padi per desa dari citra satelit Sentinel-1 dan Sentinel-2.'
        },
        { property: 'og:image', content: '/og.png' },
        { property: 'og:image:width', content: '1200' },
        { property: 'og:image:height', content: '630' },
        { name: 'twitter:card', content: 'summary_large_image' }
      ],
      link: [
        { rel: 'icon', href: '/favicon.ico', sizes: '48x48' },
        { rel: 'icon', type: 'image/png', href: '/icon-192.png', sizes: '192x192' },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' }
      ]
    }
  },

  css: ['~/assets/css/main.css', '~/assets/css/viz.css', 'maplibre-gl/dist/maplibre-gl.css'],

  // The SEO modules build absolute links, the sitemap and the share data from this address.
  // It is the Workers address for now. Change the url when the site gets a custom domain.
  site: {
    url: 'https://tikungcrops.tri-r-utomo.workers.dev',
    name: 'tikungcrops',
    description: 'Kalender tanam padi per desa di Kecamatan Tikung, dari citra satelit.',
    defaultLocale: 'id'
  },

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
  icon: { mode: 'svg' },

  image: {
    format: ['webp'],
    quality: 75
  }
})
