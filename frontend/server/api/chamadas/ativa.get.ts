export default defineEventHandler((event) => {
  return flaskFetch(event, '/chamadas/ativa')
})
