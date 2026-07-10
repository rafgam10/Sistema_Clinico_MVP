import { defineStore } from 'pinia'
import type { AuthUser, Clinica } from '~/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const clinicas = ref<Clinica[]>([])

  const _token = useCookie('auth_token', {
    maxAge: 60 * 60 * 24 * 7,
    sameSite: 'lax'
  })
  const token = computed(() => _token.value)

  const isLoggedIn = computed(() => !!_token.value)

  const _activeClinicaCookie = useCookie('active_clinica_id', {
    maxAge: 60 * 60 * 24 * 7
  })
  const activeClinicaId = ref<number | null>(
    _activeClinicaCookie.value ? Number(_activeClinicaCookie.value) : null
  )
  watch(activeClinicaId, (val) => {
    _activeClinicaCookie.value = val !== null ? String(val) : null
  })

  const activeClinica = computed(() => {
    if (!activeClinicaId.value) return null
    return clinicas.value.find(c => c.id === activeClinicaId.value) ?? null
  })

  const isMedico = computed(() => user.value?.role === 'medico')
  const isRecepcao = computed(() => user.value?.role === 'recepcao')

  async function login(credentials: Record<string, unknown>) {
    try {
      const response = await $fetch<{ token: string, user: AuthUser, clinicas: Clinica[] }>('/api/auth/login', {
        method: 'POST',
        body: credentials
      })

      _token.value = response.token
      user.value = response.user
      clinicas.value = response.clinicas

      if (response.clinicas.length > 1) {
        activeClinicaId.value = null
        if (response.user.role === 'recepcao') {
          navigateTo('/selecionar-clinica')
        } else {
          navigateTo('/selecionar-clinica')
        }
      } else {
        const primeira = response.clinicas[0]
        if (primeira) {
          activeClinicaId.value = primeira.id
        }
        if (response.user.role === 'recepcao') {
          navigateTo('/recepcao')
        } else {
          navigateTo('/')
        }
      }

      return { success: true }
    } catch (error: unknown) {
      const fetchError = error as { data?: { statusMessage?: string } }
      return {
        success: false,
        message: fetchError.data?.statusMessage || 'Erro ao realizar login'
      }
    }
  }

  function logout() {
    if (import.meta.client) useSse().disconnect()

    _token.value = null
    user.value = null
    clinicas.value = []
    activeClinicaId.value = null
    navigateTo('/login')
  }

  async function fetchUser() {
    if (_token.value && !user.value) {
      try {
        const response = await $fetch<{ user: AuthUser, clinicas: Clinica[] }>('/api/auth/me')
        user.value = response.user
        clinicas.value = response.clinicas
        if (response.clinicas.length === 1) {
          activeClinicaId.value = response.clinicas[0]!.id
        }
      } catch {
        logout()
      }
    }
  }

  function setActiveClinica(id: number) {
    activeClinicaId.value = id
  }

  return {
    user,
    token,
    clinicas,
    activeClinicaId,
    activeClinica,
    isLoggedIn,
    isMedico,
    isRecepcao,
    login,
    logout,
    fetchUser,
    setActiveClinica
  }
})
