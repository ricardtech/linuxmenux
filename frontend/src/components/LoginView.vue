<template>
  <div class="min-h-screen bg-[#18181b] flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-[#202024] border border-zinc-800 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
      <div class="flex items-center gap-3.5">
        <img src="/logo.svg" alt="Linux Menux - Monitor" class="w-11 h-11 rounded-xl shadow-lg shadow-orange-500/25 shrink-0" />
        <div>
          <h1 class="text-xl font-bold text-white">Linux Menux - Monitor</h1>
          <p class="text-xs text-zinc-400">Acesse o painel de monitoramento e controle</p>
        </div>
      </div>

      <div v-if="error" class="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
        {{ error }}
      </div>
      <div v-if="infoMsg" class="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs">
        {{ infoMsg }}
      </div>

      <form v-if="!challengeId" @submit.prevent="submitLogin" class="space-y-4">
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

      <form v-else @submit.prevent="submit2FA" class="space-y-4">
        <div class="p-3 rounded-lg bg-blue-500/10 border border-blue-500/30 text-xs text-blue-300 space-y-1">
          <div class="font-semibold">Verificação em Dois Fatores (2FA)</div>
          <p v-if="twoFactorMethods.telegram && twoFactorMethods.totp">Informe o código de 6 dígitos do aplicativo autenticador ou o código enviado no Telegram.</p>
          <p v-else-if="twoFactorMethods.telegram">Informe o código de 6 dígitos enviado para o seu Bot do Telegram.</p>
          <p v-else>Informe o código de 6 dígitos do seu aplicativo autenticador (Google Authenticator / Authy).</p>
        </div>

        <div>
          <label class="block text-xs font-medium text-zinc-300 mb-1.5">Código de 6 dígitos</label>
          <input
            v-model="twoFactorCode"
            type="text"
            inputmode="numeric"
            maxlength="6"
            required
            placeholder="000000"
            class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3.5 py-2.5 text-center text-lg tracking-widest font-mono text-white focus:outline-none focus:border-blue-500"
          />
        </div>

        <div class="flex items-center justify-between gap-2 text-xs">
          <button type="button" @click="challengeId = ''; twoFactorCode = ''; error = ''; infoMsg = ''" class="text-zinc-400 hover:text-white cursor-pointer">
            ← Voltar
          </button>
          <button v-if="twoFactorMethods.telegram" type="button" @click="resendTelegramCode" :disabled="loading" class="text-blue-400 hover:text-blue-300 cursor-pointer">
            Reenviar código no Telegram
          </button>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-bold py-2.5 rounded-lg transition cursor-pointer shadow-lg shadow-blue-600/20"
        >
          {{ loading ? 'Verificando...' : 'Verificar e Entrar' }}
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
const infoMsg = ref('')
const loading = ref(false)
const challengeId = ref('')
const twoFactorCode = ref('')
const twoFactorMethods = ref({ totp: false, telegram: false })

async function submitLogin() {
  error.value = ''
  infoMsg.value = ''
  loading.value = true
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value.trim(), password: password.value }),
    })
    const data = await res.json().catch(() => ({}))
    if (data.requires_2fa && data.challenge_id) {
      challengeId.value = data.challenge_id
      twoFactorMethods.value = data.methods || { totp: true, telegram: false }
      if (data.methods?.telegram && data.methods?.telegram_sent) {
        infoMsg.value = 'Código enviado para o seu Telegram.'
      }
      return
    }
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

async function submit2FA() {
  error.value = ''
  infoMsg.value = ''
  loading.value = true
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        challenge_id: challengeId.value,
        code: twoFactorCode.value.trim(),
      }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok || !data.token) {
      error.value = data.detail || data.message || 'Código 2FA inválido.'
      return
    }
    setAuthToken(data.token)
    emit('authenticated', { username: data.username || username.value.trim() })
  } catch {
    error.value = 'Erro de conexão ao verificar 2FA.'
  } finally {
    loading.value = false
  }
}

async function resendTelegramCode() {
  error.value = ''
  infoMsg.value = ''
  loading.value = true
  try {
    const res = await fetch('/api/auth/2fa/resend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ challenge_id: challengeId.value }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      error.value = data.detail || 'Erro ao reenviar código.'
      return
    }
    infoMsg.value = data.message || 'Novo código enviado para o Telegram.'
  } finally {
    loading.value = false
  }
}
</script>
