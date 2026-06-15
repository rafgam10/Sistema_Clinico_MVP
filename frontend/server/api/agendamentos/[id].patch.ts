export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  const body = await readBody<{ status: string, consulta?: { anamnese?: string, diagnostico?: string, medicamentos?: string, exames?: string, duracao?: number } }>(event)

  const validStatuses = ['agendado', 'em-espera', 'em_atendimento', 'atendido', 'faltou', 'cancelado']
  if (!body.status || !validStatuses.includes(body.status)) {
    throw createError({ statusCode: 400, statusMessage: 'Status inválido' })
  }

  // Concluir chamado se foi atendido ou faltou
  if (body.status === 'atendido' || body.status === 'faltou') {
    const agendamento = getAgendamento(id)
    if (agendamento) {
      concluirChamadoPorPaciente(agendamento.pacienteId)
    }
  }

  const result = atualizarStatusAgendamento(id, body.status as 'agendado' | 'em-espera' | 'em_atendimento' | 'atendido' | 'faltou' | 'cancelado', body.consulta)
  if (!result) {
    throw createError({ statusCode: 404, statusMessage: 'Agendamento não encontrado' })
  }

  return result
})
