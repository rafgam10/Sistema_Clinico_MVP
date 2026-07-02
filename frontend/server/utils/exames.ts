type RawExame = string | {
  nome?: unknown
  nome_exame?: unknown
  exameId?: unknown
  exame_id?: unknown
  exame?: { id?: unknown, nome?: unknown } | null
}

function normalizarTexto(valor: unknown) {
  return typeof valor === 'string' ? valor.trim() : ''
}

function normalizarId(valor: unknown) {
  if (valor === null || valor === undefined || valor === '') return null

  const numero = Number(valor)
  return Number.isInteger(numero) && numero > 0 ? numero : null
}

export function normalizarExamePayload(exame: RawExame) {
  if (typeof exame === 'string') {
    const nome = exame.trim()
    return nome ? { nome, exame_id: null } : null
  }

  const nome = normalizarTexto(exame.nome)
    || normalizarTexto(exame.nome_exame)
    || normalizarTexto(exame.exame?.nome)
  const exame_id = normalizarId(exame.exame_id ?? exame.exameId ?? exame.exame?.id)

  if (!nome && !exame_id) return null

  return { nome, exame_id }
}

export function mapExameModelo(exame: RawExame) {
  const normalizado = normalizarExamePayload(exame)

  return {
    nome: normalizado?.nome || '',
    exameId: normalizado?.exame_id ?? null
  }
}
