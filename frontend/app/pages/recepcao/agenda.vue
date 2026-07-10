<script setup lang="ts">
import { CalendarDate } from '@internationalized/date'
import type { AgendaSlot, AgendaStatus } from '~/types'

const agendamentosStore = useAgendamentosStore()
const auth = useAuthStore()

const selectedDate = ref(new Date())
const isPopoverOpen = ref(false)

const formattedDate = computed(() => {
  const d = selectedDate.value
  const diaSemana = formatarDiaDaSemana(d)
  return `${d.toLocaleDateString('pt-BR')} - ${diaSemana}`
})

const calendarDate = computed({
  get: () => {
    const d = selectedDate.value
    return new CalendarDate(d.getFullYear(), d.getMonth() + 1, d.getDate())
  },
  set: (val: CalendarDate) => {
    selectedDate.value = new Date(val.year, val.month - 1, val.day)
  }
})

function prevDay() {
  const d = new Date(selectedDate.value)
  d.setDate(d.getDate() - 1)
  selectedDate.value = d
}

function nextDay() {
  const d = new Date(selectedDate.value)
  d.setDate(d.getDate() + 1)
  selectedDate.value = d
}

function goToToday() {
  selectedDate.value = new Date()
  isPopoverOpen.value = false
}

function loadData() {
  const dataStr = formatarDataISO(selectedDate.value)
  agendamentosStore.fetchAgendamentos(auth.activeClinicaId ?? undefined, dataStr)
}

watch(selectedDate, loadData)

onMounted(() => {
  loadData()
})

function mapStatus(s: string): AgendaStatus {
  switch (s) {
    case 'em-atendimento': case 'atendido': return 'atendido'
    case 'faltou': return 'falta'
    case 'em-espera': return 'em-espera'
    default: return 'aguardando'
  }
}

const slots = computed<AgendaSlot[]>(() => {
  const result: AgendaSlot[] = []
  for (let h = 8; h <= 17; h++) {
    for (let m = 0; m < 60; m += 30) {
      const time = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
      if (time === '12:00') {
        result.push({ time, type: 'lunch' })
        continue
      }
      if (time >= '12:30' && time < '13:00') continue

      const ag = agendamentosStore.agendamentos.find(a => a.horario === time)
      if (ag) {
        result.push({
          time, type: 'appointment',
          patient: { id: ag.paciente.id, name: ag.paciente.nome, status: mapStatus(ag.status), description: ag.descricao, agendamentoId: ag.id, statusOriginal: ag.status }
        })
      } else {
        result.push({ time, type: 'available' })
      }
    }
  }
  return result
})

const statuses: { id: AgendaStatus, name: string, color: 'primary' | 'success' | 'warning' | 'info' | 'error' | 'neutral' }[] = [
  { id: 'em-espera', name: 'Em espera', color: 'primary' },
  { id: 'aguardando', name: 'Aguardando', color: 'warning' },
  { id: 'atendido', name: 'Atendido', color: 'success' },
  { id: 'falta', name: 'Falta', color: 'error' }
]

function statusColor(s: AgendaStatus) {
  return statuses.find(st => st.id === s)?.color ?? 'neutral'
}
</script>

<template>
  <div>
    <UHeader title="Agenda - Recepção">
      <div class="flex gap-4 pl-4">
        <div
          v-for="s in statuses"
          :key="s.id"
          class="flex items-center gap-1.5 text-sm"
        >
          <div :class="`size-2.5 rounded-full bg-${s.color}`" />{{ s.name }}
        </div>
      </div>
      <template #right>
        <UButton
          label="Agendamento via SPDATA"
          icon="i-lucide-lock"
          color="neutral"
          disabled
        />
        <UColorModeButton />
      </template>
    </UHeader>

    <div class="w-full p-5 px-10 flex gap-6 bg-neutral-100 dark:bg-neutral-950">
      <div class="flex-1">
        <UCard
          class="w-full h-full"
          :ui="{ root: 'flex flex-col overflow-hidden', body: 'flex-1 overflow-y-auto p-0 sm:p-0', header: 'py-6 px-6' }"
        >
          <template #header>
            <div class="flex items-center justify-between">
              <UButton
                icon="i-lucide-chevron-left"
                color="neutral"
                variant="ghost"
                size="lg"
                @click="prevDay"
              />
              <div class="flex items-center gap-4">
                <UPopover v-model:open="isPopoverOpen">
                  <UButton
                    color="neutral"
                    variant="link"
                    class="text-lg font-semibold"
                  >
                    {{ formattedDate }}
                  </UButton>
                  <template #content>
                    <div class="p-2">
                      <UCalendar v-model="calendarDate" />
                      <UButton
                        label="Hoje"
                        color="primary"
                        variant="soft"
                        size="sm"
                        class="mt-2 w-full"
                        @click="goToToday"
                      />
                    </div>
                  </template>
                </UPopover>
              </div>
              <UButton
                icon="i-lucide-chevron-right"
                color="neutral"
                variant="ghost"
                size="lg"
                @click="nextDay"
              />
            </div>
          </template>

          <UTable
            :columns="[{ accessorKey: 'time', header: '', size: 100 }, { id: 'content', header: '' }]"
            :data="slots"
            class="w-full"
            :ui="{ thead: 'hidden' }"
          >
            <template #time-cell="{ row }">
              <span
                v-if="row.original.type !== 'lunch'"
                class="font-mono text-sm whitespace-nowrap"
              >{{ row.original.time }}</span>
            </template>
            <template #content-cell="{ row }">
              <USeparator
                v-if="row.original.type === 'lunch'"
                label="Almoço"
                class="my-2 w-full"
              />
              <p
                v-else-if="row.original.type === 'available'"
                class="text-muted text-sm italic py-2"
              >
                Horário Livre
              </p>
              <UPageCard
                v-else
                variant="subtle"
                class="w-full"
                :ui="{ container: 'p-2 sm:p-2', root: `bg-${statusColor(row.original.patient!.status)}/10 ring-transparent border-l-4 border-${statusColor(row.original.patient!.status)}` }"
              >
                <template #title>
                  <div class="flex items-center gap-2">
                    <span class="font-medium">{{ row.original.patient!.name }}</span>
                    <UBadge
                      :label="row.original.patient!.status"
                      :color="statusColor(row.original.patient!.status)"
                      variant="subtle"
                      size="sm"
                    />
                  </div>
                </template>
                <template #description>
                  <p class="text-sm">
                    {{ row.original.patient!.description }}
                  </p>
                </template>
              </UPageCard>
            </template>
          </UTable>
        </UCard>
      </div>
    </div>
  </div>
</template>
