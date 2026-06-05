export default defineEventHandler(async (event) => {
  const body = await readBody<{
    pacienteId: number
    medicoId: number
    clinicaId: number
    data: string
    horario: string
    prioridade?: 'normal' | 'preferencial'
    descricao?: string
  }>(event)

  if (!body.pacienteId || !body.medicoId || !body.clinicaId || !body.data || !body.horario) {
    throw createError({ statusCode: 400, statusMessage: 'Campos obrigatórios: pacienteId, medicoId, clinicaId, data, horario' })
  }

  return criarAgendamento({
    pacienteId: body.pacienteId,
    medicoId: body.medicoId,
    clinicaId: body.clinicaId,
    data: body.data,
    horario: body.horario,
    prioridade: body.prioridade || 'normal',
    status: 'agendado',
    descricao: body.descricao || ''
  })
})
