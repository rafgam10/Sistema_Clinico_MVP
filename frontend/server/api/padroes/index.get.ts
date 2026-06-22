/* eslint-disable @typescript-eslint/no-explicit-any */
export default defineEventHandler(async (event) => {
  try {
    const raw = await flaskFetch<{ padroes_receitas: any[] }>(event, '/padrao_medico_receita/lista')
    return raw.padroes_receitas.map(p => ({
      id: String(p.id),
      medicoId: Number(p.medico_id) || 0,
      nome: p.nome_modelo,
      tipo: 'receita' as const,
      medicamentos: (p.medicamentos || []).map((m: any) => ({
        id: String(m.id),
        nome: m.nome_medicamento,
        dosagem: m.dosagem,
        detalhes: m.detalhes || ''
      })),
      createdAt: p.created_at,
      updatedAt: p.updated_at
    }))
  } catch (e) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Falha ao conectar com o backend Flask',
      data: String(e)
    })
  }
})
