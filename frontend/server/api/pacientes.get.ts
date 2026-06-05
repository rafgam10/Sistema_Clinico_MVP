export default defineEventHandler((event) => {
  const query = getQuery(event)
  const search = query.search ? String(query.search) : undefined
  return getPacientes(search)
})
