<script setup lang="ts">
import type { PageFeatureProps } from '@nuxt/ui'

const features = ref<PageFeatureProps[]>([
  {
    title: '+15k',
    description: 'PROFISSIONAIS',
    icon: 'i-lucide-user'
  },
  {
    title: '99.9%',
    description: 'UPTIME',
    icon: 'i-lucide-clock'
  }
])
</script>

<template>
  <div class="h-dvh flex items-center overflow-hidden">
    <div class="w-1/2 hidden sm:block h-full relative">
      <NuxtImg
        src="img/bg-login.png"
        class="absolute inset-0 w-full h-full object-cover"
        alt="Background"
      />
      <div class="absolute inset-0 bg-primary-800/80" />
      <UPageSection
        title="Gestão clínica inteligente para o futuro da saúde."
        description="Centralize Consultas Médicas, Prontuários e Agendamentos em uma plataforma única, segura e projetada para profissionais de alta performance."
        :ui="{
          root: 'text-white',
          title: 'text-white font-medium text-left',
          description: 'text-white text-left',
          headline: 'pb-15'
        }"
      >
        <template #headline>
          <div class="flex items-center gap-3">
            <UBadge
              icon="medical-icon:health-services"
              size="xl"
              variant="soft"
              class="bg-white scale-120"
            />
            <div>
              <p class="text-2xl font-medium">
                MedSystem
              </p>
              <p class="text-sm font-medium text-white">
                Gestão médica
              </p>
            </div>
          </div>
        </template>

        <template #features>
          <UPageFeature
            v-for="feature in features"
            :key="feature.title"
            :title="feature.title"
            :description="feature.description"
            :icon="feature.icon"
            :ui="{
              root: 'text-white items-center justify-center',
              title: 'text-white text-left text-2xl',
              description: 'text-white text-left',
              leadingIcon: 'size-8 text-primary-200'
            }"
          />
        </template>
      </UPageSection>
    </div>
    <div class="w-full sm:w-1/2 h-full flex items-center justify-center bg-[url('/img/bg-login.png')] bg-cover bg-center sm:bg-none">
      <div class="absolute inset-0 sm:hidden bg-primary-800/80" />
      <slot />
    </div>
  </div>
</template>
