export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event)
    const params = new URLSearchParams()
    if (query.q) params.set('q', String(query.q))
    params.set('limit', '50')

    const qs = params.toString()
    const raw = await $fetch<{ items: Record<string, unknown>[] }>(
      `http://localhost:5000/prontuario/doenca-cid?${qs}`
    )

    return raw.items.map(item => ({
      cid: item.CID,
      nome: item.DOENCA
    }))
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Falha ao conectar com o backend Flask',
      data: String(error)
    })
  }
})
