<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent, AuthFormField } from '@nuxt/ui'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const loading = ref(false)
const errorMsg = ref('')

const fields: AuthFormField[] = [{
  name: 'email',
  type: 'email',
  label: 'Email',
  placeholder: 'Digite seu email',
  required: true
}, {
  name: 'password',
  label: 'Senha',
  type: 'password',
  placeholder: 'Digite sua senha',
  required: true
}, {
  name: 'remember',
  label: 'Mantenha-me conectado',
  type: 'checkbox'
}]

const schema = z.object({
  email: z.string('O email é obrigatório.').email('Email inválido'),
  password: z.string('A senha é obrigatória.').min(8, 'A senha deve ter pelo menos 8 caracteres')
})

type Schema = z.output<typeof schema>

async function onSubmit(payload: FormSubmitEvent<Schema>) {
  loading.value = true
  errorMsg.value = ''

  const result = await auth.login(payload.data)

  if (result.success) {
    navigateTo('/')
  } else {
    errorMsg.value = result.message || 'Erro ao realizar login'
  }

  loading.value = false
}
</script>

<template>
  <div class="p-4">
    <UPageCard class="w-full max-w-md">
      <UAuthForm
        :submit="{
          label: 'Entrar',
          icon: 'i-lucide-log-in',
          color: 'primary',
          variant: 'solid',
          loading: loading
        }"
        :schema="schema"
        title="Bem vindo de volta!"
        description="Acesse sua conta para gerenciar seus pacientes."
        :fields="fields"
        :ui="{ leading: 'flex items-center justify-center' }"
        @submit="onSubmit"
      >
        <template #leading>
          <NuxtImg
            src="img/logo-temporaria.png"
            alt="MedSystem"
            width="100"
            height="100"
          />
        </template>

        <template #password-hint>
          <ULink
            to="#"
            class="text-primary font-medium hover:underline"
            tabindex="-1"
          >Esqueci minha senha</ULink>
        </template>

        <template #validation>
          <UAlert
            v-if="errorMsg"
            :title="errorMsg"
            description="Verifique suas credenciais e tente novamente."
            color="error"
            icon="i-lucide-info"
            variant="subtle"
            class="mb-4"
          />
        </template>

        <template #footer>
          <div class="flex flex-col items-center gap-3 w-full">
            <USeparator
              label="AINDA NÃO TEM ACESSO?"
              :ui="{ label: 'text-muted' }"
            />
            <UButton
              label="Solicite Acesso à sua conta"
              trailing-icon="i-lucide-arrow-right"
              color="neutral"
              variant="subtle"
              block
              to="#"
              :ui="{ trailingIcon: 'ms-0' }"
            />

            <div class="flex justify-center gap-4 w-full">
              <span class="text-sm text-muted flex items-center gap-1">
                <UIcon name="i-lucide-shield-check" />
                LGPD Compliant
              </span>
              <span class="text-sm text-muted flex items-center gap-1">
                <UIcon name="i-lucide-shield" />
                SSL Secure
              </span>
            </div>
          </div>
        </template>
      </UAuthForm>
    </UPageCard>
  </div>
</template>
