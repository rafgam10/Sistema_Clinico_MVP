// Proxy para o endpoint do backend que retorna histórico do banco local
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const query = getQuery(event)
  const params = new URLSearchParams()

  if (query.cpf) params.set('cpf', String(query.cpf))
  if (query.nome) params.set('nome', String(query.nome))
  if (query.spdataAtendimentoId) params.set('spdataAtendimentoId', String(query.spdataAtendimentoId))
  if (query.data) params.set('data', String(query.data))

  const qs = params.toString()
  return await flaskFetch(event, `/prontuario/historico-local/${id}${qs ? `?${qs}` : ''}`)
})
