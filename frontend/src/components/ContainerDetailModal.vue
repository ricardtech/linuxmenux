<template>
  <BaseModal :open="open" max-width="max-w-4xl" @close="$emit('close')">
    <div v-if="container" class="flex flex-col max-h-[88vh]">
      <!-- Header -->
      <div class="flex items-start justify-between px-6 pt-5 pb-4 border-b border-[#2e2e33]">
        <div class="flex items-center gap-3 min-w-0">
          <div
            class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
            :class="isRunning ? 'bg-emerald-500/15 text-emerald-400' : 'bg-red-500/15 text-red-400'"
          >
            <Boxes class="w-5 h-5" />
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="text-base font-bold text-white truncate">{{ detail.name || container.name }}</h3>
              <span
                class="text-xs font-bold uppercase px-2 py-0.5 rounded border"
                :class="isRunning ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30'"
              >
                {{ isRunning ? 'Em execução' : 'Parado' }}
              </span>
            </div>
            <p class="text-xs text-zinc-400 truncate mt-0.5">
              ID: {{ (detail.id || container.id || '').slice(0, 12) }} · {{ detail.image || container.image }}
            </p>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="text-zinc-400 hover:text-white cursor-pointer text-base px-1.5 py-1 rounded-md hover:bg-zinc-800 transition-colors"
          title="Fechar (Esc)"
        >
          ✕
        </button>
      </div>

      <!-- 7 Tabs (1:1 ProxMenux adaptado para Docker/Compose/Swarm/Dokploy, sem VM/LXC) -->
      <div class="px-6 pt-3 border-b border-[#2e2e33] flex items-center gap-1 overflow-x-auto no-scrollbar">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="selectTab(tab.id)"
          class="px-3 py-2 text-xs font-semibold rounded-t-lg border-b-2 transition-colors cursor-pointer whitespace-nowrap"
          :class="activeTab === tab.id ? 'border-blue-500 text-white bg-white/[0.03]' : 'border-transparent text-zinc-400 hover:text-zinc-200'"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto flex-1 space-y-4">
        <div v-if="loading" class="py-12 text-center text-xs text-zinc-400">
          Carregando detalhes em tempo real do container...
        </div>

        <!-- TAB 1: Status -->
        <template v-else-if="activeTab === 'status'">
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 tabular-nums">
            <div class="bg-[#141416] border border-[#2e2e33] rounded-lg p-3">
              <div class="text-xs text-zinc-400">Uso da CPU</div>
              <div class="text-lg font-bold text-blue-400 mt-1">{{ metrics.cpu_percent ?? 0 }}%</div>
            </div>
            <div class="bg-[#141416] border border-[#2e2e33] rounded-lg p-3">
              <div class="text-xs text-zinc-400">Memória RAM</div>
              <div class="text-lg font-bold text-indigo-400 mt-1">{{ formatBytes(metrics.mem_used || 0) }}</div>
              <div class="text-xs text-zinc-500" v-if="metrics.mem_limit">
                Limite: {{ formatBytes(metrics.mem_limit) }} ({{ metrics.mem_percent }}%)
              </div>
            </div>
            <div class="bg-[#141416] border border-[#2e2e33] rounded-lg p-3">
              <div class="text-xs text-zinc-400">E/S de Rede</div>
              <div class="text-xs font-semibold text-emerald-400 mt-1">↓ {{ formatBytes(metrics.net_rx || 0) }}</div>
              <div class="text-xs font-semibold text-blue-400">↑ {{ formatBytes(metrics.net_tx || 0) }}</div>
            </div>
            <div class="bg-[#141416] border border-[#2e2e33] rounded-lg p-3">
              <div class="text-xs text-zinc-400">E/S de Disco</div>
              <div class="text-xs font-semibold text-zinc-200 mt-1">L: {{ formatBytes(metrics.blk_read || 0) }}</div>
              <div class="text-xs font-semibold text-zinc-400">E: {{ formatBytes(metrics.blk_write || 0) }}</div>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs tabular-nums">
            <div class="bg-[#141416] border border-[#2e2e33] rounded-lg p-3 space-y-1.5">
              <div class="flex justify-between"><span class="text-zinc-400">Estado:</span> <strong class="text-white">{{ detail.state || container.state }}</strong></div>
              <div class="flex justify-between"><span class="text-zinc-400">Reinicializações:</span> <strong class="text-white">{{ detail.restart_count ?? 0 }}</strong></div>
              <div class="flex justify-between"><span class="text-zinc-400">Política Restart:</span> <strong class="text-white">{{ detail.restart_policy || 'no' }}</strong></div>
              <div class="flex justify-between"><span class="text-zinc-400">Processos (PIDs):</span> <strong class="text-white">{{ metrics.pids ?? 0 }}</strong></div>
            </div>
            <div class="bg-[#141416] border border-[#2e2e33] rounded-lg p-3 space-y-1.5">
              <div class="flex justify-between"><span class="text-zinc-400">Stack / Projeto:</span> <strong class="text-white">{{ container.stack || 'standalone' }}</strong></div>
              <div class="flex justify-between"><span class="text-zinc-400">Orquestrador:</span> <strong class="text-white uppercase">{{ container.orchestrator || 'docker' }}</strong></div>
              <div class="flex justify-between items-center gap-2">
                <span class="text-zinc-400">Domínios Traefik:</span>
                <strong class="text-blue-400 truncate">{{ (detail.traefik_domains || []).join(', ') || 'Nenhum' }}</strong>
              </div>
            </div>
          </div>
        </template>

        <!-- TAB 2: App & Links -->
        <template v-else-if="activeTab === 'app'">
          <div class="bg-[#141416] border border-[#2e2e33] rounded-xl p-4 space-y-3 text-xs">
            <h4 class="font-bold text-white">Endpoints Web &amp; Acesso Rápido</h4>
            <p class="text-zinc-400">Portas e domínios expostos por este container para acesso direto no Catálogo de Apps.</p>
            <div v-if="(detail.ports || []).length" class="space-y-2">
              <div v-for="(p, idx) in (detail.ports || [])" :key="idx" class="flex items-center justify-between p-2.5 rounded-lg bg-zinc-900 border border-zinc-800">
                <span class="font-mono text-zinc-200">Porta {{ p.host_port }} → {{ p.container_port }}</span>
                <a :href="`http://${hostName}:${p.host_port}`" target="_blank" class="text-blue-400 hover:underline font-semibold">Abrir Painel ↗</a>
              </div>
            </div>
            <div v-else class="text-zinc-500">Nenhuma porta HTTP publicada neste container.</div>
          </div>
        </template>

        <!-- TAB 3: Atualizações -->
        <template v-else-if="activeTab === 'updates'">
          <div class="bg-[#141416] border border-[#2e2e33] rounded-xl p-4 space-y-3 text-xs">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="font-bold text-white">Atualizações da Imagem &amp; Pacotes</h4>
                <p class="text-zinc-400 mt-0.5">Imagem atual: <span class="font-mono text-zinc-200">{{ detail.image || container.image }}</span></p>
              </div>
              <button @click="triggerContainerUpdate" :disabled="updating" class="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold cursor-pointer">
                {{ updating ? 'Atualizando...' : 'Atualizar Container' }}
              </button>
            </div>
            <div v-if="updateOutput" class="p-3 rounded-lg bg-black border border-zinc-800 font-mono text-zinc-300 whitespace-pre-wrap max-h-48 overflow-y-auto">{{ updateOutput }}</div>
          </div>
        </template>

        <!-- TAB 4: Volumes -->
        <template v-else-if="activeTab === 'volumes'">
          <div class="space-y-2.5">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-semibold uppercase tracking-wider text-zinc-400">Volumes e Pontos de Montagem</h4>
              <span class="text-xs text-zinc-500">{{ (detail.mounts || []).length }} volume(s)</span>
            </div>
            <div v-if="!(detail.mounts || []).length" class="py-8 text-center text-xs text-zinc-500 border border-[#2e2e33] rounded-lg">
              Nenhum volume persistente montado neste container.
            </div>
            <div v-for="(m, idx) in (detail.mounts || [])" :key="idx" class="p-3 bg-[#141416] border border-[#2e2e33] rounded-lg text-xs space-y-1">
              <div class="flex items-center justify-between gap-2">
                <span class="px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300 text-xs uppercase font-semibold">{{ m.type }}</span>
                <span class="text-xs font-semibold" :class="m.rw ? 'text-emerald-400' : 'text-amber-400'">{{ m.rw ? 'Leitura/Escrita (RW)' : 'Somente Leitura (RO)' }}</span>
              </div>
              <div class="font-mono text-zinc-300 break-all">Origem: {{ m.source }}</div>
              <div class="font-mono text-zinc-400 break-all">Destino: {{ m.destination }}</div>
            </div>
          </div>
        </template>

        <!-- TAB 5: Backups -->
        <template v-else-if="activeTab === 'backups'">
          <div class="bg-[#141416] border border-[#2e2e33] rounded-xl p-4 space-y-2 text-xs">
            <h4 class="font-bold text-white">Cópias de Segurança de Volumes</h4>
            <p class="text-zinc-400">Os volumes montados acima podem ser incluídos diretamente na aba <strong>Backup</strong> (Local, Borg ou Cloudflare R2).</p>
          </div>
        </template>

        <!-- TAB 6: Rede & Portas -->
        <template v-else-if="activeTab === 'firewall'">
          <div class="space-y-4">
            <div class="space-y-2">
              <h4 class="text-xs font-semibold uppercase tracking-wider text-zinc-400">Portas Publicadas</h4>
              <div v-if="!(detail.ports || []).length" class="py-4 text-center text-xs text-zinc-500 border border-[#2e2e33] rounded-lg">
                Nenhuma porta exposta.
              </div>
              <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div v-for="(p, idx) in (detail.ports || [])" :key="idx" class="p-2.5 bg-[#141416] border border-[#2e2e33] rounded-lg text-xs font-mono flex justify-between">
                  <span class="text-zinc-400">{{ p.host_ip }}:{{ p.host_port }}</span>
                  <span class="text-emerald-400">→ {{ p.container_port }}</span>
                </div>
              </div>
            </div>

            <div class="space-y-2">
              <h4 class="text-xs font-semibold uppercase tracking-wider text-zinc-400">Redes Conectadas</h4>
              <div v-for="(n, idx) in (detail.networks || [])" :key="idx" class="p-3 bg-[#141416] border border-[#2e2e33] rounded-lg text-xs space-y-1 tabular-nums">
                <div class="font-bold text-white">{{ n.name }}</div>
                <div class="text-zinc-400 font-mono">IP: <span class="text-zinc-200">{{ n.ip }}</span> · Gateway: <span class="text-zinc-200">{{ n.gateway }}</span> · MAC: <span class="text-zinc-200">{{ n.mac }}</span></div>
              </div>
            </div>
          </div>
        </template>

        <!-- TAB 7: Logs ao vivo -->
        <template v-else-if="activeTab === 'logs'">
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs text-zinc-400">Últimas 150 linhas de log do container</span>
              <button @click="fetchInlineLogs" class="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-xs text-zinc-200 cursor-pointer">Atualizar Logs</button>
            </div>
            <pre class="bg-black border border-zinc-800 rounded-lg p-3 text-xs font-mono text-zinc-300 max-h-72 overflow-y-auto whitespace-pre-wrap">{{ inlineLogs || 'Sem logs disponíveis.' }}</pre>
          </div>
        </template>
      </div>

      <!-- Footer Action Buttons matching ProxMenux (Iniciar, Desligar, Reiniciar, Forçar paragem + Logs) -->
      <div class="px-6 py-4 border-t border-[#2e2e33] bg-[#18181b] flex items-center justify-between flex-wrap gap-2">
        <button
          @click="$emit('logs', container)"
          class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-zinc-800 hover:bg-zinc-700 text-zinc-200 cursor-pointer transition-colors"
        >
          Ver Logs em Tela Cheia
        </button>
        <div class="flex items-center gap-2 flex-wrap">
          <button
            @click="runAction('start')"
            :disabled="isRunning || actionBusy"
            class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-40 cursor-pointer transition-colors"
          >
            Iniciar
          </button>
          <button
            @click="runAction('stop')"
            :disabled="!isRunning || actionBusy"
            class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-amber-600 hover:bg-amber-500 text-white disabled:opacity-40 cursor-pointer transition-colors"
          >
            Desligar
          </button>
          <button
            @click="runAction('restart')"
            :disabled="!isRunning || actionBusy"
            class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40 cursor-pointer transition-colors"
          >
            Reiniciar
          </button>
          <button
            @click="confirmKillOpen = true"
            :disabled="!isRunning || actionBusy"
            class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-red-600 hover:bg-red-500 text-white disabled:opacity-40 cursor-pointer transition-colors"
          >
            Forçar paragem
          </button>
        </div>
      </div>

      <!-- Confirmation Banner for Destructive Kill -->
      <div v-if="confirmKillOpen" class="px-6 py-3 bg-red-950/70 border-t border-red-500/40 flex items-center justify-between gap-3 text-xs">
        <span class="text-red-200 font-semibold">Confirmar encerramento imediato (SIGKILL) de {{ detail.name || container.name }}?</span>
        <div class="flex items-center gap-2">
          <button @click="confirmKillOpen = false" class="px-3 py-1 rounded bg-zinc-800 text-zinc-200 cursor-pointer">Cancelar</button>
          <button @click="confirmKillOpen = false; runAction('kill')" class="px-3 py-1 rounded bg-red-600 text-white font-bold cursor-pointer">Confirmar Kill</button>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Boxes } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'
import { fetchApi } from '../lib/api-config'

const props = defineProps({
  open: { type: Boolean, default: false },
  container: { type: Object, default: null },
})

const emit = defineEmits(['close', 'refresh', 'logs'])

const activeTab = ref('status')
const loading = ref(false)
const actionBusy = ref(false)
const confirmKillOpen = ref(false)
const updating = ref(false)
const updateOutput = ref('')
const inlineLogs = ref('')
const detail = ref({})
const hostName = typeof window !== 'undefined' ? window.location.hostname : 'localhost'

const tabs = [
  { id: 'status', label: 'Status' },
  { id: 'app', label: 'App & Links' },
  { id: 'updates', label: 'Atualizações' },
  { id: 'volumes', label: 'Volumes' },
  { id: 'backups', label: 'Backups' },
  { id: 'firewall', label: 'Rede & Portas' },
  { id: 'logs', label: 'Logs' },
]

const isRunning = computed(() => {
  if (typeof detail.value.running === 'boolean') return detail.value.running
  return props.container?.state === 'running' || props.container?.status === 'running'
})

const metrics = computed(() => detail.value.metrics || {})

function formatBytes(bytes) {
  const b = Number(bytes || 0)
  if (b >= 1024 ** 3) return `${(b / (1024 ** 3)).toFixed(2)} GB`
  if (b >= 1024 ** 2) return `${(b / (1024 ** 2)).toFixed(1)} MB`
  if (b >= 1024) return `${(b / 1024).toFixed(1)} KB`
  return `${b} B`
}

function selectTab(id) {
  activeTab.value = id
  if (id === 'logs' && !inlineLogs.value) fetchInlineLogs()
}

async function fetchDetail() {
  if (!props.container?.id) return
  loading.value = true
  try {
    const res = await fetchApi(`/api/docker/containers/${props.container.id}/detail`)
    if (res.ok) detail.value = await res.json()
  } finally {
    loading.value = false
  }
}

async function fetchInlineLogs() {
  if (!props.container?.id) return
  const res = await fetchApi(`/api/docker/containers/${props.container.id}/logs?tail=150`)
  if (res.ok) {
    const d = await res.json()
    inlineLogs.value = d.logs || ''
  }
}

async function triggerContainerUpdate() {
  if (!props.container?.id) return
  updating.value = true
  updateOutput.value = ''
  try {
    const res = await fetchApi(`/api/docker/containers/${props.container.id}/update`, { method: 'POST' })
    const d = await res.json().catch(() => ({}))
    updateOutput.value = d.output || d.message || (res.ok ? 'Atualização concluída.' : 'Falha ao atualizar.')
    emit('refresh')
  } finally {
    updating.value = false
  }
}

async function runAction(action) {
  if (!props.container?.id) return
  actionBusy.value = true
  try {
    await fetchApi(`/api/docker/containers/${props.container.id}/${action}`, { method: 'POST' })
    await fetchDetail()
    emit('refresh')
  } finally {
    actionBusy.value = false
  }
}

watch(
  () => [props.open, props.container?.id],
  ([isOpen]) => {
    if (isOpen) {
      activeTab.value = 'status'
      confirmKillOpen.value = false
      inlineLogs.value = ''
      updateOutput.value = ''
      detail.value = {}
      fetchDetail()
    }
  }
)
</script>
