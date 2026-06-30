interface SalaStorage {
  sala: string
  data: string
}

export function useSalaAtendimento() {
  const stored = useLocalStorage<SalaStorage | null>('sala_atendimento', null)

  const sala = computed(() => stored.value?.sala ?? null)

  const precisaSelecionar = computed(() => {
    const hoje = new Date().toISOString().split('T')[0]!
    return !stored.value?.sala || stored.value.data !== hoje
  })

  function definirSala(novaSala: string) {
    stored.value = { sala: novaSala, data: new Date().toISOString().split('T')[0]! }
  }

  function limpar() {
    stored.value = null
  }

  return { sala: readonly(sala), precisaSelecionar, definirSala, limpar }
}
