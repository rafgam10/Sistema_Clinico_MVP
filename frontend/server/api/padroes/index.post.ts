/* eslint-disable @typescript-eslint/no-explicit-any */
export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  if (!body.nome || !body.tipo) {
    throw createError({ statusCode: 400, statusMessage: 'nome e tipo são obrigatórios' })
  }
  const template = await flaskFetch<any>(event, '/padrao_medico_receita/criar', {
    method: 'POST',
    body: { nome_modelo: body.nome }
  })

  const medicamentosCriados: any[] = []
  for (const m of (body.medicamentos || [])) {
    const med = await flaskFetch<any>(event, `/padrao_medico_receita/add_medicamento/${template.id}`, {
      method: 'POST',
      body: { nome_medicamento: m.nome, dosagem: m.dosagem, detalhes: m.detalhes || '' }
    })
    medicamentosCriados.push(med)
  }

  return {
    id: String(template.id),
    medicoId: Number(template.medico_id),
    nome: template.nome_modelo,
    tipo: 'receita' as const,
    medicamentos: medicamentosCriados.map(m => ({
      nome: m.nome_medicamento,
      dosagem: m.dosagem,
      detalhes: m.detalhes || ''
    })),
    createdAt: template.created_at,
    updatedAt: template.updated_at
  }
})
