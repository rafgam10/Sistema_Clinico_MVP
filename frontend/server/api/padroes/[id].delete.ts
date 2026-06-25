export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id) throw createError({ statusCode: 400, statusMessage: 'id é obrigatório' })

  const query = getQuery(event)
  const tipo = query.tipo === 'exame' ? 'exame' : 'receita'

  if (tipo === 'exame') {
    await flaskFetch(event, `/padrao_medico_exame/deletar/${id}`, { method: 'DELETE' })
  } else {
    await flaskFetch(event, `/padrao_medico_receita/deletar/${id}`, { method: 'DELETE' })
  }

  return { success: true }
})
