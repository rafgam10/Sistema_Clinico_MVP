<script setup lang="ts">
const auth = useAuthStore()
const agendamentosStore = useAgendamentosStore()

const hoje = formatarDataISO(new Date())
const medicos = ref<{ id: number, nome: string, especialidades?: string[] }[]>([])
const checkInData = ref<{ id: number, medico: string, data: string, horario: string, paciente: string, status: string }[]>([])
const loadingCheckIn = ref(true)

onMounted(async () => {
  agendamentosStore.fetchAgendamentos(auth.activeClinicaId ?? undefined, hoje)
  const params = auth.activeClinicaId ? `?clinicaId=${auth.activeClinicaId}` : ''
  medicos.value = await $fetch<{ id: number, nome: string, especialidades?: string[] }[]>(`/api/medicos${params}`)
  try {
    checkInData.value = await $fetch('/api/check-in')
  } catch {
    checkInData.value = []
  } finally {
    loadingCheckIn.value = false
  }
})

function nomeMedico(medicoId: number) {
  return medicos.value.find(m => m.id === medicoId)?.nome ?? `Dr(a). #${medicoId}`
}

const { agora, dataFormatada } = useRelogio(60000)

const userName = computed(() => auth.user?.nome || 'Usuário')

const SLOTS_POR_MEDICO = 20

const selectedEspecialidade = ref<string | undefined>('Todos')
const selectedMedico = ref<number | null>(null)

const selectedMedicoNome = computed(() => {
  if (!selectedMedico.value) return null
  return medicos.value.find(m => m.id === selectedMedico.value)?.nome ?? ''
})

const especialidades = computed(() => {
  const all = new Set<string>()
  medicos.value.forEach(m => m.especialidades?.forEach(e => all.add(e)))
  return ['Todos', ...Array.from(all).sort()]
})

const medicosDoDia = computed(() => {
  let lista = medicos.value
  if (selectedEspecialidade.value && selectedEspecialidade.value !== 'Todos') {
    lista = lista.filter(m => m.especialidades?.includes(selectedEspecialidade.value!))
  }
  return lista.map(m => ({
    id: m.id,
    nome: m.nome,
    especialidade: m.especialidades?.[0] || '',
    pacientesCount: agendamentosStore.agendamentos.filter(a => a.medicoId === m.id).length
  }))
})

const medicosColunas = [
  { accessorKey: 'nome', header: 'Médico' },
  { accessorKey: 'especialidade', header: 'Especialidade' },
  { accessorKey: 'pacientes', header: 'Pacientes Agendados' }
]

const checkInColunas = [
  { accessorKey: 'horario', header: 'Horário' },
  { accessorKey: 'paciente', header: 'Paciente' },
  { accessorKey: 'medico', header: 'Médico' },
  { accessorKey: 'status', header: 'Status' }
]

const atendimentosColunas = [
  { accessorKey: 'horario', header: 'Horário' },
  { accessorKey: 'nome', header: 'Paciente' },
  { accessorKey: 'medico', header: 'Médico' },
  { accessorKey: 'prioridade', header: 'Prioridade' },
  { accessorKey: 'status', header: 'Status' },
  { id: 'acoes', header: 'Ações' }
]

const atendimentos = computed(() =>
  agendamentosStore.ordenados.filter((a) => {
    if (a.status === 'agendado' || a.status === 'cancelado') return false
    if (selectedMedico.value !== null && a.medicoId !== selectedMedico.value) return false
    return true
  })
)

function corStatusCheckIn(status: string) {
  return status === 'ATENDIDO' ? 'success' : 'warning'
}

function corPrioridade(p: string) {
  return p === 'preferencial' ? 'warning' : 'neutral'
}

function corStatus(s: string) {
  switch (s) {
    case 'agendado': return 'warning'
    case 'em-espera': return 'primary'
    case 'em_atendimento': return 'info'
    case 'atendido': return 'success'
    case 'faltou': return 'error'
    case 'cancelado': return 'neutral'
    default: return 'neutral'
  }
}

function rotuloStatus(s: string) {
  switch (s) {
    case 'agendado': return 'Agendado'
    case 'em-espera': return 'Em espera'
    case 'em_atendimento': return 'Em Atendimento'
    case 'atendido': return 'Atendido'
    case 'faltou': return 'Faltou'
    case 'cancelado': return 'Cancelado'
    default: return s
  }
}

async function cancelarAgendamento(id: number) {
  await agendamentosStore.atualizarStatus(id, 'cancelado')
}

function selecionarMedico(id: number) {
  selectedMedico.value = selectedMedico.value === id ? null : id
}

function limparFiltro() {
  selectedMedico.value = null
}
</script>

<template>
  <div>
    <UHeader title="Painel da Recepção">
      <template #right>
        <div class="flex items-center gap-2">
          <UBadge
            :label="userName"
            color="neutral"
            variant="soft"
          />
          <UColorModeButton />
        </div>
      </template>
    </UHeader>

    <div class="p-6 space-y-6 bg-neutral-100 dark:bg-neutral-950 min-h-screen">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-3xl font-semibold">
            {{ getSaudacao(agora) }}, {{ userName }}
          </p>
          <p class="text-base text-muted mt-1">
            {{ dataFormatada }}
          </p>
        </div>
        <div class="flex gap-2">
          <UButton
            label="Agendar Consulta"
            icon="i-lucide-plus"
            color="primary"
            to="/recepcao/agenda"
          />
          <UButton
            label="Novo Paciente"
            icon="i-lucide-user-plus"
            color="secondary"
            to="/recepcao/cadastro"
          />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ChartResumo
          :total="agendamentosStore.totalAgendamentos"
          :fila="agendamentosStore.fila.length"
          :em-atendimento="agendamentosStore.emAtendimento ? 1 : 0"
          :atendidos="agendamentosStore.totalAtendidos"
          :faltas="agendamentosStore.totalFaltas"
        />

        <UCard>
          <template #title>
            <div class="flex items-center justify-between">
              <p class="text-lg font-medium">
                Médicos do Dia
              </p>
              <UInputMenu
                v-model="selectedEspecialidade"
                :items="especialidades"
                placeholder="Filtrar por especialidade"
                clearable
                size="sm"
                class="w-48"
              />
            </div>
          </template>

          <UTable
            :columns="medicosColunas"
            :data="medicosDoDia"
          >
            <template #nome-cell="{ row }">
              <div
                class="flex items-center gap-3 cursor-pointer"
                @click="selecionarMedico(row.original.id)"
              >
                <UAvatar
                  :alt="row.original.nome"
                  color="primary"
                  size="sm"
                />
                <p
                  class="font-medium"
                  :class="selectedMedico === row.original.id ? 'text-primary' : ''"
                >
                  {{ row.original.nome }}
                </p>
              </div>
            </template>

            <template #especialidade-cell="{ row }">
              <span class="text-sm">{{ row.original.especialidade }}</span>
            </template>

            <template #pacientes-cell="{ row }">
              <UBadge
                :label="`${row.original.pacientesCount}/${SLOTS_POR_MEDICO}`"
                :color="row.original.pacientesCount >= SLOTS_POR_MEDICO ? 'error' : 'neutral'"
                variant="soft"
              />
            </template>
          </UTable>
        </UCard>
      </div>

      <UCard>
        <template #title>
          <div class="flex items-center justify-between">
            <p class="text-lg font-medium">
              {{ selectedMedico ? `Atendimentos de ${selectedMedicoNome}` : 'Atendimentos do Dia' }}
            </p>
            <UButton
              v-if="selectedMedico"
              icon="i-lucide-x"
              size="sm"
              color="neutral"
              variant="ghost"
              @click="limparFiltro"
            />
          </div>
        </template>

        <UTable
          :columns="atendimentosColunas"
          :data="atendimentos"
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
                  {{ row.original.descricao }}
                </p>
              </div>
            </div>
          </template>

          <template #medico-cell="{ row }">
            <span class="text-sm">{{ nomeMedico(row.original.medicoId) }}</span>
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
            <UButton
              v-if="row.original.status === 'em-espera'"
              icon="i-lucide-x"
              label="Cancelar"
              size="sm"
              color="error"
              variant="soft"
              @click="cancelarAgendamento(row.original.id)"
            />
          </template>
        </UTable>
      </UCard>

      <UCard class="w-full">
        <template #title>
          <div class="flex items-center gap-2">
            <span class="size-2 rounded-full bg-primary" />
            <p class="text-lg font-medium">
              Atendimentos — Firebird
            </p>
          </div>
        </template>

        <p
          v-if="loadingCheckIn"
          class="text-sm text-muted py-4"
        >
          Carregando dados do Firebird...
        </p>

        <p
          v-else-if="!checkInData.length"
          class="text-sm text-muted py-4"
        >
          Nenhum atendimento encontrado no Firebird.
        </p>

        <UTable
          v-else
          :columns="checkInColunas"
          :data="checkInData"
        >
          <template #paciente-cell="{ row }">
            <div class="flex items-center gap-3">
              <UAvatar
                :alt="row.original.paciente"
                color="primary"
                size="sm"
              />
              <p class="font-medium">
                {{ row.original.paciente }}
              </p>
            </div>
          </template>

          <template #medico-cell="{ row }">
            <span class="text-sm">{{ row.original.medico }}</span>
          </template>

          <template #status-cell="{ row }">
            <UBadge
              :label="row.original.status"
              :color="corStatusCheckIn(row.original.status)"
              variant="subtle"
            />
          </template>
        </UTable>
      </UCard>
    </div>
  </div>
</template>
