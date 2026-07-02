export interface MedicamentoUso {
  nome: string
  dosagem: string
  frequencia: string
}

export interface HistoricoItem {
  data: string
  descricao: string
  diagnostico?: string
  medicamentos?: string
  exames?: string
}

export interface Paciente {
  id: number
  nome: string
  encaixado: boolean
  sexo: 'masculino' | 'feminino'
  dataNascimento: string
  tipoSanguineo: string
  alergias: string[]
  medicamentosEmUso: MedicamentoUso[]
  convenio: string
  telefone: string
  email: string
  cpf: string
  endereco: string
  contatoEmergencia?: { nome: string, telefone: string, parentesco: string }
  responsavel?: { nome: string, telefone: string, parentesco: string }
  ultimaConsulta?: string
  historicoRecente: HistoricoItem[]
}

export interface Clinica {
  id: number
  nome: string
  endereco: string
  telefone: string
}

export type AgendamentoStatus = 'agendado' | 'em-espera' | 'em-atendimento' | 'atendido' | 'faltou' | 'cancelado'

export interface Agendamento {
  id: number
  pacienteId: number
  medicoId: number
  clinicaId: number
  data: string
  horario: string
  prioridade: 'normal' | 'preferencial'
  status: AgendamentoStatus
  descricao: string
  criadoEm: string
  duracao?: number
}

export interface AgendamentoComPaciente extends Agendamento {
  paciente: Paciente
}

export type AgendaStatus = 'em-espera' | 'aguardando' | 'atendido' | 'falta' | 'presente'

export interface AgendaSlot {
  time: string
  type: 'appointment' | 'available' | 'lunch'
  patient?: {
    id: number
    name: string
    status: AgendaStatus
    description: string
    agendamentoId?: number
    statusOriginal?: string
  }
}

export interface AuthUser {
  id: number
  nome: string
  email: string
  role: 'medico' | 'recepcao'
  especialidades?: string[]
  clinicaIds: number[]
}

export interface Chamado {
  id: number
  pacienteId: number
  pacienteNome: string
  dataChamada: string
  status: 'chamando' | 'concluido' | 'cancelado'
  localAtendimento: string
  medicoResponsavel: string
}

export interface HistoricoRecord {
  CID_PRINCIPAL: string
  DATA_CONSULTA: string
  DIAGNOSTICO_PRINCIPAL: string
  ID_ATENDIMENTO: string
  ID_EVOLUCAO: string | null
  ID_SOLICITACAO_EXAME: string | null
  ID_PACIENTE: number
  MEDICO: string | null
  OBS_ATENDIMENTO: string | null
  PACIENTE: string
}

export interface HistoricoLocalRecord {
  spdata_atendimento_id: number | null
  data_consulta: string | null
  anamnese: string | null
  cid_principal: string | null
  cid_principal_descricao: string | null
  cids_secundarios: { codigo: string, descricao: string | null }[]
  medicamentos: string[]
  exames: string[]
}

export interface Atendimento {
  id: number
  pacienteId: number
  dataInicio: string
  dataFim?: string
  observacoes?: string
}

export interface ItemMedicamento {
  nome: string
  dosagem: string
  detalhes: string
}

export interface PadraoReceita {
  id: string
  medicoId: number
  nome: string
  tipo: 'receita'
  medicamentos: ItemMedicamento[]
  createdAt: string
  updatedAt: string
}

export interface PadraoExame {
  id: string
  medicoId: number
  nome: string
  tipo: 'exame'
  exames: string[]
  createdAt: string
  updatedAt: string
}

export type Padrao = PadraoReceita | PadraoExame
