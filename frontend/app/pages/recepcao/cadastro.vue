<script setup lang="ts">
const pacientesStore = usePacientesStore()

const sexoOptions: { label: string, value: string }[] = [
  { label: 'Masculino', value: 'masculino' },
  { label: 'Feminino', value: 'feminino' }
]

const form = ref({
  nome: '',
  sexo: undefined as { label: string, value: string } | undefined,
  dataNascimento: '',
  tipoSanguineo: '',
  alergias: '',
  medicamentosEmUso: '',
  convenio: '',
  telefone: '',
  email: '',
  cpf: '',
  endereco: '',
  contatoEmergenciaNome: '',
  contatoEmergenciaTelefone: '',
  contatoEmergenciaParentesco: '',
  responsavelNome: '',
  responsavelTelefone: '',
  responsavelParentesco: ''
})

const successMsg = ref('')
const errorMsg = ref('')
const submitting = ref(false)

async function onSubmit() {
  submitting.value = true
  successMsg.value = ''
  errorMsg.value = ''

  try {
    const body: Record<string, unknown> = {
      nome: form.value.nome,
      sexo: form.value.sexo?.value,
      dataNascimento: form.value.dataNascimento,
      tipoSanguineo: form.value.tipoSanguineo,
      alergias: form.value.alergias ? form.value.alergias.split(',').map(s => s.trim()) : [],
      medicamentosEmUso: form.value.medicamentosEmUso ? form.value.medicamentosEmUso.split(',').map(s => ({ nome: s.trim(), dosagem: '', frequencia: '' })) : [],
      convenio: form.value.convenio,
      telefone: form.value.telefone,
      email: form.value.email,
      cpf: form.value.cpf,
      endereco: form.value.endereco
    }

    if (form.value.contatoEmergenciaNome) {
      body.contatoEmergencia = {
        nome: form.value.contatoEmergenciaNome,
        telefone: form.value.contatoEmergenciaTelefone,
        parentesco: form.value.contatoEmergenciaParentesco
      }
    }

    if (form.value.responsavelNome) {
      body.responsavel = {
        nome: form.value.responsavelNome,
        telefone: form.value.responsavelTelefone,
        parentesco: form.value.responsavelParentesco
      }
    }

    await $fetch('/api/pacientes', {
      method: 'POST',
      body
    })

    successMsg.value = 'Paciente cadastrado com sucesso!'
    form.value = {
      nome: '', sexo: undefined, dataNascimento: '', tipoSanguineo: '',
      alergias: '', medicamentosEmUso: '', convenio: '', telefone: '',
      email: '', cpf: '', endereco: '',
      contatoEmergenciaNome: '', contatoEmergenciaTelefone: '', contatoEmergenciaParentesco: '',
      responsavelNome: '', responsavelTelefone: '', responsavelParentesco: ''
    }
    pacientesStore.fetchPacientes()
  } catch {
    errorMsg.value = 'Erro ao cadastrar paciente. Verifique os dados.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <UHeader title="Cadastro de Paciente">
      <template #right>
        <UColorModeButton />
      </template>
    </UHeader>

    <div class="p-6 bg-neutral-100 dark:bg-neutral-950 min-h-screen">
      <UCard class="max-w-3xl mx-auto">
        <template #title>
          <p class="text-lg font-medium">
            Novo Paciente
          </p>
        </template>

        <UAlert
          v-if="successMsg"
          :title="successMsg"
          color="success"
          variant="subtle"
          class="mb-4"
          icon="i-lucide-check-circle"
        />
        <UAlert
          v-if="errorMsg"
          :title="errorMsg"
          color="error"
          variant="subtle"
          class="mb-4"
          icon="i-lucide-alert-circle"
        />

        <form
          class="space-y-6"
          @submit.prevent="onSubmit"
        >
          <div class="space-y-4">
            <h3 class="font-semibold text-sm text-muted uppercase tracking-wider">
              Dados Pessoais
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <UFormField
                label="Nome completo"
                required
              >
                <UInput
                  v-model="form.nome"
                  placeholder="Nome do paciente"
                  class="w-full"
                />
              </UFormField>
              <UFormField label="CPF">
                <UInput
                  v-model="form.cpf"
                  placeholder="000.000.000-00"
                  class="w-full"
                />
              </UFormField>
              <UFormField
                label="Sexo"
                required
              >
                <UInputMenu
                  v-model="form.sexo"
                  :items="sexoOptions"
                  placeholder="Selecione"
                  class="w-full"
                />
              </UFormField>
              <UFormField
                label="Data de Nascimento"
                required
              >
                <UInput
                  v-model="form.dataNascimento"
                  type="date"
                  class="w-full"
                />
              </UFormField>
              <UFormField
                label="Telefone"
                required
              >
                <UInput
                  v-model="form.telefone"
                  placeholder="(11) 99999-0000"
                  class="w-full"
                />
              </UFormField>
              <UFormField label="Email">
                <UInput
                  v-model="form.email"
                  type="email"
                  placeholder="paciente@email.com"
                  class="w-full"
                />
              </UFormField>
              <UFormField label="Tipo Sanguíneo">
                <UInput
                  v-model="form.tipoSanguineo"
                  placeholder="A+"
                  class="w-full"
                />
              </UFormField>
              <UFormField label="Convênio">
                <UInput
                  v-model="form.convenio"
                  placeholder="Unimed, Bradesco..."
                  class="w-full"
                />
              </UFormField>
            </div>
            <UFormField label="Endereço">
              <UInput
                v-model="form.endereco"
                placeholder="Rua, número, bairro, cidade"
                class="w-full"
              />
            </UFormField>
          </div>

          <USeparator />

          <div class="space-y-4">
            <h3 class="font-semibold text-sm text-muted uppercase tracking-wider">
              Informações Médicas
            </h3>
            <UFormField label="Alergias (separadas por vírgula)">
              <UInput
                v-model="form.alergias"
                placeholder="Penicilina, Dipirona, Poeira"
                class="w-full"
              />
            </UFormField>
            <UFormField label="Medicamentos em uso (separados por vírgula)">
              <UInput
                v-model="form.medicamentosEmUso"
                placeholder="Losartana, Omeprazol"
                class="w-full"
              />
            </UFormField>
          </div>

          <USeparator />

          <div class="space-y-4">
            <h3 class="font-semibold text-sm text-muted uppercase tracking-wider">
              Contato de Emergência
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <UFormField label="Nome">
                <UInput
                  v-model="form.contatoEmergenciaNome"
                  placeholder="Nome do contato"
                  class="w-full"
                />
              </UFormField>
              <UFormField label="Telefone">
                <UInput
                  v-model="form.contatoEmergenciaTelefone"
                  placeholder="(11) 99999-0000"
                  class="w-full"
                />
              </UFormField>
              <UFormField label="Parentesco">
                <UInput
                  v-model="form.contatoEmergenciaParentesco"
                  placeholder="Cônjuge, Filho..."
                  class="w-full"
                />
              </UFormField>
            </div>
          </div>

          <USeparator />

          <div class="space-y-4">
            <h3 class="font-semibold text-sm text-muted uppercase tracking-wider">
              Responsável (se menor de idade)
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <UFormField label="Nome">
                <UInput
                  v-model="form.responsavelNome"
                  placeholder="Nome do responsável"
                  class="w-full"
                />
              </UFormField>
              <UFormField label="Telefone">
                <UInput
                  v-model="form.responsavelTelefone"
                  placeholder="(11) 99999-0000"
                  class="w-full"
                />
              </UFormField>
              <UFormField label="Parentesco">
                <UInput
                  v-model="form.responsavelParentesco"
                  placeholder="Pai, Mãe, Tutor..."
                  class="w-full"
                />
              </UFormField>
            </div>
          </div>

          <div class="flex justify-end gap-2 pt-4">
            <UButton
              label="Cancelar"
              color="neutral"
              variant="soft"
              to="/recepcao"
            />
            <UButton
              label="Cadastrar"
              color="primary"
              type="submit"
              :loading="submitting"
            />
          </div>
        </form>
      </UCard>
    </div>
  </div>
</template>
