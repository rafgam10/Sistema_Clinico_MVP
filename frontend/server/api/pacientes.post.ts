export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body.nome || !body.telefone) {
    throw createError({ statusCode: 400, statusMessage: 'Campos obrigatórios: nome, telefone' })
  }

  return criarPaciente({
    ...body,
    sexo: body.sexo || 'masculino',
    dataNascimento: body.dataNascimento || '1900-01-01'
  })
})
