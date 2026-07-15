<script setup lang="ts">
import { Chart } from 'vue-chartjs'
import { Chart as ChartJS, BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'

ChartJS.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps<{
  medicos: string[]
  taxas: number[]
}>()

const barColor = ref<string>('#22c55e')

onMounted(() => {
  const el = document.documentElement
  barColor.value = getComputedStyle(el).getPropertyValue('--color-success-500').trim() || '#22c55e'
})

const data = computed(() => ({
  labels: props.medicos,
  datasets: [
    {
      label: 'Conversão (%)',
      data: props.taxas,
      backgroundColor: barColor.value,
      borderRadius: 4,
      borderSkipped: false
    }
  ]
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y' as const,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx: { parsed: { x: number } }) => ` ${ctx.parsed.x}% de conversão`
      }
    }
  },
  scales: {
    x: {
      beginAtZero: true,
      max: 100,
      ticks: { callback: (v: number) => `${v}%` }
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
