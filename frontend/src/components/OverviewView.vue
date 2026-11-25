<template>
  <section class="space-y-6 animate-fadeIn">
    <!-- 4 Top Cards com Gauge Circular e Números Grandes -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 xl:gap-6">
      <!-- Card 1: Uso da CPU -->
      <div @click="$emit('open-cpu')" class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 hover:border-blue-500/40 transition shadow-sm cursor-pointer">
        <div class="flex items-center justify-between text-zinc-400 mb-3">
          <span class="text-xs font-semibold uppercase tracking-wider">Uso da CPU</span>
          <div class="flex items-center gap-1 text-zinc-400">
            <Cpu class="w-4 h-4" />
            <ChevronRight class="w-3.5 h-3.5" />
          </div>
        </div>
        <div class="flex items-center gap-4">
          <div class="relative w-[76px] h-[76px] shrink-0">
            <svg viewBox="0 0 36 36" class="w-full h-full -rotate-90">
              <circle cx="18" cy="18" r="15.9155" fill="none" stroke="#27272a" stroke-width="3.2"/>
              <circle cx="18" cy="18" r="15.9155" fill="none" stroke="#3b82f6" stroke-width="3.2"
                :stroke-dasharray="`${systemData.cpu_usage || 0} 100`" stroke-linecap="round"/>
            </svg>
            <div class="absolute inset-0 flex items-center justify-center font-black text-base text-white tabular-nums">
              {{ Math.round(systemData.cpu_usage || 0) }}%
            </div>
          </div>
          <div class="flex-1 space-y-2 min-w-0">
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-zinc-400">Usuário</span>
                <span class="tabular-nums font-medium text-white">{{ systemData.cpu_user || 0 }}%</span>
              </div>
              <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 rounded-full" :style="{ width: `${systemData.cpu_user || 0}%` }"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-zinc-400">Sistema</span>
                <span class="tabular-nums font-medium text-white">{{ systemData.cpu_system || 0 }}%</span>
              </div>
              <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div class="h-full bg-indigo-500/80 rounded-full" :style="{ width: `${systemData.cpu_system || 0}%` }"></div>
              </div>
            </div>
            <div class="flex justify-between text-xs pt-1 border-t border-zinc-800/60">
              <span class="text-zinc-400">Núcleos</span>
              <span class="tabular-nums font-medium text-zinc-300">{{ systemData.cpu_cores || 0 }}/{{ systemData.cpu_threads || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Card 2: Memória RAM -->
      <div @click="$emit('open-mem')" class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 hover:border-blue-500/40 transition shadow-sm cursor-pointer">
        <div class="flex items-center justify-between text-zinc-400 mb-3">
          <span class="text-xs font-semibold uppercase tracking-wider">Memória RAM</span>
          <div class="flex items-center gap-1 text-zinc-400">
            <HardDrive class="w-4 h-4" />
            <ChevronRight class="w-3.5 h-3.5" />
          </div>
        </div>
        <div class="flex items-center gap-4">
          <div class="relative w-[76px] h-[76px] shrink-0">
            <svg viewBox="0 0 36 36" class="w-full h-full -rotate-90">
              <circle cx="18" cy="18" r="15.9155" fill="none" stroke="#27272a" stroke-width="3.2"/>
              <circle cx="18" cy="18" r="15.9155" fill="none" stroke="#a855f7" stroke-width="3.2"
                :stroke-dasharray="`${systemData.memory_usage || 0} 100`" stroke-linecap="round"/>
            </svg>
            <div class="absolute inset-0 flex items-center justify-center font-black text-base text-white tabular-nums">
              {{ Math.round(systemData.memory_usage || 0) }}%
            </div>
          </div>
          <div class="flex-1 space-y-2 min-w-0">
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-zinc-400">Usado</span>
                <span class="tabular-nums font-medium text-white">{{ (systemData.memory_used || 0).toFixed(1) }} GB</span>
              </div>
              <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 rounded-full" :style="{ width: `${systemData.memory_usage || 0}%` }"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-zinc-400">Em cache</span>
                <span class="tabular-nums font-medium text-white">{{ (systemData.memory_cached || 0).toFixed(1) }} GB</span>
              </div>
              <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div class="h-full bg-indigo-500/80 rounded-full" :style="{ width: `${systemData.memory_total ? Math.min(100, ((systemData.memory_cached || 0) / systemData.memory_total) * 100) : 0}%` }"></div>
              </div>
            </div>
            <div class="flex justify-between text-xs pt-1 border-t border-zinc-800/60">
              <span class="text-zinc-400">Total</span>
              <span class="tabular-nums font-medium text-zinc-300">{{ (systemData.memory_total || 0).toFixed(1) }} GB</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Card 3: Containers Docker & Dokploy -->
      <div @click="$emit('go-containers')" class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 hover:border-blue-500/40 transition shadow-sm cursor-pointer">
        <div class="flex items-center justify-between text-zinc-400 mb-3">
          <span class="text-xs font-semibold uppercase tracking-wider">Containers Docker</span>
          <div class="flex items-center gap-1 text-zinc-400">
            <Boxes class="w-4 h-4" />
            <ChevronRight class="w-3.5 h-3.5" />
          </div>
        </div>
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-4xl font-black text-white tabular-nums tracking-tight">{{ containerStats.running }}</span>
          <span class="text-2xl font-bold text-zinc-400 tabular-nums">/ {{ containerStats.total }}</span>
          <span class="ml-auto text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">
            {{ containerStats.running }} em execução
          </span>
        </div>
        <div class="flex flex-wrap items-center gap-1.5 mt-2">
          <span class="text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded tabular-nums font-medium">Docker Engine</span>
          <span class="text-xs bg-blue-500/10 text-blue-400 border border-purple-500/20 px-2 py-0.5 rounded tabular-nums font-medium">Dokploy / Swarm</span>
        </div>
      </div>

      <!-- Card 4: Temperatura do Host -->
      <div @click="$emit('open-temp')" class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 hover:border-blue-500/40 transition shadow-sm cursor-pointer">
        <div class="flex items-center justify-between text-zinc-400 mb-3">
          <span class="text-xs font-semibold uppercase tracking-wider">Temperatura do Host</span>
          <div class="flex items-center gap-1">
            <Thermometer class="w-4 h-4 text-zinc-400" />
            <ChevronRight class="w-3.5 h-3.5 text-zinc-400" />
          </div>
        </div>
        <div class="flex items-baseline justify-between mb-2">
          <div class="text-3xl lg:text-4xl font-black text-white tabular-nums tracking-tight">
            {{ systemData.temperature && systemData.temperature > 0 ? `${Math.round(systemData.temperature)}°C` : 'N/D' }}
          </div>
          <span class="text-xs px-2.5 py-0.5 rounded-full font-medium"
            :class="systemData.is_virtual ? 'bg-zinc-800 text-zinc-400 border border-zinc-700' : ((systemData.temperature || 0) >= 85 ? 'bg-red-500/15 text-red-400 border border-red-500/25' : ((systemData.temperature || 0) >= 75 ? 'bg-amber-500/15 text-amber-400 border border-amber-500/25' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'))">
            {{ systemData.is_virtual ? 'VPS (KVM)' : ((systemData.temperature || 0) >= 85 ? 'Crítico' : ((systemData.temperature || 0) >= 75 ? 'Esquentar' : 'Normal')) }}
          </span>
        </div>
        <div class="text-xs text-zinc-400 space-y-1 mt-2">
          <div class="flex justify-between">
            <span>Sensor:</span>
            <span class="tabular-nums text-zinc-300">{{ systemData.is_virtual ? 'Virtualizado (Sem hwmon)' : 'coretemp real' }}</span>
          </div>
          <div class="flex justify-between">
            <span>Ambiente:</span>
            <span class="tabular-nums text-zinc-300">{{ systemData.is_virtual ? 'Nuvem / VPS' : 'Bare Metal' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 2 Large Charts side-by-side -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-base font-bold text-white tracking-tight">Histórico de Desempenho</h2>
        <select
          :value="timeframe"
          @change="$emit('update:timeframe', $event.target.value)"
          class="bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 rounded-lg px-2.5 py-1.5 font-medium cursor-pointer"
        >
          <option value="hour">1 hora</option>
          <option value="day">24 horas</option>
          <option value="week">7 dias</option>
          <option value="month">30 dias</option>
        </select>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
        <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
          <div class="flex items-start justify-between mb-3 gap-2">
            <div class="flex items-center gap-2">
              <Activity class="w-4 h-4 text-zinc-400" />
              <h3 class="text-base font-bold text-white">Média de uso e carga da CPU</h3>
            </div>
            <div class="flex flex-wrap items-center justify-end gap-x-3 gap-y-0.5 text-xs tabular-nums text-zinc-300">
              <span><strong class="text-white">{{ cpuStats.avg }}%</strong> <span class="text-zinc-400">AVG</span></span>
              <span><strong class="text-white">{{ cpuStats.max }}%</strong> <span class="text-zinc-400">MAX</span></span>
              <span><strong class="text-white">{{ cpuStats.min }}%</strong> <span class="text-zinc-400">MIN</span></span>
            </div>
          </div>
          <div class="flex items-center justify-center gap-4 text-xs text-zinc-300 mb-3">
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> CPU %</span>
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Média de carga</span>
          </div>
          <div class="h-64 w-full relative">
            <div v-if="metricsLoading" class="absolute inset-0 z-10 flex items-center justify-center bg-[#18181b]/80 rounded-lg">
              <div class="w-7 h-7 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <canvas ref="cpuChartCanvas" class="w-full h-full"></canvas>
          </div>
        </div>

        <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
          <div class="flex items-start justify-between mb-3 gap-2">
            <div class="flex items-center gap-2">
              <HardDrive class="w-4 h-4 text-zinc-400" />
              <h3 class="text-base font-bold text-white">Uso de memória</h3>
            </div>
            <div class="flex flex-wrap items-center justify-end gap-x-3 gap-y-0.5 text-xs tabular-nums text-zinc-300">
              <span><strong class="text-white">{{ memStats.avg }} GB</strong> <span class="text-zinc-400">AVG</span></span>
              <span><strong class="text-white">{{ memStats.max }} GB</strong> <span class="text-zinc-400">MAX</span></span>
              <span><strong class="text-white">{{ memStats.min }} GB</strong> <span class="text-zinc-400">MIN</span></span>
            </div>
          </div>
          <div class="flex items-center justify-center gap-4 text-xs text-zinc-300 mb-3">
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Total</span>
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Usado</span>
          </div>
          <div class="h-64 w-full relative">
            <div v-if="metricsLoading" class="absolute inset-0 z-10 flex items-center justify-center bg-[#18181b]/80 rounded-lg">
              <div class="w-7 h-7 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <canvas ref="memChartCanvas" class="w-full h-full"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 2 Wide Summary Cards: Armazenamento e Rede -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
        <div class="flex items-center gap-2 mb-4">
          <HardDrive class="w-4 h-4 text-zinc-400" />
          <h3 class="text-base font-bold text-white">Visão geral do armazenamento</h3>
        </div>
        <div class="flex items-baseline justify-between mb-2">
          <span class="text-xs text-zinc-400">Capacidade total do nó:</span>
          <span class="text-sm font-bold text-white tabular-nums">{{ totalStorageFormatted }}</span>
        </div>
        <div class="h-2 bg-zinc-800 rounded-full overflow-hidden mb-2">
          <div class="h-full bg-blue-500 rounded-full transition-all duration-500" :style="{ width: `${totalStoragePercent}%` }"></div>
        </div>
        <div class="flex items-center justify-between text-xs tabular-nums mb-4">
          <div class="flex items-center gap-3">
            <span class="text-zinc-400">Usado: <strong class="text-white">{{ totalUsedStorageFormatted }}</strong></span>
            <span class="text-zinc-400">Livre: <strong class="text-emerald-400">{{ freeStorageFormatted }}</strong></span>
          </div>
          <span class="text-zinc-400 font-semibold">{{ totalStoragePercent }}%</span>
        </div>

        <div class="space-y-2 text-xs border-t border-zinc-800/80 pt-3 mb-4">
          <div class="flex items-center justify-between">
            <span class="text-zinc-400">Capacidade total:</span>
            <span class="font-semibold text-white tabular-nums">{{ totalStorageTB }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-zinc-400">Discos físicos:</span>
            <span class="font-semibold text-white tabular-nums">{{ physicalDisks.length || 0 }} disco(s)</span>
          </div>
        </div>

        <div class="space-y-3 border-t border-zinc-800/80 pt-3">
          <div v-for="m in uniqueMounts" :key="m.mountpoint" class="space-y-1.5 text-xs">
            <div class="flex items-center justify-between">
              <span class="text-zinc-300 font-medium">{{ m.mountpoint === '/' ? 'Armazenamento local (sistema)' : `Partição ${m.mountpoint}` }} <span class="text-zinc-400">({{ m.fstype }})</span></span>
              <span class="font-semibold text-white tabular-nums">{{ m.used_formatted }}</span>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-zinc-400">Disponível:</span>
              <span class="text-emerald-400 font-semibold tabular-nums">{{ m.available_formatted }}</span>
            </div>
            <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
              <div class="h-full bg-blue-500 rounded-full transition-all duration-500" :style="{ width: `${m.percent}%` }"></div>
            </div>
            <div class="flex items-center justify-between text-xs text-zinc-400 tabular-nums">
              <span>{{ m.used_formatted }} / {{ m.total_formatted }}</span>
              <span>{{ m.percent }}%</span>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <Network class="w-4 h-4 text-zinc-400" />
              <h3 class="text-base font-bold text-white">Visão geral da rede</h3>
            </div>
            <select
              :value="netTimeframe"
              @change="$emit('update:netTimeframe', $event.target.value)"
              class="bg-zinc-900 border border-zinc-800 text-xs text-zinc-200 rounded-lg px-2.5 py-1 font-medium cursor-pointer"
            >
              <option value="hour">1 hora</option>
              <option value="day">24 horas</option>
              <option value="week">7 dias</option>
              <option value="month">30 dias</option>
              <option value="year">1 ano</option>
            </select>
          </div>

          <div class="flex items-center justify-between text-xs mb-2">
            <span class="text-zinc-400">Interfaces ativas:</span>
            <span class="font-bold text-white tabular-nums">{{ (networkData.interfaces || []).filter(i => i.status === 'UP' || i.status === 'up').length }}</span>
          </div>
          <div class="flex flex-wrap gap-1.5 mb-3">
            <span v-for="iface in (networkData.interfaces || []).filter(i => i.status === 'UP' || i.status === 'up').slice(0, 6)" :key="iface.name"
              class="text-xs font-medium px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/25">
              {{ iface.name }}
            </span>
          </div>

          <div class="space-y-1 text-xs mb-3 tabular-nums">
            <div class="flex items-center justify-between">
              <span class="text-zinc-400">Recebido:</span>
              <span class="font-bold text-emerald-400">↓ {{ netPeriodStats.rx_display || `${netPeriodStats.rx_gb} GB` }} ({{ netPeriodLabel }})</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-zinc-400">Enviado:</span>
              <span class="font-bold text-blue-400">↑ {{ netPeriodStats.tx_display || `${netPeriodStats.tx_gb} GB` }} ({{ netPeriodLabel }})</span>
            </div>
          </div>

          <div class="flex items-center justify-center gap-4 text-xs text-zinc-300 mb-2">
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Recebido</span>
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Enviado</span>
          </div>
        </div>

        <div class="h-44 w-full relative">
          <div v-if="netMetricsLoading" class="absolute inset-0 z-10 flex items-center justify-center bg-[#18181b]/80 rounded-lg">
            <div class="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <canvas ref="overviewNetChartCanvas" class="w-full h-full"></canvas>
        </div>
      </div>
    </div>

    <!-- 2 Bottom Summary Cards -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
        <div class="flex items-center gap-2 mb-4">
          <Server class="w-4 h-4 text-zinc-400" />
          <h3 class="text-base font-bold text-white">Informações do sistema</h3>
        </div>
        <div class="space-y-2.5 text-xs">
          <div class="flex items-center justify-between py-1 border-b border-zinc-800/60">
            <span class="text-zinc-400">Tempo de atividade:</span>
            <span class="font-semibold text-zinc-200 tabular-nums">{{ systemData.uptime }}</span>
          </div>
          <div class="flex items-center justify-between py-1 border-b border-zinc-800/60">
            <span class="text-zinc-400">Sistema:</span>
            <span class="font-semibold text-zinc-200">{{ systemData.distro_name || 'Linux' }}</span>
          </div>
          <div class="flex items-center justify-between py-1 border-b border-zinc-800/60">
            <span class="text-zinc-400">Núcleo:</span>
            <span class="font-semibold text-zinc-200 tabular-nums">{{ systemData.kernel_version || '-' }}</span>
          </div>
          <div class="flex items-center justify-between py-1">
            <span class="text-zinc-400">Atualizações disponíveis:</span>
            <button v-if="(systemData.available_updates || 0) > 0"
              @click="$emit('open-health', 'updates')"
              class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30 hover:bg-amber-500/25 transition cursor-pointer">
              {{ systemData.available_updates }} pacotes
            </button>
            <span v-else class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Atualizado
            </span>
          </div>
        </div>
      </div>

      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
        <div class="flex items-center gap-2 mb-4">
          <Activity class="w-4 h-4 text-zinc-400" />
          <h3 class="text-base font-bold text-white">Visão geral do sistema</h3>
        </div>
        <div class="space-y-2.5 text-xs">
          <div class="flex items-center justify-between py-1 border-b border-zinc-800/60">
            <span class="text-zinc-400">Carga Média (1m):</span>
            <div class="flex items-center gap-2">
              <span class="font-bold text-zinc-200 tabular-nums">{{ systemData.load_average?.[0] ?? 0 }}</span>
              <span class="px-2 py-0.5 rounded text-xs font-semibold"
                :class="(systemData.load_average?.[0] ?? 0) > (systemData.cpu_threads || 4) ? 'bg-amber-500/15 text-amber-400' : 'bg-emerald-500/15 text-emerald-400'">
                {{ (systemData.load_average?.[0] ?? 0) > (systemData.cpu_threads || 4) ? 'Elevada' : 'Normal' }}
              </span>
            </div>
          </div>
          <div class="flex items-center justify-between py-1 border-b border-zinc-800/60">
            <span class="text-zinc-400">Threads da CPU:</span>
            <span class="font-semibold text-zinc-200 tabular-nums">{{ systemData.cpu_threads || systemData.cpu_cores || 0 }}</span>
          </div>
          <div class="flex items-center justify-between py-1 border-b border-zinc-800/60">
            <span class="text-zinc-400">Discos físicos:</span>
            <span class="font-semibold text-zinc-200 tabular-nums">{{ physicalDisks.length || 0 }}</span>
          </div>
          <div class="flex items-center justify-between py-1">
            <span class="text-zinc-400">Interfaces de rede:</span>
            <span class="font-semibold text-zinc-200 tabular-nums">{{ networkData.interfaces?.length || 0 }}</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { Cpu, ChevronRight, HardDrive, Boxes, Thermometer, Activity, Network, Server } from 'lucide-vue-next'

defineProps({
  systemData: { type: Object, required: true },
  containerStats: { type: Object, required: true },
  networkData: { type: Object, required: true },
  physicalDisks: { type: Array, default: () => [] },
  uniqueMounts: { type: Array, default: () => [] },
  totalStorageFormatted: { type: String, default: '0 GB' },
  totalUsedStorageFormatted: { type: String, default: '0 GB' },
  totalStorageTB: { type: String, default: '0.0 TB' },
  freeStorageFormatted: { type: String, default: '0 GB' },
  totalStoragePercent: { type: Number, default: 0 },
  timeframe: { type: String, default: 'day' },
  netTimeframe: { type: String, default: 'day' },
  cpuStats: { type: Object, default: () => ({ avg: 0, max: 0, min: 0 }) },
  memStats: { type: Object, default: () => ({ avg: 0, max: 0, min: 0 }) },
  netPeriodStats: { type: Object, default: () => ({ rx_gb: 0, tx_gb: 0 }) },
  netPeriodLabel: { type: String, default: '24h' },
  metricsLoading: { type: Boolean, default: false },
  netMetricsLoading: { type: Boolean, default: false },
})

defineEmits(['open-cpu', 'open-mem', 'open-temp', 'go-containers', 'open-health', 'update:timeframe', 'update:netTimeframe'])

const cpuChartCanvas = ref(null)
const memChartCanvas = ref(null)
const overviewNetChartCanvas = ref(null)

defineExpose({ cpuChartCanvas, memChartCanvas, overviewNetChartCanvas })
</script>
