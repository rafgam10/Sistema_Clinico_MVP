// Proxy para o endpoint do backend que retorna histórico do banco local
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  return await flaskFetch(event, `/prontuario/historico-local/${id}`)
})
