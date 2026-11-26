<template>
  <div class="space-y-6 animate-fadeIn">
    <!-- Page Header (1:1 ProxMenux settings.tsx) -->
    <div>
      <h1 class="text-3xl font-bold text-white">Configurações</h1>
      <p class="text-sm text-zinc-400 mt-1">Preferências da interface, limites de saúde, notificações, snippets e otimizações do sistema</p>
    </div>

    <!-- 1. Interface Language Card (1:1 ProxMenux settings.tsx) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-2.5">
          <Globe2 class="w-5 h-5 text-blue-500 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Idioma da interface</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Escolha o idioma exibido no painel e nos gráficos.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="savedCard === 'lang'" class="text-xs text-emerald-400 flex items-center gap-1"><Check class="w-3.5 h-3.5" /> Salvo</span>
          <button v-if="editing !== 'lang'" @click="editing = 'lang'" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-200 flex items-center gap-1.5 cursor-pointer">
            <Settings2 class="w-3.5 h-3.5" /> Editar
          </button>
          <template v-else>
            <button @click="editing = ''" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 text-zinc-400 cursor-pointer">Cancelar</button>
            <button @click="saveSection('lang')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1 cursor-pointer"><Check class="w-3.5 h-3.5" /> Salvar</button>
          </template>
        </div>
      </div>
      <div class="flex items-center justify-between gap-4 pt-2 border-t border-zinc-800/70">
        <span class="text-sm text-zinc-300">Idioma selecionado</span>
        <select v-model="settingsData.language" :disabled="editing !== 'lang'" class="bg-zinc-900 border border-zinc-700 rounded-md px-3 py-1.5 text-sm text-white disabled:opacity-70">
          <option value="pt-BR">Português (Brasil)</option>
          <option value="en-US">English (US)</option>
        </select>
      </div>
    </div>

    <!-- 2. Network Units Card (1:1 ProxMenux) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-2.5">
          <Ruler class="w-5 h-5 text-blue-500 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Unidades de rede</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Define como o tráfego e a largura de banda são exibidos (conversão automática KB/MB/GB).</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="savedCard === 'netunit'" class="text-xs text-emerald-400 flex items-center gap-1"><Check class="w-3.5 h-3.5" /> Salvo</span>
          <button v-if="editing !== 'netunit'" @click="editing = 'netunit'" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-200 flex items-center gap-1.5 cursor-pointer">
            <Settings2 class="w-3.5 h-3.5" /> Editar
          </button>
          <template v-else>
            <button @click="editing = ''" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 text-zinc-400 cursor-pointer">Cancelar</button>
            <button @click="saveSection('netunit')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1 cursor-pointer"><Check class="w-3.5 h-3.5" /> Salvar</button>
          </template>
        </div>
      </div>
      <div class="flex items-center justify-between gap-4 pt-2 border-t border-zinc-800/70">
        <span class="text-sm text-zinc-300">Formato de exibição</span>
        <select v-model="settingsData.network_unit" :disabled="editing !== 'netunit'" class="bg-zinc-900 border border-zinc-700 rounded-md px-3 py-1.5 text-sm text-white disabled:opacity-70">
          <option value="bytes">Bytes (KB, MB, GB)</option>
          <option value="bits">Bits (Kbps, Mbps, Gbps)</option>
        </select>
      </div>
    </div>

    <!-- 3. Navigation Tab Order Card (1:1 NavTabOrderCard) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-2.5">
          <Layers class="w-5 h-5 text-blue-500 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Ordem das abas de navegação</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Personalize a ordem das abas principais exibidas na barra superior.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="savedCard === 'taborder'" class="text-xs text-emerald-400 flex items-center gap-1"><Check class="w-3.5 h-3.5" /> Salvo</span>
          <button v-if="editing !== 'taborder'" @click="editing = 'taborder'" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-200 flex items-center gap-1.5 cursor-pointer">
            <Settings2 class="w-3.5 h-3.5" /> Editar
          </button>
          <template v-else>
            <button @click="resetTabOrder" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 flex items-center gap-1 cursor-pointer"><RotateCcw class="w-3 h-3" /> Restaurar</button>
            <button @click="saveSection('taborder')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1 cursor-pointer"><Check class="w-3.5 h-3.5" /> Salvar</button>
          </template>
        </div>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 pt-2 border-t border-zinc-800/70 text-xs">
        <div v-for="(tab, idx) in tabOrder" :key="tab" class="p-2.5 rounded-lg bg-zinc-900/70 border border-zinc-800 flex items-center justify-between gap-1">
          <span class="font-medium text-zinc-200 truncate">{{ tabLabels[tab] || tab }}</span>
          <div v-if="editing === 'taborder'" class="flex items-center gap-0.5 shrink-0">
            <button @click="moveTab(idx, -1)" :disabled="idx === 0" class="px-1 text-zinc-400 hover:text-white disabled:opacity-30 cursor-pointer">◀</button>
            <button @click="moveTab(idx, 1)" :disabled="idx === tabOrder.length - 1" class="px-1 text-zinc-400 hover:text-white disabled:opacity-30 cursor-pointer">▶</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. Storage Display Card (1:1 StorageDisplayCard) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-2.5">
          <HardDrive class="w-5 h-5 text-blue-500 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Exibição de armazenamento</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Agrupar discos físicos por controlador de armazenamento na aba Armazenamento.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="savedCard === 'storagedisp'" class="text-xs text-emerald-400 flex items-center gap-1"><Check class="w-3.5 h-3.5" /> Salvo</span>
          <button v-if="editing !== 'storagedisp'" @click="editing = 'storagedisp'" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-200 flex items-center gap-1.5 cursor-pointer">
            <Settings2 class="w-3.5 h-3.5" /> Editar
          </button>
          <template v-else>
            <button @click="editing = ''" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 text-zinc-400 cursor-pointer">Cancelar</button>
            <button @click="saveSection('storagedisp')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1 cursor-pointer"><Check class="w-3.5 h-3.5" /> Salvar</button>
          </template>
        </div>
      </div>
      <div class="flex items-center justify-between pt-2 border-t border-zinc-800/70">
        <span class="text-sm text-zinc-300">Agrupar discos por controlador</span>
        <button
          type="button"
          :disabled="editing !== 'storagedisp'"
          @click="settingsData.group_disks_by_controller = !settingsData.group_disks_by_controller"
          class="w-10 h-5 rounded-full transition-colors relative cursor-pointer disabled:opacity-60"
          :class="settingsData.group_disks_by_controller ? 'bg-blue-600' : 'bg-zinc-700'"
        >
          <span class="block w-4 h-4 rounded-full bg-white transition-transform absolute top-0.5" :class="settingsData.group_disks_by_controller ? 'translate-x-5' : 'translate-x-0.5'"></span>
        </button>
      </div>
    </div>

    <!-- 5. Limites do Monitor de Integridade (1:1 ProxMenux - Imagem 12) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div class="flex items-start gap-2.5">
          <SlidersHorizontal class="w-5 h-5 text-amber-400 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Limites do Monitor de Integridade</h3>
            <p class="text-xs text-zinc-400 mt-0.5">O Health Monitor e as notificações reagem quando esses limites são ultrapassados. Ajuste o nível de aviso (âmbar) e o nível crítico (vermelho).</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="savedCard === 'health'" class="text-xs text-emerald-400 flex items-center gap-1"><Check class="w-3.5 h-3.5" /> Salvo</span>
          <button @click="$emit('reset-thresholds')" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 flex items-center gap-1.5 cursor-pointer">
            <RotateCcw class="w-3.5 h-3.5" /> Redefinir tudo
          </button>
          <button v-if="editing !== 'health'" @click="editing = 'health'" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-200 flex items-center gap-1.5 cursor-pointer">
            <Settings2 class="w-3.5 h-3.5" /> Editar
          </button>
          <button v-else @click="saveSection('health')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1 cursor-pointer">
            <Check class="w-3.5 h-3.5" /> Salvar
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-zinc-800/70 text-xs tabular-nums">
        <div v-for="card in thresholdCards" :key="card.warnKey" class="p-4 rounded-xl bg-zinc-950/60 border border-zinc-800 space-y-3">
          <div>
            <div class="text-sm font-semibold text-white flex items-center gap-2">
              <component :is="card.icon" class="w-4 h-4 text-zinc-400" />
              <span>{{ card.title }}</span>
            </div>
            <div v-if="card.subtitle" class="text-xs text-zinc-500 mt-0.5">{{ card.subtitle }}</div>
          </div>

          <div class="flex items-center justify-end gap-4 font-bold text-sm">
            <span class="text-amber-400">{{ getWarnVal(card) }}{{ card.unit }}</span>
            <span class="text-red-500">{{ getCritVal(card) }}{{ card.unit }}</span>
          </div>

          <!-- Dual-Zone Visual Bar -->
          <div class="relative h-2 rounded-full bg-zinc-800 overflow-hidden">
            <div class="absolute inset-y-0 left-0 bg-zinc-700" :style="{ width: `${pctOf(getWarnVal(card), card.max)}%` }"></div>
            <div class="absolute inset-y-0 bg-amber-500" :style="{ left: `${pctOf(getWarnVal(card), card.max)}%`, width: `${Math.max(2, pctOf(getCritVal(card) - getWarnVal(card), card.max))}%` }"></div>
            <div class="absolute inset-y-0 right-0 bg-red-600/80" :style="{ left: `${pctOf(getCritVal(card), card.max)}%` }"></div>
          </div>

          <div v-if="editing === 'health'" class="grid grid-cols-2 gap-3 pt-1">
            <div>
              <label class="text-xs text-amber-400">Aviso ({{ card.unit }})</label>
              <input v-model.number="settingsData.thresholds[card.warnKey]" type="range" :min="card.min" :max="card.max" class="w-full accent-amber-500 cursor-pointer" />
            </div>
            <div>
              <label class="text-xs text-red-400">Crítico ({{ card.unit }})</label>
              <input v-model.number="settingsData.thresholds[card.critKey]" type="range" :min="card.min" :max="card.max" class="w-full accent-red-500 cursor-pointer" />
            </div>
          </div>

          <div class="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wide">
            <span class="text-zinc-400">OK &lt; {{ getWarnVal(card) }}{{ card.unit }}</span>
            <span class="text-amber-400">AVISAR {{ getWarnVal(card) }}-{{ getCritVal(card) }}{{ card.unit }}</span>
            <span class="text-red-400">CRÍTICO &gt; {{ getCritVal(card) }}{{ card.unit }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 6. Network Interface Exclusions Card -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-2.5">
          <Network class="w-5 h-5 text-blue-500 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Exclusões de interface de rede</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Interfaces excluídas não disparam alertas de desconexão ou notificações.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="savedCard === 'ifaces'" class="text-xs text-emerald-400 flex items-center gap-1"><Check class="w-3.5 h-3.5" /> Salvo</span>
          <button v-if="editing !== 'ifaces'" @click="editing = 'ifaces'" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-200 flex items-center gap-1.5 cursor-pointer">
            <Settings2 class="w-3.5 h-3.5" /> Editar
          </button>
          <template v-else>
            <button @click="editing = ''" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 text-zinc-400 cursor-pointer">Cancelar</button>
            <button @click="saveSection('ifaces')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1 cursor-pointer"><Check class="w-3.5 h-3.5" /> Salvar</button>
          </template>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-2 border-t border-zinc-800/70">
        <div v-for="iface in interfaces" :key="iface.name" class="flex items-center justify-between p-3 rounded-lg bg-zinc-900/70 border border-zinc-800">
          <div>
            <div class="font-mono text-sm font-semibold text-white">{{ iface.name }}</div>
            <div class="text-xs text-zinc-400 font-mono">{{ iface.ip !== 'N/A' ? iface.ip : (iface.media_type || 'Interface') }}</div>
          </div>
          <button
            type="button"
            :disabled="editing !== 'ifaces'"
            @click="toggleExcludedInterface(iface.name)"
            class="w-10 h-5 rounded-full transition-colors relative cursor-pointer disabled:opacity-60"
            :class="isInterfaceExcluded(iface.name) ? 'bg-blue-600' : 'bg-zinc-700'"
          >
            <span class="block w-4 h-4 rounded-full bg-white transition-transform absolute top-0.5" :class="isInterfaceExcluded(iface.name) ? 'translate-x-5' : 'translate-x-0.5'"></span>
          </button>
        </div>
      </div>
    </div>

    <!-- 7. Disk Exclusions Card (1:1 DiskExclusions) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-2.5">
          <Database class="w-5 h-5 text-purple-400 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Exclusões de disco</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Discos ignorados nas leituras periódicas de temperatura e SMART para permitir standby.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="savedCard === 'disks'" class="text-xs text-emerald-400 flex items-center gap-1"><Check class="w-3.5 h-3.5" /> Salvo</span>
          <button v-if="editing !== 'disks'" @click="editing = 'disks'" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-200 flex items-center gap-1.5 cursor-pointer">
            <Settings2 class="w-3.5 h-3.5" /> Editar
          </button>
          <template v-else>
            <button @click="editing = ''" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 text-zinc-400 cursor-pointer">Cancelar</button>
            <button @click="saveSection('disks')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1 cursor-pointer"><Check class="w-3.5 h-3.5" /> Salvar</button>
          </template>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-2 border-t border-zinc-800/70">
        <div v-for="d in physicalDisks" :key="d.device" class="flex items-center justify-between p-3 rounded-lg bg-zinc-900/70 border border-zinc-800">
          <div class="min-w-0">
            <div class="font-mono text-sm font-semibold text-white truncate">{{ d.name }}</div>
            <div class="text-xs text-zinc-400 truncate">{{ d.model }} · {{ d.size_formatted }}</div>
          </div>
          <button
            type="button"
            :disabled="editing !== 'disks'"
            @click="toggleExcludedDisk(d.name)"
            class="w-10 h-5 rounded-full transition-colors relative cursor-pointer disabled:opacity-60"
            :class="isDiskExcluded(d.name) ? 'bg-blue-600' : 'bg-zinc-700'"
          >
            <span class="block w-4 h-4 rounded-full bg-white transition-transform absolute top-0.5" :class="isDiskExcluded(d.name) ? 'translate-x-5' : 'translate-x-0.5'"></span>
          </button>
        </div>
      </div>
    </div>

    <!-- 8. Notificações & Aprimoramento de IA (1:1 ProxMenux - Imagens 5 a 11) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-5">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div class="flex items-start gap-2.5">
          <Bell class="w-5 h-5 text-blue-400 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white flex items-center gap-2">
              Notificações
              <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold">
                {{ settingsData.notifications_enabled !== false ? 'Ativo' : 'Desativado' }}
              </span>
            </h3>
            <p class="text-xs text-zinc-400 mt-0.5">Configure canais de notificação e filtros de eventos. Receba alertas via Telegram, Gotify, Discord, Email, Pushover ou Apprise.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="savedCard === 'notif'" class="text-xs text-emerald-400 flex items-center gap-1"><Check class="w-3.5 h-3.5" /> Salvo</span>
          <button @click="saveSection('notif')" class="h-8 px-3.5 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-1.5 cursor-pointer">
            <Check class="w-3.5 h-3.5" /> Salvar
          </button>
        </div>
      </div>

      <!-- Habilitar notificações -->
      <div class="flex items-center justify-between p-3.5 rounded-lg bg-zinc-950/60 border border-zinc-800 text-xs">
        <div>
          <div class="font-semibold text-white flex items-center gap-2"><Bell class="w-3.5 h-3.5 text-zinc-400" /> Habilitar notificações</div>
          <div class="text-zinc-400 mt-0.5">Ative o serviço de notificação</div>
        </div>
        <input type="checkbox" v-model="settingsData.notifications_enabled" class="w-4 h-4 accent-blue-600 cursor-pointer" />
      </div>

      <!-- CANAIS (6 tabs 1:1 Imagem 5) -->
      <div class="space-y-3">
        <div class="text-xs font-semibold uppercase tracking-wider text-zinc-400">Canais</div>
        <div class="grid grid-cols-3 sm:grid-cols-6 bg-zinc-950 border border-zinc-800 rounded-lg p-1 gap-1 text-xs font-semibold">
          <button v-for="ch in ['telegram', 'gotify', 'discord', 'email', 'pushover', 'apprise']" :key="ch"
            @click="activeNotifChannel = ch"
            class="py-1.5 rounded-md capitalize cursor-pointer transition"
            :class="activeNotifChannel === ch ? 'bg-zinc-800 text-white shadow' : 'text-zinc-400 hover:text-white'">
            {{ ch === 'email' ? 'Email' : ch.charAt(0).toUpperCase() + ch.slice(1) }}
          </button>
        </div>

        <div class="p-4 rounded-xl bg-zinc-950/60 border border-zinc-800 space-y-3 text-xs">
          <template v-if="activeNotifChannel === 'telegram'">
            <div class="space-y-1">
              <label class="block text-zinc-300 font-medium">Token de bot</label>
              <div class="relative">
                <input :value="telegramToken" @input="$emit('update:telegramToken', $event.target.value)" :type="showTgToken ? 'text' : 'password'" placeholder="123456789:ABCdef..." class="w-full bg-zinc-900 border border-zinc-700 rounded-md pl-3 pr-9 py-2 text-white font-mono" />
                <button type="button" @click="showTgToken = !showTgToken" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer">
                  <EyeOff v-if="showTgToken" class="w-4 h-4" /><Eye v-else class="w-4 h-4" />
                </button>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-zinc-300 font-medium mb-1">ID do bate-papo</label>
                <input :value="telegramChatId" @input="$emit('update:telegramChatId', $event.target.value)" type="text" placeholder="-1001234567890" class="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
              </div>
              <div>
                <label class="block text-zinc-300 font-medium mb-1">ID do tópico (opcional)</label>
                <input v-model="settingsData.telegram_topic_id" type="text" placeholder="123456" class="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
              </div>
            </div>
            <button type="button" @click="$emit('test-telegram')" class="px-4 py-2 rounded-md bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 font-semibold flex items-center gap-1.5 cursor-pointer">
              <Send class="w-3.5 h-3.5" /> Testar Telegram
            </button>
          </template>

          <template v-else-if="activeNotifChannel === 'discord'">
            <div class="space-y-1">
              <label class="block text-zinc-300 font-medium">Webhook URL</label>
              <div class="relative">
                <input :value="discordWebhook" @input="$emit('update:discordWebhook', $event.target.value)" :type="showDiscordUrl ? 'text' : 'password'" placeholder="https://discord.com/api/webhooks/..." class="w-full bg-zinc-900 border border-zinc-700 rounded-md pl-3 pr-9 py-2 text-white font-mono" />
                <button type="button" @click="showDiscordUrl = !showDiscordUrl" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer">
                  <EyeOff v-if="showDiscordUrl" class="w-4 h-4" /><Eye v-else class="w-4 h-4" />
                </button>
              </div>
            </div>
            <button type="button" @click="$emit('test-discord')" class="px-4 py-2 rounded-md bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 font-semibold flex items-center gap-1.5 cursor-pointer">
              <Send class="w-3.5 h-3.5" /> Testar Discord
            </button>
          </template>

          <template v-else-if="activeNotifChannel === 'gotify'">
            <input v-model="settingsData.gotify_url" type="text" placeholder="https://gotify.seu-dominio.com" class="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
            <div class="relative">
              <input v-model="settingsData.gotify_token" :type="showGotifyToken ? 'text' : 'password'" placeholder="App Token Gotify" class="w-full bg-zinc-900 border border-zinc-700 rounded-md pl-3 pr-9 py-2 text-white font-mono" />
              <button type="button" @click="showGotifyToken = !showGotifyToken" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer">
                <EyeOff v-if="showGotifyToken" class="w-4 h-4" /><Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </template>

          <template v-else-if="activeNotifChannel === 'pushover'">
            <input v-model="settingsData.pushover_user" type="text" placeholder="User Key" class="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
            <div class="relative">
              <input v-model="settingsData.pushover_token" :type="showPushoverToken ? 'text' : 'password'" placeholder="API Token" class="w-full bg-zinc-900 border border-zinc-700 rounded-md pl-3 pr-9 py-2 text-white font-mono" />
              <button type="button" @click="showPushoverToken = !showPushoverToken" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer">
                <EyeOff v-if="showPushoverToken" class="w-4 h-4" /><Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </template>

          <template v-else-if="activeNotifChannel === 'email'">
            <div class="grid grid-cols-2 gap-2">
              <input v-model="settingsData.smtp_host" type="text" placeholder="smtp.gmail.com" class="bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
              <input v-model.number="settingsData.smtp_port" type="number" placeholder="587" class="bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
            </div>
            <input v-model="settingsData.smtp_to" type="email" placeholder="alertas@seudominio.com" class="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
          </template>

          <template v-else>
            <input v-model="settingsData.webhook_url" type="text" placeholder="https://hooks.exemplo.com/webhook" class="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
            <p class="text-zinc-500">Envia payloads JSON em tempo real para automações externas (n8n, Home Assistant, Apprise).</p>
          </template>
        </div>
      </div>

      <!-- Categorias de notificação (1:1 Imagens 6-7) -->
      <div class="space-y-2 text-xs">
        <div class="font-semibold text-zinc-300 flex items-center gap-1.5"><Bell class="w-3.5 h-3.5 text-zinc-400" /> Categorias de notificação</div>
        <div class="space-y-1.5">
          <div v-for="cat in notifCategories" :key="cat.key" class="flex items-center justify-between px-3.5 py-2.5 rounded-lg bg-zinc-950/60 border border-zinc-800">
            <span class="font-medium text-emerald-400">{{ cat.label }}</span>
            <div class="flex items-center gap-3">
              <span class="text-zinc-400 font-mono">{{ cat.count }}</span>
              <input type="checkbox" v-model="settingsData[cat.key]" class="w-4 h-4 accent-blue-600 cursor-pointer" />
            </div>
          </div>
        </div>
      </div>

      <!-- Horas tranquilas & Resumo diário (1:1 Imagem 8) -->
      <div class="p-4 rounded-xl bg-zinc-950/60 border border-zinc-800 space-y-4 text-xs">
        <div class="flex items-center justify-between">
          <div>
            <div class="font-semibold text-white">Horas tranquilas</div>
            <div class="text-zinc-400">Durante esta janela apenas eventos CRÍTICOS chegam a este canal.</div>
          </div>
          <input type="checkbox" v-model="settingsData.quiet_hours_enabled" class="w-4 h-4 accent-blue-600 cursor-pointer" />
        </div>
        <div class="flex items-center gap-3">
          <span class="text-zinc-400">De</span>
          <input v-model="settingsData.quiet_start" type="text" placeholder="22:00" class="w-20 bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1 text-white font-mono" />
          <span class="text-zinc-400">Até</span>
          <input v-model="settingsData.quiet_end" type="text" placeholder="06:00" class="w-20 bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1 text-white font-mono" />
        </div>
        <div class="pt-3 border-t border-zinc-800 flex items-center justify-between">
          <div>
            <div class="font-semibold text-white">Resumo diário de eventos INFO</div>
            <div class="text-zinc-400">Os eventos INFO acumulam-se durante o dia e chegam uma vez como resumo.</div>
          </div>
          <input type="checkbox" v-model="settingsData.daily_digest_enabled" class="w-4 h-4 accent-blue-600 cursor-pointer" />
        </div>
        <div class="flex items-center gap-3">
          <span class="text-zinc-400">Enviar em</span>
          <input v-model="settingsData.daily_digest_time" type="text" placeholder="09:00" class="w-20 bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1 text-white font-mono" />
        </div>
      </div>

      <!-- Aprimoramento de IA (1:1 Imagens 9-11) -->
      <div class="p-4 rounded-xl bg-zinc-950/70 border border-purple-500/30 space-y-4 text-xs">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles class="w-4 h-4 text-purple-400" /> Aprimoramento de IA
            </div>
            <div class="text-zinc-400 mt-0.5">Use IA para gerar mensagens de notificação contextuais</div>
          </div>
          <input type="checkbox" v-model="settingsData.ai_enabled" class="w-4 h-4 accent-purple-500 cursor-pointer" />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label class="block text-zinc-300 font-medium mb-1">Provedor</label>
            <select v-model="settingsData.ai_provider" class="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white">
              <option value="openrouter">OpenRouter</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic (Claude)</option>
              <option value="gemini">Google Gemini</option>
              <option value="groq">Groq</option>
              <option value="ollama">Ollama (Local)</option>
            </select>
          </div>
          <div>
            <label class="block text-zinc-300 font-medium mb-1">Chave de API</label>
            <div class="relative">
              <input :value="aiApiKey" @input="$emit('update:aiApiKey', $event.target.value)" :type="showAiKey ? 'text' : 'password'" placeholder="sk-or-v1-..." class="w-full bg-zinc-900 border border-zinc-700 rounded-md pl-3 pr-9 py-2 text-white font-mono" />
              <button type="button" @click="showAiKey = !showAiKey" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer">
                <EyeOff v-if="showAiKey" class="w-4 h-4" /><Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </div>
          <div>
            <label class="block text-zinc-300 font-medium mb-1">Modelo</label>
            <input :value="aiModel" @input="$emit('update:aiModel', $event.target.value)" type="text" placeholder="nvidia/nemotron-3-nano-30b-a3b:reasoning:free" class="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
          </div>
        </div>
        <button type="button" @click="saveSection('notif')" class="w-full py-2.5 rounded-lg bg-purple-700/40 hover:bg-purple-700/60 border border-purple-500/40 text-purple-200 font-semibold cursor-pointer">
          ⚡ Salvar e Testar Conexão IA
        </button>
      </div>
    </div>

    <!-- 9. GitHub API Token Card (1:1 ProxMenux settings.tsx) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-3">
      <div class="flex items-start justify-between gap-4">
        <div>
          <h3 class="text-base font-semibold text-white">Token da API do GitHub</h3>
          <p class="text-xs text-zinc-400 mt-0.5">Opcional para repositórios públicos; evita limite de requisições ao verificar releases e catálogo de apps.</p>
        </div>
        <button @click="saveSection('github')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-1 cursor-pointer">
          <Check class="w-3.5 h-3.5" /> Salvar
        </button>
      </div>
      <div class="relative">
        <input v-model="settingsData.github_token" :type="showGithubToken ? 'text' : 'password'" placeholder="ghp_..." class="w-full bg-zinc-950 border border-zinc-700 rounded-md pl-3 pr-10 py-2 text-xs text-white font-mono" />
        <button type="button" @click="showGithubToken = !showGithubToken" class="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer">
          <EyeOff v-if="showGithubToken" class="w-4 h-4" /><Eye v-else class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 10. Container Update Detection (1:1 ProxMenux LxcUpdateDetection) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-2.5">
          <Package class="w-5 h-5 text-cyan-400 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Detecção de Atualizações de Containers</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Verifica periodicamente novas versões de imagens Docker e stacks Dokploy no registro remoto.</p>
          </div>
        </div>
        <button @click="saveSection('containers')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-1 cursor-pointer">
          <Check class="w-3.5 h-3.5" /> Salvar
        </button>
      </div>
      <div class="flex items-center justify-between pt-2 border-t border-zinc-800/70 text-xs">
        <span class="text-zinc-300">Verificação automática habilitada</span>
        <input type="checkbox" v-model="settingsData.container_updates_enabled" class="w-4 h-4 accent-blue-600 cursor-pointer" />
      </div>
    </div>

    <!-- 11. Snippets & Comandos Rápidos (1:1 ProxMenux settings.tsx) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start gap-2.5">
        <Code class="w-5 h-5 text-blue-400 mt-0.5 shrink-0" />
        <div>
          <h3 class="text-base font-semibold text-white">Snippets &amp; Comandos Rápidos</h3>
          <p class="text-xs text-zinc-400 mt-0.5">Salve comandos Bash frequentes para copiar e executar rapidamente no terminal.</p>
        </div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
        <input v-model="newSnippet.name" type="text" placeholder="Nome (ex: Reiniciar Docker)" class="bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white" />
        <input v-model="newSnippet.command" type="text" placeholder="Comando (ex: systemctl restart docker)" class="bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono sm:col-span-2" />
      </div>
      <div class="flex justify-end">
        <button @click="addSnippet" class="px-3.5 py-1.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 cursor-pointer">
          <Plus class="w-3.5 h-3.5" /> Adicionar Snippet
        </button>
      </div>
      <div v-if="snippets.length" class="space-y-2 text-xs">
        <div v-for="s in snippets" :key="s.id" class="flex items-center justify-between gap-3 p-3 rounded-lg bg-zinc-950/70 border border-zinc-800">
          <div class="min-w-0">
            <div class="font-semibold text-white">{{ s.name }}</div>
            <div class="font-mono text-zinc-400 truncate mt-0.5">{{ s.command }}</div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button @click="copySnippet(s.command)" class="p-1.5 rounded bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 cursor-pointer" title="Copiar">
              <Copy class="w-3.5 h-3.5" />
            </button>
            <button @click="deleteSnippet(s.id)" class="p-1.5 rounded bg-zinc-900 hover:bg-red-950 border border-zinc-700 text-red-400 cursor-pointer" title="Excluir">
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
      <div v-else class="text-xs text-zinc-500 text-center py-3 border border-dashed border-zinc-800 rounded-lg">
        Nenhum snippet salvo ainda.
      </div>
    </div>

    <!-- 12. Otimizações e Ferramentas do Sistema (1:1 ProxMenux settings.tsx) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-2.5">
          <Sparkles class="w-5 h-5 text-orange-400 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Otimizações &amp; Serviços do Host Linux</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Inventário em tempo real dos daemons e utilitários de telemetria e segurança ativos no host.</p>
          </div>
        </div>
        <span class="text-xs font-semibold text-orange-400">{{ optimizations.filter(o => o.installed).length }} / {{ optimizations.length }} ativos</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
        <div v-for="opt in optimizations" :key="opt.key"
          class="flex items-center justify-between gap-2 p-3 rounded-lg border transition-colors"
          :class="opt.installed ? 'bg-zinc-950/60 border-zinc-800' : 'bg-zinc-950/30 border-zinc-800/50 opacity-70'">
          <div class="flex items-center gap-2.5 min-w-0">
            <span class="w-2 h-2 rounded-full shrink-0" :class="opt.installed ? 'bg-emerald-500' : 'bg-zinc-600'"></span>
            <div class="min-w-0">
              <div class="text-sm font-medium text-white truncate">{{ opt.name }}</div>
              <div class="text-xs text-zinc-400 truncate">{{ opt.description }}</div>
            </div>
          </div>
          <span class="text-xs px-2 py-0.5 rounded font-mono shrink-0"
            :class="opt.installed ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'bg-zinc-900 text-zinc-500 border border-zinc-800'">
            {{ opt.status }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Globe2, Ruler, Layers, HardDrive, HeartPulse, Network, Database, Bell,
  Settings2, Check, RotateCcw, Eye, EyeOff, Send, Code, Sparkles, Copy, Trash2, Plus, Package,
  SlidersHorizontal, Cpu, MemoryStick, Thermometer
} from 'lucide-vue-next'
import { fetchApi } from '../lib/api-config'

const props = defineProps({
  settingsData: { type: Object, required: true },
  interfaces: { type: Array, default: () => [] },
  physicalDisks: { type: Array, default: () => [] },
  telegramToken: { type: String, default: '' },
  telegramChatId: { type: String, default: '' },
  discordWebhook: { type: String, default: '' },
  aiApiKey: { type: String, default: '' },
  aiModel: { type: String, default: '' },
})

const emit = defineEmits([
  'save', 'reset-thresholds', 'test-telegram', 'test-discord',
  'update:telegramToken', 'update:telegramChatId', 'update:discordWebhook', 'update:aiApiKey', 'update:aiModel',
])

const editing = ref('')
const savedCard = ref('')
const notifTab = ref('channels')
const showTgToken = ref(false)
const showDiscordUrl = ref(false)
const showGotifyToken = ref(false)
const showPushoverToken = ref(false)
const showAiKey = ref(false)
const showGithubToken = ref(false)
const activeNotifChannel = ref('telegram')

const thresholdCards = [
  { title: 'Uso da CPU', subtitle: '', warnKey: 'cpu_warn', critKey: 'cpu_crit', defWarn: 85, defCrit: 95, min: 30, max: 100, unit: '%', icon: Cpu },
  { title: 'Espaço em disco - host', subtitle: 'Aplica-se a / e aos pontos de montagem locais.', warnKey: 'disk_warn', critKey: 'disk_crit', defWarn: 85, defCrit: 95, min: 30, max: 100, unit: '%', icon: HardDrive },
  { title: 'Memória e swap', subtitle: 'RAM do sistema', warnKey: 'mem_warn', critKey: 'mem_crit', defWarn: 85, defCrit: 95, min: 30, max: 100, unit: '%', icon: MemoryStick },
  { title: 'Temperatura da CPU', subtitle: 'Sensores coretemp / k10temp', warnKey: 'temp_warn', critKey: 'temp_crit', defWarn: 75, defCrit: 90, min: 30, max: 105, unit: '°C', icon: Thermometer },
]

function getWarnVal(card) {
  return Number(props.settingsData?.thresholds?.[card.warnKey] ?? card.defWarn)
}
function getCritVal(card) {
  return Number(props.settingsData?.thresholds?.[card.critKey] ?? card.defCrit)
}
function pctOf(val, max) {
  return Math.max(0, Math.min(100, Math.round((Number(val) / max) * 100)))
}

const notifCategories = [
  { key: 'notify_containers', label: 'Containers Docker', count: '4/4' },
  { key: 'notify_backups', label: 'Cópias de segurança', count: '6/6' },
  { key: 'notify_health', label: 'Recursos & Monitor de Saúde', count: '6/7' },
  { key: 'notify_updates', label: 'Atualizações', count: '10/11' },
  { key: 'notify_security', label: 'Segurança', count: '4/4' },
]
const snippets = ref([])
const newSnippet = ref({ name: '', command: '' })
const optimizations = ref([])

onMounted(async () => {
  try {
    const [snRes, optRes] = await Promise.all([
      fetch('/api/snippets'),
      fetch('/api/optimizations'),
    ])
    if (snRes.ok) {
      const d = await snRes.json()
      snippets.value = d.snippets || []
    }
    if (optRes.ok) {
      const d = await optRes.json()
      optimizations.value = d.tools || []
    }
  } catch {}
})

async function addSnippet() {
  if (!newSnippet.value.name.trim() || !newSnippet.value.command.trim()) return
  const res = await fetchApi('/api/snippets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newSnippet.value),
  })
  if (res.ok) {
    const d = await res.json()
    snippets.value = d.snippets || []
    newSnippet.value = { name: '', command: '' }
  }
}

async function deleteSnippet(id) {
  const res = await fetchApi(`/api/snippets/${id}`, { method: 'DELETE' })
  if (res.ok) {
    const d = await res.json()
    snippets.value = d.snippets || []
  }
}

function copySnippet(cmd) {
  navigator.clipboard?.writeText(cmd)
}

const DEFAULT_TABS = ['overview', 'apps', 'containers', 'node', 'backup', 'terminal', 'admin']
const tabOrder = ref([...DEFAULT_TABS])
const tabLabels = {
  overview: 'Visão geral',
  apps: 'Apps',
  containers: 'Containers',
  node: 'Nó',
  backup: 'Backup',
  terminal: 'Terminal',
  admin: 'Admin',
}

const thresholdItems = [
  { key: 'cpu_warn', label: 'CPU Aviso', rec: 80, unit: '%' },
  { key: 'cpu_crit', label: 'CPU Crítico', rec: 95, unit: '%' },
  { key: 'mem_warn', label: 'RAM Aviso', rec: 85, unit: '%' },
  { key: 'temp_warn', label: 'Temp Aviso', rec: 75, unit: '°C' },
  { key: 'disk_warn', label: 'Disco Aviso', rec: 85, unit: '%' },
]

const eventToggles = [
  { key: 'notify_health', title: 'Alertas de Integridade', desc: 'CPU, Memória, Temperatura e Disco acima do limite' },
  { key: 'notify_updates', title: 'Atualizações Disponíveis', desc: 'Notificar quando houver novos pacotes no host' },
  { key: 'notify_containers', title: 'Estado de Containers', desc: 'Notificar quando um container parar inesperadamente' },
  { key: 'notify_backups', title: 'Conclusão de Backups', desc: 'Enviar resumo após backup local ou Cloudflare R2' },
]

function moveTab(idx, dir) {
  const target = idx + dir
  if (target < 0 || target >= tabOrder.value.length) return
  const arr = [...tabOrder.value]
  const [item] = arr.splice(idx, 1)
  arr.splice(target, 0, item)
  tabOrder.value = arr
  props.settingsData.tab_order = arr
}

function resetTabOrder() {
  tabOrder.value = [...DEFAULT_TABS]
  props.settingsData.tab_order = [...DEFAULT_TABS]
}

function isInterfaceExcluded(name) {
  return (props.settingsData.excluded_interfaces || []).includes(name)
}
function toggleExcludedInterface(name) {
  const list = props.settingsData.excluded_interfaces || []
  props.settingsData.excluded_interfaces = list.includes(name) ? list.filter(x => x !== name) : [...list, name]
}
function isDiskExcluded(name) {
  return (props.settingsData.excluded_disks || []).includes(name)
}
function toggleExcludedDisk(name) {
  const list = props.settingsData.excluded_disks || []
  props.settingsData.excluded_disks = list.includes(name) ? list.filter(x => x !== name) : [...list, name]
}

async function saveSection(section) {
  await emit('save')
  editing.value = ''
  savedCard.value = section
  setTimeout(() => { savedCard.value = '' }, 2500)
}
</script>
