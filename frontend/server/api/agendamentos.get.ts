export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const data = query.data ? String(query.data) : undefined

  const params = new URLSearchParams()
  if (data) params.set('data', data)

  try {
    return await flaskFetch(event, `/agenda-medica/${params.toString() ? `?${params.toString()}` : ''}`)
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Falha ao carregar agenda médica no backend Flask',
      data: String(error)
    })
  }
})
