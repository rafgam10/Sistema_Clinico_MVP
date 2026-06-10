<script setup lang="ts">
import type { AgendamentoComPaciente, AgendamentoStatus } from '~/types'

interface CardData {
  title: string
  value: number
  suffix?: string
  change?: string
  changeType?: 'success' | 'neutral' | 'primary' | 'secondary' | 'info' | 'warning' | 'error' | undefined
}

const auth = useAuthStore()
const agendamentosStore = useAgendamentosStore()
const chamadosStore = useChamadosStore()

const pacientesFila = ref<any[]>([])
const loadingFila = ref(true)

onMounted(() => {
  const hoje = formatarDataISO(new Date())
  agendamentosStore.init(auth.activeClinicaId ?? undefined, hoje, auth.user?.id)
  chamadosStore.init()
  carregarPacientesFila()
})

async function carregarPacientesFila() {
  try {
    pacientesFila.value = await $fetch('/api/pacientes-fila')
  } catch {
    pacientesFila.value = []
  } finally {
    loadingFila.value = false
  }
}

const userName = computed(() => auth.user?.nome || 'Usuário')

const { agora, dataFormatada } = useRelogio(60000)

const colunas = [
  { accessorKey: 'nome', header: 'Paciente', enableSorting: true },
  { accessorKey: 'horario', header: 'Horário' },
  { accessorKey: 'prioridade', header: 'Prioridade' },
  { accessorKey: 'status', header: 'Status' },
  { id: 'acoes', header: 'Ações' }
]

function corPrioridade(prioridade: string) {
  switch (prioridade) {
    case 'preferencial': return 'warning'
    default: return 'neutral'
  }
}

function corStatus(status: string) {
  switch (status) {
    case 'agendado':
    case 'confirmado':
      return 'warning'
    case 'em_atendimento': return 'info'
    case 'atendido': return 'success'
    case 'faltou': return 'error'
    default: return 'neutral'
  }
}

function rotuloStatus(status: string) {
  switch (status) {
    case 'agendado': return 'Agendado'
    case 'confirmado': return 'Confirmado'
    case 'em_atendimento': return 'Em Atendimento'
    case 'atendido': return 'Atendido'
    case 'faltou': return 'Faltou'
    default: return status
  }
}

const callingState = ref<{ pacienteId: number, secondsLeft: number } | null>(null)
let callingInterval: ReturnType<typeof setInterval> | null = null

onUnmounted(() => {
  if (callingInterval) clearInterval(callingInterval)
})

function isTerminal(status: AgendamentoStatus) {
  return status === 'atendido' || status === 'faltou' || status === 'cancelado'
}

function isCalling(pacienteId: number) {
  return callingState.value?.pacienteId === pacienteId
}

const temPacienteEmAtendimento = computed(() => !!agendamentosStore.emAtendimento)

function chamarPaciente(ag: AgendamentoComPaciente) {
  const salas = ['Consultório 1', 'Consultório 2', 'Consultório 3', 'Sala de Triagem', 'Sala de Curativos']
  const sala = salas[Math.floor(Math.random() * salas.length)]!
  chamadosStore.chamarPaciente(ag.paciente.id, ag.paciente.nome, sala, auth.user?.nome ?? 'Dr.')
  if (callingInterval) clearInterval(callingInterval)
  callingState.value = { pacienteId: ag.paciente.id, secondsLeft: 5 }
  callingInterval = setInterval(() => {
    if (callingState.value && callingState.value.secondsLeft > 1) {
      callingState.value = { ...callingState.value, secondsLeft: callingState.value.secondsLeft - 1 }
    } else {
      callingState.value = null
      if (callingInterval) {
        clearInterval(callingInterval)
        callingInterval = null
      }
    }
  }, 500)
}

async function faltouAgendamento(ag: AgendamentoComPaciente) {
  try {
    await agendamentosStore.atualizarStatus(ag.id, 'faltou')
  } catch {
    console.error('Erro ao marcar falta')
  }
}

async function atenderAgendamento(ag: AgendamentoComPaciente) {
  try {
    await agendamentosStore.atualizarStatus(ag.id, 'em_atendimento')
    await navigateTo('/atendimento-medico')
  } catch {
    console.error('Erro ao iniciar atendimento')
  }
}

function statusLabel(status: AgendamentoStatus) {
  switch (status) {
    case 'em_atendimento': return 'Em Atendimento'
    case 'atendido': return 'Finalizado'
    default: return 'Atender'
  }
}

function statusColor(status: AgendamentoStatus) {
  switch (status) {
    case 'em_atendimento': return 'info'
    case 'atendido': return 'success'
    default: return 'success'
  }
}

function atendimentoVariant(status: AgendamentoStatus) {
  switch (status) {
    case 'agendado':
    case 'confirmado':
      return 'solid'
    default: return 'soft'
  }
}

function atendimentoDisabled(status: AgendamentoStatus) {
  return status !== 'agendado' && status !== 'confirmado'
}

const cards = computed<CardData[]>(() => {
  const lista = agendamentosStore.agendamentos
  const total = lista.length
  const atendidos = lista.filter(a => a.status === 'atendido').length
  const naFila = lista.filter(a => a.status === 'agendado' || a.status === 'confirmado').length
  const faltas = lista.filter(a => a.status === 'faltou').length

  const tempos = lista.map(a => calcularMinutosDesde(a.horario, agora.value))
  const tempoMedio = tempos.length ? Math.round(tempos.reduce((a, b) => a + b, 0) / tempos.length) : 0

  return [
    { title: 'Pacientes do dia', value: total },
    { title: 'Atendidos', value: atendidos },
    { title: 'Na Fila', value: naFila },
    { title: 'Faltas', value: faltas },
    { title: 'Tempo médio espera', value: tempoMedio, suffix: 'm' }
  ]
})
</script>

<template>
  <div>
    <UHeader title="Dashboard">
      <template #right>
        <div class="flex items-center gap-2">
          <UBadge
            :label="userName"
            color="neutral"
            variant="soft"
          />
          <UButton
            icon="i-lucide-bell"
            color="neutral"
            variant="ghost"
            size="lg"
            aria-label="Notificações"
          />
          <UButton
            icon="i-lucide-circle-help"
            color="neutral"
            variant="ghost"
            size="lg"
            aria-label="Ajuda"
          />
          <UColorModeButton />
        </div>
      </template>
    </UHeader>
    <div class="p-6 space-y-8 bg-neutral-100 dark:bg-neutral-950 min-h-screen">
      <div>
        <p class="text-3xl font-semibold text-foreground">
          {{ getSaudacao(agora) }}, Dr. {{ userName }}
        </p>
        <p class="text-base text-muted mt-1">
          {{ dataFormatada }}. Veja o resumo do dia.
        </p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-5 gap-6">
        <UPageCard
          v-for="card in cards"
          :key="card.title"
        >
          <p class="text-muted font-medium">
            {{ card.title }}
          </p>
          <div class="flex items-center gap-2">
            <h2 class="text-3xl font-bold">
              {{ card.value }}{{ card.suffix }}
            </h2>
            <UBadge
              v-if="card.change"
              :label="card.change"
              :color="card.changeType"
              variant="soft"
            />
          </div>
        </UPageCard>
      </div>
      <UCard class="w-full">
        <template #title>
          <p class="text-lg font-medium">
            Pacientes na Fila de Espera
          </p>
        </template>

        <UTable
          :columns="colunas"
          :data="agendamentosStore.ordenados"
        >
          <template #nome-cell="{ row }">
            <div class="flex items-center gap-3">
              <UAvatar
                :alt="row.original.paciente.nome"
                color="primary"
                size="sm"
              />
              <div>
                <p class="font-medium">
                  {{ row.original.paciente.nome }}
                </p>
                <p class="text-xs text-muted">
                  {{ row.original.horario }}
                </p>
              </div>
            </div>
          </template>

          <template #prioridade-cell="{ row }">
            <UBadge
              :label="row.original.prioridade"
              :color="corPrioridade(row.original.prioridade)"
              variant="subtle"
            />
          </template>

          <template #status-cell="{ row }">
            <UBadge
              :label="rotuloStatus(row.original.status)"
              :color="corStatus(row.original.status)"
              variant="subtle"
            />
          </template>

          <template #acoes-cell="{ row }">
            <div class="flex items-center gap-1">
              <UButton
                icon="i-lucide-phone"
                :label="isCalling(row.original.paciente.id) ? String(callingState!.secondsLeft) : 'Chamar'"
                size="sm"
                class="min-w-20"
                :color="isTerminal(row.original.status) ? 'neutral' : 'primary'"
                :variant="isTerminal(row.original.status) ? 'soft' : 'solid'"
                :loading="isCalling(row.original.paciente.id)"
                :disabled="temPacienteEmAtendimento || isTerminal(row.original.status) || isCalling(row.original.paciente.id)"
                @click="chamarPaciente(row.original as AgendamentoComPaciente)"
              />
              <UButton
                icon="i-lucide-user-x"
                label="Faltou"
                size="sm"
                :color="row.original.status === 'faltou' ? 'error' : (isTerminal(row.original.status) ? 'neutral' : 'error')"
                :variant="isTerminal(row.original.status) ? 'soft' : 'solid'"
                :disabled="temPacienteEmAtendimento || isTerminal(row.original.status) || isCalling(row.original.paciente.id)"
                @click="faltouAgendamento(row.original as AgendamentoComPaciente)"
              />
              <UButton
                :icon="row.original.status === 'atendido' ? 'i-lucide-check-circle' : 'i-lucide-user-check'"
                :label="statusLabel(row.original.status)"
                size="sm"
                :color="statusColor(row.original.status)"
                :variant="atendimentoVariant(row.original.status)"
                :disabled="temPacienteEmAtendimento || atendimentoDisabled(row.original.status) || isCalling(row.original.paciente.id)"
                @click="atenderAgendamento(row.original as AgendamentoComPaciente)"
              />
            </div>
          </template>
        </UTable>
      </UCard>

      <UCard class="w-full">
        <template #title>
          <div class="flex items-center gap-2">
            <span class="size-2 rounded-full bg-primary" />
            <p class="text-lg font-medium">
              Fila de Espera — Firebird
            </p>
          </div>
        </template>

        <p v-if="loadingFila" class="text-sm text-muted py-4">
          Carregando dados do Firebird...
        </p>

        <p v-else-if="!pacientesFila.length" class="text-sm text-muted py-4">
          Nenhum paciente encontrado no Firebird.
        </p>

        <UTable
          v-else
          :columns="colunas"
          :data="pacientesFila"
        >
          <template #nome-cell="{ row }">
            <div class="flex items-center gap-3">
              <UAvatar
                :alt="String(row.original.paciente?.nome ?? '')"
                color="primary"
                size="sm"
              />
              <div>
                <p class="font-medium">
                  {{ row.original.paciente?.nome ?? '' }}
                </p>
                <p class="text-xs text-muted">
                  {{ row.original.horario ?? '' }}
                </p>
              </div>
            </div>
          </template>

          <template #prioridade-cell="{ row }">
            <UBadge
              :label="String(row.original.prioridade ?? '')"
              :color="corPrioridade(String(row.original.prioridade ?? ''))"
              variant="subtle"
            />
          </template>

          <template #status-cell="{ row }">
            <UBadge
              :label="rotuloStatus(String(row.original.status ?? ''))"
              :color="corStatus(String(row.original.status ?? ''))"
              variant="subtle"
            />
          </template>

          <template #acoes-cell="{ row }">
            <div class="flex items-center gap-1">
              <UButton
                icon="i-lucide-phone"
                label="Chamar"
                size="sm"
                class="min-w-20"
                color="neutral"
                variant="soft"
                disabled
              />
              <UButton
                icon="i-lucide-user-x"
                label="Faltou"
                size="sm"
                color="neutral"
                variant="soft"
                disabled
              />
              <UButton
                icon="i-lucide-user-check"
                label="Atender"
                size="sm"
                color="neutral"
                variant="soft"
                disabled
              />
            </div>
          </template>
        </UTable>
      </UCard>
    </div>
  </div>
</template>
