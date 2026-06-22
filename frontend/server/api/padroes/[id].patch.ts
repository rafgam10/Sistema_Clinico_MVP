/* eslint-disable @typescript-eslint/no-explicit-any */
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id) throw createError({ statusCode: 400, statusMessage: 'id é obrigatório' })

  const body = await readBody(event)

  if (body.nome) {
    await flaskFetch<any>(event, `/padrao_medico_receita/editar/${id}`, {
      method: 'PUT',
      body: { nome_modelo: body.nome }
    })
  }

  if (body.medicamentos) {
    const atual = await flaskFetch<any>(event, `/padrao_medico_receita/${id}`)

    for (const m of (atual.medicamentos || [])) {
      await flaskFetch(event, `/padrao_medico_receita/deletar_medicamento/${m.id}`, {
        method: 'DELETE'
      })
    }

    for (const m of body.medicamentos) {
      await flaskFetch(event, `/padrao_medico_receita/add_medicamento/${id}`, {
        method: 'POST',
        body: { nome_medicamento: m.nome, dosagem: m.dosagem, detalhes: m.detalhes || '' }
      })
    }
  }

  const final = await flaskFetch<any>(event, `/padrao_medico_receita/${id}`)
  return {
    id: String(final.id),
    medicoId: Number(final.medico_id) || 0,
    nome: final.nome_modelo,
    tipo: 'receita' as const,
    medicamentos: (final.medicamentos || []).map((m: any) => ({
      nome: m.nome_medicamento,
      dosagem: m.dosagem,
      detalhes: m.detalhes || ''
    })),
    createdAt: final.created_at,
    updatedAt: final.updated_at
  }
})
