/* eslint-disable @typescript-eslint/no-explicit-any */
import { jwtDecode } from 'jwt-decode'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { email, password } = body
  const config = useRuntimeConfig()

  let res: any
  try {
    res = await $fetch(`${config.flaskBaseUrl}/login/auth`, {
      method: 'POST',
      body: { email, senha: password }
    })
  } catch (error) {
    if (String(config.enableMockAuth) !== 'true') {
      throw createError({
        statusCode: 502,
        statusMessage: 'Falha ao conectar com o backend Flask',
        data: String(error)
      })
    }

    // Fallback: mock credentials (Flask offline)
    const validCredentials: Record<string, string> = {
      'admin@adm.com': '123123123',
      'maria@adm.com': '123123123',
      'carlos@adm.com': '123123123',
      'recepcao@adm.com': '123123123'
    }

    if (validCredentials[email as string] !== password) {
      throw createError({ statusCode: 401, statusMessage: 'Credenciais inválidas' })
    }

    const mockUser = getUserByEmail(email as string)
    if (!mockUser) {
      throw createError({ statusCode: 401, statusMessage: 'Usuário não encontrado' })
    }

    const fakeToken = `fake-jwt-token-${mockUser.id}-${Math.random().toString(36).substring(7)}`
    const clinicas = mockUser.clinicaIds.map((id: number) => getClinica(id)).filter(Boolean)

    return { token: fakeToken, user: mockUser, clinicas }
  }

  // Fluxo normal: Flask respondeu
  if (!res.access_token) {
    throw createError({ statusCode: 401, statusMessage: 'Credenciais inválidas' })
  }

  const jwt = jwtDecode<any>(res.access_token)

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

  return { token: res.access_token, user, clinicas }
})
