export default defineEventHandler((event) => {
  const query = getQuery(event)
  const search = query.search ? String(query.search) : ''
  const params = search ? `?search=${encodeURIComponent(search)}` : ''
  return flaskFetch(event, `/pacientes${params}`)
})
