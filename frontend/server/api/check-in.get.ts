export default defineEventHandler(async () => {
  try {
    const raw = await $fetch<Record<string, unknown>[]>('http://localhost:5000/check_in/')

    return raw.map(item => ({
      id: Number(item.ID) || 0,
      medico: String(item.MEDICO || ''),
      data: String(item.DATA || ''),
      horario: String(item.HORA || ''),
      paciente: String(item.PACIENTE || ''),
      status: String(item.STATUS || '').trim()
    }))
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Falha ao conectar com o backend Flask',
      data: String(error)
    })
  }
})
