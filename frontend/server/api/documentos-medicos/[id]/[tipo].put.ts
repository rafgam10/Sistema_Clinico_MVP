export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const tipo = getRouterParam(event, 'tipo')
  const body = await readBody(event)

  return await flaskFetch(event, `/documentos-medicos/${id}/${tipo}`, {
    method: 'PUT',
    body
  })
})
