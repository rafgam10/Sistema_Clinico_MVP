/* eslint-disable @typescript-eslint/no-explicit-any */
export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const q = query.q as string | undefined

  const endpoint = q && q.length >= 2
    ? `/exames/buscar?q=${encodeURIComponent(q)}`
    : '/exames'

  try {
    return await flaskFetch(event, endpoint)
  } catch (e) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Falha ao buscar exames',
      data: String(e),
    })
  }
})
