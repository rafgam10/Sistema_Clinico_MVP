<script setup lang="ts">
import type { PadraoAtestado } from '~/types'

const props = defineProps<{
  padrao?: PadraoAtestado | null
}>()

const open = defineModel<boolean>('open', { default: false })

const padroesStore = usePadroesStore()

const nome = ref('')
const html = ref('')
const saving = ref(false)

watch(open, (isOpen) => {
  if (isOpen) {
    nome.value = props.padrao?.nome ?? ''
    html.value = props.padrao?.html ?? ''
  }
}, { immediate: true })

const placeholders = [
  { label: 'Nome do paciente', value: '{nome_paciente}' },
  { label: 'Idade', value: '{idade}' },
  { label: 'Dias', value: '{dias}' },
  { label: 'Data', value: '{data}' },
  { label: 'CID', value: '{cid}' },
  { label: 'Cidade', value: '{cidade}' }
]

function inserirPlaceholder(valor: string) {
  html.value += valor
}

async function salvar() {
  if (!nome.value.trim()) return
  saving.value = true
  try {
    const data = {
      nome: nome.value.trim(),
      tipo: 'atestado' as const,
      html: html.value
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
            {{ padrao ? 'Editar' : 'Novo' }} Padrão de Atestado
          </h2>
          <p class="text-sm text-muted mt-0.5">
            Configure o nome e o texto do modelo
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
            placeholder="Ex: Atestado simples"
            size="lg"
          />
        </div>

        <div class="space-y-1">
          <label class="text-sm font-medium">Placeholders</label>
          <div class="flex flex-wrap gap-1.5">
            <UButton
              v-for="ph in placeholders"
              :key="ph.value"
              :label="ph.label"
              color="primary"
              variant="soft"
              size="xs"
              @click="inserirPlaceholder(ph.value)"
            />
          </div>
          <p class="text-xs text-muted">
            Clique para inserir. Serão substituídos pelos dados do paciente na impressão.
          </p>
        </div>

        <div class="flex flex-col flex-1 min-h-0 space-y-1">
          <label class="text-sm font-medium">Texto do atestado</label>
          <UEditor
            v-model="html"
            content-type="html"
            class="flex-1 border border-muted rounded-md min-h-[300px]"
            placeholder="Digite o texto do atestado..."
          />
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex items-center justify-between w-full">
        <span />
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
