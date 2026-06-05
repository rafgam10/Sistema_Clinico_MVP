export default defineEventHandler((event) => {
  const query = getQuery(event)
  const clinicaId = query.clinicaId ? Number(query.clinicaId) : undefined
  return getMedicos(clinicaId)
})
