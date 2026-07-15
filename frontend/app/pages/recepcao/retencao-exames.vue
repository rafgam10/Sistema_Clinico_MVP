<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui/'
import { getPaginationRowModel } from '@tanstack/vue-table'

interface ExameRetencao {
  id: number
  paciente: string
  cpf: string
  prontuario: string
  convenio: string
  medico: string
  crm: string
  especialidade: string
  exame: string
  codigoTuss: string
  dataSolicitacao: string
  diasEmAberto: number
  status: 'solicitado' | 'pendente-agendamento' | 'agendado-internamente' | 'realizado-internamente' | 'realizado-externamente' | 'sem-contato' | 'recusou' | 'expirado'
  valorEstimado: number
  valorRealizado: number | null
  ultimoContato: string | null
  responsavel: string | null
  telefone: string
}

const mockExames: ExameRetencao[] = [
  { id: 1, paciente: 'João Carlos Silva', cpf: '123.456.789-00', prontuario: 'PRT-001', convenio: 'Unimed', medico: 'Dr. Carlos Almeida', crm: 'CRM-SP 12345', especialidade: 'Cardiologia', exame: 'Eletrocardiograma', codigoTuss: '40801010', dataSolicitacao: '2026-04-10', diasEmAberto: 95, status: 'expirado', valorEstimado: 120, valorRealizado: null, ultimoContato: '2026-05-15', responsavel: 'Ana Oliveira', telefone: '(11) 98765-4321' },
  { id: 2, paciente: 'Maria Aparecida Santos', cpf: '987.654.321-00', prontuario: 'PRT-002', convenio: 'Bradesco Saúde', medico: 'Dra. Patricia Mendes', crm: 'CRM-SP 23456', especialidade: 'Ginecologia', exame: 'Ultrassom Transvaginal', codigoTuss: '40901111', dataSolicitacao: '2026-05-20', diasEmAberto: 55, status: 'pendente-agendamento', valorEstimado: 280, valorRealizado: null, ultimoContato: '2026-06-10', responsavel: 'Ana Oliveira', telefone: '(11) 97654-3210' },
  { id: 3, paciente: 'Pedro Henrique Lima', cpf: '456.789.123-00', prontuario: 'PRT-003', convenio: 'Amil', medico: 'Dr. Roberto Fernandes', crm: 'CRM-SP 34567', especialidade: 'Ortopedia', exame: 'Ressonância Magnética Joelho', codigoTuss: '40903030', dataSolicitacao: '2026-06-01', diasEmAberto: 43, status: 'pendente-agendamento', valorEstimado: 850, valorRealizado: null, ultimoContato: '2026-06-20', responsavel: 'Carlos Santos', telefone: '(11) 96543-2109' },
  { id: 4, paciente: 'Ana Beatriz Costa', cpf: '321.654.987-00', prontuario: 'PRT-004', convenio: 'SulAmérica', medico: 'Dra. Patricia Mendes', crm: 'CRM-SP 23456', especialidade: 'Ginecologia', exame: 'Papanicolau', codigoTuss: '40902020', dataSolicitacao: '2026-06-15', diasEmAberto: 29, status: 'agendado-internamente', valorEstimado: 90, valorRealizado: null, ultimoContato: '2026-07-01', responsavel: 'Ana Oliveira', telefone: '(11) 95555-1234' },
  { id: 5, paciente: 'Carlos Eduardo Nunes', cpf: '159.753.486-00', prontuario: 'PRT-005', convenio: 'NotreDame Intermédica', medico: 'Dr. Roberto Fernandes', crm: 'CRM-SP 34567', especialidade: 'Ortopedia', exame: 'Raio-X Coluna Lombar', codigoTuss: '40802020', dataSolicitacao: '2026-06-10', diasEmAberto: 34, status: 'realizado-internamente', valorEstimado: 180, valorRealizado: 180, ultimoContato: '2026-06-25', responsavel: 'Ana Oliveira', telefone: '(11) 98888-7777' },
  { id: 6, paciente: 'Fernanda Lima Rocha', cpf: '741.852.963-00', prontuario: 'PRT-006', convenio: 'Unimed', medico: 'Dr. Carlos Almeida', crm: 'CRM-SP 12345', especialidade: 'Cardiologia', exame: 'Teste Ergométrico', codigoTuss: '40803030', dataSolicitacao: '2026-06-25', diasEmAberto: 19, status: 'agendado-internamente', valorEstimado: 350, valorRealizado: null, ultimoContato: '2026-07-05', responsavel: 'Ana Oliveira', telefone: '(11) 93456-7890' },
  { id: 7, paciente: 'Ricardo Barbosa', cpf: '852.963.741-00', prontuario: 'PRT-007', convenio: 'Hapvida', medico: 'Dr. Fernando Costa', crm: 'CRM-SP 45678', especialidade: 'Dermatologia', exame: 'Biópsia de Pele', codigoTuss: '40904040', dataSolicitacao: '2026-05-05', diasEmAberto: 70, status: 'sem-contato', valorEstimado: 450, valorRealizado: null, ultimoContato: '2026-05-20', responsavel: 'Carlos Santos', telefone: '(11) 91234-5678' },
  { id: 8, paciente: 'Juliana Castro', cpf: '147.258.369-00', prontuario: 'PRT-008', convenio: 'Bradesco Saúde', medico: 'Dr. Carlos Almeida', crm: 'CRM-SP 12345', especialidade: 'Cardiologia', exame: 'Holter 24h', codigoTuss: '40805050', dataSolicitacao: '2026-06-20', diasEmAberto: 24, status: 'realizado-internamente', valorEstimado: 250, valorRealizado: 250, ultimoContato: '2026-07-01', responsavel: 'Ana Oliveira', telefone: '(11) 99887-6655' },
  { id: 9, paciente: 'Luciana Pereira Martins', cpf: '369.258.147-00', prontuario: 'PRT-009', convenio: 'SulAmérica', medico: 'Dr. Roberto Fernandes', crm: 'CRM-SP 34567', especialidade: 'Ortopedia', exame: 'Ultrassom Ombro', codigoTuss: '40905050', dataSolicitacao: '2026-07-01', diasEmAberto: 13, status: 'solicitado', valorEstimado: 220, valorRealizado: null, ultimoContato: null, responsavel: null, telefone: '(11) 97777-8888' },
  { id: 10, paciente: 'Rafael Torres', cpf: '753.951.852-00', prontuario: 'PRT-010', convenio: 'NotreDame Intermédica', medico: 'Dra. Juliana Costa', crm: 'CRM-SP 56789', especialidade: 'Dermatologia', exame: 'Exame Dermatopatológico', codigoTuss: '40906060', dataSolicitacao: '2026-05-15', diasEmAberto: 60, status: 'recusou', valorEstimado: 180, valorRealizado: null, ultimoContato: '2026-06-01', responsavel: 'Ana Oliveira', telefone: '(11) 96666-5555' },
  { id: 11, paciente: 'Beatriz Almeida Santos', cpf: '951.753.852-00', prontuario: 'PRT-011', convenio: 'Unimed', medico: 'Dr. Carlos Almeida', crm: 'CRM-SP 12345', especialidade: 'Cardiologia', exame: 'Ecocardiograma', codigoTuss: '40804040', dataSolicitacao: '2026-07-05', diasEmAberto: 9, status: 'solicitado', valorEstimado: 380, valorRealizado: null, ultimoContato: null, responsavel: null, telefone: '(11) 94444-3333' },
  { id: 12, paciente: 'Thiago Barbosa', cpf: '654.321.987-00', prontuario: 'PRT-012', convenio: 'Amil', medico: 'Dr. Roberto Fernandes', crm: 'CRM-SP 34567', especialidade: 'Ortopedia', exame: 'Densitometria Óssea', codigoTuss: '40806060', dataSolicitacao: '2026-04-20', diasEmAberto: 85, status: 'expirado', valorEstimado: 200, valorRealizado: null, ultimoContato: '2026-05-10', responsavel: 'Carlos Santos', telefone: '(11) 92222-1111' },
  { id: 13, paciente: 'Camila Fernandes', cpf: '852.147.963-00', prontuario: 'PRT-013', convenio: 'Unimed', medico: 'Dra. Juliana Costa', crm: 'CRM-SP 56789', especialidade: 'Dermatologia', exame: 'Patch Teste (Alergia)', codigoTuss: '40907070', dataSolicitacao: '2026-06-28', diasEmAberto: 16, status: 'agendado-internamente', valorEstimado: 160, valorRealizado: null, ultimoContato: '2026-07-08', responsavel: 'Ana Oliveira', telefone: '(11) 95544-3322' },
  { id: 14, paciente: 'Eduardo Gomes', cpf: '258.369.147-00', prontuario: 'PRT-014', convenio: 'Bradesco Saúde', medico: 'Dra. Patricia Mendes', crm: 'CRM-SP 23456', especialidade: 'Ginecologia', exame: 'Mamografia Digital', codigoTuss: '40908080', dataSolicitacao: '2026-05-10', diasEmAberto: 65, status: 'realizado-externamente', valorEstimado: 180, valorRealizado: null, ultimoContato: '2026-06-05', responsavel: 'Ana Oliveira', telefone: '(11) 93333-2222' },
  { id: 15, paciente: 'Larissa Dias', cpf: '753.159.486-00', prontuario: 'PRT-015', convenio: 'Hapvida', medico: 'Dra. Juliana Costa', crm: 'CRM-SP 56789', especialidade: 'Dermatologia', exame: 'Crioterapia', codigoTuss: '40909090', dataSolicitacao: '2026-06-15', diasEmAberto: 29, status: 'realizado-internamente', valorEstimado: 150, valorRealizado: 150, ultimoContato: '2026-06-28', responsavel: 'Ana Oliveira', telefone: '(11) 91111-2222' },
  { id: 16, paciente: 'Fábio Azevedo', cpf: '456.123.789-00', prontuario: 'PRT-016', convenio: 'SulAmérica', medico: 'Dr. Fernando Costa', crm: 'CRM-SP 45678', especialidade: 'Dermatologia', exame: 'Exame Micológico', codigoTuss: '40910010', dataSolicitacao: '2026-06-05', diasEmAberto: 39, status: 'sem-contato', valorEstimado: 130, valorRealizado: null, ultimoContato: '2026-06-18', responsavel: 'Carlos Santos', telefone: '(11) 98888-9999' },
  { id: 17, paciente: 'Aline Cristina Souza', cpf: '159.486.753-00', prontuario: 'PRT-017', convenio: 'NotreDame Intermédica', medico: 'Dra. Patricia Mendes', crm: 'CRM-SP 23456', especialidade: 'Ginecologia', exame: 'Colposcopia', codigoTuss: '40911111', dataSolicitacao: '2026-07-08', diasEmAberto: 6, status: 'solicitado', valorEstimado: 200, valorRealizado: null, ultimoContato: null, responsavel: null, telefone: '(11) 95555-4444' },
  { id: 18, paciente: 'Marcos Vinícius Teixeira', cpf: '852.963.741-00', prontuario: 'PRT-018', convenio: 'Unimed', medico: 'Dr. Carlos Almeida', crm: 'CRM-SP 12345', especialidade: 'Cardiologia', exame: 'MAPA 24h', codigoTuss: '40807070', dataSolicitacao: '2026-05-25', diasEmAberto: 50, status: 'realizado-internamente', valorEstimado: 300, valorRealizado: 300, ultimoContato: '2026-06-10', responsavel: 'Ana Oliveira', telefone: '(11) 94444-5555' },
  { id: 19, paciente: 'Tatiane Oliveira', cpf: '357.159.486-00', prontuario: 'PRT-019', convenio: 'Amil', medico: 'Dr. Fernando Costa', crm: 'CRM-SP 45678', especialidade: 'Dermatologia', exame: 'Exame de Sangue (PSA)', codigoTuss: '40808080', dataSolicitacao: '2026-07-10', diasEmAberto: 4, status: 'solicitado', valorEstimado: 80, valorRealizado: null, ultimoContato: null, responsavel: null, telefone: '(11) 97777-6666' },
  { id: 20, paciente: 'Gustavo Henrique Dias', cpf: '486.753.159-00', prontuario: 'PRT-020', convenio: 'Unimed', medico: 'Dr. Carlos Almeida', crm: 'CRM-SP 12345', especialidade: 'Cardiologia', exame: 'Ecocardiograma com Doppler', codigoTuss: '40809090', dataSolicitacao: '2026-06-12', diasEmAberto: 32, status: 'realizado-internamente', valorEstimado: 420, valorRealizado: 420, ultimoContato: '2026-06-28', responsavel: 'Ana Oliveira', telefone: '(11) 96666-7777' },
  { id: 21, paciente: 'Aline Cristina Souza', cpf: '159.753.486-00', prontuario: 'PRT-021', convenio: 'NotreDame Intermédica', medico: 'Dra. Patricia Mendes', crm: 'CRM-SP 23456', especialidade: 'Ginecologia', exame: 'Ultrassom Transvaginal', codigoTuss: '40901111', dataSolicitacao: '2026-07-12', diasEmAberto: 2, status: 'solicitado', valorEstimado: 280, valorRealizado: null, ultimoContato: null, responsavel: null, telefone: '(11) 97788-6655' },
  { id: 22, paciente: 'Sérgio Menezes', cpf: '357.951.486-00', prontuario: 'PRT-022', convenio: 'Bradesco Saúde', medico: 'Dr. Roberto Fernandes', crm: 'CRM-SP 34567', especialidade: 'Ortopedia', exame: 'Ressonância Magnética Ombro', codigoTuss: '40912121', dataSolicitacao: '2026-05-30', diasEmAberto: 45, status: 'agendado-internamente', valorEstimado: 780, valorRealizado: null, ultimoContato: '2026-06-15', responsavel: 'Ana Oliveira', telefone: '(11) 91122-3344' },
  { id: 23, paciente: 'Vanessa Cristina Dias', cpf: '486.159.753-00', prontuario: 'PRT-023', convenio: 'Hapvida', medico: 'Dra. Patricia Mendes', crm: 'CRM-SP 23456', especialidade: 'Ginecologia', exame: 'Ultrassom Mama', codigoTuss: '40913131', dataSolicitacao: '2026-06-18', diasEmAberto: 26, status: 'realizado-internamente', valorEstimado: 240, valorRealizado: 240, ultimoContato: '2026-06-30', responsavel: 'Ana Oliveira', telefone: '(11) 97888-7766' },
  { id: 24, paciente: 'Daniel Oliveira Santos', cpf: '951.357.852-00', prontuario: 'PRT-024', convenio: 'Bradesco Saúde', medico: 'Dr. Roberto Fernandes', crm: 'CRM-SP 34567', especialidade: 'Ortopedia', exame: 'Ultrassom Ombro', codigoTuss: '40905050', dataSolicitacao: '2026-04-05', diasEmAberto: 100, status: 'expirado', valorEstimado: 220, valorRealizado: null, ultimoContato: '2026-05-01', responsavel: 'Carlos Santos', telefone: '(11) 90000-1111' },
  { id: 25, paciente: 'Priscila Andrade', cpf: '654.987.321-00', prontuario: 'PRT-025', convenio: 'Bradesco Saúde', medico: 'Dra. Patricia Mendes', crm: 'CRM-SP 23456', especialidade: 'Ginecologia', exame: 'Ultrassom Transvaginal', codigoTuss: '40901111', dataSolicitacao: '2026-07-14', diasEmAberto: 0, status: 'solicitado', valorEstimado: 280, valorRealizado: null, ultimoContato: null, responsavel: null, telefone: '(11) 92345-6789' },
  { id: 26, paciente: 'Renato Augusto Lima', cpf: '357.159.852-00', prontuario: 'PRT-026', convenio: 'Bradesco Saúde', medico: 'Dr. Carlos Almeida', crm: 'CRM-SP 12345', especialidade: 'Cardiologia', exame: 'Eletrocardiograma', codigoTuss: '40801010', dataSolicitacao: '2026-06-22', diasEmAberto: 22, status: 'realizado-internamente', valorEstimado: 120, valorRealizado: 120, ultimoContato: '2026-07-05', responsavel: 'Ana Oliveira', telefone: '(11) 93456-7890' },
  { id: 27, paciente: 'Jéssica Martins', cpf: '753.486.159-00', prontuario: 'PRT-027', convenio: 'SulAmérica', medico: 'Dra. Juliana Costa', crm: 'CRM-SP 56789', especialidade: 'Dermatologia', exame: 'Exame de Sangue (TSH)', codigoTuss: '40810010', dataSolicitacao: '2026-07-02', diasEmAberto: 12, status: 'pendente-agendamento', valorEstimado: 60, valorRealizado: null, ultimoContato: '2026-07-09', responsavel: 'Ana Oliveira', telefone: '(11) 97888-5544' },
  { id: 28, paciente: 'Wagner Santos', cpf: '159.357.486-00', prontuario: 'PRT-028', convenio: 'NotreDame Intermédica', medico: 'Dr. Roberto Fernandes', crm: 'CRM-SP 34567', especialidade: 'Ortopedia', exame: 'Raio-X Quadril', codigoTuss: '40802020', dataSolicitacao: '2026-06-08', diasEmAberto: 36, status: 'realizado-internamente', valorEstimado: 150, valorRealizado: 150, ultimoContato: '2026-06-22', responsavel: 'Ana Oliveira', telefone: '(11) 98877-6655' },
  { id: 29, paciente: 'Débora Cristina Faria', cpf: '357.486.159-00', prontuario: 'PRT-029', convenio: 'Unimed', medico: 'Dra. Patricia Mendes', crm: 'CRM-SP 23456', especialidade: 'Ginecologia', exame: 'Preventivo (Citopatológico)', codigoTuss: '40914141', dataSolicitacao: '2026-07-11', diasEmAberto: 3, status: 'solicitado', valorEstimado: 70, valorRealizado: null, ultimoContato: null, responsavel: null, telefone: '(11) 93444-5566' },
  { id: 30, paciente: 'Márcio Roberto Lima', cpf: '486.951.357-00', prontuario: 'PRT-030', convenio: 'Bradesco Saúde', medico: 'Dr. Carlos Almeida', crm: 'CRM-SP 12345', especialidade: 'Cardiologia', exame: 'Eletrocardiograma', codigoTuss: '40801010', dataSolicitacao: '2026-05-18', diasEmAberto: 57, status: 'realizado-internamente', valorEstimado: 120, valorRealizado: 120, ultimoContato: '2026-06-05', responsavel: 'Ana Oliveira', telefone: '(11) 95566-7788' }
]

const graficosMock = {
  conversaoPorMedico: [
    { medico: 'Dr. Carlos Almeida', taxa: 45, realizados: 5, solicitados: 11 },
    { medico: 'Dra. Patricia Mendes', taxa: 30, realizados: 3, solicitados: 10 },
    { medico: 'Dr. Roberto Fernandes', taxa: 25, realizados: 2, solicitados: 8 },
    { medico: 'Dr. Fernando Costa', taxa: 20, realizados: 1, solicitados: 5 },
    { medico: 'Dra. Juliana Costa', taxa: 35, realizados: 2, solicitados: 6 }
  ],
  examesMaisSolicitados: [
    { exame: 'Eletrocardiograma', total: 5 },
    { exame: 'Ultrassom Transvaginal', total: 4 },
    { exame: 'Ressonância Magnética', total: 3 },
    { exame: 'Ultrassom Abdome', total: 3 },
    { exame: 'Ecocardiograma', total: 2 },
    { exame: 'Hemograma Completo', total: 2 },
    { exame: 'Mamografia', total: 2 },
    { exame: 'Densitometria Óssea', total: 2 },
    { exame: 'Holter 24h', total: 2 },
    { exame: 'Raio-X Coluna', total: 2 }
  ],
  oportunidadeFinanceira: [
    { convenio: 'Unimed', valor: 1520 },
    { convenio: 'Bradesco Saúde', valor: 1280 },
    { convenio: 'Amil', valor: 850 },
    { convenio: 'SulAmérica', valor: 620 },
    { convenio: 'NotreDame Intermédica', valor: 450 },
    { convenio: 'Hapvida', valor: 300 }
  ],
  porEspecialidade: [
    { label: 'Cardiologia', total: 11 },
    { label: 'Ginecologia', total: 10 },
    { label: 'Ortopedia', total: 8 },
    { label: 'Dermatologia', total: 6 },
    { label: 'Clínica Geral', total: 5 }
  ]
}

const hoje = new Date()
const anoAtual = String(hoje.getFullYear())
const mesesOpcoes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
const mesAtualNome = mesesOpcoes[hoje.getMonth()] || 'Janeiro'

const MES_PARA_NUMERO: Record<string, string> = {
  Janeiro: '01', Fevereiro: '02', Março: '03', Abril: '04',
  Maio: '05', Junho: '06', Julho: '07', Agosto: '08',
  Setembro: '09', Outubro: '10', Novembro: '11', Dezembro: '12'
}

const filtroAno = ref(anoAtual)
const filtroMesInicio = ref(mesAtualNome)
const filtroMesFim = ref(mesAtualNome)
const filtroMedico = ref('Todos')
const filtroEspecialidade = ref('Todos')
const filtroConvenio = ref('Todos')
const filtroStatus = ref('Todos')
const filtroExame = ref('')
const filtroPaciente = ref('')

const filtroAnoActive = ref(anoAtual)
const filtroMesInicioActive = ref(mesAtualNome)
const filtroMesFimActive = ref(mesAtualNome)
const filtroMedicoActive = ref('Todos')
const filtroEspecialidadeActive = ref('Todos')
const filtroConvenioActive = ref('Todos')
const filtroStatusActive = ref('Todos')

const filtroPeriodoInicioActive = computed(() => `${filtroAnoActive.value}-${MES_PARA_NUMERO[filtroMesInicioActive.value]}`)
const filtroPeriodoFimActive = computed(() => `${filtroAnoActive.value}-${MES_PARA_NUMERO[filtroMesFimActive.value]}`)

function aplicarFiltros() {
  filtroAnoActive.value = filtroAno.value
  filtroMesInicioActive.value = filtroMesInicio.value
  filtroMesFimActive.value = filtroMesFim.value
  filtroMedicoActive.value = filtroMedico.value
  filtroEspecialidadeActive.value = filtroEspecialidade.value
  filtroConvenioActive.value = filtroConvenio.value
  filtroStatusActive.value = filtroStatus.value
  pagination.value.pageIndex = 0
}

const medicosDisponiveis = computed(() => {
  const medicos = [...new Set(mockExames.map(e => e.medico))].sort()
  return ['Todos', ...medicos]
})

const especialidadesDisponiveis = computed(() => {
  const especialidades = [...new Set(mockExames.map(e => e.especialidade))].sort()
  return ['Todos', ...especialidades]
})

const conveniosDisponiveis = computed(() => {
  const convenios = [...new Set(mockExames.map(e => e.convenio))].sort()
  return ['Todos', ...convenios]
})

const STATUS_VALUE_MAP: Record<string, string> = {
  'Todos': 'Todos',
  'Solicitado': 'solicitado',
  'Pendente de Agendamento': 'pendente-agendamento',
  'Agendado Internamente': 'agendado-internamente',
  'Realizado Internamente': 'realizado-internamente',
  'Realizado Externamente': 'realizado-externamente',
  'Sem Contato': 'sem-contato',
  'Recusou': 'recusou',
  'Expirado': 'expirado'
}

const statusDisponiveis = ['Todos', 'Solicitado', 'Pendente de Agendamento', 'Agendado Internamente', 'Realizado Internamente', 'Realizado Externamente', 'Sem Contato', 'Recusou', 'Expirado']

const dadosFiltrados = computed(() => {
  return mockExames.filter((e) => {
    if (filtroMedicoActive.value !== 'Todos' && e.medico !== filtroMedicoActive.value) return false
    if (filtroEspecialidadeActive.value !== 'Todos' && e.especialidade !== filtroEspecialidadeActive.value) return false
    if (filtroConvenioActive.value !== 'Todos' && e.convenio !== filtroConvenioActive.value) return false
    if (filtroStatusActive.value !== 'Todos' && e.status !== STATUS_VALUE_MAP[filtroStatusActive.value]) return false
    if (e.dataSolicitacao.substring(0, 7) < filtroPeriodoInicioActive.value) return false
    if (e.dataSolicitacao.substring(0, 7) > filtroPeriodoFimActive.value) return false
    return true
  })
})

const pacientesVisiveis = computed(() => {
  let lista = dadosFiltrados.value
  const termoExame = filtroExame.value.toLowerCase().trim()
  const termoPaciente = filtroPaciente.value.toLowerCase().trim()
  if (termoExame) {
    lista = lista.filter(e => e.exame.toLowerCase().includes(termoExame) || e.codigoTuss.includes(termoExame))
  }
  if (termoPaciente) {
    lista = lista.filter(e => e.paciente.toLowerCase().includes(termoPaciente) || e.cpf.includes(termoPaciente) || e.prontuario.toLowerCase().includes(termoPaciente))
  }
  return lista
})

const totalExamesSolicitados = computed(() => dadosFiltrados.value.length)
const totalRealizadosInternamente = computed(() => dadosFiltrados.value.filter(e => e.status === 'realizado-internamente').length)
const totalPendentes = computed(() => dadosFiltrados.value.filter(e => ['solicitado', 'pendente-agendamento', 'sem-contato'].includes(e.status)).length)
const taxaConversao = computed(() => {
  const total = dadosFiltrados.value.length
  const realizados = dadosFiltrados.value.filter(e => e.status === 'realizado-internamente').length
  return total > 0 ? Math.round((realizados / total) * 100) : 0
})
const faturamentoRealizado = computed(() => {
  return dadosFiltrados.value
    .filter(e => e.status === 'realizado-internamente' && e.valorRealizado)
    .reduce((acc, e) => acc + (e.valorRealizado || 0), 0)
})
const oportunidadeAberto = computed(() => {
  return dadosFiltrados.value
    .filter(e => ['solicitado', 'pendente-agendamento', 'sem-contato'].includes(e.status))
    .reduce((acc, e) => acc + e.valorEstimado, 0)
})

const table = useTemplateRef('table')

const pagination = ref({
  pageIndex: 0,
  pageSize: 8
})

const colunas = [
  { accessorKey: 'paciente', header: 'Paciente' },
  { accessorKey: 'medico', header: 'Médico' },
  { accessorKey: 'exame', header: 'Exame' },
  { accessorKey: 'dataSolicitacao', header: 'Data Solic.' },
  { accessorKey: 'diasEmAberto', header: 'Dias' },
  { accessorKey: 'status', header: 'Status' },
  { accessorKey: 'valorEstimado', header: 'Valor Est.' }
]

function corStatus(status: string) {
  switch (status) {
    case 'solicitado': return 'info'
    case 'pendente-agendamento': return 'warning'
    case 'agendado-internamente': return 'success'
    case 'realizado-internamente': return 'success'
    case 'realizado-externamente': return 'neutral'
    case 'sem-contato': return 'warning'
    case 'recusou': return 'error'
    case 'expirado': return 'neutral'
    default: return 'neutral'
  }
}

function rotuloStatus(status: string) {
  switch (status) {
    case 'solicitado': return 'Solicitado'
    case 'pendente-agendamento': return 'Pendente'
    case 'agendado-internamente': return 'Agendado'
    case 'realizado-internamente': return 'Realizado Interno'
    case 'realizado-externamente': return 'Realizado Externo'
    case 'sem-contato': return 'Sem Contato'
    case 'recusou': return 'Recusou'
    case 'expirado': return 'Expirado'
    default: return status
  }
}

function formatarData(iso: string) {
  const [ano, mes, dia] = iso.split('-')
  return `${dia}/${mes}/${ano}`
}

function formatarMoeda(valor: number | null) {
  if (valor === null || valor === undefined) return '-'
  return `R$ ${valor.toLocaleString('pt-BR')}`
}

const pacienteSelecionado = ref<ExameRetencao | null>(null)
const slideoverAberto = ref(false)

const historicoContatoMock = [
  { data: '2026-07-10 14:30', canal: 'Telefone', usuario: 'Ana Oliveira', resultado: 'Paciente informou que vai agendar', observacao: 'Cliente receptivo, disse que liga amanhã' },
  { data: '2026-07-05 10:15', canal: 'WhatsApp', usuario: 'Ana Oliveira', resultado: 'Mensagem enviada', observacao: 'Enviado link de agendamento' },
  { data: '2026-06-28 16:45', canal: 'Telefone', usuario: 'Carlos Santos', resultado: 'Sem contato - caixa postal', observacao: 'Tentativa 3 - sem resposta' }
]

const examesSolicitadosMock = [
  { exame: 'Eletrocardiograma', codigoTuss: '40801010', quantidade: 1, valorEstimado: 120, status: 'solicitado' },
  { exame: 'Ecocardiograma', codigoTuss: '40804040', quantidade: 1, valorEstimado: 380, status: 'pendente-agendamento' }
]

function ligar(item: ExameRetencao) {
  console.log('Ligar para', item.paciente, item.telefone)
}

function whatsapp(item: ExameRetencao) {
  const tel = item.telefone.replace(/\D/g, '')
  window.open(`https://wa.me/55${tel}`, '_blank')
}

function agendar(item: ExameRetencao) {
  console.log('Agendar', item.paciente)
}

function atualizarStatus(item: ExameRetencao, novoStatus: string) {
  const idx = mockExames.findIndex(e => e.id === item.id)
  if (idx >= 0) {
    mockExames[idx] = { ...mockExames[idx], status: novoStatus as ExameRetencao['status'] } as ExameRetencao
  }
}

const itensAcoes = computed<DropdownMenuItem[][]>(() => {
  if (!pacienteSelecionado.value) return []
  return [
    [
      {
        label: 'WhatsApp',
        icon: 'i-lucide-message-circle',
        onSelect: () => whatsapp(pacienteSelecionado.value!)
      },
      {
        label: 'Ligar',
        icon: 'i-lucide-phone',
        onSelect: () => ligar(pacienteSelecionado.value!)
      },
      {
        label: 'Agendar',
        icon: 'i-lucide-calendar-plus',
        onSelect: () => agendar(pacienteSelecionado.value!)
      }
    ],
    [
      {
        label: 'Marcar como Realizado Interno',
        icon: 'i-lucide-check-circle',
        onSelect: () => atualizarStatus(pacienteSelecionado.value!, 'realizado-internamente')
      },
      {
        label: 'Marcar como Realizado Externo',
        icon: 'i-lucide-external-link',
        onSelect: () => atualizarStatus(pacienteSelecionado.value!, 'realizado-externamente')
      },
      {
        label: 'Marcar como Recusou',
        icon: 'i-lucide-x-circle',
        onSelect: () => atualizarStatus(pacienteSelecionado.value!, 'recusou')
      },
      {
        label: 'Marcar como Sem Contato',
        icon: 'i-lucide-phone-off',
        onSelect: () => atualizarStatus(pacienteSelecionado.value!, 'sem-contato')
      }
    ],
    [
      {
        label: 'Histórico Completo',
        icon: 'i-lucide-clock'
      }
    ]
  ]
})

const chartExamesLabels = computed(() => graficosMock.examesMaisSolicitados.map(e => e.exame))
const chartExamesDados = computed(() => graficosMock.examesMaisSolicitados.map(e => e.total))

const chartOportunidadeLabels = computed(() => graficosMock.oportunidadeFinanceira.map(o => o.convenio))
const chartOportunidadeDados = computed(() => graficosMock.oportunidadeFinanceira.map(o => o.valor))

const chartConversaoMedicos = computed(() => graficosMock.conversaoPorMedico.map(m => m.medico))
const chartConversaoTaxas = computed(() => graficosMock.conversaoPorMedico.map(m => m.taxa))

const chartEspecialidadeLabels = computed(() => graficosMock.porEspecialidade.map(e => e.label))
const chartEspecialidadeDados = computed(() => graficosMock.porEspecialidade.map(e => e.total))
</script>

<template>
  <div>
    <UHeader title="Retenção de Exames">
      <template #right>
        <div class="flex items-center gap-2">
          <UBadge
            label="Protótipo - Dados Mockados"
            color="warning"
            variant="soft"
          />
          <UColorModeButton />
        </div>
      </template>
    </UHeader>
    <div class="p-6 space-y-8 bg-neutral-100 dark:bg-neutral-950 min-h-screen">
      <UCard class="w-full">
        <template #title>
          <p class="text-lg font-medium">
            Filtros de Análise
          </p>
        </template>
        <div class="space-y-4">
          <div class="flex flex-wrap items-end gap-4">
            <div class="flex items-end gap-2">
              <UFormField label="Ano">
                <UInputMenu
                  v-model="filtroAno"
                  :items="[anoAtual, String(Number(anoAtual) - 1)]"
                  placeholder="Ano"
                  size="sm"
                  class="w-24"
                />
              </UFormField>
              <UFormField label="Mês início">
                <UInputMenu
                  v-model="filtroMesInicio"
                  :items="mesesOpcoes"
                  placeholder="Mês início"
                  size="sm"
                  class="w-36"
                />
              </UFormField>
              <span class="text-muted mb-1">até</span>
              <UFormField label="Mês fim">
                <UInputMenu
                  v-model="filtroMesFim"
                  :items="mesesOpcoes"
                  placeholder="Mês fim"
                  size="sm"
                  class="w-36"
                />
              </UFormField>
            </div>
            <UFormField label="Médico">
              <UInputMenu
                v-model="filtroMedico"
                :items="medicosDisponiveis"
                placeholder="Médico"
                size="sm"
                class="w-48"
              />
            </UFormField>
            <UFormField label="Especialidade">
              <UInputMenu
                v-model="filtroEspecialidade"
                :items="especialidadesDisponiveis"
                placeholder="Especialidade"
                size="sm"
                class="w-48"
              />
            </UFormField>
            <UFormField label="Convênio">
              <UInputMenu
                v-model="filtroConvenio"
                :items="conveniosDisponiveis"
                placeholder="Convênio"
                size="sm"
                class="w-48"
              />
            </UFormField>
            <UFormField label="Status">
              <UInputMenu
                v-model="filtroStatus"
                :items="statusDisponiveis"
                placeholder="Status"
                size="sm"
                class="w-48"
              />
            </UFormField>
            <UButton
              label="Aplicar Filtros"
              icon="i-lucide-filter"
              size="sm"
              color="primary"
              @click="aplicarFiltros"
            />
          </div>
          <div class="flex flex-wrap items-end gap-4">
            <UFormField label="Exame">
              <UInput
                v-model="filtroExame"
                placeholder="Buscar exame..."
                size="sm"
                class="w-48"
              />
            </UFormField>
            <UFormField label="Paciente">
              <UInput
                v-model="filtroPaciente"
                placeholder="Nome, CPF ou prontuário..."
                size="sm"
                class="w-64"
              />
            </UFormField>
          </div>
        </div>
      </UCard>

      <div class="w-full grid grid-cols-3 items-center gap-4">
        <CardRetencao
          titulo="Exames Solicitados"
          :valor="totalExamesSolicitados"
          cor="info"
          icone="i-lucide-flask-conical"
        />
        <CardRetencao
          titulo="Realizados Internamente"
          :valor="totalRealizadosInternamente"
          cor="success"
          icone="i-lucide-check-circle"
        />
        <CardRetencao
          titulo="Pendentes de Retenção"
          :valor="totalPendentes"
          cor="warning"
          icone="i-lucide-clock"
        />
        <CardRetencao
          titulo="Taxa de Conversão"
          :valor="taxaConversao"
          medida="%"
          cor="primary"
          icone="i-lucide-trending-up"
        />
        <CardRetencao
          titulo="Faturamento Realizado"
          :valor="`R$ ${faturamentoRealizado.toLocaleString('pt-BR')}`"
          cor="success"
          icone="i-lucide-coins"
        />
        <CardRetencao
          titulo="Oportunidade em Aberto"
          :valor="`R$ ${oportunidadeAberto.toLocaleString('pt-BR')}`"
          cor="tertiary"
          icone="i-lucide-trending-up"
        />
      </div>

      <div class="w-full grid grid-cols-2 gap-4">
        <UCard>
          <template #title>
            <p class="text-lg font-medium">
              Conversão por Médico
            </p>
          </template>
          <ChartConversaoMedico
            :medicos="chartConversaoMedicos"
            :taxas="chartConversaoTaxas"
          />
        </UCard>
        <UCard>
          <template #title>
            <p class="text-lg font-medium">
              Exames mais Solicitados
            </p>
          </template>
          <ChartExamesMaisSolicitados
            :labels="chartExamesLabels"
            :dados="chartExamesDados"
          />
        </UCard>
      </div>

      <div class="w-full grid grid-cols-2 gap-4">
        <UCard>
          <template #title>
            <p class="text-lg font-medium">
              Oportunidade Financeira por Convênio
            </p>
          </template>
          <ChartOportunidadeFinanceira
            :labels="chartOportunidadeLabels"
            :dados="chartOportunidadeDados"
          />
        </UCard>
        <UCard>
          <template #title>
            <p class="text-lg font-medium">
              Conversão por Especialidade
            </p>
          </template>
          <ChartEspecialidade
            :labels="chartEspecialidadeLabels"
            :dados="chartEspecialidadeDados"
          />
        </UCard>
      </div>

      <div class="grid grid-cols-5 gap-4 items-stretch">
        <UCard
          :ui="{
            body: 'p-4 sm:p-4 sm:py-5 min-w-55 flex items-center h-full'
          }"
          class="col-span-2"
        >
          <div class="flex items-center gap-3 w-full">
            <UBadge
              class="aspect-square"
              variant="soft"
              color="info"
            >
              <UIcon
                name="i-lucide-trending-up"
                class="size-8 text-info"
              />
            </UBadge>
            <div class="flex flex-col">
              <p class="text-sm font-bold text-nowrap">
                Tendência de Solicitações
              </p>
              <p class="text-xs text-muted">
                Período selecionado
              </p>
            </div>
          </div>
        </UCard>
        <UCard
          :ui="{
            body: 'p-5 flex items-center h-full'
          }"
          class="col-span-3"
        >
          <div class="flex items-center justify-between w-full">
            <div class="flex items-center gap-2">
              <UIcon
                name="i-lucide-download"
                class="text-primary size-5"
              />
              <span class="font-semibold">Exportar Dados</span>
            </div>
            <div class="flex items-center gap-3">
              <UButton
                icon="i-lucide-file-text"
                label="Exportar PDF"
                color="error"
                size="sm"
              />
              <UButton
                icon="i-lucide-file-spreadsheet"
                label="Exportar Excel"
                color="primary"
                size="sm"
              />
            </div>
          </div>
        </UCard>
      </div>

      <UCard class="w-full">
        <template #title>
          <div class="flex items-center justify-between">
            <p class="text-lg font-medium">
              Exames para Retenção
            </p>
            <div class="flex items-center gap-2">
              <UInput
                v-model="filtroExame"
                placeholder="Filtrar por exame..."
                size="sm"
                class="w-56"
              />
              <UInput
                v-model="filtroPaciente"
                placeholder="Filtrar por paciente, CPF ou prontuário..."
                size="sm"
                class="w-72"
              />
            </div>
          </div>
        </template>

        <p
          v-if="!pacientesVisiveis.length"
          class="py-4 text-sm text-muted"
        >
          Nenhum exame encontrado para retenção.
        </p>

        <UTable
          v-else
          ref="table"
          v-model:pagination="pagination"
          :columns="colunas"
          :data="pacientesVisiveis"
          :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
        >
          <template #paciente-cell="{ row }">
            <div class="flex items-center gap-3">
              <UAvatar
                :alt="row.original.paciente"
                color="primary"
                size="sm"
              />
              <div>
                <p class="font-medium">
                  {{ row.original.paciente }}
                </p>
                <p class="text-xs text-muted">
                  {{ row.original.convenio }}
                </p>
              </div>
            </div>
          </template>

          <template #medico-cell="{ row }">
            <div>
              <p class="text-sm font-medium">
                {{ row.original.medico }}
              </p>
              <p class="text-xs text-muted">
                {{ row.original.crm }}
              </p>
            </div>
          </template>

          <template #exame-cell="{ row }">
            <div>
              <p class="text-sm font-medium">
                {{ row.original.exame }}
              </p>
              <p class="text-xs text-muted">
                {{ row.original.codigoTuss }}
              </p>
            </div>
          </template>

          <template #dataSolicitacao-cell="{ row }">
            <span class="text-sm">{{ formatarData(row.original.dataSolicitacao) }}</span>
          </template>

          <template #diasEmAberto-cell="{ row }">
            <UBadge
              :label="String(row.original.diasEmAberto)"
              :color="row.original.diasEmAberto > 60 ? 'error' : row.original.diasEmAberto > 30 ? 'warning' : 'neutral'"
              variant="soft"
              size="sm"
            />
          </template>

          <template #status-cell="{ row }">
            <UBadge
              :label="rotuloStatus(row.original.status)"
              :color="corStatus(row.original.status)"
              variant="subtle"
            />
          </template>

          <template #valorEstimado-cell="{ row }">
            <span class="text-sm">{{ formatarMoeda(row.original.valorEstimado) }}</span>
          </template>
        </UTable>

        <div
          v-if="pacientesVisiveis.length"
          class="flex justify-center pt-4"
        >
          <UPagination
            :page="(table?.tableApi?.getState().pagination.pageIndex || 0) + 1"
            :items-per-page="table?.tableApi?.getState().pagination.pageSize || pagination.pageSize"
            :total="table?.tableApi?.getFilteredRowModel().rows.length || 0"
            @update:page="(p) => table?.tableApi?.setPageIndex(p - 1)"
          />
        </div>
      </UCard>
    </div>

    <USlideover v-model:open="slideoverAberto">
      <template #header>
        <div class="flex items-center gap-3">
          <UAvatar
            :alt="pacienteSelecionado?.paciente"
            color="primary"
            size="md"
          />
          <div>
            <p class="font-semibold text-lg">
              {{ pacienteSelecionado?.paciente }}
            </p>
            <p class="text-sm text-muted">
              {{ pacienteSelecionado?.convenio }} | {{ pacienteSelecionado?.cpf }}
            </p>
          </div>
        </div>
      </template>

      <template #body>
        <div class="space-y-6">
          <UCard>
            <template #title>
              <p class="font-semibold">
                Dados do Paciente
              </p>
            </template>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p class="text-muted">
                  Nome
                </p>
                <p class="font-medium">
                  {{ pacienteSelecionado?.paciente }}
                </p>
              </div>
              <div>
                <p class="text-muted">
                  CPF
                </p>
                <p class="font-medium">
                  {{ pacienteSelecionado?.cpf }}
                </p>
              </div>
              <div>
                <p class="text-muted">
                  Prontuário
                </p>
                <p class="font-medium">
                  {{ pacienteSelecionado?.prontuario }}
                </p>
              </div>
              <div>
                <p class="text-muted">
                  Telefone
                </p>
                <p class="font-medium">
                  {{ pacienteSelecionado?.telefone }}
                </p>
              </div>
              <div>
                <p class="text-muted">
                  Convênio
                </p>
                <p class="font-medium">
                  {{ pacienteSelecionado?.convenio }}
                </p>
              </div>
            </div>
          </UCard>

          <UCard>
            <template #title>
              <p class="font-semibold">
                Dados da Solicitação
              </p>
            </template>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p class="text-muted">
                  Médico
                </p>
                <p class="font-medium">
                  {{ pacienteSelecionado?.medico }}
                </p>
              </div>
              <div>
                <p class="text-muted">
                  CRM
                </p>
                <p class="font-medium">
                  {{ pacienteSelecionado?.crm }}
                </p>
              </div>
              <div>
                <p class="text-muted">
                  Especialidade
                </p>
                <p class="font-medium">
                  {{ pacienteSelecionado?.especialidade }}
                </p>
              </div>
              <div>
                <p class="text-muted">
                  Data da Solicitação
                </p>
                <p class="font-medium">
                  {{ pacienteSelecionado ? formatarData(pacienteSelecionado.dataSolicitacao) : '' }}
                </p>
              </div>
              <div>
                <p class="text-muted">
                  Dias em Aberto
                </p>
                <p class="font-medium">
                  {{ pacienteSelecionado?.diasEmAberto }} dias
                </p>
              </div>
              <div>
                <p class="text-muted">
                  Status
                </p>
                <UBadge
                  v-if="pacienteSelecionado"
                  :label="rotuloStatus(pacienteSelecionado.status)"
                  :color="corStatus(pacienteSelecionado.status)"
                  variant="subtle"
                />
              </div>
            </div>
          </UCard>

          <UCard>
            <template #title>
              <p class="font-semibold">
                Exames Solicitados
              </p>
            </template>
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-neutral-200 dark:border-neutral-800">
                  <th class="text-left py-2 font-medium text-muted">
                    Exame
                  </th>
                  <th class="text-left py-2 font-medium text-muted">
                    TUSS
                  </th>
                  <th class="text-right py-2 font-medium text-muted">
                    Valor Est.
                  </th>
                  <th class="text-left py-2 font-medium text-muted">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(exame, idx) in examesSolicitadosMock"
                  :key="idx"
                  class="border-t border-neutral-200 dark:border-neutral-800"
                >
                  <td class="py-2">
                    {{ exame.exame }}
                  </td>
                  <td class="py-2">
                    {{ exame.codigoTuss }}
                  </td>
                  <td class="py-2 text-right">
                    {{ formatarMoeda(exame.valorEstimado) }}
                  </td>
                  <td class="py-2">
                    <UBadge
                      :label="rotuloStatus(exame.status)"
                      :color="corStatus(exame.status)"
                      variant="subtle"
                      size="sm"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </UCard>

          <UCard>
            <template #title>
              <p class="font-semibold">
                Histórico de Contato
              </p>
            </template>
            <div class="space-y-4">
              <div
                v-for="(contato, idx) in historicoContatoMock"
                :key="idx"
                class="flex gap-3 pb-4 border-b border-neutral-200 dark:border-neutral-800 last:border-0"
              >
                <div class="flex flex-col items-center">
                  <div class="size-2 rounded-full bg-primary mt-2" />
                  <div
                    v-if="idx < historicoContatoMock.length - 1"
                    class="w-px flex-1 bg-neutral-200 dark:bg-neutral-800"
                  />
                </div>
                <div class="flex-1">
                  <div class="flex items-center justify-between">
                    <p class="text-sm font-medium">
                      {{ contato.canal }}
                    </p>
                    <p class="text-xs text-muted">
                      {{ contato.data }}
                    </p>
                  </div>
                  <p class="text-sm text-muted">
                    {{ contato.usuario }} - {{ contato.resultado }}
                  </p>
                  <p
                    v-if="contato.observacao"
                    class="text-xs text-muted mt-1"
                  >
                    {{ contato.observacao }}
                  </p>
                </div>
              </div>
            </div>
          </UCard>

          <UCard>
            <template #title>
              <p class="font-semibold">
                Ações Rápidas
              </p>
            </template>
            <div class="flex flex-wrap gap-2">
              <UButton
                icon="i-lucide-message-circle"
                label="WhatsApp"
                color="success"
                size="sm"
                @click="pacienteSelecionado ? whatsapp(pacienteSelecionado) : undefined"
              />
              <UButton
                icon="i-lucide-phone"
                label="Ligar"
                color="primary"
                size="sm"
                @click="pacienteSelecionado ? ligar(pacienteSelecionado) : undefined"
              />
              <UButton
                icon="i-lucide-calendar-plus"
                label="Agendar"
                color="warning"
                size="sm"
                @click="pacienteSelecionado ? agendar(pacienteSelecionado) : undefined"
              />
              <UDropdownMenu :items="itensAcoes">
                <UButton
                  icon="i-lucide-chevron-down"
                  label="Atualizar Status"
                  color="secondary"
                  size="sm"
                />
              </UDropdownMenu>
            </div>
          </UCard>
        </div>
      </template>
    </USlideover>
  </div>
</template>
