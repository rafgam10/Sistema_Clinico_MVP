<script setup lang="ts">
import type { PadraoAtestado } from '~/types'
import { usePdfMake } from '~/utils/pdf'
import { buildAtestado } from '~/utils/pdf-documents'

const open = defineModel<boolean>('open', { default: false })

const padroesStore = usePadroesStore()
const agendamentosStore = useAgendamentosStore()

function calcularIdade(dataNascimento?: string) {
  if (!dataNascimento) return ''
  const hoje = new Date()
  const nasc = new Date(dataNascimento)
  let idade = hoje.getFullYear() - nasc.getFullYear()
  const mes = hoje.getMonth() - nasc.getMonth()
  if (mes < 0 || (mes === 0 && hoje.getDate() < nasc.getDate())) idade--
  return String(idade)
}

const paciente = computed(() => agendamentosStore.emAtendimento?.paciente ?? null)

const templateSelected = ref<{ label: string, value: PadraoAtestado }>()

const html = ref('')
const placeholders = ref<Record<string, string>>({})

watch(templateSelected, (val) => {
  if (!val?.value) return
  const p = val.value
  html.value = p.html
  const found: Record<string, string> = {}
  const matches = p.html.match(/\{[a-z_]+\}/g)
  if (matches) {
    for (const m of matches) {
      const key = m.slice(1, -1)
      if (!(key in found)) {
        if (key === 'nome_paciente') found[key] = paciente.value?.nome ?? ''
        else if (key === 'idade') found[key] = calcularIdade(paciente.value?.dataNascimento)
        else if (key === 'data') found[key] = new Date().toLocaleDateString('pt-BR')
        else if (key === 'cidade') found[key] = 'Cidade'
        else found[key] = ''
      }
    }
  }
  placeholders.value = found
})

function substituir(texto: string) {
  let result = texto
  for (const [key, val] of Object.entries(placeholders.value)) {
    result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), val || `{${key}}`)
  }
  return result
}

const previewHtml = computed(() => substituir(html.value))

async function gerarPdf() {
  const pdfMake = await usePdfMake()
  const doc = await buildAtestado({
    paciente: paciente.value?.nome ?? 'Paciente',
    conteudoHtml: substituir(html.value)
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
        <div class="space-y-4">
          <UInputMenu
            v-if="padroesStore.atestados.length"
            v-model="templateSelected"
            :items="padroesStore.atestados.map(p => ({ label: p.nome, value: p }))"
            placeholder="Carregar padrão de atestado..."
            searchable
          />

          <UEditor
            v-model="html"
            content-type="html"
            class="w-full min-h-64 border border-muted rounded-md"
            placeholder="Digite o texto do atestado..."
          />

          <div
            v-if="Object.keys(placeholders).length"
            class="space-y-3 p-4 border border-muted rounded-md"
          >
            <p class="text-sm font-medium text-muted">
              Preencha os placeholders:
            </p>
            <div
              v-for="(val, key) in placeholders"
              :key="key"
              class="flex items-center gap-2"
            >
              <span class="text-xs font-mono text-primary min-w-28">{ {{ key }} }</span>
              <UInput
                :model-value="val"
                :placeholder="key"
                class="flex-1"
                @update:model-value="placeholders[key] = $event"
              />
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <p class="text-sm font-medium text-muted">
            Pré-visualização
          </p>
          <div
            class="p-6 border border-muted rounded-md bg-neutral-50 dark:bg-neutral-900 prose prose-sm max-w-none"
            v-html="previewHtml"
          />
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
          :disabled="!html.trim()"
          @click="gerarPdf"
        />
      </div>
    </template>
  </UModal>
</template>
