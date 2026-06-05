export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, 'id'))
  const ok = deletarPaciente(id)
  if (!ok) {
    throw createError({ statusCode: 404, statusMessage: 'Paciente não encontrado' })
  }
  return { success: true }
})
