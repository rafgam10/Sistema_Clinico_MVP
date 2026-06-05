<script setup lang="ts">
const auth = useAuthStore()
const route = useRoute()

const clinicaSelecionada = computed({
  get: () => {
    const c = auth.clinicas.find(c => c.id === auth.activeClinicaId)
    if (!c) return undefined
    return { label: c.nome, value: c.id }
  },
  set: (val: { label: string, value: number } | undefined) => {
    if (val) {
      auth.setActiveClinica(val.value)
      navigateTo(route.path)
    }
  }
})

const navItems = [
  { label: 'Dashboard', icon: 'i-lucide-layout-dashboard', to: '/dashboard' },
  { label: 'Agenda', icon: 'i-lucide-calendar', to: '/agenda' },
  { label: 'Atendimento Médico', icon: 'i-lucide-stethoscope', to: '/atendimento-medico' },
  { label: 'Padrões', icon: 'i-lucide-file-text', to: '/padroes-solicitacoes' }
]
</script>

<template>
  <div class="flex">
    <USidebar
      collapsible="icon"
      side="left"
    >
      <template #header>
        <NuxtLink to="/">
          <logoMed />
        </NuxtLink>
        <div v-if="auth.clinicas.length > 1" class="px-2 mt-2">
          <UInputMenu
            v-model="clinicaSelecionada"
            :items="auth.clinicas.map(c => ({ label: c.nome, value: c.id }))"
            size="sm"
            placeholder="Clínica..."
          />
        </div>
      </template>

      <UNavigationMenu
        orientation="vertical"
        :items="navItems"
      />

      <template #footer>
        <UButton
          icon="i-lucide-log-out"
          label="Sair"
          color="neutral"
          variant="ghost"
          class="w-full justify-start"
          @click="auth.logout()"
        />
      </template>
    </USidebar>

    <div class="flex-1 flex flex-col min-h-screen">
      <UMain>
        <slot />
      </UMain>
    </div>
  </div>
</template>
