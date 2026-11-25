<template>
  <BaseModal :open="open" max-width="max-w-3xl" @close="$emit('close')">
    <div class="flex flex-col max-h-[88vh]">
      <!-- Header -->
      <div class="flex items-start justify-between px-6 pt-5 pb-3">
        <div>
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <Cpu v-if="mode === 'cpu'" class="w-5 h-5 text-blue-500" />
            <HardDrive v-else class="w-5 h-5 text-indigo-400" />
            {{ mode === 'cpu' ? 'Principais processos por CPU' : 'Principais processos por memória' }}
          </h3>
          <p class="text-xs text-zinc-400 mt-1">
            {{
              mode === 'cpu'
                ? 'Uso atual de CPU por processo. Atualiza a cada 3 s enquanto aberto.'
                : 'Memória residente atual por processo (conversão automática B/KB/MB/GB). Atualiza a cada 3 s enquanto aberto.'
            }}
          </p>
        </div>
        <button
          @click="$emit('close')"
          class="text-zinc-400 hover:text-white cursor-pointer text-base px-1.5 py-1 rounded-md hover:bg-zinc-800 transition-colors"
          title="Fechar (Esc)"
        >
          ✕
        </button>
      </div>

      <!-- Search bar (clean match by PID, Usuário or Comando without mixing cmdline paths) -->
      <div class="px-6 pb-3 flex items-center gap-2">
        <div class="relative flex-1">
          <Search class="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            v-model="filterText"
            type="text"
            placeholder="Filtrar por PID, usuário ou comando..."
            class="w-full bg-[#141416] border border-[#2e2e33] rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500"
          />
        </div>
        <select
          v-model="filterScope"
          class="bg-[#141416] border border-[#2e2e33] rounded-lg px-2.5 py-1.5 text-xs text-zinc-300 focus:outline-none"
          title="Campo do filtro"
        >
          <option value="all">Todos</option>
          <option value="user">Usuário</option>
          <option value="pid">PID</option>
          <option value="command">Comando</option>
        </select>
      </div>

      <!-- Table (strictly separated: CPU modal shows ONLY CPU, Memory modal shows ONLY Memory) -->
      <div class="mx-6 mb-3 border border-[#2e2e33] rounded-lg overflow-hidden flex-1 flex flex-col min-h-[320px] max-h-[440px]">
        <div
          class="grid items-center gap-x-4 px-3 py-2 text-xs font-semibold uppercase tracking-wider text-zinc-400 bg-[#232327] border-b border-[#2e2e33] grid-cols-[70px_100px_minmax(140px,1fr)_130px_90px]"
        >
          <div>PID</div>
          <div>USUÁRIO</div>
          <div>COMANDO</div>
          <div :class="['text-right', mode === 'cpu' ? 'text-blue-400' : 'text-indigo-400']">
            {{ mode === 'cpu' ? 'CPU %' : 'MEMÓRIA' }}
          </div>
          <div class="text-right">AÇÃO</div>
        </div>

        <div class="overflow-y-auto flex-1 divide-y divide-[#2e2e33]/60 tabular-nums">
          <div v-if="!filteredProcesses.length" class="py-10 text-center text-xs text-zinc-500">
            {{ loading ? 'Carregando processos...' : 'Nenhum processo correspondente encontrado.' }}
          </div>

          <div
            v-for="p in filteredProcesses"
            :key="p.pid"
            class="grid items-center gap-x-4 px-3 py-2 hover:bg-white/[0.03] transition-colors grid-cols-[70px_100px_minmax(140px,1fr)_130px_90px]"
          >
            <div class="font-mono text-xs text-zinc-200 flex items-center gap-1.5 min-w-0">
              <span
                class="w-1.5 h-1.5 rounded-full shrink-0"
                :style="{ background: mode === 'cpu' ? '#3b82f6' : '#6366f1' }"
              ></span>
              <span class="truncate">{{ p.pid }}</span>
            </div>

            <div class="font-mono text-xs text-zinc-300 truncate" :title="p.user">
              {{ p.user }}
            </div>

            <div class="font-mono text-xs text-zinc-200 truncate" :title="p.cmdline || p.command">
              {{ p.command }}
            </div>

            <!-- Primary Metric ONLY -->
            <div class="flex flex-col items-end gap-1">
              <span
                class="font-mono text-xs font-semibold"
                :class="mode === 'cpu' ? 'text-blue-400' : 'text-indigo-400'"
              >
                {{ mode === 'cpu' ? `${p.cpu.toFixed(1)}%` : formatRssKb(p.rss_kb) }}
              </span>
              <div class="w-full h-1 bg-zinc-800 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full"
                  :style="{
                    width: `${Math.min(100, ((mode === 'cpu' ? p.cpu : p.rss_kb) / maxPrimary) * 100)}%`,
                    background: mode === 'cpu' ? '#3b82f6' : '#6366f1',
                  }"
                ></div>
              </div>
            </div>

            <!-- Kill Process Action -->
            <div class="flex justify-end">
              <button
                v-if="confirmPid !== p.pid"
                @click="confirmPid = p.pid"
                :disabled="p.pid <= 1 || killingPid === p.pid"
                class="px-2 py-1 rounded text-xs font-medium text-red-400 hover:bg-red-500/15 border border-red-500/20 disabled:opacity-30 cursor-pointer transition-colors"
                title="Encerrar processo (SIGTERM)"
              >
                Encerrar
              </button>
              <button
                v-else
                @click="terminateProcess(p.pid)"
                :disabled="killingPid === p.pid"
                class="px-2 py-1 rounded text-xs font-semibold bg-red-600 hover:bg-red-500 text-white cursor-pointer transition-colors"
              >
                {{ killingPid === p.pid ? '...' : 'Confirmar' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Error feedback if kill fails -->
      <div v-if="actionError" class="px-6 pb-2 text-xs text-red-400">
        {{ actionError }}
      </div>

      <!-- Footer matching ProxMenux -->
      <div class="px-6 pb-4 flex items-center justify-between text-xs text-zinc-500 tabular-nums">
        <span>Capturado {{ capturedLabel }} · Principais {{ filteredProcesses.length }} dos {{ totalFetched }} processos</span>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { Cpu, HardDrive, Search } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  mode: { type: String, default: 'cpu' }, // 'cpu' | 'mem'
})

defineEmits(['close'])

const processes = ref([])
const totalFetched = ref(0)
const capturedAt = ref(0)
const loading = ref(false)
const filterText = ref('')
const filterScope = ref('all')
const confirmPid = ref(null)
const killingPid = ref(null)
const actionError = ref('')
let pollTimer = null

function formatRssKb(kb) {
  const num = Number(kb || 0)
  if (num >= 1024 * 1024) return `${(num / (1024 * 1024)).toFixed(2)} GB`
  if (num >= 1024) return `${(num / 1024).toFixed(1)} MB`
  return `${num} KB`
}

const capturedLabel = computed(() => {
  if (!capturedAt.value) return '--:--:--'
  return new Date(capturedAt.value * 1000).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
})

const filteredProcesses = computed(() => {
  const q = filterText.value.trim().toLowerCase()
  if (!q) return processes.value.slice(0, 25)

  return processes.value.filter((p) => {
    const pidStr = String(p.pid || '')
    const userStr = (p.user || '').toLowerCase()
    const cmdStr = (p.command || '').toLowerCase()

    if (filterScope.value === 'pid') return pidStr === q || pidStr.startsWith(q)
    if (filterScope.value === 'user') return userStr.includes(q)
    if (filterScope.value === 'command') return cmdStr.includes(q)

    // Default ('all'): match PID prefix, User, or Command name (never hidden paths inside cmdline)
    return pidStr.startsWith(q) || userStr.includes(q) || cmdStr.includes(q)
  })
})

const maxPrimary = computed(() => {
  if (!filteredProcesses.value.length) return 1
  const vals = filteredProcesses.value.map(p => (props.mode === 'cpu' ? Number(p.cpu || 0) : Number(p.rss_kb || 0)))
  return Math.max(1, ...vals)
})

async function fetchProcesses() {
  loading.value = true
  try {
    const res = await fetch(`/api/processes?sort=${props.mode}&limit=200`)
    if (res.ok) {
      const json = await res.json()
      processes.value = json.processes || []
      totalFetched.value = processes.value.length
      capturedAt.value = json.captured_at || Math.floor(Date.now() / 1000)
    }
  } finally {
    loading.value = false
  }
}

async function terminateProcess(pid) {
  killingPid.value = pid
  actionError.value = ''
  try {
    const res = await fetch(`/api/processes/${pid}/kill`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ force: false }),
    })
    const data = await res.json()
    if (!data.success) {
      actionError.value = data.error || `Falha ao encerrar PID ${pid}`
    } else {
      confirmPid.value = null
      await fetchProcesses()
    }
  } catch (err) {
    actionError.value = String(err)
  } finally {
    killingPid.value = null
  }
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

watch(
  () => [props.open, props.mode],
  ([isOpen]) => {
    stopPolling()
    if (isOpen) {
      filterText.value = ''
      filterScope.value = 'all'
      confirmPid.value = null
      actionError.value = ''
      fetchProcesses()
      pollTimer = setInterval(fetchProcesses, 3000)
    }
  }
)

onUnmounted(stopPolling)
</script>
