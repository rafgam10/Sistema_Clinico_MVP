<script setup lang="ts">
import { Chart } from 'vue-chartjs'
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend, LineElement, PointElement } from 'chart.js'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend, LineElement, PointElement)

const props = defineProps<{
  labels: string[]
  dados: number[]
}>()

const barColor = ref<string>('#3271c4')
const lineColor = ref<string>('#5f7198')

onMounted(() => {
  const el = document.documentElement
  barColor.value = getComputedStyle(el).getPropertyValue('--color-primary-500').trim() || '#3271c4'
  lineColor.value = getComputedStyle(el).getPropertyValue('--color-secondary-500').trim() || '#5f7198'
})

const data = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      type: 'bar' as const,
      label: 'Faltas',
      data: props.dados,
      backgroundColor: barColor.value,
      borderRadius: 4,
      borderSkipped: false,
      order: 2
    },
    {
      type: 'line' as const,
      label: 'Tendência',
      data: props.dados,
      borderColor: lineColor.value,
      backgroundColor: lineColor.value,
      pointBackgroundColor: lineColor.value,
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
      borderWidth: 2,
      tension: 0.3,
      fill: false,
      order: 1
    }
  ]
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx: any) => {
          const v = ctx.parsed?.y ?? 0
          return ` ${ctx.dataset.label}: ${v} paciente${v !== 1 ? 's' : ''}`
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1,
        precision: 0
      }
    }
  }
}
</script>

<template>
  <ClientOnly>
    <div class="relative h-64">
      <Chart
        type="bar"
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
