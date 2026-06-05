<script setup lang="ts">
import type { PadraoReceita, PadraoExame, PadraoAtestado } from '~/types'

const padroesStore = usePadroesStore()

onMounted(() => padroesStore.fetchAll())

const activeTab = ref<'receitas' | 'exames' | 'atestados' | null>(null)

const showReceitaModal = ref(false)
const showExameModal = ref(false)
const showAtestadoModal = ref(false)

const editingReceita = ref<PadraoReceita | null>(null)
const editingExame = ref<PadraoExame | null>(null)
const editingAtestado = ref<PadraoAtestado | null>(null)

function abrirNovaReceita() {
  editingReceita.value = null
  showReceitaModal.value = true
}

function abrirNovaExame() {
  editingExame.value = null
  showExameModal.value = true
}

function abrirNovoAtestado() {
  editingAtestado.value = null
  showAtestadoModal.value = true
}

function editarReceita(p: PadraoReceita) {
  editingReceita.value = p
  showReceitaModal.value = true
}

function editarExame(p: PadraoExame) {
  editingExame.value = p
  showExameModal.value = true
}

function editarAtestado(p: PadraoAtestado) {
  editingAtestado.value = p
  showAtestadoModal.value = true
}

async function deletarReceita(p: PadraoReceita) {
  await padroesStore.deletar(p.id)
}

async function deletarExame(p: PadraoExame) {
  await padroesStore.deletar(p.id)
}

async function deletarAtestado(p: PadraoAtestado) {
  await padroesStore.deletar(p.id)
}

function gerenciarReceita() {
  activeTab.value = 'receitas'
}

function gerenciarExame() {
  activeTab.value = 'exames'
}

function gerenciarAtestado() {
  activeTab.value = 'atestados'
}

function activeTabEmpty(): boolean {
  if (activeTab.value === 'receitas') return padroesStore.receitas.length === 0
  if (activeTab.value === 'exames') return padroesStore.exames.length === 0
  if (activeTab.value === 'atestados') return padroesStore.atestados.length === 0
  return true
}
</script>

<template>
  <div>
    <UHeader title="Padrões de Solicitações">
      <template #right>
        <UColorModeButton />
      </template>
    </UHeader>

    <div class="p-6 space-y-6 bg-neutral-100 dark:bg-neutral-950 min-h-screen">
      <div class="grid grid-cols-3 gap-6">
        <UCard>
          <template #title>
            <div class="flex items-center gap-2">
              <UIcon
                name="i-lucide-pill"
                class="text-primary"
              />
              <p class="font-semibold">
                Receitas Médicas
              </p>
            </div>
          </template>

          <template #description>
            <p class="text-sm text-muted">
              Modelos de receita com listas de medicamentos pré-definidos.
            </p>
          </template>

          <div class="flex gap-2">
            <UButton
              icon="i-lucide-plus"
              label="Novo Modelo"
              size="sm"
              @click="abrirNovaReceita"
            />
            <UButton
              label="Gerenciar"
              color="neutral"
              size="sm"
              @click="gerenciarReceita"
            />
          </div>
        </UCard>

        <UCard>
          <template #title>
            <div class="flex items-center gap-2">
              <UIcon
                name="i-lucide-flask-conical"
                class="text-primary"
              />
              <p class="font-semibold">
                Pedidos de Exames
              </p>
            </div>
          </template>

          <template #description>
            <p class="text-sm text-muted">
              Conjuntos de exames para solicitação. No atendimento você seleciona quais entrarão no pedido.
            </p>
          </template>

          <div class="flex gap-2">
            <UButton
              icon="i-lucide-plus"
              label="Novo Modelo"
              size="sm"
              @click="abrirNovaExame"
            />
            <UButton
              label="Gerenciar"
              color="neutral"
              size="sm"
              @click="gerenciarExame"
            />
          </div>
        </UCard>

        <UCard>
          <template #title>
            <div class="flex items-center gap-2">
              <UIcon
                name="i-lucide-stamp"
                class="text-primary"
              />
              <p class="font-semibold">
                Atestados Médicos
              </p>
            </div>
          </template>

          <template #description>
            <p class="text-sm text-muted">
              Modelos de atestado com placeholders como <code class="text-xs">{nome_paciente}</code>, <code class="text-xs">{dias}</code>, etc.
            </p>
          </template>

          <div class="flex gap-2">
            <UButton
              icon="i-lucide-plus"
              label="Novo Modelo"
              size="sm"
              @click="abrirNovoAtestado"
            />
            <UButton
              label="Gerenciar"
              color="neutral"
              size="sm"
              @click="gerenciarAtestado"
            />
          </div>
        </UCard>
      </div>

      <UCard v-if="activeTab">
        <template #title>
          <div class="flex items-center gap-2">
            <UIcon
              :name="activeTab === 'receitas' ? 'i-lucide-pill' : activeTab === 'exames' ? 'i-lucide-flask-conical' : 'i-lucide-stamp'"
              class="text-primary"
            />
            <p class="font-semibold">
              Modelos de {{ activeTab === 'receitas' ? 'Receitas Médicas' : activeTab === 'exames' ? 'Pedidos de Exames' : 'Atestados Médicos' }}
            </p>
          </div>
        </template>

        <div class="space-y-2">
          <template v-if="activeTab === 'receitas'">
            <div
              v-for="p in padroesStore.receitas"
              :key="p.id"
              class="flex items-center justify-between p-3 rounded-lg border border-muted hover:bg-muted/50"
            >
              <div>
                <p class="font-medium">
                  {{ p.nome }}
                </p>
                <p class="text-xs text-muted">
                  {{ p.medicamentos.length }} medicamento{{ p.medicamentos.length !== 1 ? 's' : '' }}
                  &middot; {{ new Date(p.updatedAt).toLocaleDateString('pt-BR') }}
                </p>
              </div>
              <div class="flex gap-1">
                <UButton
                  icon="i-lucide-pencil"
                  color="neutral"
                  variant="ghost"
                  size="sm"
                  @click="editarReceita(p as PadraoReceita)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  color="error"
                  variant="ghost"
                  size="sm"
                  @click="deletarReceita(p as PadraoReceita)"
                />
              </div>
            </div>
          </template>

          <template v-else-if="activeTab === 'exames'">
            <div
              v-for="p in padroesStore.exames"
              :key="p.id"
              class="flex items-center justify-between p-3 rounded-lg border border-muted hover:bg-muted/50"
            >
              <div>
                <p class="font-medium">
                  {{ p.nome }}
                </p>
                <p class="text-xs text-muted">
                  {{ p.exames.length }} exame{{ p.exames.length !== 1 ? 's' : '' }}
                  &middot; {{ new Date(p.updatedAt).toLocaleDateString('pt-BR') }}
                </p>
              </div>
              <div class="flex gap-1">
                <UButton
                  icon="i-lucide-pencil"
                  color="neutral"
                  variant="ghost"
                  size="sm"
                  @click="editarExame(p as PadraoExame)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  color="error"
                  variant="ghost"
                  size="sm"
                  @click="deletarExame(p as PadraoExame)"
                />
              </div>
            </div>
          </template>

          <template v-else>
            <div
              v-for="p in padroesStore.atestados"
              :key="p.id"
              class="flex items-center justify-between p-3 rounded-lg border border-muted hover:bg-muted/50"
            >
              <div>
                <p class="font-medium">
                  {{ p.nome }}
                </p>
                <p class="text-xs text-muted">
                  {{ new Date(p.updatedAt).toLocaleDateString('pt-BR') }}
                </p>
              </div>
              <div class="flex gap-1">
                <UButton
                  icon="i-lucide-pencil"
                  color="neutral"
                  variant="ghost"
                  size="sm"
                  @click="editarAtestado(p as PadraoAtestado)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  color="error"
                  variant="ghost"
                  size="sm"
                  @click="deletarAtestado(p as PadraoAtestado)"
                />
              </div>
            </div>
          </template>

          <p
            v-if="activeTabEmpty()"
            class="text-sm text-muted italic py-4 text-center"
          >
            Nenhum modelo cadastrado.
          </p>
        </div>
      </UCard>
    </div>

    <PadraoReceitaModal
      v-model:open="showReceitaModal"
      :padrao="editingReceita"
    />

    <PadraoExameModal
      v-model:open="showExameModal"
      :padrao="editingExame"
    />

    <PadraoAtestadoModal
      v-model:open="showAtestadoModal"
      :padrao="editingAtestado"
    />
  </div>
</template>
