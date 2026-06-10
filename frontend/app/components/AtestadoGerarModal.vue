<script setup lang="ts">
import { usePdfMake } from '~/utils/pdf'
import { buildAtestado } from '~/utils/pdf-documents'

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
    conteudoHtml: `<p>${textoCompleto.value}</p>`
  })
  pdfMake.createPdf(doc).download('atestado-medico.pdf')
  open.value = false
}
</script>

<template>
  <UModal
    v-model:open="open"
    fullscreen
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
          @click="open = false"
        />
      </div>
    </template>

    <template #body>
      <div class="grid grid-cols-2 gap-6 p-6 h-full">
        <div class="space-y-6">
          <UCard>
            <template #title>
              <div class="flex items-center gap-2">
                <UIcon
                  name="i-lucide-user"
                  class="text-primary"
                />
                <p class="font-semibold">
                  Paciente
                </p>
              </div>
            </template>
            <p class="text-lg font-medium">
              {{ paciente?.nome ?? '—' }}
            </p>
          </UCard>

          <div class="grid grid-cols-2 gap-4">
            <UFormField label="Data de início">
              <UInput
                v-model="data"
                type="date"
              />
            </UFormField>

            <UFormField label="Dias de afastamento">
              <UInput
                v-model.number="dias"
                type="number"
                min="1"
                placeholder="Ex: 7"
              />
            </UFormField>
          </div>
        </div>

        <div class="space-y-4">
          <p class="text-sm font-medium text-muted">
            Pré-visualização
          </p>
          <div
            class="p-6 border border-muted rounded-md bg-neutral-50 dark:bg-neutral-900 prose prose-sm max-w-none"
          >
            <p>
              {{ textoCompleto }}
            </p>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-between">
        <UButton
          label="Cancelar"
          color="neutral"
          variant="ghost"
          @click="open = false"
        />
        <UButton
          icon="i-lucide-file-text"
          label="Gerar PDF"
          :disabled="!dias"
          @click="gerarPdf"
        />
      </div>
    </template>
  </UModal>
</template>
