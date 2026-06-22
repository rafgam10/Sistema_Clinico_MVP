/* eslint-disable @typescript-eslint/no-explicit-any */
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id) throw createError({ statusCode: 400, statusMessage: 'o id é obrigatorio ' })
  const raw = await flaskFetch<any>(event, `/padrao_medico_receita/${id}`)

  return {
    id: String(raw.id),
    medicoId: Number(raw.medico_id) || 0,
    nome: raw.nome_modelo,
    tipo: 'receita' as const,
    medicamentos: (raw.medicamentos || []).map((m: any) => ({
      nome: m.nome_medicamento,
      dosagem: m.dosagem,
      detalhes: m.detalhes || ''
    })),
    createdAt: raw.created_at,
    updatedAt: raw.updated_at
  }
})
