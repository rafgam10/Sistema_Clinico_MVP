import { defineStore } from 'pinia'
import type { PadraoOrientacaoExame } from '~/types'

export const usePadroesOrientacoesStore = defineStore('padroesOrientacoes', () => {
  const padroes = ref<PadraoOrientacaoExame[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      padroes.value = await $fetch<PadraoOrientacaoExame[]>('/api/padroes-orientacoes')
    } catch {
      console.error('Erro ao carregar padrões de orientação')
    } finally {
      loading.value = false
    }
  }

  async function criar(data: { nome: string, conteudo: string }) {
    const novo = await $fetch<PadraoOrientacaoExame>('/api/padroes-orientacoes', {
      method: 'POST',
      body: data
    })
    padroes.value.push(novo)
    return novo
  }

  async function atualizar(id: string, data: { nome?: string, conteudo?: string }) {
    const atualizado = await $fetch<PadraoOrientacaoExame>(`/api/padroes-orientacoes/${id}`, {
      method: 'PATCH',
      body: data
    })
    const idx = padroes.value.findIndex(p => p.id === id)
    if (idx !== -1) padroes.value[idx] = atualizado
    return atualizado
  }

  async function deletar(id: string) {
    await $fetch(`/api/padroes-orientacoes/${id}`, {
      method: 'DELETE'
    })
    padroes.value = padroes.value.filter(p => p.id !== id)
  }

  return {
    padroes,
    loading,
    fetchAll,
    criar,
    atualizar,
    deletar
  }
})
