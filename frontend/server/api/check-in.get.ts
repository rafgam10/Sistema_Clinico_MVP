export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const params = new URLSearchParams()

  for (const key of ['page', 'pageSize', 'status', 'medico', 'q', 'data']) {
    const value = query[key]
    if (value !== undefined && value !== null && String(value).trim()) {
      params.set(key, String(value))
    }
  }

  try {
    const qs = params.toString()
    return await flaskFetch(event, `/check_in/${qs ? `?${qs}` : ''}`)
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Falha ao conectar com o backend Flask',
      data: String(error)
    })
  }
})
