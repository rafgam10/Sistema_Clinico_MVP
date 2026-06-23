<script setup lang="ts">
const props = defineProps<{
  abrir: boolean
  titulo: string
  descricao: string
  textoConfirma?: string
  corConfirma?: string
}>()

const emit = defineEmits<{
  fechar: []
  confirmar: []
}>()

const proxyOpen = computed({
  get: () => props.abrir,
  set: (val) => { if (!val) emit('fechar') }
})
</script>

<template>
  <UModal v-model:open="proxyOpen">
    <template #content>
      <div class="p-6 space-y-4">
        <div class="flex items-center gap-2">
          <UIcon name="lucide:trash-2" />
          <h3 class="text-xl font-black">
            {{ titulo }}
          </h3>
        </div>
        <p class="text-neutral-500 dark:text-neutral-400">
          {{ descricao }}
        </p>
        <div class="grid grid-cols-2 gap-3">
          <UButton
            label="Cancelar"
            color="neutral"
            variant="ghost"
            block
            size="lg"
            class="font-bold rounded-xl"
            @click="emit('fechar')"
          />
          <UButton
            :label="textoConfirma ?? 'Confirmar'"
            :color="(corConfirma as any) ?? 'error'"
            variant="solid"
            block
            size="lg"
            class="font-bold rounded-xl"
            @click="emit('confirmar')"
          />
        </div>
      </div>
    </template>
  </UModal>
</template>
