<template>
  <section class="space-y-6 animate-fadeIn">
    <!-- Sub-Tabs Navigation for Network -->
    <div class="flex items-center gap-2 border-b border-zinc-800/80 pb-3">
      <button
        @click="$emit('update:activeTab', 'network-overview')"
        class="px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer"
        :class="activeTab === 'network-overview' || activeTab === 'network' ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'"
      >
        Visão Geral de Rede
      </button>
      <button
        @click="$emit('update:activeTab', 'network-flow')"
        class="px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1.5"
        :class="activeTab === 'network-flow' ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'"
      >
        <Share2 class="w-3.5 h-3.5 text-emerald-400" />
        <span>Fluxo de Redes (Topologia SVG)</span>
      </button>
      <button
        @click="$emit('update:activeTab', 'network-interfaces')"
        class="px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer"
        :class="activeTab === 'network-interfaces' ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'"
      >
        Interfaces Físicas &amp; Pontes
      </button>
    </div>

    <!-- Sub-tab 1: Network Overview -->
    <div v-if="activeTab === 'network-overview' || activeTab === 'network'" class="space-y-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 xl:gap-6">
        <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
          <div class="flex items-center justify-between text-zinc-400 mb-2">
            <div>
              <h3 class="text-sm font-medium text-zinc-400">Tráfego de rede</h3>
              <span class="text-xs text-zinc-400">Passadas 24 horas</span>
            </div>
            <Activity class="w-4 h-4 text-zinc-400" />
          </div>
          <div class="grid grid-cols-2 gap-3 mb-3">
            <div>
              <div class="text-xs font-medium text-zinc-400 mb-1"><span class="text-emerald-500 font-bold">↓</span> Abaixo</div>
              <div class="text-2xl lg:text-3xl font-black text-emerald-400 tabular-nums tracking-tight leading-none">
                {{ networkData.total_rx_formatted || '0 B' }}
              </div>
            </div>
            <div>
              <div class="text-xs font-medium text-zinc-400 mb-1"><span class="text-blue-500 font-bold">↑</span> Acima</div>
              <div class="text-2xl lg:text-3xl font-black text-blue-400 tabular-nums tracking-tight leading-none">
                {{ networkData.total_tx_formatted || '0 B' }}
              </div>
            </div>
          </div>
          <div class="flex h-1.5 rounded-full overflow-hidden gap-[2px]">
            <div class="bg-emerald-500 h-full" style="width: 50%"></div>
            <div class="bg-blue-500 h-full" style="width: 50%"></div>
          </div>
        </div>

        <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
          <div class="flex items-center justify-between text-zinc-400 mb-2">
            <h3 class="text-sm font-medium text-zinc-400">Interfaces ativas</h3>
            <Network class="w-4 h-4 text-zinc-400" />
          </div>
          <div class="text-3xl lg:text-4xl font-black text-white tabular-nums tracking-tight mb-2">
            {{ (networkData.physical_active_count || 0) + (networkData.bridge_active_count || 0) }}
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs tabular-nums font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded">
              Físico: {{ networkData.physical_active_count || 0 }}/{{ networkData.physical_total_count || 0 }}
            </span>
            <span class="text-xs tabular-nums font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
              Pontes: {{ networkData.bridge_active_count || 0 }}/{{ networkData.bridge_total_count || 0 }}
            </span>
          </div>
          <p class="text-xs text-zinc-400 tabular-nums mt-3">{{ networkData.total_interfaces || 0 }} interfaces totais</p>
        </div>

        <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
          <div class="flex items-center justify-between text-zinc-400 mb-2">
            <h3 class="text-sm font-medium text-zinc-400">Status da rede</h3>
            <span class="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">✓ Saudável</span>
          </div>
          <div class="text-2xl lg:text-3xl font-black text-emerald-400 tabular-nums tracking-tight leading-none mb-3">
            {{ (networkData.traffic?.packet_loss_in ?? 0).toFixed(2) }}% <span class="text-xs font-normal text-zinc-400">Perda de pacotes</span>
          </div>
          <div class="grid grid-cols-2 gap-2 pt-2 border-t border-zinc-800/60 text-xs tabular-nums">
            <div><div class="text-zinc-400">Host:</div><div class="text-zinc-200 truncate">{{ systemData.hostname || '-' }}</div></div>
            <div><div class="text-zinc-400">DNS:</div><div class="text-zinc-200 truncate">{{ (networkData.dns_servers && networkData.dns_servers[0]) || '-' }}</div></div>
          </div>
        </div>

        <div @click="openLatencyModal" class="bg-[#18181b] border border-zinc-800 hover:border-blue-500/40 rounded-xl p-5 shadow-sm cursor-pointer transition">
          <div class="flex items-center justify-between text-zinc-400 mb-2">
            <h3 class="text-sm font-medium text-zinc-400">Latência de rede</h3>
            <span class="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">
              {{ latencyData.current_ms > 0 ? (latencyData.current_ms < 20 ? 'Excelente' : 'Normal') : 'Medindo...' }}
            </span>
          </div>
          <div class="text-3xl lg:text-4xl font-black text-white tabular-nums tracking-tight mb-2">
            {{ latencyData.current_ms > 0 ? latencyData.current_ms.toFixed(1) : '—' }} <span class="text-sm font-normal text-zinc-400">ms</span>
          </div>
          <div class="h-8 w-full flex items-end gap-1 mb-2">
            <div v-for="(val, idx) in (latencyData.samples?.length ? latencyData.samples : [0,0,0,0,0,0,0,0])" :key="idx"
              class="flex-1 bg-blue-500/80 rounded-t"
              :style="{ height: `${Math.max(10, Math.min(100, (val / Math.max(1, latencyData.max_ms || 10)) * 100))}%` }"></div>
          </div>
          <div class="text-xs text-zinc-400 tabular-nums">Média: {{ latencyData.avg_ms || 0 }}ms | Máx.: {{ latencyData.max_ms || 0 }}ms</div>
        </div>
      </div>

      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <Activity class="w-4 h-4 text-emerald-500" />
            <h3 class="text-base font-bold text-white">Tráfego de rede (Entrada e Saída)</h3>
          </div>
          <div class="flex items-center gap-4 text-xs tabular-nums">
            <span class="flex items-center gap-1.5 text-emerald-400"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Recebido</span>
            <span class="flex items-center gap-1.5 text-blue-400"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Enviado</span>
          </div>
        </div>
        <div class="h-64 w-full relative">
          <canvas ref="netChartCanvas" class="w-full h-full"></canvas>
        </div>
      </div>
    </div>

    <!-- Sub-tab 2: Network Flow SVG + AIOps -->
    <div v-if="activeTab === 'network-flow'" class="space-y-4">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-[var(--card)] border border-zinc-700/60 p-4 rounded-xl">
        <div>
          <div class="flex items-center gap-2">
            <Share2 class="w-5 h-5 text-emerald-400" />
            <h3 class="text-base font-bold text-white">Fluxo de Redes Dinâmico (Topologia SVG)</h3>
            <span class="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-400">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Tempo Real
            </span>
          </div>
          <p class="text-xs text-zinc-400 mt-0.5">Topologia em tempo real entre Placas Físicas, Host Linux, Bridges e Containers.</p>
        </div>

        <div class="flex flex-wrap items-center gap-2.5">
          <div class="relative">
            <Search class="w-3.5 h-3.5 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              v-model="flowSearch"
              type="text"
              placeholder="Filtrar contêiner / nó..."
              class="bg-white/[0.04] border border-zinc-700/70 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-zinc-500 w-44 focus:outline-none focus:border-emerald-500/60"
            />
          </div>
          <button
            @click="flowOnlyActive = !flowOnlyActive"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium cursor-pointer transition"
            :class="flowOnlyActive
              ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300'
              : 'bg-white/[0.03] border-zinc-700/70 text-zinc-300 hover:bg-white/[0.06]'"
          >
            <Filter class="w-3.5 h-3.5" />
            <span>Ativos ({{ activeFlowConsumersCount }})</span>
          </button>
          <div class="hidden xl:flex items-center gap-3 text-xs border-l border-zinc-700/70 pl-3">
            <span class="flex items-center gap-1.5 text-zinc-400"><span class="w-3 h-1.5 rounded-full bg-emerald-400"></span> Download</span>
            <span class="flex items-center gap-1.5 text-zinc-400"><span class="w-3 h-1.5 rounded-full bg-cyan-400"></span> Upload</span>
          </div>
          <button
            @click="$emit('run-ai')"
            :disabled="aiLoading"
            class="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 transition cursor-pointer shrink-0"
          >
            <Sparkles class="w-4 h-4 text-amber-300" :class="{ 'animate-spin': aiLoading }" />
            <span>{{ aiLoading ? 'Analisando Tráfego com IA...' : 'Analisar Fluxo de Rede com IA' }}</span>
          </button>
        </div>
      </div>

      <div class="bg-[#151518] border border-zinc-800/80 rounded-xl p-6 overflow-x-auto min-h-[460px] flex items-center justify-center relative">
        <svg viewBox="0 0 1000 420" class="w-full max-w-5xl h-auto select-none">
          <defs>
            <filter id="glow-orange" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="5" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>
          <path d="M 120 120 C 220 120, 220 210, 300 210" :class="primaryNicUp ? 'nf-beam-base-rx' : 'stroke-zinc-800 fill-none'" stroke-width="3" />
          <path v-if="primaryNicUp" d="M 120 120 C 220 120, 220 210, 300 210" class="nf-beam-rx" stroke-width="3" />
          <path v-if="secondaryNic" d="M 120 210 L 300 210" :class="secondaryNicUp ? 'nf-beam-base-tx' : 'stroke-zinc-800/70 fill-none'" stroke-width="2.5" stroke-dasharray="4 4" />
          <path v-if="secondaryNic && secondaryNicUp" d="M 120 210 L 300 210" class="nf-beam-tx" stroke-width="3" />
          <path d="M 300 210 C 380 210, 380 140, 480 140" class="nf-beam-base-rx" stroke-width="3" />
          <path d="M 300 210 C 380 210, 380 140, 480 140" class="nf-beam-rx" stroke-width="3" />
          <path d="M 300 210 C 380 210, 380 280, 480 280" class="nf-beam-base-tx" stroke-width="3" />
          <path d="M 300 210 C 380 210, 380 280, 480 280" class="nf-beam-tx" stroke-width="3" />
          <path d="M 480 140 C 580 140, 580 90, 720 90" class="nf-beam-base-rx" stroke-width="3" />
          <path d="M 480 140 C 580 140, 580 90, 720 90" class="nf-beam-rx" stroke-width="3" />
          <path d="M 480 140 C 580 140, 580 200, 720 200" class="nf-beam-base-tx" stroke-width="3" />
          <path d="M 480 140 C 580 140, 580 200, 720 200" class="nf-beam-tx" stroke-width="3" />
          <path d="M 480 280 C 580 280, 580 320, 720 320" class="nf-beam-base-rx" stroke-width="3" />
          <path d="M 480 280 C 580 280, 580 320, 720 320" class="nf-beam-rx" stroke-width="3" />

          <g transform="translate(120, 120)">
            <circle r="22" fill="#18181b" :stroke="primaryNicUp ? '#f59e0b' : '#52525b'" stroke-width="2.5" />
            <!-- Wi-Fi / NIC icon -->
            <path d="M-8 -2a11 11 0 0 1 16 0M-5 2a7 7 0 0 1 10 0" fill="none" :stroke="primaryNicUp ? '#f59e0b' : '#71717a'" stroke-width="1.8" stroke-linecap="round" />
            <circle cx="0" cy="6" r="1.8" :fill="primaryNicUp ? '#f59e0b' : '#71717a'" />
            <text y="36" text-anchor="middle" font-size="12" font-weight="bold" fill="#f4f4f5" font-family="monospace">{{ primaryNic?.name || networkData.default_interface || 'wlp3s0' }}</text>
            <text y="50" text-anchor="middle" font-size="10" :fill="primaryNicUp ? '#10b981' : '#71717a'" font-family="monospace">{{ primaryNicUp ? (primaryNic?.speed || 'Ativa') : 'Desativada' }}</text>
          </g>
          <g v-if="secondaryNic" transform="translate(120, 210)">
            <circle r="22" fill="#18181b" :stroke="secondaryNicUp ? '#f59e0b' : '#52525b'" stroke-width="2.5" :opacity="secondaryNicUp ? 1 : 0.5" />
            <!-- Ethernet port icon -->
            <rect x="-8" y="-7" width="16" height="14" rx="2" fill="none" :stroke="secondaryNicUp ? '#f59e0b' : '#71717a'" stroke-width="1.7" />
            <path d="M-4 -7v4M0 -7v4M4 -7v4" :stroke="secondaryNicUp ? '#f59e0b' : '#71717a'" stroke-width="1.5" stroke-linecap="round" />
            <text y="36" text-anchor="middle" font-size="12" font-weight="bold" :fill="secondaryNicUp ? '#f4f4f5' : '#71717a'" font-family="monospace">{{ secondaryNic.name }}</text>
            <text y="50" text-anchor="middle" font-size="10" :fill="secondaryNicUp ? '#10b981' : '#71717a'" font-family="monospace">{{ secondaryNicUp ? (secondaryNic.speed || 'Ativa') : 'Desativada' }}</text>
          </g>
          <g transform="translate(300, 210)">
            <circle r="34" fill="#18181b" stroke="#ea580c" stroke-width="3" filter="url(#glow-orange)" />
            <!-- Distro Logo inside Central Host Node -->
            <image v-if="distroKey === 'biglinux'" :href="distroLogoUrl" x="-20" y="-20" width="40" height="40" preserveAspectRatio="xMidYMid meet" />
            <g v-else-if="distroKey === 'manjaro'">
              <path d="M-11 -11h12v6h-6v16h-6V-11zm14 0h8v22h-8V-11zm-7 8h5v14h-5V-3z" fill="#10b981" />
            </g>
            <g v-else-if="distroKey === 'arch'">
              <path d="M0 -14c-1.8 4.2-2.8 7-4.8 11 1.2 1 2.6 2.2 5 3.8-2.5-1-4.3-2-5.6-3.1-2.3 4.8-5.8 10.6-9.8 18 5.2-3 9.2-4.8 13-5.5-.1-.7-.2-1.5-.2-2.3 0-2.9 1.5-5.3 3.4-5.3s3.4 2.4 3.4 5.3c0 .8-.1 1.6-.2 2.3 3.8.7 7.8 2.5 13 5.5-1.2-2.2-2.2-4.1-3.2-6-1.5-1.2-3.1-2.7-6.4-4.5 2.2.6 3.8 1.3 5.1 2.1C7.5 -2.6 6.7 -5.2 0 -14z" fill="#38bdf8" />
            </g>
            <g v-else-if="distroKey === 'ubuntu'">
              <circle r="8" fill="none" stroke="#f97316" stroke-width="2.6" />
              <circle cx="0" cy="-12" r="2.5" fill="#f97316" />
              <circle cx="-10.5" cy="6" r="2.5" fill="#f97316" />
              <circle cx="10.5" cy="6" r="2.5" fill="#f97316" />
            </g>
            <g v-else-if="distroKey === 'debian'">
              <path d="M3 8c-4 1-8-2-8-6 0-5 4-9 9-9 4 0 7 3 7 7 0 6-5 11-11 11-6 0-10-4-10-10 0-7 6-12 13-12" fill="none" stroke="#f43f5e" stroke-width="2.4" stroke-linecap="round" />
            </g>
            <g v-else>
              <rect x="-10" y="-10" width="20" height="20" rx="3" fill="none" stroke="#ea580c" stroke-width="2" />
              <path d="M-5 -3h10M-5 3h10" stroke="#ea580c" stroke-width="1.8" stroke-linecap="round" />
            </g>
            <text y="50" text-anchor="middle" font-size="12" font-weight="bold" fill="#ffffff" font-family="monospace">{{ (systemData.distro_name || 'LINUX HOST').toUpperCase() }}</text>
            <text y="64" text-anchor="middle" font-size="10" fill="#ea580c" font-family="monospace">{{ flowData.host_rate || '0 B/s' }}</text>
          </g>
          <g transform="translate(480, 140)">
            <circle r="20" fill="#18181b" stroke="#06b6d4" stroke-width="2" filter="url(#glow-cyan)" />
            <!-- Bridge switch icon -->
            <circle cx="-6" cy="0" r="2.5" fill="#06b6d4" />
            <circle cx="6" cy="0" r="2.5" fill="#06b6d4" />
            <path d="M-3.5 0h7" stroke="#06b6d4" stroke-width="1.8" />
            <text y="34" text-anchor="middle" font-size="11" font-weight="bold" fill="#f4f4f5" font-family="monospace">{{ (flowData.bridges && flowData.bridges[0] && flowData.bridges[0].id) || 'docker0' }}</text>
            <text y="46" text-anchor="middle" font-size="10" fill="#06b6d4" font-family="monospace">{{ (flowData.bridges && flowData.bridges[0] && flowData.bridges[0].rate_formatted) || '0 B/s' }}</text>
          </g>
          <g transform="translate(480, 280)">
            <circle r="20" fill="#18181b" stroke="#06b6d4" stroke-width="2" filter="url(#glow-cyan)" />
            <circle cx="-6" cy="0" r="2.5" fill="#06b6d4" />
            <circle cx="6" cy="0" r="2.5" fill="#06b6d4" />
            <path d="M-3.5 0h7" stroke="#06b6d4" stroke-width="1.8" />
            <text y="34" text-anchor="middle" font-size="11" font-weight="bold" fill="#f4f4f5" font-family="monospace">{{ (flowData.bridges && flowData.bridges[1] && flowData.bridges[1].id) || 'br-dokploy' }}</text>
            <text y="46" text-anchor="middle" font-size="10" fill="#06b6d4" font-family="monospace">{{ (flowData.bridges && flowData.bridges[1] && flowData.bridges[1].rate_formatted) || '0 B/s' }}</text>
          </g>
          <g transform="translate(720, 90)">
            <circle r="20" fill="#18181b" stroke="#a855f7" stroke-width="2" />
            <!-- Container cube icon -->
            <path d="M0 -8l8 4.5v9L0 10l-8-4.5v-9zM0 -8v9m0 0l8-4.5M0 1l-8-4.5" fill="none" stroke="#a855f7" stroke-width="1.5" stroke-linejoin="round" />
            <text y="34" text-anchor="middle" font-size="11" font-weight="bold" fill="#f4f4f5" font-family="monospace">{{ (flowConsumers[0] && flowConsumers[0].label) || 'dokploy' }}</text>
            <text y="46" text-anchor="middle" font-size="10" fill="#a855f7" font-family="monospace">{{ (flowConsumers[0] && flowConsumers[0].rate_formatted) || '0 B/s' }}</text>
          </g>
          <g transform="translate(720, 200)">
            <circle r="20" fill="#18181b" stroke="#06b6d4" stroke-width="2" />
            <path d="M0 -8l8 4.5v9L0 10l-8-4.5v-9zM0 -8v9m0 0l8-4.5M0 1l-8-4.5" fill="none" stroke="#06b6d4" stroke-width="1.5" stroke-linejoin="round" />
            <text y="34" text-anchor="middle" font-size="11" font-weight="bold" fill="#f4f4f5" font-family="monospace">{{ (flowConsumers[1] && flowConsumers[1].label) || 'traefik' }}</text>
            <text y="46" text-anchor="middle" font-size="10" fill="#06b6d4" font-family="monospace">{{ (flowConsumers[1] && flowConsumers[1].rate_formatted) || '0 B/s' }}</text>
          </g>
          <g transform="translate(720, 320)">
            <circle r="20" fill="#18181b" stroke="#a855f7" stroke-width="2" />
            <path d="M0 -8l8 4.5v9L0 10l-8-4.5v-9zM0 -8v9m0 0l8-4.5M0 1l-8-4.5" fill="none" stroke="#a855f7" stroke-width="1.5" stroke-linejoin="round" />
            <text y="34" text-anchor="middle" font-size="11" font-weight="bold" fill="#f4f4f5" font-family="monospace">{{ (flowConsumers[2] && flowConsumers[2].label) || 'custom-builder0' }}</text>
            <text y="46" text-anchor="middle" font-size="10" fill="#a855f7" font-family="monospace">{{ (flowConsumers[2] && flowConsumers[2].rate_formatted) || '0 B/s' }}</text>
          </g>
        </svg>
      </div>

      <!-- Lista de Containers & Consumidores Mapeados (1:1 MonitorSystem NetworkFlow) -->
      <div class="bg-[var(--card)] border border-zinc-700/60 rounded-xl p-4 space-y-3">
        <div class="flex items-center justify-between text-xs">
          <span class="font-semibold text-white">Consumidores &amp; Containers Mapeados ({{ filteredFlowConsumers.length }})</span>
          <span class="text-zinc-400">Host total: <strong class="text-orange-400 font-mono">{{ flowData.host_rate || '0 B/s' }}</strong></span>
        </div>
        <div v-if="!filteredFlowConsumers.length" class="border border-dashed border-zinc-700/70 rounded-lg py-6 text-center text-xs text-zinc-400 bg-white/[0.015]">
          Nenhum consumidor/container com o filtro atual.
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 text-xs">
          <div
            v-for="c in filteredFlowConsumers"
            :key="c.id || c.label"
            class="flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-lg bg-white/[0.025] border border-zinc-700/60"
          >
            <div class="flex items-center gap-2.5 min-w-0">
              <span class="w-2 h-2 rounded-full shrink-0" :class="(c.rate_bytes || 0) > 0 || c.active ? 'bg-emerald-400' : 'bg-zinc-500'"></span>
              <div class="min-w-0">
                <div class="font-mono font-semibold text-white truncate">{{ c.label || c.name }}</div>
                <div class="text-[11px] text-zinc-400 truncate">{{ c.bridge || 'docker0' }}</div>
              </div>
            </div>
            <span class="font-mono text-cyan-400 font-semibold shrink-0">{{ c.rate_formatted || '0 B/s' }}</span>
          </div>
        </div>
      </div>

      <div v-if="aiReport" class="bg-[#18181b] border border-purple-500/40 rounded-xl p-5 shadow-xl animate-fadeIn space-y-4">
        <div class="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div class="flex items-center gap-2"><Sparkles class="w-5 h-5 text-blue-400" /><h4 class="font-bold text-base text-white">{{ aiReport.title }}</h4></div>
          <span class="text-xs tabular-nums text-zinc-400">{{ aiReport.timestamp }}</span>
        </div>
        <p class="text-xs text-zinc-300 tabular-nums bg-zinc-900/80 p-3 rounded-lg border border-zinc-800">{{ aiReport.interface_summary }}</p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div v-for="(f, idx) in aiReport.findings" :key="idx" class="bg-zinc-900 border border-zinc-800 p-3 rounded-lg space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-blue-400">{{ f.badge }}</span>
              <CheckCircle class="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <p class="text-xs text-zinc-300">{{ f.message }}</p>
          </div>
        </div>
        <div class="pt-2 text-xs text-zinc-400 flex items-center gap-2">
          <ShieldCheck class="w-4 h-4 text-emerald-400" />
          <span><strong>Recomendação de Engenharia:</strong> {{ aiReport.recommendation }}</span>
        </div>
      </div>
    </div>

    <!-- Sub-tab 3: Interfaces -->
    <div v-if="activeTab === 'network-interfaces'" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="iface in (networkData.interfaces || [])" :key="iface.name" @click="$emit('open-iface', iface)"
          class="bg-[#18181b] border border-zinc-800 hover:border-blue-500/40 rounded-xl p-5 shadow-sm space-y-3 cursor-pointer transition">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="font-bold tabular-nums text-base text-white">{{ iface.name }}</span>
              <span class="text-xs uppercase tabular-nums px-2 py-0.5 rounded font-semibold" :class="iface.type === 'bridge' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'">
                {{ iface.media_type }}
              </span>
            </div>
            <span class="text-xs tabular-nums font-bold uppercase tracking-wider flex items-center gap-1.5" :class="iface.status === 'UP' || iface.status === 'up' ? 'text-emerald-400' : 'text-zinc-400'">
              <span class="w-2 h-2 rounded-full" :class="iface.status === 'UP' || iface.status === 'up' ? 'bg-emerald-400' : 'bg-zinc-600'"></span>
              {{ iface.status }}
            </span>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs tabular-nums text-zinc-400 pt-2 border-t border-zinc-800/60">
            <div>IP: <span class="text-white">{{ iface.ip }}</span></div>
            <div>Velocidade: <span class="text-white">{{ iface.speed_str || iface.speed }}</span></div>
            <div>MAC: <span class="text-zinc-300">{{ iface.mac || '—' }}</span></div>
            <div>MTU: <span class="text-white">{{ iface.mtu || 1500 }}</span></div>
          </div>
        </div>
      </div>
    </div>

    <LatencyDetailModal :open="latencyModalOpen" :initial-data="latencyData" @close="latencyModalOpen = false" />
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Share2, Activity, Network, Sparkles, CheckCircle, ShieldCheck, Search, Filter } from 'lucide-vue-next'
import LatencyDetailModal from './LatencyDetailModal.vue'
import { fetchApi } from '../lib/api-config'

const latencyData = ref({ current_ms: 0, avg_ms: 0, max_ms: 0, samples: [] })
const latencyModalOpen = ref(false)

function openLatencyModal() {
  latencyModalOpen.value = true
}

onMounted(async () => {
  try {
    const res = await fetchApi('/api/network/latency?target=1.1.1.1')
    if (res.ok) latencyData.value = await res.json()
  } catch {}
})

const props = defineProps({
  activeTab: { type: String, required: true },
  networkData: { type: Object, required: true },
  systemData: { type: Object, required: true },
  flowData: { type: Object, default: () => ({}) },
  flowConsumers: { type: Array, default: () => [] },
  aiLoading: { type: Boolean, default: false },
  aiReport: { type: Object, default: null },
})

defineEmits(['update:activeTab', 'run-ai', 'open-iface'])

const physicalNics = computed(() =>
  (props.networkData?.interfaces || []).filter(
    (i) => i.name && i.name !== 'lo' && !i.name.startsWith('docker') && !i.name.startsWith('br-') && !i.name.startsWith('veth')
  )
)
const primaryNic = computed(() => {
  const def = props.networkData?.default_interface
  const found = physicalNics.value.find((i) => i.name === def) || physicalNics.value[0]
  if (found) return found
  const flowNic = (props.flowData?.nics || []).find((n) => n.name === def) || (props.flowData?.nics || [])[0]
  if (flowNic) return { name: flowNic.name, status: 'UP', speed: flowNic.rate || 'Ativa' }
  return null
})
const secondaryNic = computed(() =>
  physicalNics.value.find((i) => i.name !== primaryNic.value?.name) || null
)
const primaryNicUp = computed(() => {
  if (!primaryNic.value) return Boolean(props.networkData?.default_ip && props.networkData.default_ip !== 'N/A')
  return (primaryNic.value.status || '').toUpperCase() === 'UP'
})
const secondaryNicUp = computed(() => (secondaryNic.value?.status || '').toUpperCase() === 'UP')

const distroLogoUrl = '/api/distro/logo'
const distroKey = computed(() => {
  const raw = `${props.systemData?.distro_id || ''} ${props.systemData?.distro_name || ''}`.toLowerCase()
  if (raw.includes('biglinux')) return 'biglinux'
  if (raw.includes('manjaro')) return 'manjaro'
  if (raw.includes('arch') || raw.includes('endeavour')) return 'arch'
  if (raw.includes('ubuntu') || raw.includes('pop') || raw.includes('mint')) return 'ubuntu'
  if (raw.includes('debian')) return 'debian'
  return 'default'
})

const flowSearch = ref('')
const flowOnlyActive = ref(false)

const activeFlowConsumersCount = computed(() =>
  (props.flowConsumers || []).filter((c) => (c.rate_bytes || 0) > 0 || c.active).length
)

const filteredFlowConsumers = computed(() => {
  const q = flowSearch.value.trim().toLowerCase()
  return (props.flowConsumers || []).filter((c) => {
    const label = `${c.label || ''} ${c.name || ''} ${c.bridge || ''}`.toLowerCase()
    if (q && !label.includes(q)) return false
    if (flowOnlyActive.value && !(c.rate_bytes > 0 || c.active)) return false
    return true
  })
})

const netChartCanvas = ref(null)
defineExpose({ netChartCanvas })
</script>
