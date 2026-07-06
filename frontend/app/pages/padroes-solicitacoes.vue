<script setup lang="ts">
import type { PadraoReceita, PadraoExame, PadraoAnamnese } from '~/types'

const padroesStore = usePadroesStore()
const padroesAnamneseStore = usePadroesAnamneseStore()
const toast = useToast()

onMounted(() => {
  padroesStore.fetchAll()
  padroesAnamneseStore.fetchAll()
})

const activeTab = ref<'receitas' | 'exames' | 'anamnese' | null>(null)

const showReceitaModal = ref(false)
const showExameModal = ref(false)
const showAnamneseModal = ref(false)

const editingReceita = ref<PadraoReceita | null>(null)
const editingExame = ref<PadraoExame | null>(null)
const editingAnamnese = ref<PadraoAnamnese | null>(null)

const confirmDeleteId = ref<string | null>(null)
const confirmDeleteTipo = ref<'receita' | 'exame' | 'anamnese' | null>(null)

function abrirNovaReceita() {
  editingReceita.value = null
  showReceitaModal.value = true
}

function abrirNovaExame() {
  editingExame.value = null
  showExameModal.value = true
}

function abrirNovaAnamnese() {
  editingAnamnese.value = null
  showAnamneseModal.value = true
}

function editarReceita(p: PadraoReceita) {
  editingReceita.value = p
  showReceitaModal.value = true
}

function editarExame(p: PadraoExame) {
  editingExame.value = p
  showExameModal.value = true
}

function editarAnamnese(p: PadraoAnamnese) {
  editingAnamnese.value = p
  showAnamneseModal.value = true
}

function confirmarDeletar(p: PadraoReceita | PadraoExame | PadraoAnamnese, tipo: 'receita' | 'exame' | 'anamnese') {
  confirmDeleteId.value = p.id
  confirmDeleteTipo.value = tipo
}

async function executarDeletar() {
  if (confirmDeleteId.value !== null) {
    try {
      if (confirmDeleteTipo.value === 'anamnese') {
        await padroesAnamneseStore.deletar(confirmDeleteId.value)
      } else {
        await padroesStore.deletar(confirmDeleteId.value)
      }
    } catch {
      toast.add({
        title: 'Erro ao Deletar',
        description: 'Não foi possível deletar o padrão',
        color: 'error',
        icon: 'lucide:octagon-x'
      })
    } finally {
      confirmDeleteId.value = null
      confirmDeleteTipo.value = null
    }
  }
}

function gerenciarReceita() {
  activeTab.value = 'receitas'
}

function gerenciarExame() {
  activeTab.value = 'exames'
}

function gerenciarAnamnese() {
  activeTab.value = 'anamnese'
}

function activeTabEmpty(): boolean {
  if (activeTab.value === 'receitas') return padroesStore.receitas.length === 0
  if (activeTab.value === 'exames') return padroesStore.exames.length === 0
  if (activeTab.value === 'anamnese') return padroesAnamneseStore.padroes.length === 0
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
                name="i-lucide-notebook-text"
                class="text-primary"
              />
              <p class="font-semibold">
                Anamnese
              </p>
            </div>
          </template>

          <template #description>
            <p class="text-sm text-muted">
              Modelos de anamnese com texto pré-formatado. No atendimento você insere o padrão no editor.
            </p>
          </template>

          <div class="flex gap-2">
            <UButton
              icon="i-lucide-plus"
              label="Novo Modelo"
              size="sm"
              @click="abrirNovaAnamnese"
            />
            <UButton
              label="Gerenciar"
              color="neutral"
              size="sm"
              @click="gerenciarAnamnese"
            />
          </div>
        </UCard>
      </div>

      <UCard v-if="activeTab">
        <template #title>
          <div class="flex items-center gap-2">
            <UIcon
              :name="activeTab === 'receitas' ? 'i-lucide-pill' : activeTab === 'exames' ? 'i-lucide-flask-conical' : 'i-lucide-notebook-text'"
              class="text-primary"
            />
            <p class="font-semibold">
              Modelos de {{ activeTab === 'receitas' ? 'Receitas Médicas' : activeTab === 'exames' ? 'Pedidos de Exames' : 'Anamnese' }}
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
                  @click="editarReceita(p)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  color="error"
                  variant="ghost"
                  size="sm"
                  @click="confirmarDeletar(p, 'receita')"
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
                  @click="editarExame(p)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  color="error"
                  variant="ghost"
                  size="sm"
                  @click="confirmarDeletar(p, 'exame')"
                />
              </div>
            </div>
          </template>

          <template v-else-if="activeTab === 'anamnese'">
            <div
              v-for="p in padroesAnamneseStore.padroes"
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
                  @click="editarAnamnese(p)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  color="error"
                  variant="ghost"
                  size="sm"
                  @click="confirmarDeletar(p, 'anamnese')"
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

    <PadraoAnamneseModal
      v-model:open="showAnamneseModal"
      :padrao="editingAnamnese"
    />

    <ModalConfirmacao
      :abrir="confirmDeleteId !== null"
      titulo="Deletar Padrão?"
      descricao="Tem certeza que deseja deletar este padrão?"
      texto-confirma="Deletar"
      @fechar="confirmDeleteId = null"
      @confirmar="executarDeletar"
    />
  </div>
</template>
