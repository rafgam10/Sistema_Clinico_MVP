<script setup lang="ts">
import type { AgendamentoComPaciente, HistoricoLocalRecord } from '~/types'
import { CalendarDate, DateFormatter, getLocalTimeZone } from '@internationalized/date'
import { usePdfMake } from '~/utils/pdf'
import {
  buildAtestadoComparecimento,
  buildReceita,
  buildSolicitacaoExames
} from '~/utils/pdf-documents'

const auth = useAuthStore()

const df = new DateFormatter('pt-BR', {
  dateStyle: 'medium'
})

function hojeComoCalendarDate() {
  const d = new Date()
  return new CalendarDate(d.getFullYear(), d.getMonth() + 1, d.getDate())
}

const buscaNome = ref('')
const filtroData = shallowRef(hojeComoCalendarDate())
const isLoading = ref(false)

const todosAgendamentos = ref<AgendamentoComPaciente[]>([])

const showAtestadoModal = ref(false)
const showEncaminhamentoModal = ref(false)
const showProcedimentoModal = ref(false)
const showHistoricoSlideover = ref(false)

const agendamentoSelecionado = ref<AgendamentoComPaciente | null>(null)
const pacienteSelecionado = computed(() => agendamentoSelecionado.value?.paciente ?? undefined)

const temBuscaNome = computed(() => buscaNome.value.trim().length > 0)

const agendamentosFiltrados = computed(() => {
  let lista = todosAgendamentos.value.filter(a => a.status === 'atendido')

  if (temBuscaNome.value) {
    const termo = buscaNome.value.trim().toLowerCase()
    lista = lista.filter(a => a.paciente.nome.toLowerCase().includes(termo))
  }

  if (!temBuscaNome.value && filtroData.value) {
    lista = lista.filter(a => a.data === filtroData.value.toString())
  }

  return lista.sort((a, b) => b.data.localeCompare(a.data) || b.horario.localeCompare(a.horario))
})

onMounted(async () => {
  await carregarAgendamentos()
})

async function carregarAgendamentos() {
  isLoading.value = true
  try {
    const params = new URLSearchParams()
    if (filtroData.value) params.set('data', filtroData.value.toString())
    const qs = params.toString()

    const raw = await $fetch<(AgendamentoComPaciente | Record<string, unknown>)[]>(`/api/agendamentos${qs ? `?${qs}` : ''}`)

    const comPaciente = (raw as AgendamentoComPaciente[]).filter(
      a => 'paciente' in a && a.medicoId === auth.user?.id
    )

    if (!temBuscaNome.value) {
      todosAgendamentos.value = comPaciente
    } else {
      const idsExistentes = new Set(todosAgendamentos.value.map(a => a.id))
      for (const ag of comPaciente) {
        if (!idsExistentes.has(ag.id)) {
          todosAgendamentos.value.push(ag)
        }
      }
    }
  } catch {
    console.error('Erro ao carregar agendamentos')
  } finally {
    isLoading.value = false
  }
}

watch(filtroData, () => {
  void carregarAgendamentos()
})

let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(buscaNome, () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    void carregarAgendamentos()
  }, 400)
})

function calcularIdade(dataNascimento: string) {
  const hoje = new Date()
  const nasc = new Date(dataNascimento)
  let idade = hoje.getFullYear() - nasc.getFullYear()
  const mes = hoje.getMonth() - nasc.getMonth()
  if (mes < 0 || (mes === 0 && hoje.getDate() < nasc.getDate())) idade--
  return idade
}

function formatarDataPtBR(dataISO: string) {
  if (!dataISO) return ''
  return new Date(dataISO + 'T12:00:00').toLocaleDateString('pt-BR')
}

function abrirHistorico(ag: AgendamentoComPaciente) {
  agendamentoSelecionado.value = ag
  showHistoricoSlideover.value = true
}

function abrirAtestado(ag: AgendamentoComPaciente) {
  agendamentoSelecionado.value = ag
  showAtestadoModal.value = true
}

function abrirEncaminhamento(ag: AgendamentoComPaciente) {
  agendamentoSelecionado.value = ag
  showEncaminhamentoModal.value = true
}

function abrirProcedimento(ag: AgendamentoComPaciente) {
  agendamentoSelecionado.value = ag
  showProcedimentoModal.value = true
}

function formatarDataParaPdf(dataISO: string) {
  if (!dataISO) return ''
  return new Date(dataISO + 'T12:00:00').toLocaleDateString('pt-BR')
}

async function buscarHistoricoLocal(pacienteId: number): Promise<HistoricoLocalRecord[]> {
  try {
    return await $fetch<HistoricoLocalRecord[]>(`/api/historico-local/${pacienteId}`)
  } catch {
    return []
  }
}

function encontrarRegistroPorData(historico: HistoricoLocalRecord[], dataISO: string): HistoricoLocalRecord | null {
  const registro = historico.find((h) => {
    if (!h.data_consulta) return false
    const dataHist = h.data_consulta.split('T')[0]
    return dataHist === dataISO
  })
  if (registro) return registro
  if (historico.length > 0) return historico[0]!
  return null
}

async function gerarAtestadoComparecimento(ag: AgendamentoComPaciente) {
  const pdfMake = await usePdfMake()
  const doc = await buildAtestadoComparecimento({
    paciente: ag.paciente.nome,
    data: formatarDataParaPdf(ag.data),
    horario: ag.horario,
    medico: auth.user?.nome,
    crm: auth.user?.crm,
    especialidade: auth.user?.especialidades?.join(', ')
  })
  pdfMake.createPdf(doc).open()
}

async function gerarSolicitacaoExames(ag: AgendamentoComPaciente) {
  const historico = await buscarHistoricoLocal(ag.paciente.id)
  const registro = encontrarRegistroPorData(historico, ag.data)

  const exames = registro?.exames?.map((e) => {
    if (typeof e === 'string') return e
    return e.nome || e.descricao || ''
  }).filter(Boolean) ?? []

  if (exames.length === 0) {
    console.warn('Nenhum exame encontrado para esta consulta')
    return
  }

  const pdfMake = await usePdfMake()
  const doc = await buildSolicitacaoExames({
    paciente: ag.paciente.nome,
    data: formatarDataParaPdf(ag.data),
    exames,
    medico: auth.user?.nome,
    crm: auth.user?.crm,
    especialidade: auth.user?.especialidades?.join(', ')
  })
  pdfMake.createPdf(doc).open()
}

async function gerarReceita(ag: AgendamentoComPaciente) {
  const historico = await buscarHistoricoLocal(ag.paciente.id)
  const registro = encontrarRegistroPorData(historico, ag.data)

  const medicamentos = registro?.medicamentos?.join('\n') ?? ''

  if (!medicamentos) {
    console.warn('Nenhum medicamento encontrado para esta consulta')
    return
  }

  const pdfMake = await usePdfMake()
  const doc = await buildReceita({
    paciente: ag.paciente.nome,
    data: formatarDataParaPdf(ag.data),
    medicamentos: [],
    texto: medicamentos,
    medico: auth.user?.nome,
    crm: auth.user?.crm,
    especialidade: auth.user?.especialidades?.join(', ')
  })
  pdfMake.createPdf(doc).open()
}

function dropdownItems(ag: AgendamentoComPaciente) {
  return [
    [
      { label: 'Atestado Médico', icon: 'i-lucide-file-text', onSelect: () => abrirAtestado(ag) },
      { label: 'Solicitação de Procedimento', icon: 'i-lucide-clipboard-list', onSelect: () => abrirProcedimento(ag) },
      { label: 'Encaminhamento Médico', icon: 'i-lucide-arrow-right-circle', onSelect: () => abrirEncaminhamento(ag) },
      { label: 'Atestado de Comparecimento', icon: 'i-lucide-calendar-check', onSelect: () => gerarAtestadoComparecimento(ag) },
      { label: 'Solicitação de Exames', icon: 'i-lucide-flask-conical', onSelect: () => gerarSolicitacaoExames(ag) },
      { label: 'Receita Médica', icon: 'i-lucide-pill', onSelect: () => gerarReceita(ag) }
    ]
  ]
}
</script>

<template>
  <div>
    <UHeader title="Meus Pacientes" />
    <div class="p-6 bg-neutral-100 dark:bg-neutral-950 min-h-screen space-y-6">
      <div class="flex flex-col sm:flex-row gap-3">
        <UInput
          v-model="buscaNome"
          icon="i-lucide-search"
          placeholder="Buscar por nome do paciente..."
          class="flex-1"
          :ui="{ root: 'w-full' }"
        />
        <UPopover>
          <UButton
            color="neutral"
            variant="subtle"
            icon="i-lucide-calendar"
          >
            {{ filtroData ? df.format(filtroData.toDate(getLocalTimeZone())) : 'Select a date' }}
          </UButton>

          <template #content>
            <UCalendar
              v-model="filtroData"
              class="p-2"
            />
          </template>
        </UPopover>
      </div>

      <div
        v-if="isLoading"
        class="flex justify-center py-12"
      >
        <UIcon
          name="i-lucide-loader-circle"
          class="size-8 animate-spin text-muted"
        />
      </div>

      <div
        v-else-if="agendamentosFiltrados.length === 0"
        class="flex flex-col items-center py-16 gap-3 text-center"
      >
        <p class="text-lg font-medium text-muted">
          Nenhum paciente encontrado
        </p>
        <p class="text-sm text-muted">
          {{ temBuscaNome ? 'Tente buscar com outro nome.' : 'Nenhum paciente atendido nesta data.' }}
        </p>
      </div>

      <div
        v-else
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
      >
        <UCard
          v-for="ag in agendamentosFiltrados"
          :key="ag.id"
          class="flex flex-col items-center text-center"
        >
          <UAvatar
            :alt="ag.paciente.nome"
            color="primary"
            size="xl"
          />

          <p class="mt-3 font-semibold text-base">
            {{ ag.paciente.nome }}
          </p>
          <p class="text-sm text-muted">
            {{ calcularIdade(ag.paciente.dataNascimento) }} anos · {{ ag.paciente.convenio }}
          </p>

          <div class="mt-2 space-y-0.5 text-xs text-muted">
            <p v-if="ag.paciente.telefone">
              <span class="inline-flex items-center gap-1">
                <UIcon
                  name="i-lucide-phone"
                  class="size-3"
                />
                {{ ag.paciente.telefone }}
              </span>
            </p>
            <p v-if="ag.paciente.email">
              <span class="inline-flex items-center gap-1">
                <UIcon
                  name="i-lucide-mail"
                  class="size-3"
                />
                {{ ag.paciente.email }}
              </span>
            </p>
          </div>

          <p
            v-if="temBuscaNome"
            class="mt-2 text-xs text-muted"
          >
            <span class="inline-flex items-center gap-1">
              <UIcon
                name="i-lucide-calendar"
                class="size-3"
              />
              {{ formatarDataPtBR(ag.data) }} · {{ ag.horario }}
            </span>
          </p>

          <div class="mt-3 flex items-center gap-2 w-full justify-center">
            <UButton
              icon="i-lucide-clock"
              color="neutral"
              variant="outline"
              size="sm"
              aria-label="Histórico"
              @click="abrirHistorico(ag)"
            />
            <UDropdownMenu
              :items="dropdownItems(ag)"
              :ui="{ content: 'w-56' }"
            >
              <UButton
                label="Ações"
                icon="i-lucide-chevron-down"
                color="primary"
                variant="outline"
                size="sm"
              />
            </UDropdownMenu>
          </div>
        </UCard>
      </div>
    </div>

    <AtestadoGerarModal
      v-model:open="showAtestadoModal"
      :paciente="pacienteSelecionado"
      :data-atendimento="agendamentoSelecionado?.data"
    />
    <EncaminhamentoGerarModal
      v-model:open="showEncaminhamentoModal"
      :paciente="pacienteSelecionado"
      :data-atendimento="agendamentoSelecionado?.data"
    />
    <ProcedimentoGerarModal
      v-model:open="showProcedimentoModal"
      :paciente="pacienteSelecionado"
      :data-atendimento="agendamentoSelecionado?.data"
    />
    <HistoricoSlideover
      v-model:open="showHistoricoSlideover"
      :paciente="pacienteSelecionado"
    />
  </div>
</template>
