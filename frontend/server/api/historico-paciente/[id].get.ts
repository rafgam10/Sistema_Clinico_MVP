function normalizarCpf(valor: unknown): string | undefined {
  const texto = String(valor || '').trim()
  const semDecimal = texto.endsWith('.0') && texto.slice(0, -2).replace(/\D/g, '').length === 11
    ? texto.slice(0, -2)
    : texto
  const cpf = semDecimal.replace(/\D/g, '')

  if (cpf.length !== 11) return undefined
  if (new Set(cpf).size === 1) return undefined

  return cpf
}

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const query = getQuery(event)
  const params = new URLSearchParams()
  const cpf = normalizarCpf(query.cpf)

  if (cpf) params.set('cpf', cpf)
  if (query.nome) params.set('nome', String(query.nome))

  const qs = params.toString()
  return await flaskFetch(event, `/prontuario/historico-paciente/${id}${qs ? `?${qs}` : ''}`)
})
