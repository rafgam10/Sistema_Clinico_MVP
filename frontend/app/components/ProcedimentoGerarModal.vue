<script setup lang="ts">
import type { AgendamentoComPaciente, DocumentoMedico, Paciente, SolicitacaoProcedimentoDocumentoDados } from '~/types'
import { usePdfMake } from '~/utils/pdf'
import { buildSolicitacaoProcedimento } from '~/utils/pdf-documents'

const props = defineProps<{
  paciente?: Paciente
  agendamento?: AgendamentoComPaciente | null
  dataAtendimento?: string
  documento?: DocumentoMedico | null
}>()

const emit = defineEmits<{
  saved: [documento: DocumentoMedico]
}>()

const open = defineModel<boolean>('open', { default: false })

const agendamentosStore = useAgendamentosStore()
const toast = useToast()

const paciente = computed(() => props.paciente ?? props.agendamento?.paciente ?? agendamentosStore.emAtendimento?.paciente ?? null)
const medSpdataAtendimentoId = computed(() => props.agendamento?.id ?? agendamentosStore.emAtendimento?.id ?? null)
const podeEditar = computed(() => props.documento?.podeEditar ?? true)

function hojeIso() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const dataAtendimentoPadrao = computed(() => props.dataAtendimento ?? props.agendamento?.data ?? hojeIso())

const data = ref(dataAtendimentoPadrao.value)
const descricao = ref('')
const salvando = ref(false)

function preencherFormulario() {
  const dados = props.documento?.tipoDocumento === 'SOLICITACAO_PROCEDIMENTO'
    ? props.documento.dados as SolicitacaoProcedimentoDocumentoDados
    : null

  data.value = dados?.data ?? dataAtendimentoPadrao.value
  descricao.value = dados?.descricao ?? ''
}

watch(
  () => [open.value, props.documento?.id, props.documento?.updatedAt, dataAtendimentoPadrao.value] as const,
  ([isOpen]) => {
    if (isOpen) preencherFormulario()
  },
  { immediate: true }
)

function formatarDataPdf(dataISO: string) {
  if (!dataISO) return ''
  return new Date(dataISO + 'T12:00:00').toLocaleDateString('pt-BR')
}

const podeEnviar = computed(() => {
  if (!podeEditar.value) return Boolean(props.documento)
  return Boolean(medSpdataAtendimentoId.value && data.value && descricao.value.trim())
})

const botaoLabel = computed(() => podeEditar.value ? 'Salvar e Imprimir' : 'Imprimir')

async function gerarPdf(documento: DocumentoMedico) {
  if (documento.tipoDocumento !== 'SOLICITACAO_PROCEDIMENTO') return

  const dados = documento.dados as SolicitacaoProcedimentoDocumentoDados
  const pdfMake = await usePdfMake()
  const doc = await buildSolicitacaoProcedimento({
    paciente: paciente.value?.nome ?? 'Paciente',
    data: formatarDataPdf(dados.data),
    descricao: dados.descricao,
    medico: dados.medico ?? undefined,
    crm: dados.crm ?? undefined,
    especialidade: dados.especialidade ?? undefined
  })
  pdfMake.createPdf(doc).open()
}

async function fecharEAbrirPdf(documento: DocumentoMedico) {
  open.value = false
  await nextTick()
  await gerarPdf(documento)
}

async function salvarEImprimir() {
  if (!podeEnviar.value) return

  if (!podeEditar.value && props.documento) {
    await fecharEAbrirPdf(props.documento)
    return
  }

  salvando.value = true
  try {
    const documento = await $fetch<DocumentoMedico>(`/api/documentos-medicos/${medSpdataAtendimentoId.value}/SOLICITACAO_PROCEDIMENTO`, {
      method: 'PUT',
      body: {
        dados: {
          data: data.value,
          descricao: descricao.value.trim()
        }
      }
    })

    emit('saved', documento)
    await fecharEAbrirPdf(documento)
  } catch {
    toast.add({
      title: 'Erro ao salvar solicitação',
      description: 'Não foi possível salvar o documento médico.',
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
  } finally {
    salvando.value = false
  }
}
</script>

<template>
  <UModal v-model:open="open">
    <template #header>
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold">
          Solicitação de Procedimento
        </h2>
        <UButton
          icon="i-lucide-x"
          color="neutral"
          variant="ghost"
          @click="void (open = false)"
        />
      </div>
    </template>

    <template #body>
      <div class="space-y-4 p-4">
        <UFormField label="Paciente">
          <UInput
            :model-value="paciente?.nome ?? '—'"
            disabled
            class="w-full"
          />
        </UFormField>

        <UFormField label="Data">
          <UInput
            v-model="data"
            type="date"
            :disabled="!podeEditar"
            class="w-full"
          />
        </UFormField>

        <UFormField label="Descrição do procedimento">
          <UTextarea
            v-model="descricao"
            placeholder="Descreva o procedimento solicitado..."
            class="w-full"
            :disabled="!podeEditar"
            :rows="6"
          />
        </UFormField>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-between">
        <UButton
          label="Cancelar"
          color="neutral"
          variant="ghost"
          @click="void (open = false)"
        />
        <UButton
          icon="i-lucide-printer"
          :label="botaoLabel"
          :disabled="!podeEnviar"
          :loading="salvando"
          @click="salvarEImprimir"
        />
      </div>
    </template>
  </UModal>
</template>
