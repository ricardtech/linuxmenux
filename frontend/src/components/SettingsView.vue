<template>
  <div class="space-y-6 animate-fadeIn">
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

    <!-- 5. Health Thresholds Card (1:1 HealthThresholds) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-2.5">
          <HeartPulse class="w-5 h-5 text-emerald-500 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Monitor de integridade e limiares</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Define quando os alertas de CPU, Memória, Temperatura e Disco mudam para Aviso ou Crítico.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="savedCard === 'health'" class="text-xs text-emerald-400 flex items-center gap-1"><Check class="w-3.5 h-3.5" /> Salvo</span>
          <button v-if="editing !== 'health'" @click="editing = 'health'" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-200 flex items-center gap-1.5 cursor-pointer">
            <Settings2 class="w-3.5 h-3.5" /> Editar
          </button>
          <template v-else>
            <button @click="$emit('reset-thresholds')" class="h-8 px-3 text-xs rounded-md border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 flex items-center gap-1 cursor-pointer"><RotateCcw class="w-3 h-3" /> Redefinir</button>
            <button @click="saveSection('health')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1 cursor-pointer"><Check class="w-3.5 h-3.5" /> Salvar</button>
          </template>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-2 border-t border-zinc-800/70 text-xs tabular-nums">
        <div v-for="item in thresholdItems" :key="item.key" class="p-3 rounded-lg bg-zinc-900/70 border border-zinc-800 space-y-1.5">
          <div class="flex items-center justify-between">
            <label class="text-zinc-300 font-medium">{{ item.label }}</label>
            <span class="text-xs text-zinc-500">Rec: {{ item.rec }}{{ item.unit }}</span>
          </div>
          <input
            v-model.number="settingsData.thresholds[item.key]"
            :disabled="editing !== 'health'"
            type="number"
            class="w-full bg-zinc-950 border border-zinc-700 rounded px-2.5 py-1.5 text-sm text-white text-right disabled:opacity-70"
          />
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

    <!-- 8. Notifications & AI Card (1:1 NotificationSettings with sub-tabs) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-2.5">
          <Bell class="w-5 h-5 text-amber-400 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Notificações &amp; Aprimoramento de IA</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Configure canais (Telegram, Discord), eventos monitorados e análise inteligente via OpenRouter.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="savedCard === 'notif'" class="text-xs text-emerald-400 flex items-center gap-1"><Check class="w-3.5 h-3.5" /> Salvo</span>
          <button @click="saveSection('notif')" class="h-8 px-3.5 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-1.5 cursor-pointer">
            <Check class="w-3.5 h-3.5" /> Salvar Notificações &amp; IA
          </button>
        </div>
      </div>

      <!-- Sub-tabs: Canais | Eventos | IA / OpenRouter -->
      <div class="grid grid-cols-3 bg-zinc-900 border border-zinc-800 rounded-lg p-1 text-xs font-semibold">
        <button @click="notifTab = 'channels'" class="py-1.5 rounded-md cursor-pointer transition" :class="notifTab === 'channels' ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white'">
          Canais
        </button>
        <button @click="notifTab = 'events'" class="py-1.5 rounded-md cursor-pointer transition" :class="notifTab === 'events' ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white'">
          Eventos
        </button>
        <button @click="notifTab = 'ai'" class="py-1.5 rounded-md cursor-pointer transition" :class="notifTab === 'ai' ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white'">
          IA (OpenRouter)
        </button>
      </div>

      <!-- Sub-tab: Canais -->
      <div v-if="notifTab === 'channels'" class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 text-xs">
        <div class="p-4 rounded-lg bg-zinc-900/70 border border-zinc-800 space-y-3">
          <div class="font-semibold text-sm text-white">Telegram Bot</div>
          <div class="space-y-1">
            <label class="block text-zinc-400">Bot Token</label>
            <div class="relative">
              <input :value="telegramToken" @input="$emit('update:telegramToken', $event.target.value)" :type="showTgToken ? 'text' : 'password'" placeholder="123456789:ABCdef..." class="w-full bg-zinc-950 border border-zinc-700 rounded-md pl-3 pr-9 py-2 text-white font-mono" />
              <button type="button" @click="showTgToken = !showTgToken" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white cursor-pointer">
                <EyeOff v-if="showTgToken" class="w-3.5 h-3.5" /><Eye v-else class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
          <div class="space-y-1">
            <label class="block text-zinc-400">Chat ID</label>
            <input :value="telegramChatId" @input="$emit('update:telegramChatId', $event.target.value)" type="text" placeholder="-1001234567890" class="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
          </div>
          <button type="button" @click="$emit('test-telegram')" class="w-full py-2 rounded-md bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 font-semibold flex items-center justify-center gap-1.5 cursor-pointer">
            <Send class="w-3.5 h-3.5" /> Testar Telegram
          </button>
        </div>

        <div class="p-4 rounded-lg bg-zinc-900/70 border border-zinc-800 space-y-3">
          <div class="font-semibold text-sm text-white">Discord Webhook</div>
          <div class="space-y-1">
            <label class="block text-zinc-400">Webhook URL</label>
            <div class="relative">
              <input :value="discordWebhook" @input="$emit('update:discordWebhook', $event.target.value)" :type="showDiscordUrl ? 'text' : 'password'" placeholder="https://discord.com/api/webhooks/..." class="w-full bg-zinc-950 border border-zinc-700 rounded-md pl-3 pr-9 py-2 text-white font-mono" />
              <button type="button" @click="showDiscordUrl = !showDiscordUrl" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white cursor-pointer">
                <EyeOff v-if="showDiscordUrl" class="w-3.5 h-3.5" /><Eye v-else class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
          <button type="button" @click="$emit('test-discord')" class="w-full py-2 rounded-md bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 font-semibold flex items-center justify-center gap-1.5 cursor-pointer">
            <Send class="w-3.5 h-3.5" /> Testar Discord
          </button>
        </div>

        <div class="p-4 rounded-lg bg-zinc-900/70 border border-zinc-800 space-y-2.5">
          <div class="font-semibold text-sm text-white">Gotify Server</div>
          <input v-model="settingsData.gotify_url" type="text" placeholder="https://gotify.seu-dominio.com" class="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
          <input v-model="settingsData.gotify_token" type="password" placeholder="App Token Gotify" class="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
        </div>

        <div class="p-4 rounded-lg bg-zinc-900/70 border border-zinc-800 space-y-2.5">
          <div class="font-semibold text-sm text-white">Pushover</div>
          <input v-model="settingsData.pushover_user" type="text" placeholder="User Key" class="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
          <input v-model="settingsData.pushover_token" type="password" placeholder="API Token" class="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
        </div>

        <div class="p-4 rounded-lg bg-zinc-900/70 border border-zinc-800 space-y-2.5">
          <div class="font-semibold text-sm text-white">E-mail (SMTP)</div>
          <div class="grid grid-cols-2 gap-2">
            <input v-model="settingsData.smtp_host" type="text" placeholder="smtp.gmail.com" class="bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
            <input v-model.number="settingsData.smtp_port" type="number" placeholder="587" class="bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
          </div>
          <input v-model="settingsData.smtp_to" type="email" placeholder="alertas@seudominio.com" class="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
        </div>

        <div class="p-4 rounded-lg bg-zinc-900/70 border border-zinc-800 space-y-2.5">
          <div class="font-semibold text-sm text-white">Webhook Genérico / Apprise</div>
          <input v-model="settingsData.webhook_url" type="text" placeholder="https://hooks.exemplo.com/webhook" class="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
          <p class="text-zinc-500">Envia payloads JSON em tempo real para automações externas (n8n, Home Assistant, etc.).</p>
        </div>
      </div>

      <!-- Sub-tab: Eventos -->
      <div v-else-if="notifTab === 'events'" class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
        <div v-for="ev in eventToggles" :key="ev.key" class="flex items-center justify-between p-3 rounded-lg bg-zinc-900/70 border border-zinc-800">
          <div>
            <div class="font-semibold text-white">{{ ev.title }}</div>
            <div class="text-zinc-400">{{ ev.desc }}</div>
          </div>
          <button
            type="button"
            @click="settingsData[ev.key] = !settingsData[ev.key]"
            class="w-10 h-5 rounded-full transition-colors relative cursor-pointer"
            :class="settingsData[ev.key] !== false ? 'bg-blue-600' : 'bg-zinc-700'"
          >
            <span class="block w-4 h-4 rounded-full bg-white transition-transform absolute top-0.5" :class="settingsData[ev.key] !== false ? 'translate-x-5' : 'translate-x-0.5'"></span>
          </button>
        </div>
      </div>

      <!-- Sub-tab: IA -->
      <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 text-xs">
        <div class="space-y-1.5">
          <label class="block text-zinc-300 font-medium">Provedor de IA</label>
          <select v-model="settingsData.ai_provider" class="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white">
            <option value="openrouter">OpenRouter</option>
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic (Claude)</option>
            <option value="gemini">Google Gemini</option>
            <option value="groq">Groq</option>
            <option value="ollama">Ollama (Local)</option>
          </select>
        </div>
        <div class="space-y-1.5">
          <label class="block text-zinc-300 font-medium">Chave da API</label>
          <div class="relative">
            <input :value="aiApiKey" @input="$emit('update:aiApiKey', $event.target.value)" :type="showAiKey ? 'text' : 'password'" placeholder="sk-or-v1-..." class="w-full bg-zinc-950 border border-zinc-700 rounded-md pl-3 pr-9 py-2 text-white font-mono" />
            <button type="button" @click="showAiKey = !showAiKey" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white cursor-pointer">
              <EyeOff v-if="showAiKey" class="w-3.5 h-3.5" /><Eye v-else class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        <div class="space-y-1.5">
          <label class="block text-zinc-300 font-medium">Modelo</label>
          <input :value="aiModel" @input="$emit('update:aiModel', $event.target.value)" type="text" placeholder="nvidia/nemotron-3-nano-30b-a3b:reasoning:free" class="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white font-mono" />
        </div>
      </div>
    </div>

    <!-- 9. GitHub API Token Card (1:1 ProxMenux settings.tsx) -->
    <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-3">
      <div class="flex items-start justify-between gap-4">
        <div>
          <h3 class="text-base font-semibold text-white">Token da API do GitHub</h3>
          <p class="text-xs text-zinc-400 mt-0.5">Evita limite de requisições ao verificar releases e catálogo de apps.</p>
        </div>
        <button @click="saveSection('github')" class="h-8 px-3 text-xs rounded-md bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-1 cursor-pointer">
          <Check class="w-3.5 h-3.5" /> Salvar
        </button>
      </div>
      <input v-model="settingsData.github_token" type="password" placeholder="ghp_..." class="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-xs text-white font-mono" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Globe2, Ruler, Layers, HardDrive, HeartPulse, Network, Database, Bell,
  Settings2, Check, RotateCcw, Eye, EyeOff, Send
} from 'lucide-vue-next'

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
const showAiKey = ref(false)

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
