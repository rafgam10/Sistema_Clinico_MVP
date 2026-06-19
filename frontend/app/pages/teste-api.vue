<script setup lang="ts">
const result = ref<{ success: boolean, data?: Record<string, unknown>[] } | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const showRaw = ref(false)

const totalItems = computed(() => result.value?.data?.length ?? 0)

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return '—'
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}

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

    <UCard
      v-else-if="error"
      color="error"
    >
      <template #title>
        <p class="text-red-500 font-semibold">
          Erro
        </p>
      </template>
      <pre class="text-sm">{{ error }}</pre>
    </UCard>

    <template v-else-if="result">
      <UCard :color="result.success ? 'success' : 'error'">
        <template #title>
          <p class="font-semibold">
            {{ result.success ? 'Conectado ao Flask!' : 'Falha na conexão' }}
          </p>
        </template>
        <p
          v-if="result.success"
          class="text-sm"
        >
          Total de registros: {{ totalItems }}
        </p>
      </UCard>

      <div
        v-if="result.success && totalItems"
        class="flex justify-end"
      >
        <UButton
          :icon="showRaw ? 'i-lucide-table' : 'i-lucide-code'"
          :label="showRaw ? 'Ver Cards' : 'Ver Raw JSON'"
          size="sm"
          variant="outline"
          @click="showRaw = !showRaw"
        />
      </div>

      <div
        v-if="result.success && totalItems && !showRaw"
        class="space-y-6"
      >
        <div
          v-for="(item, i) in result.data"
          :key="i"
        >
          <div class="flex items-center gap-2 mb-3">
            <span class="size-2 rounded-full bg-primary" />
            <p class="text-sm font-semibold text-foreground">
              Registro #{{ i + 1 }}
            </p>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            <div
              v-for="([key, val], j) in Object.entries(item)"
              :key="j"
              class="rounded-lg border border-muted bg-neutral-50 dark:bg-neutral-900 overflow-hidden hover:border-primary/50 transition-colors"
            >
              <p class="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted bg-neutral-100 dark:bg-neutral-800 truncate border-b border-muted">
                {{ key }}
              </p>
              <p
                class="px-3 py-2 text-sm text-foreground wrap-break-word"
                :class="val === null || val === undefined ? 'text-muted italic' : ''"
              >
                {{ formatValue(val) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <UCard v-if="result.success && totalItems && showRaw">
        <template #title>
          <p class="font-semibold">
            Dados Brutos
          </p>
        </template>
        <pre class="text-sm whitespace-pre-wrap overflow-x-auto max-h-150 overflow-y-auto">{{ JSON.stringify(result.data, null, 2) }}</pre>
      </UCard>
    </template>
  </div>
</template>
