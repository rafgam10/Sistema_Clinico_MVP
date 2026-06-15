interface AuthUser {
  id: number
  nome: string
  email: string
  role: 'medico' | 'recepcao'
  especialidades?: string[]
  clinicaIds: number[]
}

const users: AuthUser[] = [
  { id: 1, nome: 'Dr. João Medeiros', email: 'admin@adm.com', role: 'medico', especialidades: ['Cardiologia'], clinicaIds: [1] },
  { id: 2, nome: 'Dra. Maria Santos', email: 'maria@adm.com', role: 'medico', especialidades: ['Dermatologia'], clinicaIds: [2] },
  { id: 3, nome: 'Dr. Carlos Oliveira', email: 'carlos@adm.com', role: 'medico', especialidades: ['Ortopedia'], clinicaIds: [1, 2] },
  { id: 4, nome: 'Ana Paula Costa', email: 'recepcao@adm.com', role: 'recepcao', clinicaIds: [1] }
]

export function getUserByEmail(email: string) {
  return users.find(u => u.email === email) ?? null
}

export function getUserByToken(token: string) {
  if (!token.startsWith('fake-jwt-token-')) return null
  const parts = token.split('-')
  const userId = Number(parts[3])
  return users.find(u => u.id === userId) ?? null
}

export function getUserById(id: number) {
  return users.find(u => u.id === id) ?? null
}

export function getMedicos(clinicaId?: number) {
  const medicos = users.filter(u => u.role === 'medico')
  if (clinicaId) return medicos.filter(m => m.clinicaIds.includes(clinicaId))
  return medicos
}
