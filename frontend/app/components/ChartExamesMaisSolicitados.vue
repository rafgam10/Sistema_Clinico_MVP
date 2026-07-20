<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import type { ChartOptions, TooltipItem } from 'chart.js'

ChartJS.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps<{
  labels: string[]
  dados: number[]
}>()

const barColor = ref<string>('#0ea5e9')

onMounted(() => {
  const el = document.documentElement
  barColor.value = getComputedStyle(el).getPropertyValue('--color-info-500').trim() || '#0ea5e9'
})

const data = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      label: 'Solicitações',
      data: props.dados,
      backgroundColor: barColor.value,
      borderRadius: 4,
      borderSkipped: false
    }
  ]
}))

const options: ChartOptions<'bar'> = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y' as const,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx: TooltipItem<'bar'>) => {
          const total = ctx.parsed.x || 0
          return ` ${total} solicitação${total !== 1 ? 'ões' : ''}`
        }
      }
    }
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: { precision: 0 }
    }
  }
}
</script>

<template>
  <ClientOnly>
    <div class="relative h-64">
      <Bar
        :data="data"
        :options="options"
        class="h-full w-full"
      />
    </div>
    <template #fallback>
      <div class="h-64 flex items-center justify-center">
        <div class="w-full h-48 bg-neutral-200 dark:bg-neutral-800 rounded animate-pulse" />
      </div>
    </template>
  </ClientOnly>
</template>
