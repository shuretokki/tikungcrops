// Serves one exported JSON file from data/web while pages prerender.
// Nitro does not serve public/ files to $fetch during prerender, server assets it does.
export default defineEventHandler(async (event) => {
  const { slug, file } = getRouterParams(event)
  // only names the exporter writes, so the route cannot read anything else
  if (!slug || !file || !/^[a-z0-9-]+$/.test(slug) || !/^[a-z_]+\.(json|geojson)$/.test(file)) {
    throw createError({ statusCode: 400, statusMessage: 'Bad area or file name' })
  }
  const raw = await useStorage('assets:areas').getItemRaw(`${slug}:${file}`)
  if (!raw) throw createError({ statusCode: 404, statusMessage: `${slug}/${file} not exported` })
  return JSON.parse(raw.toString())
})
