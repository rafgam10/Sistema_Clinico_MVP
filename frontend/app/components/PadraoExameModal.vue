<script setup lang="ts">
import type { PadraoExame } from '~/types'

const props = defineProps<{
  padrao?: PadraoExame | null
}>()

const open = defineModel<boolean>('open', { default: false })

const padroesStore = usePadroesStore()

const nome = ref('')
const exames = ref<string[]>([])
const saving = ref(false)

const selectedExame = ref('')
const buscaTermo = ref('')
const sugestoesExames = ref<{ nome: string, codigo_alfanumerico: string | null, codigo_amb: string | null }[]>([])
const carregandoExames = ref(false)

let buscaTimeout: ReturnType<typeof setTimeout> | null = null
let examesController: AbortController | null = null
let examesRequestId = 0

function adicionarExame(texto: string) {
  if (!texto?.trim()) return
  if (exames.value.includes(texto.trim())) return
  exames.value.push(texto.trim())
  selectedExame.value = ''
  buscaTermo.value = ''
}

watch(selectedExame, (val) => {
  if (val?.trim()) adicionarExame(val.trim())
})

watch(buscaTermo, (val) => {
  if (buscaTimeout) clearTimeout(buscaTimeout)

  if (!val || val.length < 2) {
    sugestoesExames.value = []
    return
  }

  buscaTimeout = setTimeout(() => {
    buscarExames(val)
  }, 300)
})

async function buscarExames(q: string) {
  const termo = q.trim()
  if (termo.length < 2) return

  const requestId = ++examesRequestId
  examesController?.abort()
  examesController = new AbortController()

  carregandoExames.value = true
  try {
    const data = await $fetch<{ exames: { nome: string, codigo_alfanumerico: string | null, codigo_amb: string | null }[] }>('/api/exames/buscar', {
      query: { q: termo },
      signal: examesController.signal,
    })

    if (requestId !== examesRequestId) return
    if (buscaTermo.value.trim() !== termo) return

    sugestoesExames.value = data.exames || []
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') return
    if (requestId !== examesRequestId) return
    sugestoesExames.value = []
  } finally {
    carregandoExames.value = false
  }
}

watch(open, (isOpen) => {
  if (isOpen) {
    nome.value = props.padrao?.nome ?? ''
    exames.value = props.padrao?.exames?.length ? [...props.padrao.exames] : []
    selectedExame.value = ''
    buscaTermo.value = ''
    sugestoesExames.value = []
  }
})

function removerExame(i: number) {
  exames.value.splice(i, 1)
}

async function salvar() {
  if (!nome.value.trim()) return
  saving.value = true
  try {
    const data = {
      nome: nome.value.trim(),
      tipo: 'exame' as const,
      exames: exames.value
    }
    if (props.padrao) {
      await padroesStore.atualizar(props.padrao.id, data)
    } else {
      await padroesStore.criar(data)
    }
    open.value = false
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <UModal
    v-model:open="open"
    fullscreen
  >
    <template #header>
      <div class="flex items-center justify-between w-full">
        <div>
          <h2 class="text-lg font-semibold">
            {{ padrao ? 'Editar' : 'Novo' }} Padrão de Exames
          </h2>
          <p class="text-sm text-muted mt-0.5">
            Configure o nome e os exames do modelo
          </p>
        </div>
        <UButton
          icon="i-lucide-x"
          color="neutral"
          variant="ghost"
          @click="open = false"
        />
      </div>
    </template>

    <template #body>
      <div class="h-full overflow-y-auto p-6 space-y-6">
        <div class="space-y-1 flex flex-col">
          <label class="text-sm font-medium">Nome do modelo</label>
          <UInput
            v-model="nome"
            placeholder="Ex: Check-up anual"
            size="lg"
          />
        </div>

        <div class="space-y-1">
          <p class="text-sm font-medium">
            Exames
          </p>

          <div class="flex items-center gap-3 mb-3">
            <UInputMenu
              v-model="selectedExame"
              v-model:search-term="buscaTermo"
              :items="sugestoesExames"
              :loading="carregandoExames"
              value-key="nome"
              placeholder="Digite o nome do exame..."
              class="flex-1"
              clear
              ignore-filter
            >
              <template #item-label="{ item }">
                <span class="text-sm">
                  {{ item.codigo_alfanumerico ? `${item.codigo_alfanumerico} — ` : '' }}{{ item.nome }}{{ item.codigo_amb ? ` (${item.codigo_amb})` : '' }}
                </span>
              </template>
            </UInputMenu>
          </div>

          <div class="space-y-2">
            <div
              v-for="(exame, i) in exames"
              :key="i"
              class="flex items-center justify-between p-3 rounded-lg border border-muted"
            >
              <span class="text-sm">{{ exame }}</span>
              <UButton
                icon="i-lucide-x"
                color="error"
                variant="ghost"
                size="sm"
                @click="removerExame(i)"
              />
            </div>

            <p
              v-if="!exames.length"
              class="text-sm text-muted italic py-4 text-center"
            >
              Nenhum exame adicionado.
            </p>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex items-center justify-between w-full">
        <p class="text-sm text-muted">
          {{ exames.length }} exame{{ exames.length !== 1 ? 's' : '' }} válido{{ exames.length !== 1 ? 's' : '' }}
        </p>
        <div class="flex gap-2">
          <UButton
            label="Cancelar"
            color="neutral"
            variant="ghost"
            @click="open = false"
          />
          <UButton
            label="Salvar"
            :loading="saving"
            :disabled="!nome.trim()"
            @click="salvar"
          />
        </div>
      </div>
    </template>
  </UModal>
</template>
