export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const params = new URLSearchParams()

  for (const key of ['dataIni', 'dataFim', 'medico', 'especialidade', 'convenio', 'status', 'q', 'page', 'pageSize']) {
    const value = query[key]
    if (value !== undefined && value !== null && String(value).trim()) {
      params.set(key, String(value))
    }
  }

  try {
    const qs = params.toString()
    return await flaskFetch(event, `/no_show/${qs ? `?${qs}` : ''}`)
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Falha ao carregar no-show no backend Flask',
      data: String(error)
    })
  }
})
