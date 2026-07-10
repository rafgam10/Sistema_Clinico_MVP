interface ServerClinica {
  id: number
  nome: string
  endereco: string
  telefone: string
}

const clinicas: ServerClinica[] = [
  { id: 1, nome: 'Clínica Centro', endereco: 'Rua Augusta, 1500 - Centro, São Paulo - SP', telefone: '(11) 3000-0001' },
  { id: 2, nome: 'Clínica Norte', endereco: 'Av. Paulista, 2000 - Bela Vista, São Paulo - SP', telefone: '(11) 3000-0002' }
]

export function getClinicas() {
  return clinicas
}

export function getClinica(id: number) {
  return clinicas.find(c => c.id === id) ?? null
}
