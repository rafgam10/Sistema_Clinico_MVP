export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id) throw createError({ statusCode: 400, statusMessage: 'id é obrigatório' })
  const body = await readBody(event)
  const padrao = atualizarPadrao(id, body)
  if (!padrao) {
    throw createError({ statusCode: 404, statusMessage: 'Padrão não encontrado' })
  }
  return padrao
})
