<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, DoughnutController } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend, DoughnutController)

const props = defineProps<{
  labels: string[]
  dados: number[]
}>()

const cores = ['#22c55e', '#0ea5e9', '#d97706', '#8b5cf6', '#ef4444', '#f97316', '#06b6d4']

const data = computed(() => ({
  labels: props.labels,
  datasets: [{
    data: props.dados,
    backgroundColor: cores.slice(0, props.labels.length),
    borderWidth: 0
  }]
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '50%',
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { padding: 16, usePointStyle: true, font: { size: 12 } }
    },
    tooltip: {
      callbacks: {
        label: (ctx: { parsed: number, label: string }) => {
          const total = ctx.dataset.data.reduce((a: number, b: number) => a + b, 0)
          const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : '0'
          return ` ${ctx.label}: R$ ${ctx.parsed.toLocaleString('pt-BR')} (${pct}%)`
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
        <div class="size-48 rounded-full bg-neutral-200 dark:bg-neutral-800 animate-pulse" />
      </template>
    </ClientOnly>
  </div>
</template>
