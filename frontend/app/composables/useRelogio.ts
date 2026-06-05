export function useRelogio(intervalo: number = 1000) {
  const agora = ref(new Date())

  useIntervalFn(() => {
    agora.value = new Date()
  }, intervalo)

  const horaFormatada = computed(() => formatarHora(agora.value))
  const dataFormatada = computed(() => formatarDataCompleta(agora.value))

  return { agora, horaFormatada, dataFormatada }
}
