export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const body = await readBody(event)
  return flaskFetch(event, `/chamadas/${id}`, { method: 'PATCH', body })
})
