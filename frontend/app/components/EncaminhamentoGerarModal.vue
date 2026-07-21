<script setup lang="ts">
import type { Paciente } from '~/types'
import { usePdfMake } from '~/utils/pdf'
import { buildEncaminhamento } from '~/utils/pdf-documents'

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
const encaminharPara = ref('')
const profissionalExterno = ref('')

async function gerarPdf() {
  if (!encaminharPara.value.trim()) return
  const pdfMake = await usePdfMake()
  const doc = await buildEncaminhamento({
    paciente: paciente.value?.nome ?? 'Paciente',
    data: data.value ? new Date(data.value + 'T12:00:00').toLocaleDateString('pt-BR') : '',
    encaminharPara: encaminharPara.value.trim(),
    profissionalExterno: profissionalExterno.value.trim(),
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
          Encaminhamento Médico
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

        <UFormField label="Encaminhar para">
          <UInput
            v-model="encaminharPara"
            placeholder="Ex: Cardiologia, Ortopedia..."
            class="w-full"
          />
        </UFormField>

        <UFormField label="Profissional externo">
          <UInput
            v-model="profissionalExterno"
            placeholder="Não informado"
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
          :disabled="!encaminharPara.trim()"
          @click="gerarPdf"
        />
      </div>
    </template>
  </UModal>
</template>
