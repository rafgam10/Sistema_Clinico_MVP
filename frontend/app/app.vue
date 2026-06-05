<script setup lang="ts">
const auth = useAuthStore()
onMounted(() => auth.fetchUser())

const route = useRoute()
const layoutName = computed(() => {
  const path = route.path
  if (path === '/login') return 'auth'
  if (path === '/painel-chamada') return 'tv'
  if (path === '/atendimento-medico') return 'atendimento'
  if (path.startsWith('/recepcao')) return 'recepcao'
  return 'default'
})

useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ],
  link: [
    { rel: 'icon', href: '/favicon.ico' }
  ],
  htmlAttrs: {
    lang: 'pt-BR'
  }
})

const title = 'MedSystem'
const description = 'Gestão clínica inteligente para o futuro da saúde.'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description
})
</script>

<template>
  <UApp>
    <NuxtLayout :name="layoutName">
      <NuxtPage :key="$route.fullPath" />
    </NuxtLayout>
  </UApp>
</template>
