export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const params = new URLSearchParams()

  for (const key of ['dataIni', 'dataFim']) {
    const value = query[key]
    if (value !== undefined && value !== null && String(value).trim()) {
      params.set(key, String(value))
    }
  }

  try {
    const qs = params.toString()
    return await flaskFetch(event, `/retencao-exames/${qs ? `?${qs}` : ''}`)
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Falha ao carregar retenção de exames no backend Flask',
      data: String(error)
    })
  }
})
