export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  if (!body.nome || !body.tipo) {
    throw createError({ statusCode: 400, statusMessage: 'nome e tipo são obrigatórios' })
  }
  const authToken = getCookie(event, 'auth_token')
  const user = authToken ? getUserByToken(authToken) : null
  const medicoId = user?.id ?? 1
  return criarPadrao({ ...body, medicoId })
})
