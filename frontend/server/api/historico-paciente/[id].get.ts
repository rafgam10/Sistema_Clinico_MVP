export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  return await flaskFetch(event, `/prontuario/historico-paciente/${id}`)
})
