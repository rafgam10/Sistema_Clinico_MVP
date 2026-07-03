<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, DoughnutController } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend, DoughnutController)

const props = defineProps<{
  total: number
  esquecimento: number
  transporte: number
  outros: number
}>()

const colors = ref<string[]>(['#0ea5e9', '#d97706', '#5f7198'])

onMounted(() => {
  const el = document.documentElement
  colors.value = [
    getComputedStyle(el).getPropertyValue('--color-info-500').trim() || '#0ea5e9',
    getComputedStyle(el).getPropertyValue('--color-warning-500').trim() || '#d97706',
    getComputedStyle(el).getPropertyValue('--color-secondary-500').trim() || '#5f7198'
  ]
})

const data = computed(() => ({
  labels: ['Esquecimento', 'Transporte', 'Outros'],
  datasets: [
    {
      data: [props.esquecimento, props.transporte, props.outros],
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
              v-for="i in 3"
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
