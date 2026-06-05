export default defineEventHandler((event) => {
  const id = getRouterParam(event, 'id')
  if (!id) throw createError({ statusCode: 400, statusMessage: 'id é obrigatório' })
  const deleted = deletarPadrao(id)
  if (!deleted) {
    throw createError({ statusCode: 404, statusMessage: 'Padrão não encontrado' })
  }
  return { success: true }
})
