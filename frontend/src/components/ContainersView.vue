<template>
  <section class="space-y-6 animate-fadeIn">
    <!-- Top 4 Cards matching ProxMenux virtual-machines.tsx (Circular SVG Gauges + Disk Bar) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 tabular-nums">
      <!-- Card 1: Total de Containers -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between text-xs font-semibold text-zinc-400">
          <span>Total de Containers</span>
          <Boxes class="w-4 h-4 text-zinc-500" />
        </div>
        <div class="flex items-center justify-between mt-3">
          <span class="text-3xl font-black text-white">{{ containerStats.total }}</span>
          <div class="flex flex-col items-end gap-1">
            <span class="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">
              {{ containerStats.running }} Em execução
            </span>
            <span class="text-xs bg-zinc-800 text-zinc-400 border border-zinc-700 px-2 py-0.5 rounded-full font-medium">
              {{ containerStats.stopped }} Parado
            </span>
          </div>
        </div>
      </div>

      <!-- Card 2: Total de CPU alocada (Circular Gauge) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between text-xs font-semibold text-zinc-400">
          <span>Total de CPU alocada</span>
          <Cpu class="w-4 h-4 text-zinc-500" />
        </div>
        <div class="flex items-center gap-4 mt-3">
          <div class="relative w-14 h-14 shrink-0">
            <svg class="w-14 h-14 -rotate-90" viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="15.5" fill="none" stroke="#27272a" stroke-width="3.2" />
              <circle
                cx="18" cy="18" r="15.5" fill="none" stroke="#3b82f6" stroke-width="3.2"
                stroke-linecap="round"
                :stroke-dasharray="`${Math.min(100, cpuPct) * 0.974} 100`"
              />
            </svg>
            <span class="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">{{ Math.round(cpuPct) }}%</span>
          </div>
          <div class="text-xs space-y-1 flex-1">
            <div class="flex justify-between"><span class="text-zinc-400">Núcleos:</span> <span class="text-zinc-200 font-semibold">{{ systemData.cpu_cores || 0 }} vCPU</span></div>
            <div class="flex justify-between"><span class="text-zinc-400">Em uso:</span> <span class="text-blue-400 font-semibold">{{ cpuPct.toFixed(1) }}%</span></div>
          </div>
        </div>
      </div>

      <!-- Card 3: Memória total (Circular Gauge) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between text-xs font-semibold text-zinc-400">
          <span>Memória total</span>
          <HardDrive class="w-4 h-4 text-zinc-500" />
        </div>
        <div class="flex items-center gap-4 mt-3">
          <div class="relative w-14 h-14 shrink-0">
            <svg class="w-14 h-14 -rotate-90" viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="15.5" fill="none" stroke="#27272a" stroke-width="3.2" />
              <circle
                cx="18" cy="18" r="15.5" fill="none" stroke="#8b5cf6" stroke-width="3.2"
                stroke-linecap="round"
                :stroke-dasharray="`${Math.min(100, memPct) * 0.974} 100`"
              />
            </svg>
            <span class="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">{{ Math.round(memPct) }}%</span>
          </div>
          <div class="text-xs space-y-1 flex-1">
            <div class="flex justify-between"><span class="text-zinc-400">Usado:</span> <span class="text-blue-400 font-semibold">{{ (systemData.memory_used || 0).toFixed(1) }} GB</span></div>
            <div class="flex justify-between"><span class="text-zinc-400">Total:</span> <span class="text-zinc-200 font-semibold">{{ (systemData.memory_total || 0).toFixed(1) }} GB</span></div>
          </div>
        </div>
      </div>

      <!-- Card 4: Disco total -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between text-xs font-semibold text-zinc-400">
          <span>Disco total</span>
          <Database class="w-4 h-4 text-zinc-500" />
        </div>
        <div class="mt-3 space-y-2">
          <div class="flex items-baseline justify-between">
            <span class="text-2xl font-black text-white">{{ diskUsedGb }} GB</span>
            <span class="text-xs text-zinc-400">de {{ diskTotalGb }} GB ({{ diskPercent }}%)</span>
          </div>
          <div class="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
            <div class="h-full bg-blue-500 rounded-full transition-all" :style="{ width: `${Math.min(100, diskPercent)}%` }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Container List Card matching ProxMenux virtual-machines.tsx -->
    <div class="bg-[#18181b] border border-zinc-800 rounded-xl overflow-hidden shadow-sm">
      <div class="p-4 border-b border-zinc-800 flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <Boxes class="w-5 h-5 text-blue-500" />
          <h3 class="text-base font-bold text-white">Containers Docker &amp; Dokploy</h3>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <!-- Search -->
          <div class="relative flex-1 sm:flex-initial">
            <Search class="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar por nome, ID ou imagem..."
              class="bg-zinc-900 border border-zinc-800 text-xs text-zinc-200 pl-8 pr-3 py-1.5 rounded-lg focus:outline-none focus:border-blue-500 w-full sm:w-56"
            />
          </div>

          <!-- Filter Pills: Todos | Em execução | Parado | Atualizações -->
          <div class="flex items-center bg-zinc-900 border border-zinc-800 rounded-lg p-0.5 text-xs">
            <button
              @click="statusFilter = 'all'"
              class="px-2.5 py-1 rounded-md font-medium transition-colors cursor-pointer"
              :class="statusFilter === 'all' ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-zinc-200'"
            >
              Todos {{ containerStats.total }}
            </button>
            <button
              @click="statusFilter = 'running'"
              class="px-2.5 py-1 rounded-md font-medium transition-colors cursor-pointer"
              :class="statusFilter === 'running' ? 'bg-emerald-600 text-white' : 'text-zinc-400 hover:text-zinc-200'"
            >
              Em execução {{ containerStats.running }}
            </button>
            <button
              @click="statusFilter = 'stopped'"
              class="px-2.5 py-1 rounded-md font-medium transition-colors cursor-pointer"
              :class="statusFilter === 'stopped' ? 'bg-red-600 text-white' : 'text-zinc-400 hover:text-zinc-200'"
            >
              Parado {{ containerStats.stopped }}
            </button>
            <button
              @click="statusFilter = 'updates'"
              class="px-2.5 py-1 rounded-md font-medium transition-colors cursor-pointer"
              :class="statusFilter === 'updates' ? 'bg-amber-600 text-white' : 'text-zinc-400 hover:text-zinc-200'"
            >
              Atualizações {{ updatesCount }}
            </button>
          </div>

          <button
            @click="$emit('check-updates')"
            :disabled="checkingUpdates"
            class="text-xs px-2.5 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 flex items-center gap-1 cursor-pointer"
          >
            <RefreshCw class="w-3 h-3" :class="{ 'animate-spin': checkingUpdates }" />
            Verificar
          </button>
        </div>
      </div>

      <!-- Container Rows (click row to open ContainerDetailModal) -->
      <div class="divide-y divide-zinc-800/60">
        <div v-if="!filteredList.length" class="p-10 text-center text-xs text-zinc-500">
          Nenhum container encontrado com os filtros atuais.
        </div>

        <div
          v-for="c in filteredList"
          :key="c.id"
          @click="openDetail(c)"
          class="p-4 hover:bg-zinc-900/50 transition space-y-3 cursor-pointer"
        >
          <!-- Row 1: Status + Type + Name + ID + Actions -->
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-2 flex-wrap min-w-0">
              <span
                class="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded tabular-nums border"
                :class="isContainerRunning(c) ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25' : 'bg-red-500/10 text-red-400 border-red-500/25'"
              >
                {{ isContainerRunning(c) ? 'EM EXECUÇÃO' : 'PARADO' }}
              </span>
              <span class="text-xs bg-blue-500/10 text-blue-400 border border-blue-500/25 px-2 py-0.5 rounded font-semibold uppercase">
                {{ c.is_dokploy ? 'DOKPLOY' : (c.orchestrator || 'DOCKER') }}
              </span>
              <h4 class="font-bold text-sm text-white truncate">{{ c.name }}</h4>
              <span class="text-xs text-zinc-400 font-mono">ID: {{ String(c.id || '').slice(0, 12) }}</span>
              <span
                v-if="updatesMap[c.id]?.has_update"
                class="text-xs bg-amber-500/15 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded font-semibold"
              >
                ⬆ {{ updatesMap[c.id].pending_count }} atualização(ões)
              </span>
            </div>

            <div class="flex items-center gap-2 shrink-0" @click.stop>
              <button
                v-if="updatesMap[c.id]?.has_update"
                @click="$emit('update-container', c)"
                :disabled="updatingId === c.id"
                class="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-xs px-3 py-1.5 rounded text-white font-semibold transition cursor-pointer"
              >
                {{ updatingId === c.id ? 'Atualizando...' : 'Atualizar' }}
              </button>
              <button
                @click="$emit('restart-container', c)"
                class="bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-xs px-2.5 py-1.5 rounded text-zinc-200 font-medium transition cursor-pointer"
              >
                Reiniciar
              </button>
              <button
                @click="$emit('open-logs', c)"
                class="bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-xs px-2.5 py-1.5 rounded text-zinc-200 font-medium transition cursor-pointer"
              >
                Logs
              </button>
            </div>
          </div>

          <!-- Row 2: Left Uptime/Ports + 5-Column Live Metrics Grid (1:1 ProxMenux VMs & LXCs) -->
          <div class="flex flex-col lg:flex-row gap-4 items-start lg:items-center">
            <div class="lg:w-48 shrink-0 space-y-0.5 text-xs">
              <div class="text-zinc-400 truncate">{{ c.status || 'Parado' }}</div>
              <div class="text-zinc-300 font-mono truncate">{{ formatPorts(c.ports) }}</div>
            </div>
            <div class="flex-1 w-full grid grid-cols-2 sm:grid-cols-5 gap-3 tabular-nums text-xs">
              <div>
                <div class="text-zinc-400 mb-1">Uso da CPU</div>
                <div class="text-sm font-semibold text-white mb-1">{{ (c.stats?.cpu_percent ?? 0).toFixed(1) }}%</div>
                <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div class="h-full bg-blue-500 rounded-full" :style="{ width: `${Math.min(100, c.stats?.cpu_percent || 0)}%` }"></div>
                </div>
              </div>
              <div>
                <div class="text-zinc-400 mb-1">Memória</div>
                <div class="text-sm font-semibold text-white mb-1 truncate">{{ c.stats?.mem_usage || '0 B / 0 B' }}</div>
                <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div class="h-full bg-blue-500 rounded-full" :style="{ width: `${Math.min(100, c.stats?.mem_percent || 0)}%` }"></div>
                </div>
              </div>
              <div>
                <div class="text-zinc-400 mb-1">Imagem</div>
                <div class="text-sm font-semibold text-zinc-200 truncate" :title="c.image">{{ c.image }}</div>
              </div>
              <div>
                <div class="text-zinc-400 mb-1">E/S de disco</div>
                <div class="text-emerald-400 font-semibold">↓ {{ c.stats?.block_read || '0 B' }}</div>
                <div class="text-blue-400 font-semibold">↑ {{ c.stats?.block_write || '0 B' }}</div>
              </div>
              <div>
                <div class="text-zinc-400 mb-1">E/S de rede</div>
                <div class="text-emerald-400 font-semibold">↓ {{ c.stats?.net_rx || '0 B' }}</div>
                <div class="text-blue-400 font-semibold">↑ {{ c.stats?.net_tx || '0 B' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Container Detail Modal (1:1 with ProxMenux VM/LXC detail modal) -->
    <ContainerDetailModal
      :open="detailModalOpen"
      :container="selectedContainer"
      @close="detailModalOpen = false"
      @refresh="$emit('refresh')"
      @logs="(c) => { detailModalOpen = false; $emit('open-logs', c) }"
    />
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Boxes, Cpu, HardDrive, Database, Search, RefreshCw } from 'lucide-vue-next'
import ContainerDetailModal from './ContainerDetailModal.vue'

const props = defineProps({
  containers: { type: Array, default: () => [] },
  containerStats: { type: Object, default: () => ({ total: 0, running: 0, stopped: 0 }) },
  systemData: { type: Object, default: () => ({}) },
  diskUsedGb: { type: [Number, String], default: 0 },
  diskTotalGb: { type: [Number, String], default: 0 },
  diskPercent: { type: Number, default: 0 },
  updatesMap: { type: Object, default: () => ({}) },
  updatesCount: { type: Number, default: 0 },
  checkingUpdates: { type: Boolean, default: false },
  updatingId: { type: String, default: '' },
})

defineEmits(['check-updates', 'update-container', 'restart-container', 'open-logs', 'refresh'])

const searchQuery = ref('')
const statusFilter = ref('all')
const detailModalOpen = ref(false)
const selectedContainer = ref(null)

const cpuPct = computed(() => Number(props.systemData?.cpu_usage || 0))
const memPct = computed(() => Number(props.systemData?.memory_usage || 0))

function isContainerRunning(c) {
  return c?.state === 'running' || c?.status === 'running'
}

function formatPorts(ports) {
  if (!Array.isArray(ports) || !ports.length) return 'Host/Bridge'
  const formatted = ports.map((p) => {
    if (typeof p === 'string') return p
    if (p && typeof p === 'object') {
      const priv = p.PrivatePort || ''
      const pub = p.PublicPort || ''
      const typ = p.Type || 'tcp'
      return pub ? `${pub}:${priv}/${typ}` : `${priv}/${typ}`
    }
    return ''
  }).filter(Boolean)
  return formatted.length ? [...new Set(formatted)].join(', ') : 'Host/Bridge'
}

const filteredList = computed(() => {
  let list = props.containers || []
  if (statusFilter.value === 'running') {
    list = list.filter(isContainerRunning)
  } else if (statusFilter.value === 'stopped') {
    list = list.filter(c => !isContainerRunning(c))
  } else if (statusFilter.value === 'updates') {
    list = list.filter(c => props.updatesMap[c.id]?.has_update)
  }

  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(c =>
      (c.name || '').toLowerCase().includes(q) ||
      (c.id || '').toLowerCase().includes(q) ||
      (c.image || '').toLowerCase().includes(q)
    )
  }
  return list
})

function openDetail(c) {
  selectedContainer.value = c
  detailModalOpen.value = true
}
</script>
