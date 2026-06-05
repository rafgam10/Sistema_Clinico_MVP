import type { ItemMedicamento } from '~/types'

function header() {
  return { fontSize: 16, bold: true, alignment: 'center' as const, margin: [0, 0, 0, 20] }
}

const defaultStyle = { fontSize: 11, lineHeight: 1.5 }

export function buildSolicitacaoExames(params: { paciente: string, data: string, exames: string[] }) {
  return {
    pageSize: 'A4',
    pageMargins: [60, 60, 60, 60],
    content: [
      { text: 'Solicitação de Exames', style: 'header' },
      { text: `Paciente: ${params.paciente}`, margin: [0, 10, 0, 0] },
      { text: `Data: ${params.data}`, margin: [0, 0, 0, 10] },
      { text: '\n' },
      { ul: params.exames.map(e => ({ text: e })) },
      { text: '\n\n\n' },
      { text: `${params.paciente},` },
      { text: '\n__________________________' },
      { text: 'Médico Responsável' }
    ],
    styles: { header: header() },
    defaultStyle
  }
}

export function buildReceita(params: { paciente: string, data: string, medicamentos: ItemMedicamento[] }) {
  return {
    pageSize: 'A4',
    pageMargins: [60, 60, 60, 60],
    content: [
      { text: 'Receita Médica', style: 'header' },
      { text: `Paciente: ${params.paciente}`, margin: [0, 10, 0, 0] },
      { text: `Data: ${params.data}`, margin: [0, 0, 0, 10] },
      { text: '\n' },
      ...params.medicamentos.map(m => ({
        columns: [
          { text: `${m.nome} — ${m.dosagem}`, bold: true, width: '40%' },
          { text: m.detalhes, width: '60%' }
        ],
        margin: [0, 0, 0, 8] as [number, number, number, number]
      })),
      { text: '\n\n\n' },
      { text: `${params.paciente},` },
      { text: '\n__________________________' },
      { text: 'Médico Responsável' }
    ],
    styles: { header: header() },
    defaultStyle
  }
}

export async function buildAtestado(params: { paciente: string, conteudoHtml: string }) {
  const htmlToPdfmake = (await import('html-to-pdfmake')).default

  return {
    pageSize: 'A4',
    pageMargins: [60, 60, 60, 60],
    content: [
      { text: 'ATESTADO MÉDICO', style: 'header' },
      { text: '\n' },
      ...htmlToPdfmake(params.conteudoHtml, { window }),
      { text: '\n\n\n' },
      { text: `${params.paciente}, ____________________________________________________` },
      { text: '\n' },
      { text: 'Médico Responsável, ____________________________________________________' }
    ],
    styles: { header: header() },
    defaultStyle
  }
}
