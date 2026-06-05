import { getCookie } from 'h3'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  const { email, password } = body

  // Credenciais de teste
  const validCredentials: Record<string, string> = {
    'admin@adm.com': '123123123',
    'maria@adm.com': '123123123',
    'carlos@adm.com': '123123123',
    'recepcao@adm.com': '123123123'
  }

  const expectedPassword = validCredentials[email as string]
  if (!expectedPassword || password !== expectedPassword) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Credenciais inválidas'
    })
  }

  const user = getUserByEmail(email as string)
  if (!user) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Usuário não encontrado'
    })
  }

  const token = `fake-jwt-token-${user.id}-${Math.random().toString(36).substring(7)}`

  const clinicas = user.clinicaIds.map(id => getClinica(id)).filter(Boolean)

  return { token, user, clinicas }
})
