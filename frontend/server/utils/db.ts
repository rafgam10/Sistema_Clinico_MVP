interface ServerClinica {
  id: number
  nome: string
  endereco: string
  telefone: string
}

interface ServerPaciente {
  id: number
  nome: string
  sexo: 'masculino' | 'feminino'
  dataNascimento: string
  tipoSanguineo: string
  alergias: string[]
  medicamentosEmUso: { nome: string, dosagem: string, frequencia: string }[]
  convenio: string
  telefone: string
  email: string
  cpf: string
  endereco: string
  contatoEmergencia?: { nome: string, telefone: string, parentesco: string }
  responsavel?: { nome: string, telefone: string, parentesco: string }
  ultimaConsulta?: string
  historicoRecente: { data: string, descricao: string, diagnostico?: string, medicamentos?: string, exames?: string }[]
}

interface ServerAgendamento {
  id: number
  pacienteId: number
  medicoId: number
  clinicaId: number
  data: string
  horario: string
  prioridade: 'normal' | 'preferencial'
  status: 'agendado' | 'em-espera' | 'em_atendimento' | 'atendido' | 'faltou' | 'cancelado'
  descricao: string
  criadoEm: string
  duracao?: number
}

interface ServerChamado {
  id: number
  pacienteId: number
  pacienteNome: string
  dataChamada: string
  status: 'chamando' | 'concluido' | 'cancelado'
  localAtendimento: string
  medicoResponsavel: string
}

interface ServerPadrao {
  id: string
  medicoId: number
  nome: string
  tipo: 'receita' | 'exame'
  medicamentos?: { nome: string, dosagem: string, detalhes: string }[]
  exames?: string[]
  html?: string
  createdAt: string
  updatedAt: string
}

// ── DATE SHIFT (ajusta datas mockadas pro dia atual) ──
const DATA_REF = new Date('2026-06-05T12:00:00')
const DIFF_DIAS = Math.round((Date.now() - DATA_REF.getTime()) / (1000 * 60 * 60 * 24))

function shiftISO(iso: string): string {
  const d = new Date(iso + 'T12:00:00')
  d.setDate(d.getDate() + DIFF_DIAS)
  return d.toISOString().split('T')[0]
}

function shiftISOFull(iso: string): string {
  const d = new Date(iso)
  d.setDate(d.getDate() + DIFF_DIAS)
  return d.toISOString()
}

function shiftBR(br: string): string {
  const [d, m, y] = br.split('/')
  const date = new Date(`${y}-${m}-${d}T12:00:00`)
  date.setDate(date.getDate() + DIFF_DIAS)
  return date.toLocaleDateString('pt-BR')
}

// ── CLÍNICAS ──
const clinicas: ServerClinica[] = [
  { id: 1, nome: 'Clínica Centro', endereco: 'Rua Augusta, 1500 - Centro, São Paulo - SP', telefone: '(11) 3000-0001' },
  { id: 2, nome: 'Clínica Norte', endereco: 'Av. Paulista, 2000 - Bela Vista, São Paulo - SP', telefone: '(11) 3000-0002' }
]

// ── PACIENTES ──
let nextPacienteId = 26

const pacientes: ServerPaciente[] = [
  {
    id: 1, nome: 'Carlos Pereira', sexo: 'masculino', dataNascimento: '1981-03-12',
    tipoSanguineo: 'A+', alergias: ['Penicilina', 'Dipirona', 'Poeira'],
    medicamentosEmUso: [{ nome: 'Losartana', dosagem: '50mg', frequencia: '1x ao dia' }, { nome: 'Omeprazol', dosagem: '20mg', frequencia: '1x ao dia em jejum' }],
    convenio: 'Unimed', telefone: '(11) 99999-0001', email: 'carlos.pereira@email.com', cpf: '123.456.789-01',
    endereco: 'Rua das Flores, 100 - Apto 42 - Centro, São Paulo - SP',
    contatoEmergencia: { nome: 'Marina Pereira', telefone: '(11) 99999-0002', parentesco: 'Cônjuge' },
    ultimaConsulta: '10/05/2026',
    historicoRecente: [
      { data: '10/05/2026', descricao: '<p><strong>Paciente</strong> relata <em>dor de cabeça</em> persistente há 3 dias, localizada na região frontal, com intensidade 7/10. Nega febre ou náuseas.</p><ul><li>Sem sinais neurológicos focais</li><li>PA: 120x80 mmHg</li><li>FC: 72 bpm</li></ul><p>Conduta: solicitar <u>hemograma</u> e RNM de crânio. Prescrever <strong>Paracetamol 750mg</strong> 6/6h se dor.</p>', diagnostico: 'J00 — Infecção respiratória', medicamentos: 'Amoxicilina 500mg 3x/dia por 7 dias', exames: 'Raio-X de tórax' },
      { data: '22/04/2026', descricao: 'Exame de sangue', diagnostico: 'E78.0 — Colesterol alto', medicamentos: 'Sinvastatina 20mg 1x/dia', exames: 'Hemograma completo, Glicemia em jejum' }
    ]
  },
  {
    id: 2, nome: 'Maria Santos', sexo: 'feminino', dataNascimento: '1994-07-25',
    tipoSanguineo: 'O-', alergias: [],
    medicamentosEmUso: [{ nome: 'Dipirona', dosagem: '1g', frequencia: 'se necessário' }],
    convenio: 'Bradesco Saúde', telefone: '(11) 99999-0003', email: 'maria.santos@email.com', cpf: '123.456.789-02',
    endereco: 'Av. Brigadeiro, 500 - Apto 10 - Jardins, São Paulo - SP',
    contatoEmergencia: { nome: 'Luis Santos', telefone: '(11) 99999-0004', parentesco: 'Irmão' },
    ultimaConsulta: '22/04/2026',
    historicoRecente: [
      { data: '22/04/2026', descricao: 'Check-up anual', diagnostico: 'Z00.0 — Exame geral de rotina', medicamentos: 'Nenhum', exames: 'Eletrocardiograma' },
      { data: '10/01/2026', descricao: 'Dermatologista', diagnostico: 'L20.8 — Dermatite atópica', medicamentos: 'Hidrocortisona creme 2x/dia', exames: 'Teste alérgico' }
    ]
  },
  {
    id: 3, nome: 'João Lima', sexo: 'masculino', dataNascimento: '1998-11-03',
    tipoSanguineo: 'B+', alergias: ['Sulfa'],
    medicamentosEmUso: [],
    convenio: 'SulAmérica', telefone: '(11) 99999-0005', email: 'joao.lima@email.com', cpf: '123.456.789-03',
    endereco: 'Rua dos Pinheiros, 200 - Pinheiros, São Paulo - SP',
    ultimaConsulta: '03/03/2026',
    historicoRecente: [
      { data: '03/03/2026', descricao: '<p>Paciente comparece para <strong>retorno</strong> de cefaleia. Relata melhora parcial com Paracetamol.</p><p><em>Exame físico:</em></p><ul><li>PA: 130x85 mmHg</li><li>FC: 80 bpm</li><li>Tax: 36.5°C</li></ul><p>Manteve prescrição anterior. <u>Retorno em 30 dias</u> se sem melhora.</p>', diagnostico: 'R51 — Cefaleia', medicamentos: 'Paracetamol 750mg 6/6h', exames: 'Nenhum' }
    ]
  },
  {
    id: 4, nome: 'Ana Oliveira', sexo: 'feminino', dataNascimento: '1968-02-18',
    tipoSanguineo: 'AB+', alergias: [],
    medicamentosEmUso: [{ nome: 'Enalapril', dosagem: '10mg', frequencia: '1x ao dia' }, { nome: 'AAS', dosagem: '100mg', frequencia: '1x ao dia' }],
    convenio: 'Unimed', telefone: '(11) 99999-0006', email: 'ana.oliveira@email.com', cpf: '123.456.789-04',
    endereco: 'Alameda Santos, 800 - Apto 15 - Cerqueira César, São Paulo - SP',
    contatoEmergencia: { nome: 'Paulo Oliveira', telefone: '(11) 99999-0007', parentesco: 'Filho' },
    ultimaConsulta: '15/05/2026',
    historicoRecente: [
      { data: '15/05/2026', descricao: 'Cardiologia', diagnostico: 'I10 — Hipertensão arterial', medicamentos: 'Enalapril 10mg 1x/dia, AAS 100mg 1x/dia', exames: 'Ecocardiograma' },
      { data: '02/03/2026', descricao: 'Exame de sangue', diagnostico: 'E78.0 — Dislipidemia', medicamentos: 'Nenhum', exames: 'Hemograma, Glicemia, Colesterol total e frações' }
    ]
  },
  {
    id: 5, nome: 'Pedro Alves', sexo: 'masculino', dataNascimento: '1964-09-30',
    tipoSanguineo: 'A-', alergias: ['Dipirona'],
    medicamentosEmUso: [{ nome: 'Metformina', dosagem: '850mg', frequencia: '2x ao dia' }, { nome: 'Glibenclamida', dosagem: '5mg', frequencia: '1x ao dia' }],
    convenio: 'Bradesco Saúde', telefone: '(11) 99999-0008', email: 'pedro.alves@email.com', cpf: '123.456.789-05',
    endereco: 'Rua da Consolação, 300 - Consolação, São Paulo - SP',
    contatoEmergencia: { nome: 'Tereza Alves', telefone: '(11) 99999-0009', parentesco: 'Cônjuge' },
    ultimaConsulta: '28/02/2026',
    historicoRecente: [
      { data: '28/02/2026', descricao: '<p><strong>Paciente</strong> assintomático, em consulta de <strong>check-up</strong> rotineiro.</p><p>Exames solicitados na consulta anterior:</p><ol><li><strong>Hemograma</strong> — sem alterações</li><li><strong>Creatinina</strong> — 0.9 mg/dL (normal)</li><li><strong>Uréia</strong> — 32 mg/dL (normal)</li></ol><p>PA: <strong>135x85 mmHg</strong>. Frequência cardíaca: 76 bpm.</p><p>Conduta: manter <strong>Losartana 50mg</strong> 1x/dia. <u>Solicitado novo lipidograma</u> para controle. Retorno em 6 meses.</p>', diagnostico: 'I10 — Hipertensão estágio 1', medicamentos: 'Losartana 50mg 1x/dia', exames: 'Hemograma, Creatinina, Uréia' },
      { data: '30/08/2025', descricao: 'Exame de sangue', diagnostico: 'E11.9 — Diabetes tipo 2', medicamentos: 'Metformina 850mg 2x/dia', exames: 'Glicemia, Hemoglobina glicada' }
    ]
  },
  {
    id: 6, nome: 'Lúcia Mendes', sexo: 'feminino', dataNascimento: '1988-05-14',
    tipoSanguineo: 'O+', alergias: ['Látex'],
    medicamentosEmUso: [],
    convenio: 'Amil', telefone: '(11) 99999-0010', email: 'lucia.mendes@email.com', cpf: '123.456.789-06',
    endereco: 'Rua Oscar Freire, 600 - Jardins, São Paulo - SP',
    contatoEmergencia: { nome: 'Roberto Mendes', telefone: '(11) 99999-0011', parentesco: 'Cônjuge' },
    ultimaConsulta: '01/06/2026',
    historicoRecente: [
      { data: '01/06/2026', descricao: 'Pré-operatório', diagnostico: 'Z01.8 — Exame pré-cirúrgico', medicamentos: 'Nenhum', exames: 'Eletrocardiograma, Raio-X de tórax' }
    ]
  },
  {
    id: 7, nome: 'Roberto Castro', sexo: 'masculino', dataNascimento: '1974-08-22',
    tipoSanguineo: 'B-', alergias: ['AAS'],
    medicamentosEmUso: [{ nome: 'Diclofenaco', dosagem: '50mg', frequencia: '2x ao dia se dor' }],
    convenio: 'Unimed', telefone: '(11) 99999-0012', email: 'roberto.castro@email.com', cpf: '123.456.789-07',
    endereco: 'Av. Angélica, 400 - Higienópolis, São Paulo - SP',
    ultimaConsulta: '20/04/2026',
    historicoRecente: [
      { data: '20/04/2026', descricao: 'Ortopedia', diagnostico: 'M54.5 — Lombalgia', medicamentos: 'Diclofenaco 50mg 2x/dia', exames: 'Raio-X de coluna lombar' }
    ]
  },
  {
    id: 8, nome: 'Fernanda Brito', sexo: 'feminino', dataNascimento: '1999-01-09',
    tipoSanguineo: 'A+', alergias: ['Pólen', 'Perfume'],
    medicamentosEmUso: [{ nome: 'Loratadina', dosagem: '10mg', frequencia: '1x ao dia' }],
    convenio: 'Bradesco Saúde', telefone: '(11) 99999-0013', email: 'fernanda.brito@email.com', cpf: '123.456.789-08',
    endereco: 'Rua Haddock Lobo, 900 - Cerqueira César, São Paulo - SP',
    contatoEmergencia: { nome: 'Clara Brito', telefone: '(11) 99999-0014', parentesco: 'Mãe' },
    ultimaConsulta: '12/03/2026',
    historicoRecente: [
      { data: '12/03/2026', descricao: '<p>Paciente retorna ao consultório com <strong>lesões eritematosas</strong> em membros superiores e tronco. Relata piora após contato com <em>perfumes</em> e <em>produtos de limpeza</em>.</p><p><u>Exame dermatológico:</u></p><ul><li>Lesões eritemato-descamativas em antebraços bilateral</li><li>Pápulas pruriginosas em tronco anterior</li><li>Sem sinais de infecção secundária</li></ul><p>Conduta: manter <strong>Hidrocortisona creme 2x/dia</strong> por 14 dias. Orientado evitar exposição a alérgenos. <u>Retorno em 30 dias</u> para reavaliação.</p>', diagnostico: 'L20.8 — Dermatite alérgica', medicamentos: 'Hidrocortisona creme 2x/dia', exames: 'Teste de alergia' }
    ]
  },
  {
    id: 9, nome: 'Márcio Souza', sexo: 'masculino', dataNascimento: '1985-06-17',
    tipoSanguineo: 'A-', alergias: [],
    medicamentosEmUso: [],
    convenio: 'SulAmérica', telefone: '(11) 99999-0015', email: 'marcio.souza@email.com', cpf: '123.456.789-09',
    endereco: 'Rua Augusta, 2500 - Consolação, São Paulo - SP',
    ultimaConsulta: '10/04/2026',
    historicoRecente: [
      { data: '10/04/2026', descricao: 'Admissional', diagnostico: 'Z00.0 — Exame admissional', medicamentos: 'Nenhum', exames: 'Hemograma, Urina, Glicemia' }
    ]
  },
  {
    id: 10, nome: 'Carla Dias', sexo: 'feminino', dataNascimento: '1971-12-05',
    tipoSanguineo: 'O-', alergias: ['Penicilina', 'Sulfa'],
    medicamentosEmUso: [{ nome: 'Levotiroxina', dosagem: '75mcg', frequencia: '1x ao dia em jejum' }, { nome: 'Atorvastatina', dosagem: '20mg', frequencia: '1x ao dia' }],
    convenio: 'Amil', telefone: '(11) 99999-0016', email: 'carla.dias@email.com', cpf: '123.456.789-10',
    endereco: 'Alameda Campinas, 700 - Apto 32 - Cerqueira César, São Paulo - SP',
    contatoEmergencia: { nome: 'Marcos Dias', telefone: '(11) 99999-0017', parentesco: 'Filho' },
    ultimaConsulta: '04/06/2026',
    historicoRecente: [
      { data: '04/06/2026', descricao: 'Retorno pós-operatório', diagnostico: 'Z48.8 — Cuidado pós-cirúrgico', medicamentos: 'Atorvastatina 20mg 1x/dia, Levotiroxina 75mcg 1x/dia', exames: 'Hemograma, TSH, T4 livre' },
      { data: '10/03/2026', descricao: 'Cirurgia', diagnostico: 'K80.2 — Colelitíase', medicamentos: 'Dipirona 1g se dor', exames: 'Ultrassom de abdômen' }
    ]
  },
  {
    id: 11, nome: 'Tiago Nunes', sexo: 'masculino', dataNascimento: '1991-04-28',
    tipoSanguineo: 'AB-', alergias: [],
    medicamentosEmUso: [],
    convenio: 'Unimed', telefone: '(11) 99999-0018', email: 'tiago.nunes@email.com', cpf: '123.456.789-11',
    endereco: 'Rua Bela Cintra, 300 - Consolação, São Paulo - SP',
    ultimaConsulta: '15/05/2026',
    historicoRecente: [
      { data: '15/05/2026', descricao: 'Consulta geral', diagnostico: 'Z00.0 — Exame de rotina', medicamentos: 'Nenhum', exames: 'Hemograma, Lipidograma' }
    ]
  },
  {
    id: 12, nome: 'Sandra Rocha', sexo: 'feminino', dataNascimento: '1997-10-11',
    tipoSanguineo: 'B+', alergias: ['Ibuprofeno'],
    medicamentosEmUso: [],
    convenio: 'Bradesco Saúde', telefone: '(11) 99999-0019', email: 'sandra.rocha@email.com', cpf: '123.456.789-12',
    endereco: 'Av. Rebouças, 1500 - Pinheiros, São Paulo - SP',
    ultimaConsulta: '22/04/2026',
    historicoRecente: [
      { data: '22/04/2026', descricao: 'Ginecologia', diagnostico: 'N94.6 — Dismenorreia', medicamentos: 'Ácido mefenâmico 500mg 8/8h', exames: 'Ultrassom pélvico' }
    ]
  },
  {
    id: 13, nome: 'Gustavo Lima', sexo: 'masculino', dataNascimento: '1978-03-08',
    tipoSanguineo: 'O+', alergias: [],
    medicamentosEmUso: [{ nome: 'Omeprazol', dosagem: '20mg', frequencia: '1x ao dia' }],
    convenio: 'SulAmérica', telefone: '(11) 99999-0020', email: 'gustavo.lima@email.com', cpf: '123.456.789-13',
    endereco: 'Rua Dr. Fausto, 200 - Perdizes, São Paulo - SP',
    ultimaConsulta: '18/03/2026',
    historicoRecente: [
      { data: '18/03/2026', descricao: 'Gastroenterologia', diagnostico: 'K21.9 — DRGE', medicamentos: 'Omeprazol 20mg 1x/dia', exames: 'Endoscopia digestiva' }
    ]
  },
  {
    id: 14, nome: 'Juliana Costa', sexo: 'feminino', dataNascimento: '1985-08-20',
    tipoSanguineo: 'A+', alergias: ['Dipirona'],
    medicamentosEmUso: [{ nome: 'Sinvastatina', dosagem: '20mg', frequencia: '1x ao dia' }],
    convenio: 'Amil', telefone: '(11) 99999-0021', email: 'juliana.costa@email.com', cpf: '123.456.789-14',
    endereco: 'Rua Tabapuã, 500 - Itaim Bibi, São Paulo - SP',
    ultimaConsulta: '12/04/2026',
    historicoRecente: [
      { data: '12/04/2026', descricao: 'Consulta geral', diagnostico: 'E78.0 — Colesterol alto', medicamentos: 'Sinvastatina 20mg 1x/dia', exames: 'Hemograma, Lipidograma' }
    ]
  },
  {
    id: 15, nome: 'Rafael Santos', sexo: 'masculino', dataNascimento: '1959-05-15',
    tipoSanguineo: 'O-', alergias: ['Penicilina'],
    medicamentosEmUso: [{ nome: 'Losartana', dosagem: '50mg', frequencia: '1x ao dia' }, { nome: 'Hidroclorotiazida', dosagem: '25mg', frequencia: '1x ao dia' }, { nome: 'AAS', dosagem: '100mg', frequencia: '1x ao dia' }],
    convenio: 'Bradesco Saúde', telefone: '(11) 99999-0022', email: 'rafael.santos@email.com', cpf: '123.456.789-15',
    endereco: 'Rua Maestro Cardim, 100 - Paraíso, São Paulo - SP',
    contatoEmergencia: { nome: 'Sônia Santos', telefone: '(11) 99999-0023', parentesco: 'Cônjuge' },
    ultimaConsulta: '20/03/2026',
    historicoRecente: [
      { data: '20/03/2026', descricao: 'Cardiologia', diagnostico: 'I10 — Hipertensão arterial', medicamentos: 'Hidroclorotiazida 25mg 1x/dia', exames: 'Ecocardiograma' }
    ]
  }
]

// ── AGENDAMENTOS ──
let nextAgendamentoId = 100

const agendamentos: ServerAgendamento[] = [
  // 05/06/2026 — Clínica Centro — Dr. João (medicoId: 1)
  { id: 1, pacienteId: 1, medicoId: 1, clinicaId: 1, data: '2026-06-05', horario: '08:00', prioridade: 'preferencial', status: 'em-espera', descricao: 'Consulta geral — Hipertensão arterial', criadoEm: '2026-05-20T10:00:00Z' },
  { id: 2, pacienteId: 2, medicoId: 1, clinicaId: 1, data: '2026-06-05', horario: '08:30', prioridade: 'normal', status: 'em-espera', descricao: 'Check-up anual — Rotina', criadoEm: '2026-05-19T14:30:00Z' },
  { id: 3, pacienteId: 3, medicoId: 1, clinicaId: 1, data: '2026-06-05', horario: '09:30', prioridade: 'normal', status: 'agendado', descricao: 'Retorno — Cefaleia persistente', criadoEm: '2026-05-25T09:00:00Z' },
  { id: 4, pacienteId: 4, medicoId: 1, clinicaId: 1, data: '2026-06-05', horario: '10:00', prioridade: 'preferencial', status: 'em-espera', descricao: 'Cardiologia — Avaliação de risco cirúrgico', criadoEm: '2026-05-18T11:00:00Z' },
  { id: 5, pacienteId: 5, medicoId: 1, clinicaId: 1, data: '2026-06-05', horario: '10:30', prioridade: 'normal', status: 'faltou', descricao: 'Endocrinologia — Ajuste de medicação diabetes', criadoEm: '2026-05-10T08:00:00Z' },
  { id: 6, pacienteId: 6, medicoId: 1, clinicaId: 1, data: '2026-06-05', horario: '11:00', prioridade: 'normal', status: 'em-espera', descricao: 'Consulta pré-operatória — Cirurgia de vesícula', criadoEm: '2026-05-30T15:00:00Z' },
  { id: 7, pacienteId: 7, medicoId: 1, clinicaId: 1, data: '2026-06-05', horario: '14:00', prioridade: 'normal', status: 'agendado', descricao: 'Ortopedia — Dor no joelho direito', criadoEm: '2026-06-01T09:00:00Z' },
  { id: 8, pacienteId: 8, medicoId: 1, clinicaId: 1, data: '2026-06-05', horario: '14:30', prioridade: 'normal', status: 'em-espera', descricao: 'Dermatologia — Alergia cutânea recorrente', criadoEm: '2026-05-22T10:00:00Z' },
  { id: 9, pacienteId: 11, medicoId: 1, clinicaId: 1, data: '2026-06-05', horario: '15:00', prioridade: 'normal', status: 'agendado', descricao: 'Retorno — Resultados de exames', criadoEm: '2026-06-02T11:00:00Z' },
  { id: 10, pacienteId: 12, medicoId: 1, clinicaId: 1, data: '2026-06-05', horario: '16:00', prioridade: 'normal', status: 'em-espera', descricao: 'Ginecologia — Cólicas intensas', criadoEm: '2026-05-28T13:00:00Z' },

  // 05/06/2026 — Clínica Norte — Dra. Maria (medicoId: 2)
  { id: 11, pacienteId: 14, medicoId: 2, clinicaId: 2, data: '2026-06-05', horario: '08:00', prioridade: 'normal', status: 'em-espera', descricao: 'Retorno — Resultados de exames laboratoriais', criadoEm: '2026-05-21T09:00:00Z' },
  { id: 12, pacienteId: 15, medicoId: 2, clinicaId: 2, data: '2026-06-05', horario: '09:00', prioridade: 'preferencial', status: 'agendado', descricao: 'Cardiologia — Acompanhamento hipertensão', criadoEm: '2026-05-15T08:00:00Z' },
  { id: 13, pacienteId: 16, medicoId: 2, clinicaId: 2, data: '2026-06-05', horario: '10:00', prioridade: 'normal', status: 'em-espera', descricao: 'Dermatologia — Acne persistente', criadoEm: '2026-05-26T10:00:00Z' },
  { id: 14, pacienteId: 17, medicoId: 2, clinicaId: 2, data: '2026-06-05', horario: '14:30', prioridade: 'normal', status: 'agendado', descricao: 'Gastroenterologia — Retorno gastrite', criadoEm: '2026-06-01T14:00:00Z' },
  { id: 15, pacienteId: 18, medicoId: 2, clinicaId: 2, data: '2026-06-05', horario: '15:30', prioridade: 'normal', status: 'em-espera', descricao: 'Ginecologia — Consulta de rotina', criadoEm: '2026-05-27T16:00:00Z' },

  // 05/06/2026 — Clínica Centro — Dr. Carlos (medicoId: 3, clinicaId: 1)
  { id: 16, pacienteId: 7, medicoId: 3, clinicaId: 1, data: '2026-06-05', horario: '11:00', prioridade: 'normal', status: 'agendado', descricao: 'Medicina Esportiva — Avaliação de retorno ao esporte', criadoEm: '2026-06-03T10:00:00Z' },
  { id: 17, pacienteId: 9, medicoId: 3, clinicaId: 1, data: '2026-06-05', horario: '15:00', prioridade: 'normal', status: 'em-espera', descricao: 'Ortopedia — Dor no ombro', criadoEm: '2026-05-29T10:00:00Z' },

  // 06/06/2026 — Clínica Centro — Dr. João (medicoId: 1)
  { id: 18, pacienteId: 9, medicoId: 1, clinicaId: 1, data: '2026-06-06', horario: '08:00', prioridade: 'normal', status: 'em-espera', descricao: 'Exame admissional — Nova empresa', criadoEm: '2026-05-18T10:00:00Z' },
  { id: 19, pacienteId: 13, medicoId: 1, clinicaId: 1, data: '2026-06-06', horario: '08:30', prioridade: 'normal', status: 'agendado', descricao: 'Gastroenterologia — Retorno DRGE', criadoEm: '2026-06-02T10:00:00Z' },
  { id: 20, pacienteId: 4, medicoId: 1, clinicaId: 1, data: '2026-06-06', horario: '09:00', prioridade: 'normal', status: 'em-espera', descricao: 'Pré-natal — 2º trimestre', criadoEm: '2026-05-25T11:00:00Z' },
  { id: 21, pacienteId: 4, medicoId: 1, clinicaId: 1, data: '2026-06-06', horario: '10:00', prioridade: 'preferencial', status: 'agendado', descricao: 'Clínico geral — Acompanhamento diabetes e HAS', criadoEm: '2026-05-20T08:00:00Z' },
  { id: 22, pacienteId: 8, medicoId: 1, clinicaId: 1, data: '2026-06-06', horario: '11:00', prioridade: 'normal', status: 'em-espera', descricao: 'Retorno — Rinite alérgica sazonal', criadoEm: '2026-06-01T10:00:00Z' },
  { id: 23, pacienteId: 7, medicoId: 1, clinicaId: 1, data: '2026-06-06', horario: '14:00', prioridade: 'normal', status: 'em-espera', descricao: 'Ortopedia — Avaliação de fratura por estresse', criadoEm: '2026-06-01T15:00:00Z' },
  { id: 24, pacienteId: 6, medicoId: 1, clinicaId: 1, data: '2026-06-06', horario: '15:00', prioridade: 'normal', status: 'agendado', descricao: 'Psiquiatria — Retorno tratamento depressão', criadoEm: '2026-06-03T09:00:00Z' },

  // 06/06/2026 — Clínica Norte — Dra. Maria (medicoId: 2)
  { id: 25, pacienteId: 10, medicoId: 2, clinicaId: 2, data: '2026-06-06', horario: '08:30', prioridade: 'normal', status: 'agendado', descricao: 'Urologia — Retorno hiperplasia prostática', criadoEm: '2026-05-30T08:00:00Z' },
  { id: 26, pacienteId: 5, medicoId: 2, clinicaId: 2, data: '2026-06-06', horario: '10:30', prioridade: 'preferencial', status: 'faltou', descricao: 'Endocrinologia — Controle de tireoide', criadoEm: '2026-05-10T10:00:00Z' },

  // 04/06/2026 — Histórico — Clínica Centro — Dr. João (medicoId: 1)
  { id: 27, pacienteId: 10, medicoId: 1, clinicaId: 1, data: '2026-06-04', horario: '09:00', prioridade: 'preferencial', status: 'atendido', descricao: 'Retorno cirurgia — Pós-colecistectomia', criadoEm: '2026-05-12T10:00:00Z' },

  // 06/06/2026 — Clínica Centro — Dr. Carlos (medicoId: 3, clinicaId: 1)
  { id: 28, pacienteId: 11, medicoId: 3, clinicaId: 1, data: '2026-06-06', horario: '10:00', prioridade: 'normal', status: 'agendado', descricao: 'Ortopedia — Avaliação de joelho', criadoEm: '2026-06-04T11:00:00Z' },

  // 05/06/2026 — Clínica Norte — Dr. Carlos (medicoId: 3, clinicaId: 2)
  { id: 29, pacienteId: 3, medicoId: 3, clinicaId: 2, data: '2026-06-05', horario: '15:00', prioridade: 'normal', status: 'agendado', descricao: 'Medicina Esportiva — Consulta inicial', criadoEm: '2026-06-02T11:00:00Z' }
]

// ── CHAMADOS (preservado) ──
const chamados: ServerChamado[] = []

// ── PADRÕES (preservado) ──
const padroes: ServerPadrao[] = []

// ── Ajusta todas as datas mockadas pro dia atual ──
if (DIFF_DIAS !== 0) {
  for (const a of agendamentos) {
    a.data = shiftISO(a.data)
    a.criadoEm = shiftISOFull(a.criadoEm)
  }
  for (const p of pacientes) {
    if (p.ultimaConsulta) p.ultimaConsulta = shiftBR(p.ultimaConsulta)
    for (const h of p.historicoRecente) {
      h.data = shiftBR(h.data)
    }
  }
}

// ── SSE ──
const sseClients: Set<{ write: (data: string) => void, close: () => void }> = new Set()

// ── HELPERS: CLÍNICAS ──
export function getClinicas() {
  return clinicas
}

export function getClinica(id: number) {
  return clinicas.find(c => c.id === id) ?? null
}

// ── HELPERS: PACIENTES ──
export function getPacientes(search?: string) {
  let result = pacientes
  if (search) {
    const term = search.toLowerCase()
    result = result.filter(p =>
      p.nome.toLowerCase().includes(term) ||
      p.cpf.includes(term) ||
      p.telefone.includes(term)
    )
  }
  return result
}

export function getPaciente(id: number) {
  return pacientes.find(p => p.id === id) ?? null
}

export function criarPaciente(data: Omit<ServerPaciente, 'id' | 'ultimaConsulta' | 'historicoRecente'>) {
  const paciente: ServerPaciente = {
    id: nextPacienteId++,
    ...data,
    historicoRecente: []
  }
  pacientes.push(paciente)
  return paciente
}

export function atualizarPaciente(id: number, data: Partial<Omit<ServerPaciente, 'id'>>) {
  const p = pacientes.find(p => p.id === id)
  if (!p) return null
  Object.assign(p, data)
  return p
}

export function deletarPaciente(id: number) {
  const idx = pacientes.findIndex(p => p.id === id)
  if (idx === -1) return false
  pacientes.splice(idx, 1)
  agendamentos.forEach(a => {
    if (a.pacienteId === id) a.status = 'cancelado'
  })
  return true
}

export function adicionarHistoricoPaciente(pacienteId: number, entry: ServerPaciente['historicoRecente'][0]) {
  const p = pacientes.find(p => p.id === pacienteId)
  if (!p) return
  p.historicoRecente.unshift(entry)
  p.ultimaConsulta = entry.data
}

// ── HELPERS: AGENDAMENTOS ──
export function getAgendamentos(clinicaId?: number, data?: string, medicoId?: number) {
  let result = agendamentos
  if (clinicaId) result = result.filter(a => a.clinicaId === clinicaId)
  if (data) result = result.filter(a => a.data === data)
  if (medicoId) result = result.filter(a => a.medicoId === medicoId)
  return result
}

export function getAgendamento(id: number) {
  return agendamentos.find(a => a.id === id) ?? null
}

export function criarAgendamento(data: Omit<ServerAgendamento, 'id' | 'criadoEm'>) {
  const agendamento: ServerAgendamento = {
    id: nextAgendamentoId++,
    ...data,
    criadoEm: new Date().toISOString()
  }
  agendamentos.push(agendamento)
  return agendamento
}

export function atualizarStatusAgendamento(id: number, status: ServerAgendamento['status'], consulta?: { anamnese?: string, diagnostico?: string, medicamentos?: string, exames?: string, duracao?: number }) {
  const a = agendamentos.find(a => a.id === id)
  if (!a) return null
  a.status = status
  if (consulta?.duracao) a.duracao = consulta.duracao

  // Se foi atendido, atualiza ultimaConsulta e histórico do paciente
  if (status === 'atendido') {
    const entry: ServerPaciente['historicoRecente'][0] = {
      data: a.data.split('-').reverse().join('/'),
      descricao: consulta?.anamnese || a.descricao,
      diagnostico: consulta?.diagnostico,
      medicamentos: consulta?.medicamentos,
      exames: consulta?.exames
    }
    adicionarHistoricoPaciente(a.pacienteId, entry)
  }

  broadcast({ type: 'agendamento:status', data: { id, status, pacienteId: a.pacienteId } })
  return a
}

// ── HELPERS: CHAMADOS ──
export function getChamados() {
  return chamados
}

export function getChamadoAtivo() {
  return chamados.find(c => c.status === 'chamando') ?? null
}

export function getHistoricoChamados(limit = 10) {
  return chamados.filter(c => c.status !== 'chamando').reverse().slice(0, limit)
}

export function criarChamado(data: Omit<ServerChamado, 'id'>) {
  chamados.forEach((c) => {
    if (c.status === 'chamando') {
      c.status = 'concluido'
      broadcast({ type: 'chamado:concluido', data: c })
    }
  })
  const chamado: ServerChamado = { id: Date.now(), ...data }
  chamados.push(chamado)
  broadcast({ type: 'chamado:novo', data: chamado })
  return chamado
}

export function concluirChamado(id: number) {
  const c = chamados.find(c => c.id === id)
  if (!c) return null
  c.status = 'concluido'
  broadcast({ type: 'chamado:concluido', data: c })
  return c
}

export function concluirChamadoPorPaciente(pacienteId: number) {
  const c = chamados.find(c => c.pacienteId === pacienteId && c.status === 'chamando')
  if (!c) return null
  c.status = 'concluido'
  broadcast({ type: 'chamado:concluido', data: c })
  return c
}

// ── HELPERS: PADRÕES (preservado) ──
export function getPadroes(tipo?: string, medicoId?: number) {
  let result = padroes
  if (tipo) result = result.filter(p => p.tipo === tipo)
  if (medicoId) result = result.filter(p => p.medicoId === medicoId)
  return result
}

export function getPadrao(id: string) {
  return padroes.find(p => p.id === id) ?? null
}

export function criarPadrao(data: Omit<ServerPadrao, 'id' | 'createdAt' | 'updatedAt'>) {
  const now = new Date().toISOString()
  const padrao: ServerPadrao = { id: crypto.randomUUID(), ...data, createdAt: now, updatedAt: now }
  padroes.push(padrao)
  return padrao
}

export function atualizarPadrao(id: string, data: Partial<Omit<ServerPadrao, 'id' | 'createdAt'>>) {
  const p = padroes.find(p => p.id === id)
  if (!p) return null
  Object.assign(p, data, { updatedAt: new Date().toISOString() })
  return p
}

export function deletarPadrao(id: string) {
  const idx = padroes.findIndex(p => p.id === id)
  if (idx === -1) return false
  padroes.splice(idx, 1)
  return true
}

// ── SSE ──
export function addSseClient(client: { write: (data: string) => void, close: () => void }) {
  sseClients.add(client)
  return () => {
    sseClients.delete(client)
  }
}

function broadcast(event: { type: string, data: unknown }) {
  const message = `event: ${event.type}\ndata: ${JSON.stringify(event.data)}\n\n`
  for (const client of sseClients) {
    try {
      client.write(message)
    } catch {
      sseClients.delete(client)
    }
  }
}
