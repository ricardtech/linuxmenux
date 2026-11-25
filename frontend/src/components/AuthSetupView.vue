<template>
  <div class="min-h-screen bg-[#18181b] flex items-center justify-center p-4">
    <div class="w-full max-w-lg bg-[#202024] border border-zinc-800 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
      <div class="flex items-center gap-3.5">
        <img src="/logo.svg" alt="Linux Menux Monitor" class="w-11 h-11 rounded-xl shadow-lg shadow-orange-500/25 shrink-0" />
        <div>
          <h1 class="text-xl font-bold text-white">Bem-vindo ao Linux Menux Monitor</h1>
          <p class="text-xs text-zinc-400">Configuração inicial de segurança e credenciais do administrador</p>
        </div>
      </div>

      <div v-if="error" class="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
        {{ error }}
      </div>

      <form @submit.prevent="submitSetup" class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-zinc-300 mb-1.5">Usuário Administrador</label>
          <input
            v-model="username"
            type="text"
            required
            autocomplete="username"
            placeholder="Ex: AlaxRicard ou admin"
            class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-zinc-300 mb-1.5">Senha (mínimo 8 caracteres)</label>
          <div class="relative">
            <input
              v-model="password"
              :type="showPass ? 'text' : 'password'"
              required
              minlength="8"
              autocomplete="new-password"
              placeholder="Digite uma senha forte"
              class="w-full bg-[#141416] border border-zinc-700 rounded-lg pl-3.5 pr-10 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
            />
            <button type="button" @click="showPass = !showPass" class="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer" title="Mostrar/ocultar senha">
              <EyeOff v-if="showPass" class="w-4 h-4" />
              <Eye v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-zinc-300 mb-1.5">Confirmar Senha</label>
          <div class="relative">
            <input
              v-model="confirmPassword"
              :type="showConfirm ? 'text' : 'password'"
              required
              minlength="8"
              autocomplete="new-password"
              placeholder="Repita a senha"
              class="w-full bg-[#141416] border border-zinc-700 rounded-lg pl-3.5 pr-10 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
            />
            <button type="button" @click="showConfirm = !showConfirm" class="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer" title="Mostrar/ocultar senha">
              <EyeOff v-if="showConfirm" class="w-4 h-4" />
              <Eye v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <button
          type="submit"
          :disabled="submitting"
          class="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-bold py-2.5 rounded-lg transition cursor-pointer shadow-lg shadow-blue-600/20"
        >
          {{ submitting ? 'Salvando credencial...' : 'Criar Credencial e Entrar' }}
        </button>
      </form>

      <div class="pt-4 border-t border-zinc-800 flex items-center justify-between gap-4">
        <span class="text-xs text-zinc-400">Ambiente local confiável? Você pode ativar depois em Segurança.</span>
        <button
          @click="skipAuthSetup"
          :disabled="submitting"
          class="text-xs text-zinc-300 hover:text-white underline cursor-pointer shrink-0"
        >
          Continuar sem senha
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Eye, EyeOff } from 'lucide-vue-next'
import { setAuthToken } from '../lib/api-config'

const emit = defineEmits(['completed'])
const username = ref('admin')
const password = ref('')
const confirmPassword = ref('')
const showPass = ref(false)
const showConfirm = ref(false)
const error = ref('')
const submitting = ref(false)

async function submitSetup() {
  error.value = ''
  if (password.value !== confirmPassword.value) {
    error.value = 'As senhas informadas não coincidem.'
    return
  }
  if (password.value.length < 8) {
    error.value = 'A senha deve ter pelo menos 8 caracteres.'
    return
  }
  submitting.value = true
  try {
    const res = await fetch('/api/auth/setup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value.trim(), password: password.value }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      error.value = data.detail || data.message || 'Erro ao configurar credencial.'
      return
    }
    if (data.token) setAuthToken(data.token)
    emit('completed', { authEnabled: true, username: username.value.trim() })
  } catch {
    error.value = 'Falha de comunicação com o servidor.'
  } finally {
    submitting.value = false
  }
}

async function skipAuthSetup() {
  submitting.value = true
  try {
    await fetch('/api/auth/decline', { method: 'POST' })
    emit('completed', { authEnabled: false, username: 'admin' })
  } finally {
    submitting.value = false
  }
}
</script>
