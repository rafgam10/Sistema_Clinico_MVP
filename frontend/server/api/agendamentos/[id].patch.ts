export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  const body = await readBody<{ status: string, consulta?: { anamnese?: string, diagnostico?: string, medicamentos?: string, exames?: string, duracao?: number } }>(event)

  const validStatuses = ['em-espera', 'em-atendimento', 'atendido', 'faltou']
  if (!body.status || !validStatuses.includes(body.status)) {
    throw createError({ statusCode: 400, statusMessage: 'Status inválido' })
  }

  if (body.status === 'em-espera') {
    throw createError({ statusCode: 400, statusMessage: 'Status em-espera é calculado pelo backend' })
  }

  try {
    const result = await flaskFetch<{ pacienteId: number }>(event, `/agenda-medica/${id}/status`, {
      method: 'PATCH',
      body
    })

    if (body.status === 'atendido' || body.status === 'faltou') {
      concluirChamadoPorPaciente(Number(result.pacienteId) || 0)
    }

    return result
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Falha ao atualizar status no backend Flask',
      data: String(error)
    })
  }
})
