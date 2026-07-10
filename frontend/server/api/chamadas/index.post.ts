export default defineEventHandler(async (event) => {
  const body = await readBody<{ pacienteId: number, pacienteNome: string, localAtendimento: string, medicoResponsavel: string }>(event)

  if (!body.pacienteId || !body.pacienteNome || !body.localAtendimento || !body.medicoResponsavel) {
    throw createError({ statusCode: 400, statusMessage: 'Campos obrigatórios: pacienteId, pacienteNome, localAtendimento, medicoResponsavel' })
  }

  return flaskFetch(event, '/chamadas', { method: 'POST', body })
})
