<script setup lang="ts">
const auth = useAuthStore()

const userName = computed(() => auth.user?.nome || 'Usuário')

interface PacienteNoShow {
  id: number
  nome: string
  telefone: string
  convenio: string
  medico: string
  dataFalta: string
  status: 'nao-confirmado' | 'faltou'
  motivo: 'esquecimento' | 'transporte' | 'outros'
  recuperado: boolean
}

const pacientesNoShow = ref<PacienteNoShow[]>([
  { id: 1, nome: 'Maria da Silva', telefone: '(11) 99999-0001', convenio: 'Unimed', medico: 'Dr. Carlos Almeida', dataFalta: '2025-01-15', status: 'faltou', motivo: 'esquecimento', recuperado: true },
  { id: 2, nome: 'João Santos', telefone: '(11) 99999-0002', convenio: 'SUS', medico: 'Dra. Marina Costa', dataFalta: '2025-01-22', status: 'nao-confirmado', motivo: 'transporte', recuperado: false },
  { id: 3, nome: 'Ana Oliveira', telefone: '(11) 99999-0003', convenio: 'Bradesco Saúde', medico: 'Dr. Paulo Oliveira', dataFalta: '2025-02-05', status: 'faltou', motivo: 'outros', recuperado: true },
  { id: 4, nome: 'Carlos Pereira', telefone: '(11) 99999-0004', convenio: 'Amil', medico: 'Dr. Carlos Almeida', dataFalta: '2025-02-12', status: 'faltou', motivo: 'esquecimento', recuperado: false },
  { id: 5, nome: 'Juliana Costa', telefone: '(11) 99999-0005', convenio: 'SulAmérica', medico: 'Dra. Renata Santos', dataFalta: '2025-02-18', status: 'nao-confirmado', motivo: 'esquecimento', recuperado: false },
  { id: 6, nome: 'Pedro Almeida', telefone: '(11) 99999-0006', convenio: 'Unimed', medico: 'Dr. Paulo Oliveira', dataFalta: '2025-03-10', status: 'faltou', motivo: 'transporte', recuperado: true },
  { id: 7, nome: 'Lucia Fernandes', telefone: '(11) 99999-0007', convenio: 'SUS', medico: 'Dra. Marina Costa', dataFalta: '2025-04-03', status: 'faltou', motivo: 'esquecimento', recuperado: true },
  { id: 8, nome: 'Roberto Lima', telefone: '(11) 99999-0008', convenio: 'NotreDame', medico: 'Dr. Carlos Almeida', dataFalta: '2025-04-14', status: 'nao-confirmado', motivo: 'outros', recuperado: false },
  { id: 9, nome: 'Cristina Rocha', telefone: '(11) 99999-0009', convenio: 'Unimed', medico: 'Dra. Renata Santos', dataFalta: '2025-04-28', status: 'faltou', motivo: 'transporte', recuperado: true },
  { id: 10, nome: 'Fernando Barbosa', telefone: '(11) 99999-0010', convenio: 'Amil', medico: 'Dr. Paulo Oliveira', dataFalta: '2025-05-07', status: 'faltou', motivo: 'esquecimento', recuperado: true },
  { id: 11, nome: 'Marina Duarte', telefone: '(11) 99999-0011', convenio: 'Bradesco Saúde', medico: 'Dra. Marina Costa', dataFalta: '2025-05-19', status: 'nao-confirmado', motivo: 'esquecimento', recuperado: false },
  { id: 12, nome: 'Ricardo Campos', telefone: '(11) 99999-0012', convenio: 'SulAmérica', medico: 'Dr. Carlos Almeida', dataFalta: '2025-06-02', status: 'faltou', motivo: 'transporte', recuperado: false },
  { id: 13, nome: 'Tatiana Neves', telefone: '(11) 99999-0013', convenio: 'Unimed', medico: 'Dra. Renata Santos', dataFalta: '2025-06-15', status: 'faltou', motivo: 'esquecimento', recuperado: true },
  { id: 14, nome: 'Gustavo Martins', telefone: '(11) 99999-0014', convenio: 'SUS', medico: 'Dr. Paulo Oliveira', dataFalta: '2025-06-25', status: 'nao-confirmado', motivo: 'outros', recuperado: false },
  { id: 15, nome: 'Sandra Vieira', telefone: '(11) 99999-0015', convenio: 'NotreDame', medico: 'Dra. Marina Costa', dataFalta: '2025-07-08', status: 'faltou', motivo: 'esquecimento', recuperado: true },
  { id: 16, nome: 'Marcos Souza', telefone: '(11) 99999-0016', convenio: 'Amil', medico: 'Dr. Carlos Almeida', dataFalta: '2025-07-21', status: 'faltou', motivo: 'transporte', recuperado: true }
])

const filtro = ref('')
const filtroAno = ref('2025')
const filtroMesInicio = ref('Fevereiro')
const filtroMesFim = ref('Julho')
const filtroMedico = ref('Todos')
const filtroConvenio = ref('Todos')

const filtroAnoActive = ref('2025')
const filtroMesInicioActive = ref('Fevereiro')
const filtroMesFimActive = ref('Julho')
const filtroMedicoActive = ref('Todos')
const filtroConvenioActive = ref('Todos')

const MES_PARA_NUMERO: Record<string, string> = {
  Janeiro: '01', Fevereiro: '02', Março: '03', Abril: '04',
  Maio: '05', Junho: '06', Julho: '07', Agosto: '08',
  Setembro: '09', Outubro: '10', Novembro: '11', Dezembro: '12'
}

const filtroPeriodoInicioActive = computed(() => `${filtroAnoActive.value}-${MES_PARA_NUMERO[filtroMesInicioActive.value]}`)
const filtroPeriodoFimActive = computed(() => `${filtroAnoActive.value}-${MES_PARA_NUMERO[filtroMesFimActive.value]}`)

function aplicarFiltros() {
  filtroAnoActive.value = filtroAno.value
  filtroMesInicioActive.value = filtroMesInicio.value
  filtroMesFimActive.value = filtroMesFim.value
  filtroMedicoActive.value = filtroMedico.value
  filtroConvenioActive.value = filtroConvenio.value
}

const mesesOpcoes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

const anosDisponiveis = computed(() => {
  const anos = [...new Set(pacientesNoShow.value.map(p => p.dataFalta.substring(0, 4)))].sort()
  return anos.length ? anos : ['2025']
})

const medicosOptions = computed(() => {
  const all = [...new Set(pacientesNoShow.value.map(p => p.medico))]
  return ['Todos', ...all.sort()]
})

const conveniosOptions = computed(() => {
  const all = [...new Set(pacientesNoShow.value.map(p => p.convenio))]
  return ['Todos', ...all.sort()]
})

const dadosFiltrados = computed(() => {
  return pacientesNoShow.value.filter((p) => {
    if (filtroMedicoActive.value !== 'Todos' && p.medico !== filtroMedicoActive.value) return false
    if (filtroConvenioActive.value !== 'Todos' && p.convenio !== filtroConvenioActive.value) return false
    if (p.dataFalta.substring(0, 7) < filtroPeriodoInicioActive.value) return false
    if (p.dataFalta.substring(0, 7) > filtroPeriodoFimActive.value) return false
    return true
  })
})

const faltasPorMes = computed(() => {
  const meses = Array(12).fill(0)
  dadosFiltrados.value.forEach((p) => {
    const mes = parseInt(p.dataFalta.split('-')[1]!) - 1
    meses[mes]++
  })
  return meses
})

const MESES_LABELS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

const chartMeses = computed(() => {
  const inicio = parseInt(MES_PARA_NUMERO[filtroMesInicioActive.value]!) - 1
  const fim = parseInt(MES_PARA_NUMERO[filtroMesFimActive.value]!)
  return MESES_LABELS.slice(inicio, fim)
})

const chartDados = computed(() => {
  const inicio = parseInt(MES_PARA_NUMERO[filtroMesInicioActive.value]!) - 1
  const fim = parseInt(MES_PARA_NUMERO[filtroMesFimActive.value]!)
  return faltasPorMes.value.slice(inicio, fim)
})

const totalFiltrado = computed(() => dadosFiltrados.value.length)
const totalEsquecimento = computed(() => dadosFiltrados.value.filter(p => p.motivo === 'esquecimento').length)
const totalTransporte = computed(() => dadosFiltrados.value.filter(p => p.motivo === 'transporte').length)
const totalOutros = computed(() => dadosFiltrados.value.filter(p => p.motivo === 'outros').length)

const agendamentosRecuperados = computed(() => dadosFiltrados.value.filter(p => p.recuperado).length)

const taxaRecuperacao = computed(() => {
  const total = dadosFiltrados.value.length
  return total > 0 ? Math.round((agendamentosRecuperados.value / total) * 100) : 0
})

const totalFaltasMes = computed(() => {
  const dados = dadosFiltrados.value
  if (dados.length === 0) return 0
  const mesesUnicos = [...new Set(dados.map(p => p.dataFalta.substring(0, 7)))].sort()
  const ultimoMes = mesesUnicos[mesesUnicos.length - 1]
  return dados.filter(p => p.dataFalta.substring(0, 7) === ultimoMes).length
})

const pacientesVisiveis = computed(() => {
  let lista = dadosFiltrados.value
  const termo = filtro.value.toLowerCase().trim()
  if (termo) {
    lista = lista.filter(p => p.nome.toLowerCase().includes(termo) || p.telefone.includes(termo))
  }
  return lista
})

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
      <UCard>
        <template #title>
          <p class="text-lg font-medium">
            Filtros de Análise
          </p>
        </template>
        <div class="flex flex-wrap items-end gap-4">
          <div class="flex items-center gap-2">
            <p class="text-sm text-muted whitespace-nowrap">
              Período:
            </p>
            <UInputMenu
              v-model="filtroAno"
              :items="anosDisponiveis"
              placeholder="Ano"
              size="sm"
              class="w-24"
            />
            <UInputMenu
              v-model="filtroMesInicio"
              :items="mesesOpcoes"
              placeholder="Mês início"
              size="sm"
              class="w-36"
            />
            <span class="text-muted">até</span>
            <UInputMenu
              v-model="filtroMesFim"
              :items="mesesOpcoes"
              placeholder="Mês fim"
              size="sm"
              class="w-36"
            />
          </div>
          <UInputMenu
            v-model="filtroMedico"
            :items="medicosOptions"
            placeholder="Médico"
            size="sm"
            class="w-48"
          />
          <UInputMenu
            v-model="filtroConvenio"
            :items="conveniosOptions"
            placeholder="Convênio"
            size="sm"
            class="w-48"
          />
          <UButton
            label="Aplicar Filtros"
            icon="i-lucide-filter"
            size="sm"
            color="primary"
            @click="aplicarFiltros"
          />
        </div>
      </UCard>

      <UCard>
        <template #title>
          <p class="text-lg font-medium">
            Tendência de No-Show
          </p>
        </template>
        <ChartTendencia
          :labels="chartMeses"
          :dados="chartDados"
        />
      </UCard>

      <div class="flex flex-col lg:flex-row gap-6">
        <UCard class="w-full lg:w-1/3">
          <template #title>
            <p class="text-lg font-medium">
              Motivos de Falta
            </p>
          </template>
          <ChartMotivosFaltas
            :total="totalFiltrado"
            :esquecimento="totalEsquecimento"
            :transporte="totalTransporte"
            :outros="totalOutros"
          />
        </UCard>
        <div class="flex-1 flex items-stretch gap-4">
          <UCard class="flex-1 flex flex-col items-center py-6 gap-3">
            <UIcon name="i-lucide-trending-up" class="size-8 text-primary" />
            <p class="text-xl font-bold text-center">
              Taxa de Recuperação
            </p>
            <div class="flex-1 flex items-center justify-center w-full">
              <p class="text-5xl font-bold text-primary">
                {{ taxaRecuperacao }}%
              </p>
            </div>
          </UCard>
          <UCard class="flex-1 flex flex-col items-center py-6 gap-3">
            <UIcon name="i-lucide-calendar-x" class="size-8 text-error" />
            <p class="text-xl font-bold text-center">
              Total Faltas (mês)
            </p>
            <div class="flex-1 flex items-center justify-center w-full">
              <p class="text-5xl font-bold text-error">
                {{ totalFaltasMes }}
              </p>
            </div>
          </UCard>
          <UCard class="flex-1 flex flex-col items-center py-6 gap-3">
            <UIcon name="i-lucide-calendar-check" class="size-8 text-success" />
            <p class="text-xl font-bold text-center">
              Agend. Recuperados
            </p>
            <div class="flex-1 flex items-center justify-center w-full">
              <p class="text-5xl font-bold text-success">
                {{ agendamentosRecuperados }}
              </p>
            </div>
          </UCard>
        </div>
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
          :data="pacientesVisiveis"
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
