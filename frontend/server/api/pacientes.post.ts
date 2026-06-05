export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body.nome || !body.sexo || !body.dataNascimento || !body.telefone) {
    throw createError({ statusCode: 400, statusMessage: 'Campos obrigatórios: nome, sexo, dataNascimento, telefone' })
  }

  return criarPaciente(body)
})
