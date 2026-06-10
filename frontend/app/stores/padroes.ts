import { defineStore } from 'pinia'
import type { Padrao, PadraoReceita, PadraoExame } from '~/types'

export const usePadroesStore = defineStore('padroes', () => {
  const padroes = ref<Padrao[]>([])
  const loading = ref(false)

  const receitas = computed(() => padroes.value.filter((p): p is PadraoReceita => p.tipo === 'receita'))
  const exames = computed(() => padroes.value.filter((p): p is PadraoExame => p.tipo === 'exame'))

  async function fetchAll() {
    loading.value = true
    try {
      padroes.value = await $fetch<Padrao[]>('/api/padroes')
    } catch {
      console.error('Erro ao carregar padrões')
    } finally {
      loading.value = false
    }
  }

  async function criar(data: { nome: string, tipo: string, [key: string]: unknown }) {
    const novo = await $fetch('/api/padroes', {
      method: 'POST',
      body: data
    })
    padroes.value.push(novo as Padrao)
    return novo
  }

  async function atualizar(id: string, data: { nome?: string, [key: string]: unknown }) {
    const atualizado = await $fetch(`/api/padroes/${id}`, {
      method: 'PATCH',
      body: data
    })
    const idx = padroes.value.findIndex(p => p.id === id)
    if (idx !== -1) padroes.value[idx] = atualizado as Padrao
    return atualizado
  }

  async function deletar(id: string) {
    await $fetch(`/api/padroes/${id}`, { method: 'DELETE' })
    padroes.value = padroes.value.filter(p => p.id !== id)
  }

  return {
    padroes,
    loading,
    receitas,
    exames,
    fetchAll,
    criar,
    atualizar,
    deletar
  }
})
