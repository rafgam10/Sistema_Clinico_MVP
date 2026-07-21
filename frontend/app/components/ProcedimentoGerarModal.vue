<script setup lang="ts">
import type { Paciente } from '~/types'
import { usePdfMake } from '~/utils/pdf'
import { buildSolicitacaoProcedimento } from '~/utils/pdf-documents'

const props = defineProps<{
  paciente?: Paciente
  dataAtendimento?: string
}>()

const auth = useAuthStore()
const open = defineModel<boolean>('open', { default: false })

const agendamentosStore = useAgendamentosStore()

const paciente = computed(() => props.paciente ?? agendamentosStore.emAtendimento?.paciente ?? null)

const data = ref(props.dataAtendimento ?? new Date().toISOString().split('T')[0])

watch(() => props.dataAtendimento, (val) => {
  if (val) data.value = val
})
const descricao = ref('')

async function gerarPdf() {
  if (!descricao.value.trim()) return
  const pdfMake = await usePdfMake()
  const doc = await buildSolicitacaoProcedimento({
    paciente: paciente.value?.nome ?? 'Paciente',
    data: data.value ? new Date(data.value + 'T12:00:00').toLocaleDateString('pt-BR') : '',
    descricao: descricao.value.trim(),
    medico: auth.user?.nome,
    crm: auth.user?.crm,
    especialidade: auth.user?.especialidades?.join(', ')
  })
  pdfMake.createPdf(doc).open()
  open.value = false
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
            class="w-full"
          />
        </UFormField>

        <UFormField label="Descrição do procedimento">
          <UTextarea
            v-model="descricao"
            placeholder="Descreva o procedimento solicitado..."
            class="w-full"
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
          label="Visualizar / Imprimir"
          :disabled="!descricao.trim()"
          @click="gerarPdf"
        />
      </div>
    </template>
  </UModal>
</template>
