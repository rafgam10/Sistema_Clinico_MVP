<script setup lang="ts">
const agendamentosStore = useAgendamentosStore()

onMounted(() => {
  if (!agendamentosStore.emAtendimento) {
    navigateTo('/dashboard')
  }
})

const agendamento = computed(() => agendamentosStore.emAtendimento)

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

const cardHeaderColors: Record<string, string> = {
  Anamnese: 'bg-primary dark:bg-primary-800',
  diagnostico: 'bg-neutral-600 dark:bg-neutral-800',
  receita: 'bg-secondary dark:bg-secondary-800',
  exames: 'bg-tertiary dark:bg-tertiary-800'
}

const historicoItems = computed(() =>
  (agendamento.value?.paciente.historicoRecente ?? []).map(item => ({
    title: item.data,
    icon: 'i-lucide-calendar',
    content: {
      Anamnese: {
        icon: 'i-lucide-file-text',
        description: item.descricao
      },
      diagnostico: {
        icon: 'i-lucide-clipboard-check',
        description: item.diagnostico
      },
      receita: {
        icon: 'i-lucide-pill',
        description: item.medicamentos
      },
      exames: {
        icon: 'i-lucide-flask-conical',
        description: item.exames
      }
    }
  }))
)
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
            :items="historicoItems"
            color="primary"
            :default-value="historicoItems.length"
            size="xs"
          >
            <template #description="{ item }">
              <div class="space-y-2 py-2">
                <UCard
                  v-for="(contentitem, key) in item.content"
                  :key="key"
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
                  <p class="text-sm">
                    {{ contentitem.description }}
                  </p>
                </UCard>
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
          @click="navigateTo('/dashboard')"
        />
      </div>
    </UCard>
  </div>
</template>
