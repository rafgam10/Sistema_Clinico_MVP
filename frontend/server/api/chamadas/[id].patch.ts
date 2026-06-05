export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  const body = await readBody<{ status: string }>(event)

  if (body.status !== 'concluido' && body.status !== 'cancelado') {
    throw createError({ statusCode: 400, statusMessage: 'Status inválido' })
  }

  const chamado = concluirChamado(id)
  if (!chamado) {
    throw createError({ statusCode: 404, statusMessage: 'Chamado não encontrado' })
  }

  return chamado
})
