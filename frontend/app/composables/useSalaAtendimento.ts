export function useSalaAtendimento() {
  const stored = useLocalStorage<string | null>('sala_atendimento', null)

  const sala = readonly(computed(() => stored.value))

  const precisaSelecionar = computed(() => !stored.value)

  function definirSala(novaSala: string) {
    stored.value = novaSala
  }

  function limpar() {
    stored.value = null
  }

  return { sala, precisaSelecionar, definirSala, limpar }
}
