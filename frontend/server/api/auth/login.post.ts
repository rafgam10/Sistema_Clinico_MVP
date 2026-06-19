/* eslint-disable @typescript-eslint/no-explicit-any */
import { jwtDecode } from 'jwt-decode'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { email, password } = body

  const res: any = await $fetch('http://localhost:5000/login/auth', {
    method: 'POST',
    body: { email, senha: password }
  }).catch(() => {
    throw createError({ statusCode: 502, statusMessage: 'Falha ao conectar com o servidor' })
  })

  if (!res.access_token) {
    throw createError({ statusCode: 401, statusMessage: 'Credenciais inválidas' })
  }

  const jwt = jwtDecode<any>(res.access_token)

  const user = {
    id: jwt.id,
    nome: jwt.nome_completo,
    email: jwt.email,
    role: jwt.role as 'medico' | 'recepcao',
    especialidades: [] as string[],
    clinicaIds: jwt.role === 'recepcao' ? [1] : [1, 2]
  }

  const clinicas = user.clinicaIds
    .map((id: number) => getClinica(id))
    .filter(Boolean)

  return { token: res.access_token, user, clinicas }
})
