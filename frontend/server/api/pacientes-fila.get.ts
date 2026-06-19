export default defineEventHandler(async (event) => {
  try {
    const raw = await flaskFetch<Record<string, unknown>[]>(event, '/dashboard/pacientes')

    return raw.map((item: Record<string, unknown>) => {
      const entrada = item.DATA_HORA_ENTRADA ? new Date(String(item.DATA_HORA_ENTRADA)) : new Date()
      const dataStr = entrada.toISOString().slice(0, 10)
      const horarioStr = entrada.toISOString().slice(11, 16)

      return {
        id: Number(item.COD_ATENDIMENTO) || 0,
        pacienteId: Number(item.PACIENTE_ID) || 0,
        medicoId: 0,
        clinicaId: 0,
        data: dataStr,
        horario: horarioStr,
        prioridade: 'Normal',
        status: String(item.ATIVO) === 'T' ? 'em-espera' : 'agendado',
        descricao: '',
        criadoEm: dataStr,
        paciente: {
          id: Number(item.ID_RICADPAC) || null,
          nome: String(item.NOME || ''),
          sexo: String(item.SEXO) === 'F' ? 'Feminino' : 'Masculino',
          dataNascimento: String(item.NASC || ''),
          tipoSanguineo: '',
          alergias: [],
          medicamentosEmUso: [],
          convenio: String(item.ID_TBCONVEN),
          telefone: String(item.CELULAR),
          email: String(item.EMAIL || 'Não Informado'),
          cpf: String(item.CNPJ_CPF),
          endereco: String(item.LOCAL),
          historicoRecente: []
        }
      }
    })
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Falha ao conectar com o backend Flask',
      data: String(error)
    })
  }
})
