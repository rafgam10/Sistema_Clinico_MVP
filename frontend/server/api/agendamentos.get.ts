export default defineEventHandler((event) => {
  const query = getQuery(event)
  const clinicaId = query.clinicaId ? Number(query.clinicaId) : undefined
  const data = query.data ? String(query.data) : undefined
  const medicoId = query.medicoId ? Number(query.medicoId) : undefined
  return getAgendamentos(clinicaId, data, medicoId)
})
