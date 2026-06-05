import { getCookie } from 'h3'

export default defineEventHandler(async (event) => {
  const token = getCookie(event, 'auth_token')

  if (!token) {
    throw createError({ statusCode: 401, statusMessage: 'Não autorizado' })
  }

  const user = getUserByToken(token)
  if (!user) {
    throw createError({ statusCode: 401, statusMessage: 'Não autorizado' })
  }

  const clinicas = user.clinicaIds.map(id => getClinica(id)).filter(Boolean)

  return { user, clinicas }
})
