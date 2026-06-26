export default defineEventHandler(async () => {
  const config = useRuntimeConfig()

  try {
    const data = await $fetch(`${config.flaskBaseUrl}/dashboard/pacientes`)
    return { success: true, data }
  } catch (error) {
    return {
      success: false,
      message: 'Falha ao conectar com o backend Flask',
      error: String(error)
    }
  }
})
