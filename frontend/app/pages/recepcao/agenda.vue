<script setup lang="ts">
import { CalendarDate } from '@internationalized/date'
import type { AgendaSlot, AgendaStatus } from '~/types'

const agendamentosStore = useAgendamentosStore()
const auth = useAuthStore()
const pacientesStore = usePacientesStore()

const selectedDate = ref(new Date())
const isPopoverOpen = ref(false)
const showNovoAgendamento = ref(false)
const submitting = ref(false)
const successMsg = ref('')

const novoAgendamento = ref({
  paciente: undefined as { label: string, value: number } | undefined,
  medico: undefined as { label: string, value: number } | undefined,
  horario: '',
  descricao: ''
})

const pacientes = ref<{ label: string, value: number }[]>([])
const medicos = ref<{ label: string, value: number }[]>([])

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

onMounted(async () => {
  loadData()
  await pacientesStore.fetchPacientes()
  pacientes.value = pacientesStore.pacientes.map(p => ({ label: p.nome, value: p.id }))

  const params = auth.activeClinicaId ? `?clinicaId=${auth.activeClinicaId}` : ''
  const meds = await $fetch<{ id: number, nome: string }[]>(`/api/medicos${params}`)
  medicos.value = meds.map(m => ({ label: m.nome, value: m.id }))
})

function mapStatus(s: string): AgendaStatus {
  switch (s) {
    case 'em_atendimento': case 'atendido': return 'presente'
    case 'faltou': return 'falta'
    case 'confirmado': return 'confirmado'
    default: return 'aguardando'
  }
}

const slots = computed<AgendaSlot[]>(() => {
  const result: AgendaSlot[] = []
  for (let h = 8; h <= 17; h++) {
    for (let m = 0; m < 60; m += 30) {
      const time = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
      if (time === '12:00') { result.push({ time, type: 'lunch' }); continue }
      if (time >= '12:30' && time < '13:00') continue

      const ag = agendamentosStore.agendamentos.find(a => a.horario === time)
      if (ag) {
        result.push({
          time, type: 'appointment',
          patient: { id: ag.paciente.id, name: ag.paciente.nome, status: mapStatus(ag.status), description: ag.descricao }
        })
      } else {
        result.push({ time, type: 'available' })
      }
    }
  }
  return result
})

const statuses: { id: AgendaStatus, name: string, color: 'success' | 'warning' | 'info' | 'error' | 'neutral' }[] = [
  { id: 'confirmado', name: 'Confirmado', color: 'success' },
  { id: 'aguardando', name: 'Aguardando', color: 'warning' },
  { id: 'presente', name: 'Presente', color: 'info' },
  { id: 'falta', name: 'Falta', color: 'error' }
]

function statusColor(s: AgendaStatus) {
  return statuses.find(st => st.id === s)?.color ?? 'neutral'
}

function abrirFormulario() {
  successMsg.value = ''
  showNovoAgendamento.value = true
}

async function criarAgendamento() {
  if (!novoAgendamento.value.paciente || !novoAgendamento.value.medico || !novoAgendamento.value.horario) return
  if (!auth.activeClinicaId) return

  submitting.value = true
  successMsg.value = ''

  try {
    await $fetch('/api/agendamentos', {
      method: 'POST',
      body: {
        pacienteId: novoAgendamento.value.paciente.value,
        medicoId: novoAgendamento.value.medico.value,
        clinicaId: auth.activeClinicaId,
        data: formatarDataISO(selectedDate.value),
        horario: novoAgendamento.value.horario,
        descricao: novoAgendamento.value.descricao
      }
    })
    successMsg.value = 'Consulta agendada com sucesso!'
    showNovoAgendamento.value = false
    novoAgendamento.value = { paciente: undefined, medico: undefined, horario: '', descricao: '' }
    loadData()
  } catch {
    successMsg.value = 'Erro ao criar agendamento'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="h-screen flex flex-col">
    <UHeader title="Agenda - Recepção">
      <template #right>
        <UButton
          label="Novo Agendamento"
          icon="i-lucide-plus"
          color="primary"
          :disabled="!auth.activeClinicaId"
          @click="abrirFormulario"
        />
        <UColorModeButton />
      </template>
    </UHeader>

    <div class="flex-1 w-full p-5 px-10 flex gap-6 bg-neutral-100 dark:bg-neutral-950">
      <div class="flex-1">
        <UCard
          class="w-full h-full"
          :ui="{ root: 'flex flex-col overflow-hidden', body: 'flex-1 overflow-y-auto p-0 sm:p-0' }"
        >
          <template #header>
            <div class="flex items-center justify-between">
              <UButton icon="i-lucide-chevron-left" color="neutral" variant="ghost" size="lg" @click="prevDay" />
              <UPopover v-model:open="isPopoverOpen">
                <UButton color="neutral" variant="link" class="text-lg font-semibold">
                  {{ formattedDate }}
                </UButton>
                <template #content>
                  <div class="p-2">
                    <UCalendar v-model="calendarDate" />
                    <UButton label="Hoje" color="primary" variant="soft" size="sm" class="mt-2 w-full" @click="goToToday" />
                  </div>
                </template>
              </UPopover>
              <UButton icon="i-lucide-chevron-right" color="neutral" variant="ghost" size="lg" @click="nextDay" />
            </div>
            <div class="flex gap-4 mt-2">
              <div v-for="s in statuses" :key="s.id" class="flex items-center gap-1.5 text-sm">
                <div :class="`size-2.5 rounded-full bg-${s.color}`" />{{ s.name }}
              </div>
            </div>
          </template>

          <UTable :columns="[{ accessorKey: 'time', header: '', size: 100 }, { id: 'content', header: '' }]" :data="slots" class="w-full" :ui="{ thead: 'hidden' }">
            <template #time-cell="{ row }">
              <span v-if="row.original.type !== 'lunch'" class="font-mono text-sm whitespace-nowrap">{{ row.original.time }}</span>
            </template>
            <template #content-cell="{ row }">
              <USeparator v-if="row.original.type === 'lunch'" label="Almoço" class="my-2 w-full" />
              <p v-else-if="row.original.type === 'available'" class="text-muted text-sm italic py-2">Horário Livre</p>
              <UPageCard v-else variant="subtle" class="w-full" :ui="{ container: 'p-2 sm:p-2', root: `bg-${statusColor(row.original.patient!.status)}/10 ring-transparent border-l-4 border-${statusColor(row.original.patient!.status)}` }">
                <template #title>
                  <div class="flex items-center gap-2">
                    <span class="font-medium">{{ row.original.patient!.name }}</span>
                    <UBadge :label="row.original.patient!.status" :color="statusColor(row.original.patient!.status)" variant="subtle" size="sm" />
                  </div>
                </template>
                <template #description>
                  <p class="text-sm">{{ row.original.patient!.description }}</p>
                </template>
              </UPageCard>
            </template>
          </UTable>
        </UCard>
      </div>

      <div v-if="showNovoAgendamento" class="w-80 shrink-0">
        <UCard>
          <template #title>
            <div class="flex items-center justify-between">
              <span class="font-medium">Novo Agendamento</span>
              <UButton icon="i-lucide-x" color="neutral" variant="ghost" size="sm" @click="showNovoAgendamento = false" />
            </div>
          </template>

          <UAlert v-if="successMsg" :title="successMsg" :color="successMsg.includes('sucesso') ? 'success' : 'error'" variant="subtle" class="mb-4" />

          <div class="space-y-4">
            <UFormField label="Paciente" required>
              <UInputMenu v-model="novoAgendamento.paciente" :items="pacientes" placeholder="Buscar paciente..." searchable class="w-full" />
            </UFormField>
            <UFormField label="Médico" required>
              <UInputMenu v-model="novoAgendamento.medico" :items="medicos" placeholder="Selecione o médico" class="w-full" />
            </UFormField>
            <UFormField label="Horário" required>
              <UInput v-model="novoAgendamento.horario" type="time" class="w-full" />
            </UFormField>
            <UFormField label="Descrição">
              <UInput v-model="novoAgendamento.descricao" placeholder="Motivo da consulta" class="w-full" />
            </UFormField>
            <div class="flex justify-end gap-2 pt-2">
              <UButton label="Cancelar" color="neutral" variant="soft" @click="showNovoAgendamento = false" />
              <UButton label="Agendar" color="primary" :loading="submitting" @click="criarAgendamento" />
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>
