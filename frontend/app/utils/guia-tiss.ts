export interface ExameTiss {
  nome: string
  codigo_amb?: string | null
  codigo_alfanumerico?: string | null
}

const EXAMES_POR_PAGINA = 4

export async function gerarHtmlGuiaTiss(params: {
  paciente: string
  cpf?: string
  convenio: string
  data: string
  exames: ExameTiss[]
  medico?: string
  crm?: string
}): Promise<string> {
  const template = await $fetch<string>('/guia_tiss_sadt-v2.html', { responseType: 'text' })

  const bodyStart = template.indexOf('<body>') + '<body>'.length
  const bodyEnd = template.indexOf('</body>')
  const beforeBody = template.slice(0, bodyStart)
  const bodyContent = template.slice(bodyStart, bodyEnd).trim()
  const afterBody = template.slice(bodyEnd)

  const batches = chunk(params.exames, EXAMES_POR_PAGINA)

  const pages = batches.map((batch, batchIdx) => {
    const startNum = batchIdx * EXAMES_POR_PAGINA
    const examesRows = batch.map((e, i) =>
      exameRowHtml(startNum + i + 1, e)
    ).join('')
    const blankRows = Array.from({ length: EXAMES_POR_PAGINA - batch.length }, (_, i) =>
      exameRowHtml(startNum + batch.length + i + 1, { nome: '' })
    ).join('')

    return bodyContent
      .replaceAll('{{CONVENIO}}', escapeHtml(params.convenio))
      .replaceAll('{{PACIENTE}}', escapeHtml(params.paciente))
      .replaceAll('{{CPF}}', escapeHtml(params.cpf ?? ''))
      .replaceAll('{{MEDICO}}', escapeHtml(params.medico ?? ''))
      .replaceAll('{{CRM_NUMERO}}', extractCrmNumero(params.crm))
      .replaceAll('{{DATA_SOLICITACAO}}', escapeHtml(params.data))
      .replaceAll('{{EXAMES_ROWS}}', examesRows + blankRows)
  })

  return beforeBody + '\n' + pages.join('\n') + '\n' + afterBody
}

export function imprimirGuiaTiss(html: string) {
  const w = window.open('', '_blank')
  if (!w) return
  w.document.open()
  w.document.write(html)
  w.document.close()
  w.focus()
  setTimeout(() => {
    w.print()
    w.close()
  }, 250)
}

function exameRowHtml(index: number, e: ExameTiss): string {
  return `            <tr>
                <td>${index} - <input type="text" value="" style="width: 60%; float: right; height:12px;"></td>
                <td><input type="text" value=""></td>
                <td><input type="text" value="${escapeHtml(e.nome)}"></td>
                <td><input type="text" value="1"></td>
                <td><input type="text" value=""></td>
            </tr>`
}

function chunk<T>(arr: T[], size: number): T[][] {
  const chunks: T[][] = []
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size))
  }
  return chunks
}

function escapeHtml(text: string): string {
  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

function extractCrmNumero(crm?: string): string {
  if (!crm) return ''
  const match = crm.match(/\d+/)
  return match ? escapeHtml(match[0]) : ''
}
