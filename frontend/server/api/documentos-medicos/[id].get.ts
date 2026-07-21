export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')

  return await flaskFetch(event, `/documentos-medicos/${id}`)
})
