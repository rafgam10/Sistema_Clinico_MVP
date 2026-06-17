<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  total: number
  naoConfirmado: number
  recuperados: number
  faltas: number
}>()

const colors = ref<string[]>(['#0ea5e9', '#22c55e', '#ef4444'])

onMounted(() => {
  const el = document.documentElement
  colors.value = [
    getComputedStyle(el).getPropertyValue('--color-warning-500').trim() || '#0ea5e9',
    getComputedStyle(el).getPropertyValue('--color-success-500').trim() || '#22c55e',
    getComputedStyle(el).getPropertyValue('--color-error-500').trim() || '#ef4444'
  ]
})

const data = computed(() => ({
  labels: ['não confirmado', 'Recuperados', 'total de Faltas'],
  datasets: [
    {
      data: [props.naoConfirmado, props.recuperados, props.faltas],
      backgroundColor: colors.value,
      borderWidth: 0
    }
  ]
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '70%',
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        padding: 16,
        usePointStyle: true,
        font: { size: 12 }
      }
    },
    tooltip: {
      callbacks: {
        label: (ctx: { parsed: number, dataIndex: number }) => {
          return ` ${ctx.parsed} paciente${ctx.parsed !== 1 ? 's' : ''}`
        }
      }
    }
  }
}
</script>

<template>
  <div class="relative flex items-center justify-center min-h-64">
    <ClientOnly>
      <Doughnut
        :data="data"
        :options="options"
        class="w-64 h-64"
      />
      <template #fallback>
        <div class="flex items-center gap-8">
          <div class="size-48 rounded-full bg-neutral-200 dark:bg-neutral-800 animate-pulse" />
          <div class="space-y-3">
            <div
              v-for="i in 4"
              :key="i"
              class="h-4 w-24 bg-neutral-200 dark:bg-neutral-800 rounded animate-pulse"
            />
          </div>
        </div>
      </template>
    </ClientOnly>
    <div class="absolute inset-0 flex items-center justify-center pointer-events-none mb-8">
      <div class="text-center">
        <p class="text-4xl font-bold">
          {{ props.total }}
        </p>
        <p class="text-xs text-muted">
          Total
        </p>
      </div>
    </div>
  </div>
</template>
