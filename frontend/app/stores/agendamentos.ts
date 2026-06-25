import { defineStore } from 'pinia'
import type { Agendamento, AgendamentoComPaciente, AgendamentoStatus, Paciente } from '~/types'

export const useAgendamentosStore = defineStore('agendamentos', () => {
  const agendamentos = ref<AgendamentoComPaciente[]>([])
  const loading = ref(true)
  let sse: ReturnType<typeof useSse> | null = null

  const emAtendimento = computed(() =>
    agendamentos.value.find(a => a.status === 'em-atendimento') ?? null
  )

  const fila = computed(() =>
    agendamentos.value.filter(a => a.status === 'agendado' || a.status === 'em-espera')
  )

  const totalAgendamentos = computed(() => agendamentos.value.length)
  const totalAtendidos = computed(() => agendamentos.value.filter(a => a.status === 'atendido').length)
  const totalFaltas = computed(() => agendamentos.value.filter(a => a.status === 'faltou').length)

  const ordemStatus: Record<string, number> = {
    'agendado': 0,
    'em-espera': 1,
    'em-atendimento': 2,
    'atendido': 3,
    'faltou': 4
  }

  const ordenados = computed(() =>
    [...agendamentos.value].sort((a, b) => {
      const statusDiff = (ordemStatus[a.status] ?? 99) - (ordemStatus[b.status] ?? 99)
      if (statusDiff !== 0) return statusDiff
      return a.horario.localeCompare(b.horario)
    })
  )

  async function fetchAgendamentos(clinicaId?: number, data?: string, medicoId?: number) {
    try {
      const params = new URLSearchParams()
      if (clinicaId) params.set('clinicaId', String(clinicaId))
      if (data) params.set('data', data)
      if (medicoId) params.set('medicoId', String(medicoId))
      const qs = params.toString()

      const raw = await $fetch<(Agendamento | AgendamentoComPaciente)[]>(`/api/agendamentos${qs ? `?${qs}` : ''}`)

      if (raw.every(a => 'paciente' in a)) {
        agendamentos.value = raw as AgendamentoComPaciente[]
        return
      }

      const allPacientes = await $fetch<Paciente[]>('/api/pacientes')
      const pacienteMap = new Map(allPacientes.map(p => [p.id, p]))

      agendamentos.value = (raw as Agendamento[])
        .filter(a => pacienteMap.has(a.pacienteId))
        .map(a => ({
          ...a,
          paciente: pacienteMap.get(a.pacienteId)!
        }))
    } catch {
      console.error('Erro ao carregar agendamentos')
    } finally {
      loading.value = false
    }
  }

  async function init(clinicaId?: number, data?: string, medicoId?: number) {
    sse = useSse()
    sse.on('agendamento:status', (data: unknown) => {
      const ev = data as { id: number, status: AgendamentoStatus, pacienteId: number }
      const a = agendamentos.value.find(ag => ag.id === ev.id)
      if (a) a.status = ev.status
    })
    sse.connect()
    await fetchAgendamentos(clinicaId, data, medicoId)
  }

  async function atualizarStatus(id: number, status: AgendamentoStatus, consulta?: { anamnese?: string, diagnostico?: string, medicamentos?: string, exames?: string, duracao?: number }) {
    try {
      await $fetch(`/api/agendamentos/${id}`, {
        method: 'PATCH',
        body: { status, consulta }
      })
      const ag = agendamentos.value.find(a => a.id === id)
      if (ag) ag.status = status
    } catch {
      console.error('Erro ao atualizar status do agendamento')
    }
  }

  return {
    agendamentos,
    loading,
    emAtendimento,
    fila,
    ordenados,
    totalAgendamentos,
    totalAtendidos,
    totalFaltas,
    init,
    fetchAgendamentos,
    atualizarStatus
  }
})
