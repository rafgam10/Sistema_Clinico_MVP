export default defineEventHandler((event) => {
  const query = getQuery(event)
  const tipo = query.tipo as string | undefined
  const medicoId = query.medicoId ? Number(query.medicoId) : undefined
  return getPadroes(tipo, medicoId)
})
