<template>
  <div class="min-h-screen bg-[#18181b] flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-[#202024] border border-zinc-800 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
      <div class="flex items-center gap-3.5">
        <img src="/logo.svg" alt="Linux Menux Monitor" class="w-11 h-11 rounded-xl shadow-lg shadow-orange-500/25 shrink-0" />
        <div>
          <h1 class="text-xl font-bold text-white">Linux Menux Monitor</h1>
          <p class="text-xs text-zinc-400">Acesse o painel de monitoramento e controle</p>
        </div>
      </div>

      <div v-if="error" class="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
        {{ error }}
      </div>

      <form @submit.prevent="submitLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-zinc-300 mb-1.5">Usuário</label>
          <input
            v-model="username"
            type="text"
            required
            autocomplete="username"
            placeholder="Usuário"
            class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-zinc-300 mb-1.5">Senha</label>
          <div class="relative">
            <input
              v-model="password"
              :type="showPass ? 'text' : 'password'"
              required
              autocomplete="current-password"
              placeholder="••••••••"
              class="w-full bg-[#141416] border border-zinc-700 rounded-lg pl-3.5 pr-10 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
            />
            <button type="button" @click="showPass = !showPass" class="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer" title="Mostrar/ocultar senha">
              <EyeOff v-if="showPass" class="w-4 h-4" />
              <Eye v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-bold py-2.5 rounded-lg transition cursor-pointer shadow-lg shadow-blue-600/20"
        >
          {{ loading ? 'Autenticando...' : 'Entrar no Painel' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Eye, EyeOff } from 'lucide-vue-next'
import { setAuthToken } from '../lib/api-config'

const emit = defineEmits(['authenticated'])
const username = ref('')
const password = ref('')
const showPass = ref(false)
const error = ref('')
const loading = ref(false)

async function submitLogin() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value.trim(), password: password.value }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok || !data.token) {
      error.value = data.detail || data.message || 'Usuário ou senha inválidos.'
      return
    }
    setAuthToken(data.token)
    emit('authenticated', { username: username.value.trim() })
  } catch {
    error.value = 'Erro de conexão ao autenticar.'
  } finally {
    loading.value = false
  }
}
</script>
