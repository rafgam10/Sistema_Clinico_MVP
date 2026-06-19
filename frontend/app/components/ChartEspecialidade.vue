<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  labels: string[]
  dados: number[]
}>()

const cores = ['#0ea5e9', '#d97706', '#22c55e', '#ef4444', '#8b5cf6', '#f97316', '#06b6d4']

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
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        label: (ctx: any) => ` ${ctx.parsed} paciente${ctx.parsed !== 1 ? 's' : ''}`
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
