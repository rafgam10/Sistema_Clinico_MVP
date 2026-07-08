export interface ExameTiss {
  nome: string
  codigo_amb?: string | null
  codigo_alfanumerico?: string | null
}

export async function gerarHtmlGuiaTiss(params: {
  paciente: string
  cpf?: string
  convenio: string
  data: string
  exames: ExameTiss[]
  medico?: string
  crm?: string
}): Promise<string> {
  const template = await $fetch<string>('/guia_tiss_sadt.html', { responseType: 'text' })

  const examesRows = params.exames.map((e, i) => exameRowHtml(i + 1, e)).join('')
  const blankRows = Array.from({ length: 5 }, (_, i) =>
    exameRowHtml(params.exames.length + i + 1, { nome: '' })
  ).join('')

  return template
    .replaceAll('{{CONVENIO}}', escapeHtml(params.convenio))
    .replaceAll('{{PACIENTE}}', escapeHtml(params.paciente))
    .replaceAll('{{CPF}}', escapeHtml(params.cpf ?? ''))
    .replaceAll('{{MEDICO}}', escapeHtml(params.medico ?? ''))
    .replaceAll('{{CRM_NUMERO}}', extractCrmNumero(params.crm))
    .replaceAll('{{DATA_SOLICITACAO}}', escapeHtml(params.data))
    .replaceAll('{{EXAMES_ROWS}}', examesRows + blankRows)
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
                <td>${index} - <input type="text" value="" style="width: 80%; float: right;"></td>
                <td><input type="text" value=""></td>
                <td><input type="text" value="${escapeHtml(e.nome)}"></td>
                <td><input type="text" value="1"></td>
                <td><input type="text" value=""></td>
            </tr>`
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
