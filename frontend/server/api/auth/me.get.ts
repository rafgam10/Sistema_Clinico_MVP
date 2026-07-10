/* eslint-disable @typescript-eslint/no-explicit-any */
import { getCookie } from 'h3'
import { jwtDecode } from 'jwt-decode'

export default defineEventHandler(async (event) => {
  const token = getCookie(event, 'auth_token')

  if (!token) {
    throw createError({ statusCode: 401, statusMessage: 'Não autorizado' })
  }

  try {
    const jwt = jwtDecode<any>(token)

    const user = {
      id: jwt.id,
      nome: jwt.nome_completo,
      email: jwt.email,
      role: jwt.role as 'medico' | 'recepcao',
      crm: jwt.crm ?? undefined,
      especialidades: jwt.especialidade ? [jwt.especialidade] : [],
      clinicaIds: jwt.role === 'recepcao' ? [1] : [1, 2]
    }

    const clinicas = user.clinicaIds
      .map((id: number) => getClinica(id))
      .filter(Boolean)

    return { user, clinicas }
  } catch {
    throw createError({ statusCode: 401, statusMessage: 'Não autorizado' })
  }
})
