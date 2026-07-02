<!-- eslint-disable vue/no-v-html -->
<script setup lang="ts">
import type { HistoricoRecord, HistoricoLocalRecord } from '~/types'
import { formatarDataHistorico } from '~/utils/time'

const { sanitizeHtml } = useSanitize()

const agendamentosStore = useAgendamentosStore()

const expandedContent = ref<Record<string, boolean>>({})

function toggleContent(id: string) {
  expandedContent.value[id] = !expandedContent.value[id]
}

onMounted(() => {
  if (!agendamentosStore.emAtendimento) {
    navigateTo('/dashboard')
    return
  }
  fetchHistorico()
})

const agendamento = computed(() => agendamentosStore.emAtendimento)

const historicoItems = ref<{ title: string, subtitle?: string, icon: string, content: Record<string, { icon: string, description: string }> }[]>([])
const isLoadingHistorico = ref(false)

function temConteudoUtil(descricao: string): boolean {
  const texto = descricao?.trim() || ''
  if (!texto) return false
  const lower = texto.toLowerCase()
  if (lower === 'não informado' || lower === 'nao informado') return false
  if (/^[\s—–-]+$/.test(texto)) return false
  return true
}

const historicoItemsVisiveis = computed(() => {
  return historicoItems.value.filter((item) => {
    if (!item.title) return false
    return Object.values(item.content).some(c => temConteudoUtil(c.description))
  })
})

const cardHeaderColors: Record<string, string> = {
  Anamnese: 'bg-primary dark:bg-primary-800',
  diagnostico: 'bg-neutral-600 dark:bg-neutral-800',
  receita: 'bg-secondary dark:bg-secondary-800',
  exames: 'bg-tertiary dark:bg-tertiary-800'
}

async function fetchHistorico() {
  // Busca histórico de dois lugares:
  //   1. Firebird legado (historico-paciente) — dados de consultas antigas
  //   2. Banco local (historico-local) — dados salvos pelo médico no MedSystem
  // Faz o merge usando spdata_atendimento_id como chave, priorizando o local
  // quando há correspondência.
  const pacienteId = agendamento.value?.paciente?.id
  if (!pacienteId) return

  isLoadingHistorico.value = true
  try {
    const [legado, local] = await Promise.all([
      $fetch<HistoricoRecord[]>(`/api/historico-paciente/${pacienteId}`),
      $fetch<HistoricoLocalRecord[]>(`/api/historico-local/${pacienteId}`)
    ])

    // Indexa registros locais por spdata_atendimento_id para merge
    const mapaLocal = new Map(
      local.filter(l => l.spdata_atendimento_id != null)
        .map(l => [String(l.spdata_atendimento_id), l])
    )

    const visitados = new Set<string>()

    // Constrói itens em array local com _sortKey (raw ISO) para ordenação correta
    const items: ({
      title: string
      subtitle?: string
      icon: string
      content: Record<string, { icon: string, description: string }>
      _sortKey: string
    })[] = []

    // Mapeia registros do legado, substituindo/complementando com dados locais
    for (const r of legado) {
      const localItem = r.ID_ATENDIMENTO ? mapaLocal.get(r.ID_ATENDIMENTO) : undefined
      if (r.ID_ATENDIMENTO) visitados.add(r.ID_ATENDIMENTO)

      items.push({
        title: formatarDataHistorico(r.DATA_CONSULTA),
        icon: 'i-lucide-calendar',
        subtitle: r.MEDICO || undefined,
        _sortKey: r.DATA_CONSULTA,
        content: {
          Anamnese: { icon: 'i-lucide-file-text', description: localItem?.anamnese || r.OBS_ATENDIMENTO || '' },
          diagnostico: { icon: 'i-lucide-clipboard-check', description: localItem ? montarDiagnosticos(localItem) : [r.CID_PRINCIPAL, r.DIAGNOSTICO_PRINCIPAL].filter(Boolean).join(' — ') },
          receita: { icon: 'i-lucide-pill', description: localItem?.medicamentos?.join('\n') || '' },
          exames: { icon: 'i-lucide-flask-conical', description: montarExames(localItem?.exames) }
        }
      })
    }

    // Adiciona registros que existem apenas no banco local
    for (const l of local) {
      const key = String(l.spdata_atendimento_id)
      if (!key || key === 'null' || visitados.has(key)) continue
      visitados.add(key)

      items.push({
        title: formatarDataHistorico(l.data_consulta || ''),
        icon: 'i-lucide-calendar',
        subtitle: l.medico_nome || undefined,
        _sortKey: l.data_consulta || '',
        content: {
          Anamnese: { icon: 'i-lucide-file-text', description: l.anamnese || '' },
          diagnostico: { icon: 'i-lucide-clipboard-check', description: montarDiagnosticos(l) },
          receita: { icon: 'i-lucide-pill', description: l.medicamentos?.join('\n') || '' },
          exames: { icon: 'i-lucide-flask-conical', description: montarExames(l.exames) }
        }
      })
    }

    // Ordena por data+hora (mais recente primeiro)
    items.sort((a, b) => new Date(b._sortKey).getTime() - new Date(a._sortKey).getTime())

    historicoItems.value = items
  } catch (err) {
    console.error('Erro ao buscar histórico:', err)
    historicoItems.value = []
  } finally {
    isLoadingHistorico.value = false
  }
}

function montarDiagnosticos(item: HistoricoLocalRecord): string {
  // Formata CID principal + secundários para exibição no card de diagnóstico
  const partes: string[] = []
  if (item.cid_principal) {
    partes.push(`${item.cid_principal} — ${item.cid_principal_descricao || ''} (principal)`)
  }
  for (const s of item.cids_secundarios) {
    partes.push(`${s.codigo} — ${s.descricao || ''}`)
  }
  return partes.join('\n')
}

function montarExames(exames?: HistoricoLocalRecord['exames']): string {
  if (!exames?.length) return ''

  return exames
    .map((exame) => {
      if (typeof exame === 'string') return exame
      return exame.nome || exame.descricao || exame.tipo_exame || ''
    })
    .filter(Boolean)
    .join('\n')
}

function calcularIdade(dataNascimento: string) {
  const hoje = new Date()
  const nasc = new Date(dataNascimento)
  let idade = hoje.getFullYear() - nasc.getFullYear()
  const mes = hoje.getMonth() - nasc.getMonth()
  if (mes < 0 || (mes === 0 && hoje.getDate() < nasc.getDate())) idade--
  return idade
}

function voltarDashboard() {
  navigateTo('/dashboard')
}
</script>

<template>
  <div
    v-if="agendamento"
    class="h-screen flex overflow-hidden"
  >
    <USidebar
      collapsible="icon"
      :style="{ '--sidebar-width': '35rem' }"
    >
      <template #header>
        <UButton
          icon="i-lucide-arrow-left"
          label="Voltar pro Dashboard"
          variant="ghost"
          color="neutral"
          @click="voltarDashboard"
        />
      </template>
      <div class="flex justify-center items-center py-2 gap-2">
        <UAvatar
          size="3xl"
          color="primary"
          :alt="agendamento.paciente.nome"
        />
        <div>
          <p class="text-md font-semibold">
            {{ agendamento.paciente.nome }}
          </p>
          <p class="text-sm text-muted">
            {{ calcularIdade(agendamento.paciente.dataNascimento) }} anos
            · {{ agendamento.paciente.sexo === 'masculino' ? 'Masculino' : 'Feminino' }}
            · Tipo Sanguíneo: {{ agendamento.paciente.tipoSanguineo }}
            · Convênio: {{ agendamento.paciente.convenio }}
          </p>
        </div>
      </div>
      <div class="space-y-2 flex flex-col gap-1 justify-center items-center overflow-y-hidden">
        <USeparator />
        <div class="flex flex-col items-center justify-center gap-2">
          <div class="flex items-center gap-1">
            <UIcon
              name="i-lucide-shield-alert"
              class="text-error mt-0.5 shrink-0"
            />
            <p class="text-xs text-error font-bold uppercase tracking-wider">
              Alergias
            </p>
          </div>

          <div class="flex flex-wrap gap-1 mt-1">
            <template v-if="agendamento.paciente.alergias.length">
              <UBadge
                v-for="(alergia, i) in agendamento.paciente.alergias"
                :key="i"
                :label="alergia"
                color="error"
                variant="subtle"
              />
            </template>
            <UBadge
              v-else
              label="Nenhuma"
              color="success"
              variant="subtle"
            />
          </div>
        </div>
        <USeparator />
        <div class="flex flex-col items-center justify-center gap-2">
          <div class="flex items-center gap-1">
            <UIcon
              name="i-lucide-pill"
              class="text-tertiary mt-0.5 shrink-0"
            />
            <p class="text-xs text-tertiary font-bold uppercase tracking-wider">
              Medicação em Uso
            </p>
          </div>
          <div class="flex flex-wrap gap-1 mt-1">
            <template v-if="agendamento.paciente.medicamentosEmUso.length">
              <UBadge
                v-for="(med, i) in agendamento.paciente.medicamentosEmUso"
                :key="i"
                :label="med.nome"
                color="tertiary"
                variant="subtle"
              />
            </template>
            <UBadge
              v-else
              label="Nenhuma"
              color="success"
              variant="subtle"
            />
          </div>
        </div>
        <USeparator />
        <div class="overflow-y-auto max-h-max w-full px-2">
          <UTimeline
            :items="historicoItemsVisiveis"
            color="primary"
            :default-value="historicoItemsVisiveis.length"
            size="xs"
          >
            <template #title="{ item }">
              <div class="flex items-center justify-between w-full">
                <span>{{ item.title }}</span>
                <span
                  v-if="item.subtitle"
                  class="text-xs text-muted truncate ml-2"
                >{{ item.subtitle }}</span>
              </div>
            </template>
            <template #description="{ item }">
              <div class="space-y-2 py-2">
                <template
                  v-for="(contentitem, key) in item.content"
                  :key="key"
                >
                  <UCard
                    v-if="temConteudoUtil(contentitem.description)"
                    class="rounded-lg border border-muted hover:bg-muted/50"
                    :ui="{
                      header: `p-0.5 sm:px-2 ${cardHeaderColors[key] ?? 'bg-primary dark:bg-primary-800'}`,
                      body: 'p-2 sm:p-2'
                    }"
                  >
                    <template #title>
                      <div class="flex items-center gap-2">
                        <UIcon
                          :name="contentitem.icon"
                          class="text-white"
                        />
                        <p class="font-semibold text-sm text-white capitalize">
                          {{ key }}
                        </p>
                      </div>
                    </template>
                    <div class="relative">
                      <!-- eslint-disable-next-line vue/no-v-html -->
                      <div
                        class="text-sm cursor-pointer"
                        :class="expandedContent[item.title + '-' + key] ? '' : 'line-clamp-3'"
                        @click="toggleContent(item.title + '-' + key)"
                        v-html="sanitizeHtml(contentitem.description)"
                      />
                      <UIcon
                        v-if="contentitem.description.length > 100"
                        :name="expandedContent[item.title + '-' + key] ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down'"
                        class="absolute bottom-0 right-0 dark:bg-neutral-900 px-1 cursor-pointer text-muted"
                        @click.stop="toggleContent(item.title + '-' + key)"
                      />
                    </div>
                  </UCard>
                </template>
              </div>
            </template>
          </UTimeline>
        </div>
      </div>
    </USidebar>
    <main class="flex-1 overflow-y-auto bg-neutral-100 dark:bg-neutral-950">
      <slot />
    </main>
  </div>
  <div
    v-else
    class="h-screen flex items-center justify-center bg-neutral-100 dark:bg-neutral-950"
  >
    <UCard>
      <div class="flex flex-col items-center py-12 gap-4">
        <div class="text-muted">
          <div class="i-lucide-stethoscope text-6xl mx-auto" />
        </div>
        <p class="text-xl font-medium">
          Nenhum paciente em atendimento
        </p>
        <p class="text-sm text-muted">
          Selecione um paciente no Dashboard e clique em "Atender" para iniciar o atendimento.
        </p>
        <UButton
          label="Ir para o Dashboard"
          color="primary"
          @click="voltarDashboard"
        />
      </div>
    </UCard>
  </div>
</template>
