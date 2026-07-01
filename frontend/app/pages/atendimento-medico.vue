<script setup lang="ts">
import type { PadraoReceita, PadraoExame, ItemMedicamento } from '~/types'
import { usePdfMake } from '~/utils/pdf'
import { buildSolicitacaoExames, buildReceita } from '~/utils/pdf-documents'

const agendamentosStore = useAgendamentosStore()
const padroesStore = usePadroesStore()
const cronometro = useCronometroStore()
const toast = useToast()
onMounted(() => {
  padroesStore.fetchAll()
  cronometro.start()
})

onBeforeRouteLeave(() => {
  salvarDraftAgora()
  if (cronometro.isRunning) cronometro.pause()
})

const agendamento = computed(() => agendamentosStore.emAtendimento)

const tabAtiva = ref('0')
const tabItems = [
  { label: 'Anamnese e Evolução', icon: 'i-lucide-notebook-text' },
  { label: 'Receita', icon: 'i-lucide-pill' },
  { label: 'Solicitar Exames', icon: 'i-lucide-flask-conical' },
  { label: 'Conclusão', icon: 'i-lucide-check-circle' }
]

type CidResultado = { cid: string, nome: string }

type AtendimentoDraft = {
  version: 1
  savedAt: string
  agendamentoId: number
  pacienteId: number | null
  tabAtiva: string
  anamneseTexto: string
  cidSelecionado: CidResultado | null
  searchCid: string
  receitaTexto: string
  remedioNome: string
  remedioDosagem: string
  remedioDetalhes: string
  examesSelecionados: string[]
  exameSelecionado: string
  buscaTermoExame: string
}

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

const examesSelecionados = ref<string[]>([])
const exameSelecionado = ref('')
const buscaTermoExame = ref('')
const sugestoesExames = ref<{ nome: string, codigo_alfanumerico: string | null, codigo_amb: string | null }[]>([])
const carregandoExames = ref(false)
const exameTemplateSelected = ref<{ label: string, value: PadraoExame }>()

let buscaExameTimeout: ReturnType<typeof setTimeout> | null = null
let examesController: AbortController | null = null
let examesRequestId = 0

watch(exameSelecionado, (val) => {
  if (val?.trim()) adicionarExame(val.trim())
})

watch(buscaTermoExame, (val) => {
  if (buscaExameTimeout) clearTimeout(buscaExameTimeout)

  if (!val || val.length < 2) {
    sugestoesExames.value = []
    return
  }

  buscaExameTimeout = setTimeout(() => {
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
    if (buscaTermoExame.value.trim() !== termo) return

    sugestoesExames.value = data.exames || []
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') return
    if (requestId !== examesRequestId) return
    sugestoesExames.value = []
  } finally {
    carregandoExames.value = false
  }
}

function adicionarExame(texto: string) {
  if (!texto?.trim()) return
  if (examesSelecionados.value.includes(texto.trim())) return
  examesSelecionados.value.push(texto.trim())
  exameSelecionado.value = ''
  buscaTermoExame.value = ''
}

function removerExameDaLista(i: number) {
  examesSelecionados.value.splice(i, 1)
}

function adicionarPadraoExame() {
  if (!exameTemplateSelected.value) return
  for (const e of exameTemplateSelected.value.value.exames) {
    examesSelecionados.value.push(e)
  }
  exameTemplateSelected.value = undefined
}

const showAtestadoModal = ref(false)
const finalizandoConsulta = ref(false)
const draftSalvoEm = ref<string | null>(null)
const draftRestaurado = ref(false)

let draftTimer: ReturnType<typeof setTimeout> | null = null
let restaurandoDraft = false
let draftDesativado = false

const DRAFT_TTL_MS = 7 * 24 * 60 * 60 * 1000

const draftKey = computed(() => {
  const ag = agendamento.value
  if (!ag) return null

  return `medsystem:atendimento-draft:${ag.id}:${ag.paciente.id}`
})

const draftSalvoHorario = computed(() => {
  if (!draftSalvoEm.value) return ''

  return new Date(draftSalvoEm.value).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  })
})

function montarDraft(): AtendimentoDraft | null {
  const ag = agendamento.value
  if (!ag) return null

  return {
    version: 1,
    savedAt: new Date().toISOString(),
    agendamentoId: ag.id,
    pacienteId: ag.paciente.id ?? null,
    tabAtiva: tabAtiva.value,
    anamneseTexto: anamneseTexto.value,
    cidSelecionado: cidSelecionado.value,
    searchCid: searchCid.value,
    receitaTexto: receitaTexto.value,
    remedioNome: remedioNome.value,
    remedioDosagem: remedioDosagem.value,
    remedioDetalhes: remedioDetalhes.value,
    examesSelecionados: [...examesSelecionados.value],
    exameSelecionado: exameSelecionado.value,
    buscaTermoExame: buscaTermoExame.value
  }
}

function draftTemConteudo(draft: AtendimentoDraft) {
  return Boolean(
    draft.anamneseTexto.trim()
    || draft.cidSelecionado
    || draft.searchCid.trim()
    || draft.receitaTexto.trim()
    || draft.remedioNome.trim()
    || draft.remedioDosagem.trim()
    || draft.remedioDetalhes.trim()
    || draft.examesSelecionados.length
    || draft.exameSelecionado.trim()
    || draft.buscaTermoExame.trim()
  )
}

function salvarDraftAgora() {
  if (!import.meta.client || !draftKey.value || draftDesativado) return

  const draft = montarDraft()
  if (!draft) return

  if (!draftTemConteudo(draft)) {
    localStorage.removeItem(draftKey.value)
    draftSalvoEm.value = null
    draftRestaurado.value = false
    return
  }

  localStorage.setItem(draftKey.value, JSON.stringify(draft))
  draftSalvoEm.value = draft.savedAt
}

function salvarDraftComDebounce() {
  if (restaurandoDraft) return
  if (draftTimer) clearTimeout(draftTimer)

  draftTimer = setTimeout(() => {
    salvarDraftAgora()
  }, 700)
}

function restaurarDraft() {
  if (!import.meta.client || !draftKey.value) return

  const raw = localStorage.getItem(draftKey.value)
  if (!raw) return

  try {
    const draft = JSON.parse(raw) as AtendimentoDraft
    const savedAt = new Date(draft.savedAt).getTime()

    if (!savedAt || Date.now() - savedAt > DRAFT_TTL_MS) {
      localStorage.removeItem(draftKey.value)
      return
    }

    restaurandoDraft = true

    tabAtiva.value = draft.tabAtiva || '0'
    anamneseTexto.value = draft.anamneseTexto || ''
    cidSelecionado.value = draft.cidSelecionado || null
    searchCid.value = draft.searchCid || ''
    receitaTexto.value = draft.receitaTexto || ''
    remedioNome.value = draft.remedioNome || ''
    remedioDosagem.value = draft.remedioDosagem || ''
    remedioDetalhes.value = draft.remedioDetalhes || ''
    examesSelecionados.value = Array.isArray(draft.examesSelecionados) ? draft.examesSelecionados : []
    exameSelecionado.value = draft.exameSelecionado || ''
    buscaTermoExame.value = draft.buscaTermoExame || ''
    draftSalvoEm.value = draft.savedAt
    draftRestaurado.value = true

    toast.add({
      title: 'Rascunho recuperado',
      description: 'Os dados digitados anteriormente foram restaurados neste atendimento.',
      color: 'success',
      icon: 'i-lucide-save'
    })
  } catch {
    localStorage.removeItem(draftKey.value)
  } finally {
    setTimeout(() => {
      restaurandoDraft = false
    }, 0)
  }
}

function limparDraft() {
  if (!import.meta.client || !draftKey.value) return

  draftDesativado = true
  localStorage.removeItem(draftKey.value)
  draftSalvoEm.value = null
  draftRestaurado.value = false
}

watch(
  [
    tabAtiva,
    anamneseTexto,
    cidSelecionado,
    searchCid,
    receitaTexto,
    remedioNome,
    remedioDosagem,
    remedioDetalhes,
    examesSelecionados,
    exameSelecionado,
    buscaTermoExame
  ],
  () => {
    salvarDraftComDebounce()
  },
  { deep: true }
)

watch(
  draftKey,
  (key) => {
    if (!key) return
    draftDesativado = false
    restaurarDraft()
  },
  { immediate: true }
)

onMounted(() => {
  window.addEventListener('beforeunload', salvarDraftAgora)
})

onUnmounted(() => {
  window.removeEventListener('beforeunload', salvarDraftAgora)

  if (draftTimer) {
    clearTimeout(draftTimer)
    salvarDraftAgora()
  }
})

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
  if (!examesSelecionados.value.length) return
  const pdfMake = await usePdfMake()
  const doc = buildSolicitacaoExames({
    paciente: agendamento.value?.paciente.nome ?? 'Paciente',
    data: new Date().toLocaleDateString('pt-BR'),
    exames: examesSelecionados.value
  })
  pdfMake.createPdf(doc).download('solicitacao-exames.pdf')
}

async function finalizarConsulta() {
  if (!agendamento.value || finalizandoConsulta.value) return

  finalizandoConsulta.value = true
  const agendamentoAtual = agendamento.value
  const duracao = cronometro.elapsed

  try {
    await agendamentosStore.atualizarStatus(agendamentoAtual.id, 'atendido', {
      anamnese: anamneseTexto.value,
      diagnostico: diagnosticoSelected.value?.value,
      medicamentos: receitaTexto.value,
      exames: examesSelecionados.value.join('\n'),
      duracao
    })
    limparDraft()
    cronometro.stop()
    await navigateTo('/dashboard')
  } catch (error) {
    console.error('Erro ao finalizar consulta', error)
    toast.add({
      title: 'Erro ao finalizar consulta',
      description: 'Não foi possível salvar os dados do atendimento. Tente novamente.',
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
  } finally {
    finalizandoConsulta.value = false
  }
}
</script>

<template>
  <div class="h-screen flex flex-col">
    <UHeader title="Consulta Atual">
      <template #right>
        <div class="flex items-center gap-2">
          <UBadge
            v-if="draftSalvoEm"
            :color="draftRestaurado ? 'success' : 'neutral'"
            variant="soft"
            icon="i-lucide-save"
          >
            Rascunho salvo às {{ draftSalvoHorario }}
          </UBadge>
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


                <div class="shrink-0 flex gap-2">
                  <UInputMenu
                    v-model="exameTemplateSelected"
                    :items="padroesStore.exames.map(p => ({ label: p.nome, value: p }))"
                    searchable
                    placeholder="Selecionar padrão de exames..."
                    class="flex-1 w-full"
                  />
                  <UButton
                    icon="i-lucide-copy-plus"
                    label="Adicionar Padrão"
                    color="secondary"
                    :disabled="!exameTemplateSelected"
                    @click="adicionarPadraoExame"
                  />
                </div>

                                <UFormField
                  label="Nome do exame"
                  class="w-full"
                >
                  <UInputMenu
                    v-model="exameSelecionado"
                    v-model:search-term="buscaTermoExame"
                    :items="sugestoesExames"
                    :loading="carregandoExames"
                    value-key="nome"
                    placeholder="Buscar exame..."
                    class="flex-1 w-full"
                    clear
                    ignore-filter
                  >
                    <template #item-label="{ item }">
                      <span class="text-sm">
                        {{ item.codigo_alfanumerico ? `${item.codigo_alfanumerico} — ` : '' }}{{ item.nome }}{{ item.codigo_amb ? ` (${item.codigo_amb})` : '' }}
                      </span>
                    </template>
                  </UInputMenu>
                </UFormField>

                <p
                  v-if="!padroesStore.exames.length"
                  class="shrink-0 text-sm text-muted italic"
                >
                  Nenhum padrão de exames cadastrado. Crie padrões em "Padrões de Solicitações".
                </p>

                <UCard
                  class="grow flex flex-col min-h-0"
                  :ui="{
                    body: 'overflow-y-auto p-3 grow',
                    header: 'shrink-0'
                  }"
                >
                  <template #title>
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Exames selecionados</span>
                      <span class="text-xs text-muted">{{ examesSelecionados.length }} exame(s)</span>
                    </div>
                  </template>

                  <div
                    v-if="examesSelecionados.length"
                    class="space-y-2"
                  >
                    <div
                      v-for="(exame, i) in examesSelecionados"
                      :key="i"
                      class="flex items-center justify-between p-3 rounded-lg border border-muted"
                    >
                      <span class="text-sm">{{ exame }}</span>
                      <UButton
                        icon="i-lucide-x"
                        color="error"
                        variant="ghost"
                        size="sm"
                        @click="removerExameDaLista(i)"
                      />
                    </div>
                  </div>
                  <p
                    v-else
                    class="text-sm text-muted italic py-4 text-center"
                  >
                    Nenhum exame adicionado.
                  </p>
                </UCard>

                <UButton
                  icon="i-lucide-file-text"
                  label="Gerar Solicitação (PDF)"
                  color="primary"
                  class="w-full shrink-0"
                  :disabled="!examesSelecionados.length"
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
              <div class="flex items-center justify-center gap-2">
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
                class="w-full p-3 text-lg font-bold"
              />
              <UButton
                icon="i-lucide-stamp"
                label="Atestado Médico"
                color="neutral"
                class="w-full p-3 text-lg font-bold"
                @click="showAtestadoModal = true"
              />
              <UButton
                icon="i-lucide-send"
                label="Encaminhamento Médico"
                color="secondary"
                class="w-full p-3 text-lg font-bold"
              />
              <UButton
                icon="i-lucide-clipboard-list"
                label="Solicitação de Procedimento"
                color="tertiary"
                class="w-full p-3 text-lg font-bold"
              />
              <UButton
                icon="i-lucide-file-text"
                label="Gerar Receita (PDF)"
                color="quaternary"
                class="w-full p-3 text-lg font-bold"
                :disabled="!receitaTexto.trim()"
                @click="tabAtiva = '1'"
              />
              <UButton
                icon="i-lucide-flask-conical"
                label="Gerar Exames (PDF)"
                color="warning"
                class="w-full p-3 text-lg font-bold"
                :disabled="!examesSelecionados.length"
                @click="tabAtiva = '2'"
              />
            </div>
          </UCard>
          <UCard
            :ui="{ body: 'flex justify-center' }"
          >
            <UButton
              icon="i-lucide-check-circle"
              label="Finalizar Consulta"
              color="success"
              size="xl"
              class="p-3 text-lg font-bold min-w-110"
              :loading="finalizandoConsulta"
              :disabled="finalizandoConsulta"
              @click="finalizarConsulta"
            />
          </UCard>
        </div>
      </template>
    </UTabs>

    <AtestadoGerarModal
      v-model:open="showAtestadoModal"
    />
  </div>
</template>
