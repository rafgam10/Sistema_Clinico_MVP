export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const ids = query.ids ? String(query.ids) : ''
  const params = new URLSearchParams()

  if (ids) params.set('ids', ids)

  return await flaskFetch(event, `/documentos-medicos${params.toString() ? `?${params.toString()}` : ''}`)
})
