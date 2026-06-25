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
const inputKey = ref(0)
const inputMenuRef = ref()

function adicionarExame(texto: string) {
  exames.value.push(texto)
  selectedExame.value = ''
  inputKey.value++
  nextTick(() => inputMenuRef.value?.inputRef?.focus())
}

watch(selectedExame, (val) => {
  if (val?.trim()) adicionarExame(val.trim())
})

watch(open, (isOpen) => {
  if (isOpen) {
    nome.value = props.padrao?.nome ?? ''
    exames.value = props.padrao?.exames?.length ? [...props.padrao.exames] : []
    selectedExame.value = ''
  }
}, { immediate: true })

const examesComuns = [
  'Hemograma completo',
  'Glicemia em jejum',
  'Colesterol total e frações',
  'Triglicerídeos',
  'Creatinina',
  'Uréia',
  'TGO/TGP (Transaminases)',
  'TSH e T4 livre',
  'PSA total',
  'Eletrocardiograma (ECG)',
  'Raio-X de tórax',
  'Ecocardiograma transtorácico',
  'Ultrassonografia de abdome total',
  'Densitometria óssea',
  'Teste ergométrico',
  'Urocultura com antibiograma',
  'PCR e VHS',
  'Hemoglobina glicada',
  'Dosagem de vitamina D',
  'Dosagem de vitamina B12',
  'Ferritina',
  'Ácido úrico',
  'EAS (Urina tipo I)',
  'Parcela de fezes',
  'Endoscopia digestiva alta',
  'Colonoscopia'
]

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
              ref="inputMenuRef"
              :key="inputKey"
              v-model="selectedExame"
              :items="examesComuns"
              searchable
              placeholder="Digite um exame..."
              class="flex-1"
              clear
            />
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
