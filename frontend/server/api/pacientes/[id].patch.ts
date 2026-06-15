export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  const body = await readBody(event)

  // If updating status (old behavior from agenda)
  if (body.status) {
    const validStatuses = ['agendado', 'em-espera', 'em_atendimento', 'atendido', 'faltou', 'cancelado']
    if (!validStatuses.includes(body.status)) {
      throw createError({ statusCode: 400, statusMessage: 'Status inválido' })
    }

    // Concluir chamado se foi atendido ou faltou
    if (body.status === 'atendido' || body.status === 'faltou') {
      concluirChamadoPorPaciente(id)
    }

    // Atualizar status via agendamento (pegar último agendamento do paciente)
    const agendamentosPaciente = getAgendamentos(undefined, undefined, undefined)
      .filter(a => a.pacienteId === id)
      .sort((a, b) => new Date(b.criadoEm).getTime() - new Date(a.criadoEm).getTime())

    if (agendamentosPaciente.length > 0) {
      const ultimoAgendamento = agendamentosPaciente[0]!
      return atualizarStatusAgendamento(ultimoAgendamento.id, body.status as 'agendado' | 'em-espera' | 'em_atendimento' | 'atendido' | 'faltou' | 'cancelado')
    }

    throw createError({ statusCode: 404, statusMessage: 'Nenhum agendamento encontrado para o paciente' })
  }

  // Otherwise, update paciente data
  const paciente = atualizarPaciente(id, body)
  if (!paciente) {
    throw createError({ statusCode: 404, statusMessage: 'Paciente não encontrado' })
  }
  return paciente
})
