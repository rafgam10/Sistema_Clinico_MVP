export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  return await $fetch(`http://localhost:5000/prontuario/historico-paciente/${id}`)
})
