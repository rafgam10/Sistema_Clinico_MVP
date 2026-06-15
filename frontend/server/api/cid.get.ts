export default defineEventHandler(async () => {
  try {
    const raw = await $fetch<Record<string, unknown>[]>('http://localhost:5000/prontuario/doenca-cid')

    return raw.map(item => ({
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
