<script setup lang="ts">
const auth = useAuthStore()

const userName = computed(() => auth.user?.nome || 'Usuário')

interface PacienteNoShow {
  id: number
  nome: string
  telefone: string
  convenio: string
  dataFalta: string
  status: 'nao-confirmado' | 'faltou'
}

const pacientesNoShow = ref<PacienteNoShow[]>([
  { id: 1, nome: 'Maria da Silva', telefone: '(11) 99999-0001', convenio: 'Unimed', dataFalta: '2025-06-15', status: 'faltou' },
  { id: 2, nome: 'João Santos', telefone: '(11) 99999-0002', convenio: 'SUS', dataFalta: '2025-06-14', status: 'nao-confirmado' },
  { id: 3, nome: 'Ana Oliveira', telefone: '(11) 99999-0003', convenio: 'Bradesco Saúde', dataFalta: '2025-06-14', status: 'faltou' },
  { id: 4, nome: 'Carlos Pereira', telefone: '(11) 99999-0004', convenio: 'Amil', dataFalta: '2025-06-13', status: 'nao-confirmado' },
  { id: 5, nome: 'Juliana Costa', telefone: '(11) 99999-0005', convenio: 'SulAmérica', dataFalta: '2025-06-13', status: 'nao-confirmado' },
  { id: 6, nome: 'Pedro Almeida', telefone: '(11) 99999-0006', convenio: 'Unimed', dataFalta: '2025-06-12', status: 'faltou' },
  { id: 7, nome: 'Lucia Fernandes', telefone: '(11) 99999-0007', convenio: 'SUS', dataFalta: '2025-06-12', status: 'nao-confirmado' },
  { id: 8, nome: 'Roberto Lima', telefone: '(11) 99999-0008', convenio: 'NotreDame', dataFalta: '2025-06-11', status: 'faltou' }
])

const filtro = ref('')

const pacientesFiltrados = computed(() => {
  const termo = filtro.value.toLowerCase().trim()
  if (!termo) return pacientesNoShow.value
  return pacientesNoShow.value.filter(p =>
    p.nome.toLowerCase().includes(termo)
    || p.telefone.includes(termo)
  )
})

const total = computed(() => pacientesNoShow.value.length)
const naoConfirmados = computed(() => pacientesNoShow.value.filter(p => p.status === 'nao-confirmado').length)
const faltas = computed(() => pacientesNoShow.value.filter(p => p.status === 'faltou').length)

const colunas = [
  { accessorKey: 'paciente', header: 'Paciente' },
  { accessorKey: 'telefone', header: 'Telefone' },
  { accessorKey: 'dataFalta', header: 'Data da Falta' },
  { accessorKey: 'status', header: 'Status' },
  { id: 'acoes', header: 'Ações' }
]

function corStatus(status: string) {
  switch (status) {
    case 'nao-confirmado': return 'warning'
    case 'faltou': return 'error'
    default: return 'neutral'
  }
}

function rotuloStatus(status: string) {
  switch (status) {
    case 'nao-confirmado': return 'Não confirmado'
    case 'faltou': return 'Faltou'
    default: return status
  }
}

function formatarData(iso: string) {
  const [ano, mes, dia] = iso.split('-')
  return `${dia}/${mes}/${ano}`
}

function ligar(paciente: PacienteNoShow) {
  console.log('Ligar para', paciente.nome, paciente.telefone)
}

function reagendar(paciente: PacienteNoShow) {
  console.log('Reagendar', paciente.nome)
}

function recusou(paciente: PacienteNoShow) {
  pacientesNoShow.value = pacientesNoShow.value.filter(p => p.id !== paciente.id)
}
</script>

<template>
  <div>
    <UHeader title="No-show">
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
    <div class="p-6 space-y-8 bg-neutral-100 dark:bg-neutral-950 min-h-screen">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ChartRecuperacao
          :total="total"
          :nao-confirmado="naoConfirmados"
          :recuperados="0"
          :faltas="faltas"
        />
        <UPageCard>
          <div class="flex gap-2 items-center">
            <div class="size-3 bg-azu-500 rounded-full" />
            <p class="text-xl font-medium">
              Total: {{ total }} pacientes
            </p>
          </div>
          <div class="flex gap-2 items-center">
            <div class="size-3 bg-warning rounded-full" />
            <p class="text-xl font-medium">
              Não confirmados: {{ naoConfirmados }}
            </p>
          </div>
          <div class="flex gap-2 items-center">
            <div class="size-3 bg-error rounded-full" />
            <p class="text-xl font-medium">
              Faltas: {{ faltas }}
            </p>
          </div>
          <div class="flex gap-2 items-center">
            <div class="size-3 bg-success rounded-full" />
            <p class="text-xl font-medium">
              Recuperados: 0
            </p>
          </div>
        </UPageCard>
      </div>
      <UCard class="w-full">
        <template #title>
          <div class="flex items-center justify-between">
            <p class="text-lg font-medium">
              Resgate de pacientes
            </p>
            <UInput
              v-model="filtro"
              placeholder="Filtrar por paciente ou telefone..."
              size="sm"
              class="w-72"
            />
          </div>
        </template>

        <UTable
          :columns="colunas"
          :data="pacientesFiltrados"
        >
          <template #paciente-cell="{ row }">
            <div class="flex items-center gap-3">
              <UAvatar
                :alt="row.original.nome"
                color="primary"
                size="sm"
              />
              <div>
                <p class="font-medium">
                  {{ row.original.nome }}
                </p>
                <p class="text-xs text-muted">
                  {{ row.original.convenio }}
                </p>
              </div>
            </div>
          </template>

          <template #telefone-cell="{ row }">
            <span class="text-sm">{{ row.original.telefone }}</span>
          </template>

          <template #dataFalta-cell="{ row }">
            <span class="text-sm">{{ formatarData(row.original.dataFalta) }}</span>
          </template>

          <template #status-cell="{ row }">
            <UBadge
              :label="rotuloStatus(row.original.status)"
              :color="corStatus(row.original.status)"
              variant="subtle"
            />
          </template>

          <template #acoes-cell="{ row }">
            <div class="flex items-center gap-2">
              <UButton
                icon="i-lucide-phone"
                label="Ligar"
                size="sm"
                color="primary"
                variant="soft"
                @click="ligar(row.original)"
              />
              <UButton
                icon="i-lucide-calendar-plus"
                label="Reagendar"
                size="sm"
                color="warning"
                variant="soft"
                @click="reagendar(row.original)"
              />
              <UButton
                icon="i-lucide-x-circle"
                label="Recusou"
                size="sm"
                color="error"
                variant="soft"
                @click="recusou(row.original)"
              />
            </div>
          </template>
        </UTable>
      </UCard>
    </div>
  </div>
</template>
