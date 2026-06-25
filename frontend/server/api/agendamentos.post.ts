export default defineEventHandler(() => {
  throw createError({ statusCode: 501, statusMessage: 'Agendamentos são importados do SPDATA nesta fase' })
})
