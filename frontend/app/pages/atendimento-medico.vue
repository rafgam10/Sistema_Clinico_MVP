<script setup lang="ts">
import type { PadraoReceita, PadraoExame, ItemMedicamento } from '~/types'
import { usePdfMake } from '~/utils/pdf'
import { buildSolicitacaoExames, buildReceita } from '~/utils/pdf-documents'

const agendamentosStore = useAgendamentosStore()
const padroesStore = usePadroesStore()
const cronometro = useCronometroStore()
onMounted(() => {
  padroesStore.fetchAll()
  cronometro.start()
})

onBeforeRouteLeave(() => {
  if (cronometro.isRunning) cronometro.pause()
})

const agendamento = computed(() => agendamentosStore.emAtendimento)

const tabAtiva = ref('0')
const tabItems = [
  { label: 'Anamnese e Evolução', icon: 'i-lucide-notebook-text' },
  { label: 'Receita', icon: 'i-lucide-pill' },
  { label: 'Solicitar Exames', icon: 'i-lucide-flask-conical' },
  { label: 'Finalizar', icon: 'i-lucide-check-circle' }
]

type CidResultado = { cid: string, nome: string }

let buscaTimeout: ReturnType<typeof setTimeout> | null = null
let cidController: AbortController | null = null
let cidRequestId = 0

const searchCid = ref('')
const resultadosCid = ref<CidResultado[]>([])
const cidSelecionado = ref<CidResultado | null>(null)
const isLoadingCid = ref(false)

watch(searchCid, (val) => {
  onSearchInput(val)
})

const CID_CODE_PATTERN = /^[A-Za-z][0-9.]*$/

function podeBuscarCid(q: string) {
  const termo = q.trim()

  if (!termo) return false

  if (CID_CODE_PATTERN.test(termo)) {
    return termo.length >= 2
  }

  return termo.length >= 3
}

function limparResultadosCid() {
  cidRequestId++
  cidController?.abort()
  resultadosCid.value = []
}

async function buscarCid(q: string) {
  const termo = q.trim()

  if (!podeBuscarCid(termo)) {
    limparResultadosCid()
    return
  }

  const requestId = ++cidRequestId

  cidController?.abort()
  cidController = new AbortController()

  isLoadingCid.value = true

  try {
    const data = await $fetch<CidResultado[]>('/api/cid', {
      query: {
        q: termo,
        limit: 20
      },
      signal: cidController.signal
    })

    if (requestId !== cidRequestId) return
    if (searchCid.value.trim() !== termo) return

    resultadosCid.value = data
  } catch (error) {
    const name = error instanceof Error ? error.name : ''

    if (name === 'AbortError') return
    if (requestId !== cidRequestId) return

    resultadosCid.value = []
  } finally {
    isLoadingCid.value = false
  }
}

function onSearchInput(val: string) {
  if (buscaTimeout) clearTimeout(buscaTimeout)

  if (!podeBuscarCid(val)) {
    limparResultadosCid()
    return
  }

  buscaTimeout = setTimeout(() => {
    buscarCid(val)
  }, 300)
}

function limparCid() {
  cidSelecionado.value = null
}

const anamneseTexto = ref('')
const diagnosticoSelected = computed(() => {
  if (!cidSelecionado.value) return undefined
  return { label: `${cidSelecionado.value.nome} (${cidSelecionado.value.cid})`, value: cidSelecionado.value.cid }
})

const receitaTexto = ref('')
const remedioNome = ref('')
const remedioDosagem = ref('')
const remedioDetalhes = ref('')
const padraoReceitaSelected = ref<{ label: string, value: PadraoReceita }>()

function adicionarRemedio() {
  if (!remedioNome.value && !remedioDosagem.value) return
  receitaTexto.value += `• ${remedioNome.value}${remedioDosagem.value ? ` — ${remedioDosagem.value}` : ''}${remedioDetalhes.value ? `\n  ${remedioDetalhes.value}` : ''}\n`
  remedioNome.value = ''
  remedioDosagem.value = ''
  remedioDetalhes.value = ''
}

function adicionarPadraoReceita() {
  if (!padraoReceitaSelected.value) return
  for (const m of padraoReceitaSelected.value.value.medicamentos) {
    receitaTexto.value += `• ${m.nome} — ${m.dosagem}${m.detalhes ? `\n  ${m.detalhes}` : ''}\n`
  }
  padraoReceitaSelected.value = undefined
}

const examesTexto = ref('')
const exameInput = ref('')
const exameTemplateSelected = ref<{ label: string, value: PadraoExame }>()

function adicionarExame() {
  if (!exameInput.value) return
  examesTexto.value += `• ${exameInput.value}\n`
  exameInput.value = ''
}

function adicionarPadraoExame() {
  if (!exameTemplateSelected.value) return
  for (const e of exameTemplateSelected.value.value.exames) {
    examesTexto.value += `• ${e}\n`
  }
  exameTemplateSelected.value = undefined
}

const showAtestadoModal = ref(false)

async function gerarReceitaPdf() {
  if (!receitaTexto.value.trim()) return
  const pdfMake = await usePdfMake()
  const linhas = receitaTexto.value.trim().split('\n').filter(l => l.trim())
  const medicamentos: ItemMedicamento[] = linhas.map((l) => {
    const text = l.replace(/^[•\-\s]*/, '').trim()
    const idx = text.indexOf('—')
    if (idx !== -1) {
      return { nome: text.slice(0, idx).trim(), dosagem: text.slice(idx + 1).trim(), detalhes: '' }
    }
    return { nome: text, dosagem: '', detalhes: '' }
  })
  const doc = buildReceita({
    paciente: agendamento.value?.paciente.nome ?? 'Paciente',
    data: new Date().toLocaleDateString('pt-BR'),
    medicamentos
  })
  pdfMake.createPdf(doc).download('receita-medica.pdf')
}

async function gerarSolicitacaoExames() {
  if (!examesTexto.value.trim()) return
  const pdfMake = await usePdfMake()
  const exames = examesTexto.value.trim().split('\n').filter(l => l.trim()).map(l => l.replace(/^[•\-\s]*/, '').trim())
  const doc = buildSolicitacaoExames({
    paciente: agendamento.value?.paciente.nome ?? 'Paciente',
    data: new Date().toLocaleDateString('pt-BR'),
    exames
  })
  pdfMake.createPdf(doc).download('solicitacao-exames.pdf')
}

function finalizarConsulta() {
  if (!agendamento.value) return
  const duracao = cronometro.stop()
  agendamentosStore.atualizarStatus(agendamento.value.id, 'atendido', {
    anamnese: anamneseTexto.value,
    diagnostico: diagnosticoSelected.value?.value,
    medicamentos: receitaTexto.value,
    exames: examesTexto.value,
    duracao
  })
  navigateTo('/dashboard')
}
</script>

<template>
  <div class="h-screen flex flex-col">
    <UHeader title="Consulta Atual">
      <template #right>
        <div class="flex items-center gap-2">
          <UBadge
            color="neutral"
            variant="subtle"
          >
            <p>`Tempo: {{ cronometro.formatted }}</p>
            <UButton
              :key="cronometro.isRunning ? 'pause' : 'play'"
              :icon="cronometro.isRunning ? 'i-lucide-pause' : 'i-lucide-play'"
              color="neutral"
              variant="ghost"
              size="sm"
              @click="cronometro.isRunning ? cronometro.pause() : cronometro.resume()"
            />
          </UBadge>
        </div>
        <UColorModeButton />
      </template>
    </UHeader>

    <UTabs
      v-model="tabAtiva"
      :items="tabItems"
      color="primary"
      size="lg"
      :ui="{
        content: 'grow min-h-0 flex flex-col',
        list: 'bg-default/75 backdrop-blur border-b border-default rounded-tl-none rounded-tr-none'
      }"
      class="flex-1 overflow-hidden "
    >
      <template #content="{ index }">
        <div
          v-if="index === 0"
          class="px-2 flex flex-col gap-4 py-2 pb-20  grow"
        >
          <UCard
            :ui="{ header: 'p-1 sm:px-2', body: 'p-0 sm:p-0 grow flex flex-col' }"
            class="grow flex flex-col"
          >
            <template #title>
              <div class="flex items-center gap-2">
                <UIcon
                  name="i-lucide-notebook-text"
                  class="text-primary"
                />
                <p class="font-semibold">
                  Anamnese e Evolução
                </p>
              </div>
            </template>
            <UEditor
              v-model="anamneseTexto"
              content-type="html"
              placeholder="Descreva a anamnese e evolução do paciente..."
              class="grow flex flex-col"
            >
              <template #default="{ editor }">
                <div class="flex flex-wrap gap-1 p-2 border-b border-muted bg-neutral-50 dark:bg-neutral-900 rounded-t-lg">
                  <UButton
                    icon="i-lucide-bold"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    :class="{ 'bg-primary/10 text-primary': editor?.isActive('bold') }"
                    @click="editor?.chain().focus().toggleBold().run()"
                  />
                  <UButton
                    icon="i-lucide-italic"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    :class="{ 'bg-primary/10 text-primary': editor?.isActive('italic') }"
                    @click="editor?.chain().focus().toggleItalic().run()"
                  />
                  <UButton
                    icon="i-lucide-strikethrough"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    :class="{ 'bg-primary/10 text-primary': editor?.isActive('strike') }"
                    @click="editor?.chain().focus().toggleStrike().run()"
                  />
                  <USeparator
                    orientation="vertical"
                    class="h-6"
                  />
                  <UButton
                    icon="i-lucide-heading-1"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    :class="{ 'bg-primary/10 text-primary': editor?.isActive('heading', { level: 1 }) }"
                    @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
                  />
                  <UButton
                    icon="i-lucide-heading-2"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    :class="{ 'bg-primary/10 text-primary': editor?.isActive('heading', { level: 2 }) }"
                    @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
                  />
                  <UButton
                    icon="i-lucide-heading-3"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    :class="{ 'bg-primary/10 text-primary': editor?.isActive('heading', { level: 3 }) }"
                    @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
                  />
                  <USeparator
                    orientation="vertical"
                    class="h-6"
                  />
                  <UButton
                    icon="i-lucide-list"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    :class="{ 'bg-primary/10 text-primary': editor?.isActive('bulletList') }"
                    @click="editor?.chain().focus().toggleBulletList().run()"
                  />
                  <UButton
                    icon="i-lucide-list-ordered"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    :class="{ 'bg-primary/10 text-primary': editor?.isActive('orderedList') }"
                    @click="editor?.chain().focus().toggleOrderedList().run()"
                  />
                  <UButton
                    icon="i-lucide-text-quote"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    :class="{ 'bg-primary/10 text-primary': editor?.isActive('blockquote') }"
                    @click="editor?.chain().focus().toggleBlockquote().run()"
                  />
                  <USeparator
                    orientation="vertical"
                    class="h-6"
                  />
                  <UButton
                    icon="i-lucide-undo"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    @click="editor?.chain().focus().undo().run()"
                  />
                  <UButton
                    icon="i-lucide-redo"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    @click="editor?.chain().focus().redo().run()"
                  />
                </div>
              </template>
            </UEditor>
          </UCard>

          <UCard
            :ui="{ header: 'p-1 sm:px-2', body: 'p-2 sm:p-2 ' }"
          >
            <template #title>
              <div class="flex items-center gap-2">
                <UIcon
                  name="i-lucide-stethoscope"
                  class="text-primary"
                />
                <p class="font-semibold">
                  Diagnóstico (CID-10)
                </p>
              </div>
            </template>
            <div class="relative">
              <UInputMenu
                v-model="cidSelecionado"
                v-model:search-term="searchCid"
                :items="resultadosCid"
                :loading="isLoadingCid"
                label-key="nome"
                placeholder="Buscar CID por código ou nome..."
                icon="i-lucide-search"
                clear
                ignore-filter
                class="w-full"
              >
                <template #item-label="{ item }">
                  <span class="font-mono text-xs font-semibold text-primary min-w-10">{{ item.cid }}</span>
                  <span class="text-muted"> — </span>
                  <span class="truncate">{{ item.nome }}</span>
                </template>
                <template #empty>
                  <p
                    v-if="searchCid"
                    class="px-3 py-4 text-sm text-muted text-center"
                  >
                    Nenhum CID encontrado
                  </p>
                </template>
              </UInputMenu>

              <div
                v-if="cidSelecionado"
                class="mt-2"
              >
                <UBadge
                  color="primary"
                  variant="soft"
                  size="lg"
                >
                  {{ cidSelecionado.cid }} — {{ cidSelecionado.nome }}
                  <UButton
                    icon="i-lucide-x"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    @click="limparCid()"
                  />
                </UBadge>
              </div>
            </div>
          </UCard>
        </div>

        <div
          v-if="index === 1"
          class="px-2 flex flex-col gap-4 py-2  grow"
        >
          <UCard
            :ui="{ body: 'grow flex flex-col p-0 sm:p-0' }"
            class="grow flex flex-col"
          >
            <template #title>
              <div class="flex items-center gap-2">
                <UIcon
                  name="i-lucide-pill"
                  class="text-primary"
                />
                <p class="font-semibold">
                  Receita Digital
                </p>
              </div>
            </template>

            <div class="flex flex-col gap-4 grow p-4">
              <div class="shrink-0 flex items-end gap-3 p-4 rounded-lg border border-muted bg-neutral-50 dark:bg-neutral-900">
                <UFormField
                  label="Nome do medicamento"
                  class="flex-1"
                >
                  <UInput
                    v-model="remedioNome"
                    placeholder="Ex: Amoxicilina"
                    class="w-full"
                  />
                </UFormField>
                <UFormField
                  label="Dosagem"
                  class="w-48"
                >
                  <UInput
                    v-model="remedioDosagem"
                    placeholder="Ex: 500mg 3x/dia"
                  />
                </UFormField>
                <UFormField
                  label="Detalhes"
                  class="flex-1"
                >
                  <UInput
                    v-model="remedioDetalhes"
                    placeholder="Observações..."
                    class="w-full"
                  />
                </UFormField>
                <UButton
                  icon="i-lucide-plus"
                  label="Adicionar"
                  color="primary"
                  :disabled="!remedioNome && !remedioDosagem"
                  @click="adicionarRemedio"
                />
              </div>

              <div class="shrink-0 flex gap-2">
                <UInputMenu
                  v-model="padraoReceitaSelected"
                  :items="padroesStore.receitas.map(p => ({ label: p.nome, value: p }))"
                  searchable
                  placeholder="Selecionar padrão de receita..."
                  class="flex-1"
                />
                <UButton
                  icon="i-lucide-copy-plus"
                  label="Adicionar Padrão"
                  color="secondary"
                  :disabled="!padraoReceitaSelected"
                  @click="adicionarPadraoReceita"
                />
              </div>

              <p
                v-if="!padroesStore.receitas.length"
                class="shrink-0 text-sm text-muted italic"
              >
                Nenhum padrão de receita cadastrado. Crie padrões em "Padrões de Solicitações".
              </p>

              <UTextarea
                v-model="receitaTexto"
                placeholder="Os medicamentos adicionados aparecerão aqui..."
                class="w-full grow min-h-0"
                :ui="{ base: 'h-full min-h-0' }"
              />

              <UButton
                icon="i-lucide-file-text"
                label="Gerar Receita (PDF)"
                color="primary"
                class="w-full shrink-0"
                :disabled="!receitaTexto.trim()"
                @click="gerarReceitaPdf"
              />
            </div>
          </UCard>
        </div>

        <div
          v-if="index === 2"
          class="px-2 flex flex-col gap-4 py-2  grow"
        >
          <UCard
            :ui="{ body: 'grow flex flex-col p-0 sm:p-0' }"
            class="grow flex flex-col"
          >
            <template #title>
              <div class="flex items-center gap-2">
                <UIcon
                  name="i-lucide-flask-conical"
                  class="text-primary"
                />
                <p class="font-semibold">
                  Pedido de Exames
                </p>
              </div>
            </template>

            <div class="flex flex-col gap-4 grow p-4">
              <div class="shrink-0 flex items-end gap-3 p-4 rounded-lg border border-muted bg-neutral-50 dark:bg-neutral-900">
                <UFormField
                  label="Nome do exame"
                  class="flex-1"
                >
                  <UInput
                    v-model="exameInput"
                    placeholder="Ex: Hemograma completo"
                    class="w-full"
                    @keydown.enter="adicionarExame"
                  />
                </UFormField>
                <UButton
                  icon="i-lucide-plus"
                  label="Adicionar"
                  color="primary"
                  :disabled="!exameInput"
                  @click="adicionarExame"
                />
              </div>

              <div class="shrink-0 flex gap-2">
                <UInputMenu
                  v-model="exameTemplateSelected"
                  :items="padroesStore.exames.map(p => ({ label: p.nome, value: p }))"
                  searchable
                  placeholder="Selecionar padrão de exames..."
                  class="flex-1"
                />
                <UButton
                  icon="i-lucide-copy-plus"
                  label="Adicionar Padrão"
                  color="secondary"
                  :disabled="!exameTemplateSelected"
                  @click="adicionarPadraoExame"
                />
              </div>

              <p
                v-if="!padroesStore.exames.length"
                class="shrink-0 text-sm text-muted italic"
              >
                Nenhum padrão de exames cadastrado. Crie padrões em "Padrões de Solicitações".
              </p>

              <UTextarea
                v-model="examesTexto"
                class="w-full grow min-h-0"
                :ui="{ base: 'h-full min-h-0' }"
              />

              <UButton
                icon="i-lucide-file-text"
                label="Gerar Solicitação (PDF)"
                color="primary"
                class="w-full shrink-0"
                :disabled="!examesTexto.trim()"
                @click="gerarSolicitacaoExames"
              />
            </div>
          </UCard>
        </div>

        <div
          v-if="index === 3"
          class="px-2 flex flex-col gap-4 py-2  grow"
        >
          <UCard>
            <template #title>
              <div class="flex items-center gap-2">
                <UIcon
                  name="i-lucide-printer"
                  class="text-primary"
                />
                <p class="font-semibold">
                  Documentos
                </p>
              </div>
            </template>
            <div class="grid grid-cols-2 gap-4">
              <UButton
                icon="i-lucide-file-check"
                label="Atestado de Comparecimento"
                color="primary"
                class="w-full"
              />
              <UButton
                icon="i-lucide-stamp"
                label="Atestado Médico"
                color="neutral"
                class="w-full"
                @click="showAtestadoModal = true"
              />
              <UButton
                icon="i-lucide-send"
                label="Encaminhamento Médico"
                color="secondary"
                class="w-full"
              />
              <UButton
                icon="i-lucide-clipboard-list"
                label="Solicitação de Procedimento"
                color="tertiary"
                class="w-full"
              />
              <UButton
                icon="i-lucide-file-text"
                label="Gerar Receita (PDF)"
                color="success"
                class="w-full"
                :disabled="!receitaTexto.trim()"
                @click="tabAtiva = '1'"
              />
              <UButton
                icon="i-lucide-flask-conical"
                label="Gerar Exames (PDF)"
                color="warning"
                class="w-full"
                :disabled="!examesTexto.trim()"
                @click="tabAtiva = '2'"
              />
            </div>
          </UCard>

          <UButton
            icon="i-lucide-check-circle"
            label="Finalizar Consulta"
            color="success"
            size="xl"
            class="w-full py-6 text-lg font-bold"
            @click="finalizarConsulta"
          />
        </div>
      </template>
    </UTabs>

    <AtestadoGerarModal
      v-model:open="showAtestadoModal"
    />
  </div>
</template>
