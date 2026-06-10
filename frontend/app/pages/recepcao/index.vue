<script setup lang="ts">
const auth = useAuthStore()
const agendamentosStore = useAgendamentosStore()

const hoje = formatarDataISO(new Date())
const medicos = ref<{ id: number, nome: string }[]>([])

onMounted(async () => {
  agendamentosStore.fetchAgendamentos(auth.activeClinicaId ?? undefined, hoje)
  const params = auth.activeClinicaId ? `?clinicaId=${auth.activeClinicaId}` : ''
  medicos.value = await $fetch<{ id: number, nome: string }[]>(`/api/medicos${params}`)
})

function nomeMedico(medicoId: number) {
  return medicos.value.find(m => m.id === medicoId)?.nome ?? `Dr(a). #${medicoId}`
}

const { agora, dataFormatada } = useRelogio(60000)

const userName = computed(() => auth.user?.nome || 'Usuário')

const colunas = [
  { accessorKey: 'horario', header: 'Horário' },
  { accessorKey: 'nome', header: 'Paciente' },
  { accessorKey: 'medico', header: 'Médico' },
  { accessorKey: 'prioridade', header: 'Prioridade' },
  { accessorKey: 'status', header: 'Status' },
  { id: 'acoes', header: 'Ações' }
]

function corPrioridade(p: string) {
  return p === 'preferencial' ? 'warning' : 'neutral'
}

function corStatus(s: string) {
  switch (s) {
    case 'agendado': return 'warning'
    case 'confirmado': return 'success'
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
    case 'confirmado': return 'Confirmado'
    case 'em_atendimento': return 'Em Atendimento'
    case 'atendido': return 'Atendido'
    case 'faltou': return 'Faltou'
    case 'cancelado': return 'Cancelado'
    default: return s
  }
}

async function confirmarAgendamento(id: number) {
  await agendamentosStore.atualizarStatus(id, 'confirmado')
}

async function cancelarAgendamento(id: number) {
  await agendamentosStore.atualizarStatus(id, 'cancelado')
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

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <UPageCard>
          <p class="text-muted font-medium">
            Total Hoje
          </p>
          <p class="text-3xl font-bold">
            {{ agendamentosStore.totalAgendamentos }}
          </p>
        </UPageCard>
        <UPageCard>
          <p class="text-muted font-medium">
            Na Fila
          </p>
          <p class="text-3xl font-bold">
            {{ agendamentosStore.fila.length }}
          </p>
        </UPageCard>
        <UPageCard>
          <p class="text-muted font-medium">
            Em Atendimento
          </p>
          <p class="text-3xl font-bold">
            {{ agendamentosStore.emAtendimento ? 1 : 0 }}
          </p>
        </UPageCard>
        <UPageCard>
          <p class="text-muted font-medium">
            Faltas
          </p>
          <p class="text-3xl font-bold">
            {{ agendamentosStore.totalFaltas }}
          </p>
        </UPageCard>
      </div>

      <UCard>
        <template #title>
          <p class="text-lg font-medium">
            Agenda do Dia
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
            <div class="flex items-center gap-1">
              <UButton
                v-if="row.original.status === 'agendado'"
                icon="i-lucide-check"
                label="Confirmar"
                size="sm"
                color="success"
                variant="solid"
                @click="confirmarAgendamento(row.original.id)"
              />
              <UButton
                v-if="row.original.status === 'agendado' || row.original.status === 'confirmado'"
                icon="i-lucide-x"
                label="Cancelar"
                size="sm"
                color="error"
                variant="soft"
                @click="cancelarAgendamento(row.original.id)"
              />
            </div>
          </template>
        </UTable>
      </UCard>
    </div>
  </div>
</template>
