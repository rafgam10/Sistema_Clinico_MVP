export default defineEventHandler(async () => {
  try {
    const data = await $fetch('http://localhost:5000/dashboard/pacientes')
    return { success: true, data }
  } catch (error) {
    return {
      success: false,
      message: 'Falha ao conectar com o backend Flask',
      error: String(error)
    }
  }
})
