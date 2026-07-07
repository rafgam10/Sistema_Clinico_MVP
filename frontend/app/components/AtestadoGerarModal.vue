<script setup lang="ts">
import { usePdfMake } from '~/utils/pdf'
import { buildAtestado } from '~/utils/pdf-documents'

const auth = useAuthStore()
const open = defineModel<boolean>('open', { default: false })

const agendamentosStore = useAgendamentosStore()

const paciente = computed(() => agendamentosStore.emAtendimento?.paciente ?? null)

const data = ref(new Date().toISOString().split('T')[0])
const dias = ref<number | null>(null)

const TEXTO_ATESTADO = `Atesto que o(a) paciente {nome} esteve sob meus cuidados médicos, necessitando de {dias} dias de repouso/afastamento a partir de {data}.`

const textoCompleto = computed(() => {
  return TEXTO_ATESTADO
    .replace('{nome}', paciente.value?.nome ?? 'Paciente')
    .replace('{dias}', String(dias.value ?? '{dias}'))
    .replace('{data}', data.value ? new Date(data.value + 'T12:00:00').toLocaleDateString('pt-BR') : '{data}')
})

async function gerarPdf() {
  if (!dias.value) return
  const pdfMake = await usePdfMake()
  const doc = await buildAtestado({
    paciente: paciente.value?.nome ?? 'Paciente',
    conteudoHtml: `<p>${textoCompleto.value}</p>`,
    medico: auth.user?.nome,
    crm: auth.user?.crm
  })
  pdfMake.createPdf(doc).open()
  open.value = false
}
</script>

<template>
  <UModal
    v-model:open="open"
  >
    <template #header>
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold">
          Gerar Atestado Médico
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

        <UFormField label="Data de início">
          <UInput
            v-model="data"
            type="date"
            class="w-full"
          />
        </UFormField>

        <UFormField label="Dias de afastamento">
          <UInput
            v-model.number="dias"
            type="number"
            min="1"
            placeholder="Ex: 7"
            class="w-full"
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
          label="Visualizar / Imprimir"
          :disabled="!dias"
          @click="gerarPdf"
        />
      </div>
    </template>
  </UModal>
</template>
