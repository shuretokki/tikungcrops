<script setup lang="ts">
import { LngLatBounds, Map as MapLibreMap, NavigationControl, setWorkerUrl, type GeoJSONSource } from 'maplibre-gl'
// MapLibre 6 finds its worker with new URL(..., import.meta.url) at runtime, which Vite does not see,
// so the ?url import makes Vite emit the file and setWorkerUrl points MapLibre at it
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url'
import type { FeatureCollection } from 'geojson'
import { STAGES, type Cell } from '~/composables/useArea'

const props = defineProps<{
  outer?: FeatureCollection | null
  inner?: FeatureCollection | null
  cells?: Cell[] | null
  labels?: { name: string, lon: number, lat: number }[] | null
  selected?: string | null
}>()
const emit = defineEmits<{ select: [unit: string] }>()
setWorkerUrl(workerUrl)

const container = ref<HTMLDivElement>()
const colorMode = useColorMode()
let map: MapLibreMap | undefined

// OpenFreeMap: free, no key, OpenStreetMap data, attribution comes with the style
const basemap = () => `https://tiles.openfreemap.org/styles/${colorMode.value === 'dark' ? 'dark' : 'positron'}`

// MapLibre paint needs real colors, not CSS variables, so read the tokens at draw time
function token(name: string) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

const EMPTY: FeatureCollection = { type: 'FeatureCollection', features: [] }

function cellsGeojson(cells: Cell[] | null | undefined): FeatureCollection {
  if (!cells) return EMPTY
  return {
    type: 'FeatureCollection',
    features: cells.map(c => ({
      type: 'Feature',
      properties: { unit: c.unit, stage: c.stage ?? 'unknown', paddy: c.paddy_frac },
      geometry: { type: 'Point', coordinates: [c.lon, c.lat] }
    }))
  }
}

function labelsGeojson(labels: typeof props.labels): FeatureCollection {
  if (!labels) return EMPTY
  return {
    type: 'FeatureCollection',
    features: labels.map(l => ({ type: 'Feature', properties: { name: l.name }, geometry: { type: 'Point', coordinates: [l.lon, l.lat] } }))
  }
}

// Sources start empty when their file is still loading, and the watchers below fill them in.
function addLayers() {
  if (!map) return
  const outline = token('--viz-outline')
  map.addSource('outer', { type: 'geojson', data: props.outer ?? EMPTY })
  map.addLayer({ id: 'outer-line', type: 'line', source: 'outer', paint: { 'line-color': outline, 'line-width': 1, 'line-opacity': 0.6 } })
  map.addSource('cells', { type: 'geojson', data: cellsGeojson(props.cells) })
  map.addLayer({
    id: 'cells',
    type: 'circle',
    source: 'cells',
    filter: ['!=', ['get', 'stage'], 'unknown'],
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 11, 1.5, 14, 5],
      'circle-color': ['match', ['get', 'stage'], 'planted', token('--viz-3'), 'peaked', token('--viz-2'), token('--viz-neutral')],
      'circle-opacity': 0.9
    }
  })
  if (props.inner) {
    map.addSource('inner', { type: 'geojson', data: props.inner, promoteId: 'unit' })
    map.addLayer({ id: 'inner-fill', type: 'fill', source: 'inner', paint: { 'fill-color': outline, 'fill-opacity': ['case', ['boolean', ['feature-state', 'hover'], false], 0.12, 0] } })
    map.addLayer({
      id: 'inner-line',
      type: 'line',
      source: 'inner',
      paint: { 'line-color': outline, 'line-width': ['case', ['==', ['get', 'unit'], props.selected ?? ''], 2.5, 1] }
    })
    let hovered: string | number | undefined
    map.on('mousemove', 'inner-fill', (e) => {
      const id = e.features?.[0]?.id
      if (hovered !== undefined) map!.setFeatureState({ source: 'inner', id: hovered }, { hover: false })
      hovered = id
      if (id !== undefined) map!.setFeatureState({ source: 'inner', id }, { hover: true })
      map!.getCanvas().style.cursor = 'pointer'
    })
    map.on('mouseleave', 'inner-fill', () => {
      if (hovered !== undefined) map!.setFeatureState({ source: 'inner', id: hovered }, { hover: false })
      hovered = undefined
      map!.getCanvas().style.cursor = ''
    })
    map.on('click', 'inner-fill', (e) => {
      const unit = e.features?.[0]?.properties?.unit
      if (unit) emit('select', unit)
    })
  }
  // Desa names use the basemap's own font, so no extra glyph source is needed.
  map.addSource('labels', { type: 'geojson', data: labelsGeojson(props.labels) })
  map.addLayer({
    id: 'labels',
    type: 'symbol',
    source: 'labels',
    layout: {
      'text-field': ['get', 'name'],
      'text-font': ['Noto Sans Bold'],
      'text-size': ['interpolate', ['linear'], ['zoom'], 11, 10, 14, 14],
      'text-padding': 2
    },
    paint: {
      'text-color': token('--ui-text-highlighted') || outline,
      'text-halo-color': token('--ui-bg') || '#fff',
      'text-halo-width': 1.5
    }
  })
}

function fit() {
  const fc = props.inner ?? props.outer
  if (!map || !fc) return
  const b = new LngLatBounds()
  for (const f of fc.features) {
    const g = f.geometry
    const polys = g.type === 'MultiPolygon' ? g.coordinates : g.type === 'Polygon' ? [g.coordinates] : []
    for (const p of polys) for (const [x, y] of p[0]!) b.extend([x!, y!])
  }
  if (!b.isEmpty()) map.fitBounds(b, { padding: 24, duration: 0 })
}

onMounted(async () => {
  // a .client component swaps its placeholder for the real template only after mount,
  // so the container element exists one tick later
  await nextTick()
  if (!container.value) return
  map = new MapLibreMap({ container: container.value, style: basemap(), attributionControl: { compact: true } })
  map.addControl(new NavigationControl({ showCompass: false }), 'top-right')
  // sources and layers go in after the style loads, and again after every style change
  map.on('style.load', () => {
    addLayers()
    fit()
  })
})

watch(() => colorMode.value, () => map?.setStyle(basemap()))
watch(() => props.cells, cells => (map?.getSource('cells') as GeoJSONSource | undefined)?.setData(cellsGeojson(cells)))
watch(() => props.outer, outer => (map?.getSource('outer') as GeoJSONSource | undefined)?.setData(outer ?? EMPTY))
watch(() => props.labels, labels => (map?.getSource('labels') as GeoJSONSource | undefined)?.setData(labelsGeojson(labels)))
watch(() => props.selected, (unit) => {
  if (map?.getLayer('inner-line')) map.setPaintProperty('inner-line', 'line-width', ['case', ['==', ['get', 'unit'], unit ?? ''], 2.5, 1])
})
onBeforeUnmount(() => map?.remove())

const legend = Object.entries(STAGES).filter(([k]) => k !== 'unknown')
</script>

<template>
  <div class="relative h-full min-h-80 w-full overflow-hidden rounded-md ring ring-default">
    <div
      ref="container"
      class="h-full w-full"
      role="region"
      aria-label="Peta sel sawah dan batas wilayah"
    />
    <ul class="absolute bottom-2 left-2 flex flex-col gap-1 rounded-lg bg-muted px-2 py-1.5 text-xs shadow-(--shadow-elev)">
      <li
        v-for="[key, s] in legend"
        :key="key"
        class="flex items-center gap-1.5"
      >
        <span
          class="size-2.5 rounded-full"
          :style="{ background: s.color }"
        />
        <span>{{ s.label }}</span>
      </li>
    </ul>
  </div>
</template>
