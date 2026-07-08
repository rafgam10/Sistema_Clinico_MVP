// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({

  modules: [
    '@nuxt/eslint',
    '@nuxt/ui',
    '@nuxt/image',
    '@pinia/nuxt',
    '@vueuse/nuxt'
  ],

  devtools: {
    enabled: true
  },

  css: ['~/assets/css/main.css'],
  colorMode: {
    preference: 'light'
  },

  ui: {
    theme: {
      colors: ['tertiary', 'error', 'success', 'info', 'warning', 'secondary', 'quaternary', 'quinary']
    }
  }, runtimeConfig: {
    flaskBaseUrl: process.env.NUXT_FLASK_BASE_URL || 'http://localhost:5000',
    enableMockAuth: process.env.NUXT_ENABLE_MOCK_AUTH === 'true'
  },

  routeRules: {
    '/': { prerender: true }
  },

  compatibilityDate: '2025-01-15',

  vite: {
    optimizeDeps: {
      include: [
        '@nuxt/ui > prosemirror-state',
        '@nuxt/ui > prosemirror-transform',
        '@nuxt/ui > prosemirror-model',
        '@nuxt/ui > prosemirror-view',
        '@nuxt/ui > prosemirror-gapcursor'
      ]
    }
  },

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  }
})
