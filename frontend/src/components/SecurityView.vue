<template>
  <section class="space-y-6 animate-fadeIn">
    <!-- Section 1: Linux Menux Monitor (1:1 ProxMenux security.tsx) -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-cyan-400">Linux Menux Monitor</h2>
        <span class="text-xs text-zinc-400">Autenticação, Tokens da API e SSL</span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Auth & Password Card -->
        <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-sm font-bold text-white flex items-center gap-2">
                <Lock class="w-4 h-4 text-cyan-400" />
                Autenticação &amp; Credenciais
              </h4>
              <p class="text-xs text-zinc-400 mt-0.5">Proteção do painel com PBKDF2-HMAC-SHA256 e JWT.</p>
            </div>
            <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold"
              :class="authEnabled ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'">
              {{ authEnabled ? 'Protegido' : 'Desativado' }}
            </span>
          </div>

          <div class="space-y-2.5 text-xs bg-[#141416] border border-zinc-800 rounded-lg p-3.5">
            <div class="font-semibold text-zinc-200">{{ authEnabled ? 'Atualizar senha de acesso' : 'Ativar proteção por senha' }}</div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <input v-model="authUser" type="text" placeholder="Usuário admin" class="bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 text-white" />
              <div class="relative">
                <input v-model="authPass" :type="showAuthPass ? 'text' : 'password'" placeholder="Nova senha (mín. 8 chars)" class="w-full bg-zinc-900 border border-zinc-700 rounded pl-3 pr-9 py-1.5 text-white" />
                <button type="button" @click="showAuthPass = !showAuthPass" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer">
                  <EyeOff v-if="showAuthPass" class="w-3.5 h-3.5" /><Eye v-else class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
            <div class="flex items-center justify-between pt-1">
              <span v-if="authMsg" class="text-emerald-400">{{ authMsg }}</span>
              <span v-else class="text-zinc-500">Sessões protegidas via Bearer JWT</span>
              <button @click="saveAuthCredentials" class="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold cursor-pointer">
                Salvar Credencial
              </button>
            </div>
          </div>
        </div>

        <!-- API Tokens + Swagger /docs Documentation Card -->
        <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-3">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <div>
              <h4 class="text-sm font-bold text-white flex items-center gap-2">
                <Key class="w-4 h-4 text-amber-400" />
                Tokens de API &amp; Documentação
              </h4>
              <p class="text-xs text-zinc-400 mt-0.5">Chaves `lmx_*` para integrações e automações externas.</p>
            </div>
            <div class="flex items-center gap-2">
              <a href="/docs" target="_blank" class="px-2.5 py-1 rounded-lg bg-blue-600/15 hover:bg-blue-600/25 border border-blue-500/30 text-blue-300 text-xs font-semibold flex items-center gap-1">
                Swagger /docs ↗
              </a>
              <a href="/redoc" target="_blank" class="px-2.5 py-1 rounded-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 text-xs font-semibold">
                ReDoc ↗
              </a>
            </div>
          </div>

          <div class="flex gap-2">
            <input :value="newTokenName" @input="$emit('update:newTokenName', $event.target.value)" type="text" placeholder="Nome do token (ex: Automação / N8N)" class="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-1.5 text-xs text-white" />
            <button @click="$emit('generate-token')" class="bg-blue-600 hover:bg-blue-500 text-white text-xs px-3 py-1.5 rounded-lg font-semibold cursor-pointer">Gerar token</button>
          </div>

          <div v-if="lastGeneratedToken" class="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-xs tabular-nums text-emerald-300 space-y-1.5">
            <div class="font-bold">Token gerado (copie agora — não será exibido novamente):</div>
            <div class="font-mono break-all bg-black/50 p-2 rounded">{{ lastGeneratedToken }}</div>
            <div class="text-zinc-300 font-mono text-xs">curl -H "Authorization: Bearer {{ lastGeneratedToken }}" {{ originUrl }}/api/system-info</div>
          </div>

          <div class="space-y-1.5 text-xs tabular-nums max-h-36 overflow-y-auto">
            <div v-if="!(securityData.api_tokens || []).length" class="text-zinc-500 py-2">Nenhum token de API ativo. Use `Authorization: Bearer &lt;token&gt;` nas requisições.</div>
            <div v-for="t in (securityData.api_tokens || [])" :key="t.id" class="flex justify-between items-center p-2 bg-zinc-900 rounded border border-zinc-800">
              <span><strong>{{ t.name }}</strong> <span class="text-zinc-400 font-mono">({{ t.prefix || 'lmx_***' }})</span></span>
              <button @click="$emit('revoke-token', t.id)" class="text-red-400 hover:text-red-300 font-semibold cursor-pointer">Revogar</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Section 2: Sistema Linux (1:1 ProxMenux PVE section adapted for Linux) -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-orange-400">Sistema Linux</h2>
        <span class="text-xs text-zinc-400">Firewall, Gateway Seguro, Fail2Ban e Auditoria Lynis</span>
      </div>

      <!-- Firewall Card -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="text-sm font-bold text-white">Firewall ({{ securityData.firewall?.engine || 'Detectando' }})</h4>
          <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold" :class="securityData.firewall?.active ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'">
            {{ securityData.firewall?.active ? 'Ativo' : 'Inativo' }}
          </span>
        </div>
        <div class="max-h-40 overflow-y-auto bg-zinc-950 border border-zinc-800 rounded-lg p-2.5 text-xs tabular-nums text-zinc-300 space-y-1 font-mono">
          <div v-if="!(securityData.firewall?.rules || []).length" class="text-zinc-400 font-sans">Nenhuma regra listada.</div>
          <div v-for="(r, i) in (securityData.firewall?.rules || [])" :key="i">{{ r }}</div>
        </div>
        <div class="flex flex-wrap gap-2 pt-2 border-t border-zinc-800 text-xs">
          <input :value="newFwPort" @input="$emit('update:newFwPort', $event.target.value)" type="text" placeholder="Porta (ex: 8008)" class="w-32 bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-white" />
          <select :value="newFwProto" @change="$emit('update:newFwProto', $event.target.value)" class="bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-white">
            <option value="tcp">TCP</option>
            <option value="udp">UDP</option>
          </select>
          <select :value="newFwAction" @change="$emit('update:newFwAction', $event.target.value)" class="bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-white">
            <option value="allow">Permitir</option>
            <option value="deny">Bloquear</option>
          </select>
          <button @click="$emit('add-fw-rule')" class="bg-blue-600 hover:bg-blue-500 text-white px-3.5 py-1.5 rounded-lg font-semibold cursor-pointer">+ Adicionar regra</button>
        </div>
      </div>

      <!-- Tailscale, Fail2Ban & Lynis -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-2">
          <h4 class="text-sm font-bold text-white">Security Gateway (Tailscale)</h4>
          <p class="text-xs tabular-nums" :class="securityData.tailscale?.running ? 'text-emerald-400' : 'text-zinc-400'">
            {{ securityData.tailscale?.running ? `Conectado (${securityData.tailscale.ip})` : (securityData.tailscale?.installed ? 'Instalado (Desconectado)' : 'Não instalado') }}
          </p>
        </div>
        <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-3">
          <h4 class="text-sm font-bold text-white">Fail2Ban</h4>
          <p class="text-xs tabular-nums text-zinc-400">{{ securityData.fail2ban?.installed ? `Instalado (${(securityData.fail2ban?.jails || []).length} jails)` : 'Fail2Ban não está instalado' }}</p>
          <button v-if="!securityData.fail2ban?.installed" @click="$emit('install-tool', 'fail2ban')" :disabled="secInstalling === 'fail2ban'"
            class="bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-xs px-3 py-1.5 rounded-lg font-semibold cursor-pointer">
            {{ secInstalling === 'fail2ban' ? 'Instalando...' : 'Instalar e configurar' }}
          </button>
        </div>
        <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-3">
          <h4 class="text-sm font-bold text-white">Auditoria Lynis</h4>
          <p class="text-xs tabular-nums text-zinc-400">{{ securityData.lynis?.installed ? 'Instalado e pronto para auditar' : 'Lynis não está instalado' }}</p>
          <div v-if="(securityData.lynis?.reports || []).length" class="grid grid-cols-3 gap-2 text-center text-xs tabular-nums">
            <div class="p-2 bg-zinc-900 rounded border border-zinc-800"><div class="font-bold text-blue-400">{{ securityData.lynis.reports[0].hardening_index }}</div><div class="text-zinc-400">Índice</div></div>
            <div class="p-2 bg-zinc-900 rounded border border-zinc-800"><div class="font-bold text-amber-400">{{ securityData.lynis.reports[0].warnings }}</div><div class="text-zinc-400">Avisos</div></div>
            <div class="p-2 bg-zinc-900 rounded border border-zinc-800"><div class="font-bold text-zinc-200">{{ securityData.lynis.reports[0].suggestions }}</div><div class="text-zinc-400">Sugestões</div></div>
          </div>
          <div class="flex gap-2">
            <button v-if="!securityData.lynis?.installed" @click="$emit('install-tool', 'lynis')" :disabled="secInstalling === 'lynis'"
              class="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs px-3 py-1.5 rounded-lg font-semibold cursor-pointer">
              {{ secInstalling === 'lynis' ? 'Instalando...' : 'Instalar Lynis' }}
            </button>
            <button v-else @click="$emit('run-lynis')" :disabled="lynisRunning"
              class="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs px-3 py-1.5 rounded-lg font-semibold cursor-pointer">
              {{ lynisRunning ? 'Auditando...' : 'Executar auditoria' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Lock, Key, Eye, EyeOff } from 'lucide-vue-next'
import { fetchApi, setAuthToken } from '../lib/api-config'

const authEnabled = ref(false)
const authUser = ref('admin')
const authPass = ref('')
const showAuthPass = ref(false)
const authMsg = ref('')
const originUrl = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8008'

onMounted(async () => {
  try {
    const res = await fetch('/api/auth/status')
    if (res.ok) {
      const d = await res.json()
      authEnabled.value = Boolean(d.enabled)
      if (d.username) authUser.value = d.username
    }
  } catch {}
})

async function saveAuthCredentials() {
  authMsg.value = ''
  if (!authPass.value || authPass.value.length < 8) {
    authMsg.value = 'Senha deve ter pelo menos 8 caracteres.'
    return
  }
  const res = await fetchApi('/api/auth/setup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: authUser.value.trim() || 'admin', password: authPass.value }),
  })
  if (res.ok) {
    const d = await res.json().catch(() => ({}))
    if (d.token) setAuthToken(d.token)
    authEnabled.value = true
    authPass.value = ''
    authMsg.value = 'Credencial salva e proteção ativada.'
  } else {
    authMsg.value = 'Erro ao atualizar credencial.'
  }
}

defineProps({
  securityData: { type: Object, default: () => ({}) },
  newFwPort: { type: String, default: '' },
  newFwProto: { type: String, default: 'tcp' },
  newFwAction: { type: String, default: 'allow' },
  newTokenName: { type: String, default: '' },
  lastGeneratedToken: { type: String, default: '' },
  secInstalling: { type: String, default: '' },
  lynisRunning: { type: Boolean, default: false },
})
defineEmits(['update:newFwPort', 'update:newFwProto', 'update:newFwAction', 'update:newTokenName', 'add-fw-rule', 'generate-token', 'revoke-token', 'install-tool', 'run-lynis'])
</script>
