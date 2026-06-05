<script setup lang="ts">
const result = ref<Record<string, unknown> | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    result.value = await $fetch('/api/test-flask')
  } catch (e) {
    error.value = String(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="p-6 space-y-4">
    <UHeader title="Teste de Conexão Backend" />

    <UCard v-if="loading">
      <p>Conectando ao backend Flask...</p>
      <ULoading />
    </UCard>

    <UCard v-else-if="error" color="error">
      <template #title>
        <p class="text-red-500 font-semibold">Erro</p>
      </template>
      <pre class="text-sm">{{ error }}</pre>
    </UCard>

    <UCard v-else-if="result" :color="result.success ? 'success' : 'error'">
      <template #title>
        <p class="font-semibold">
          {{ result.success ? 'Conectado ao Flask!' : 'Falha na conexão' }}
        </p>
      </template>
      <pre class="text-sm whitespace-pre-wrap">{{ JSON.stringify(result, null, 2) }}</pre>
    </UCard>
  </div>
</template>
