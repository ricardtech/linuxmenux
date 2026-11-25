<template>
  <section class="space-y-4 animate-fadeIn">
    <!-- Header 1:1 ProxMenux Terminal (+ Novo, Procurar, Limpar, Fechar) -->
    <div class="bg-[#202024] border border-[#2e2e33] rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-sm">
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center gap-2 text-xs tabular-nums">
          <Activity class="w-4 h-4 text-blue-400" />
          <span class="w-2 h-2 rounded-full" :class="connected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'"></span>
          <span class="font-semibold text-zinc-200">{{ activeTabIndex + 1 }} / {{ tabs.length }} terminais</span>
        </div>
        <div class="flex items-center gap-1.5">
          <button
            v-for="(tab, idx) in tabs"
            :key="tab.id"
            @click="activeTabIndex = idx"
            class="px-2.5 py-1 rounded-md text-xs font-medium transition cursor-pointer"
            :class="activeTabIndex === idx ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <button
          @click="addTerminalTab"
          :disabled="tabs.length >= 4"
          class="bg-emerald-600/20 hover:bg-emerald-600/30 disabled:opacity-40 border border-emerald-500/40 text-emerald-300 text-xs font-semibold px-3 py-1.5 rounded-lg transition cursor-pointer flex items-center gap-1.5"
        >
          <Plus class="w-3.5 h-3.5" /> Novo
        </button>
        <button
          @click="showSearch = !showSearch"
          class="bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-300 text-xs font-semibold px-3 py-1.5 rounded-lg transition cursor-pointer flex items-center gap-1.5"
        >
          <Search class="w-3.5 h-3.5" /> Procurar
        </button>
        <button
          @click="$emit('send', 'clear')"
          class="bg-amber-600/20 hover:bg-amber-600/30 border border-amber-500/40 text-amber-300 text-xs font-semibold px-3 py-1.5 rounded-lg transition cursor-pointer flex items-center gap-1.5"
        >
          <Trash2 class="w-3.5 h-3.5" /> Limpar
        </button>
        <button
          @click="closeCurrentTab"
          class="bg-red-600/20 hover:bg-red-600/30 border border-red-500/40 text-red-300 text-xs font-semibold px-3 py-1.5 rounded-lg transition cursor-pointer flex items-center gap-1.5"
        >
          <X class="w-3.5 h-3.5" /> Fechar
        </button>
        <button
          @click="$emit('reconnect')"
          class="bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 text-xs font-semibold px-3 py-1.5 rounded-lg transition cursor-pointer flex items-center gap-1.5"
          title="Reconectar sessão PTY"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': connecting }" />
        </button>
      </div>
    </div>

    <!-- Optional Search Bar -->
    <div v-if="showSearch" class="bg-[#202024] border border-[#2e2e33] rounded-xl px-4 py-2.5 flex items-center gap-2">
      <Search class="w-4 h-4 text-zinc-400 shrink-0" />
      <input
        v-model="searchQuery"
        @keyup.enter="runHistorySearch"
        type="text"
        placeholder="Pesquisar comando no histórico (pressione Enter para buscar com grep)..."
        class="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
      />
      <button @click="runHistorySearch" class="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold cursor-pointer">
        Buscar
      </button>
    </div>

    <!-- Quick Commands -->
    <div class="bg-[#202024] border border-[#2e2e33] rounded-xl p-3 flex items-center gap-2 overflow-x-auto text-xs no-scrollbar shadow-sm">
      <span class="text-zinc-400 font-semibold text-xs uppercase tracking-wider shrink-0 mr-1 tabular-nums">Comandos Rápidos:</span>
      <button @click="$emit('send', 'docker ps')" class="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 px-2.5 py-1 rounded tabular-nums text-xs border border-zinc-700 shrink-0 transition cursor-pointer">docker ps</button>
      <button @click="$emit('send', 'docker stats --no-stream')" class="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 px-2.5 py-1 rounded tabular-nums text-xs border border-zinc-700 shrink-0 transition cursor-pointer">docker stats</button>
      <button @click="$emit('send', 'free -h')" class="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 px-2.5 py-1 rounded tabular-nums text-xs border border-zinc-700 shrink-0 transition cursor-pointer">free -h</button>
      <button @click="$emit('send', 'df -h')" class="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 px-2.5 py-1 rounded tabular-nums text-xs border border-zinc-700 shrink-0 transition cursor-pointer">df -h</button>
      <button @click="$emit('send', 'ip addr show')" class="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 px-2.5 py-1 rounded tabular-nums text-xs border border-zinc-700 shrink-0 transition cursor-pointer">ip a</button>
      <button @click="$emit('send', 'speedtest || speedtest-cli')" class="bg-purple-900/60 hover:bg-purple-800 text-purple-200 px-2.5 py-1 rounded tabular-nums text-xs border border-purple-700/60 shrink-0 transition cursor-pointer font-bold">🚀 speedtest</button>
    </div>

    <!-- Terminal PTY Canvas -->
    <div class="bg-black border border-[#2e2e33] rounded-xl p-3 min-h-[480px] shadow-2xl relative">
      <div class="text-xs text-blue-400 font-semibold mb-2 px-1">{{ tabs[activeTabIndex]?.label || 'Terminal 1' }}</div>
      <div ref="terminalContainer" class="w-full h-[460px]"></div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { Activity, Plus, Search, Trash2, X, RefreshCw } from 'lucide-vue-next'

defineProps({
  connected: { type: Boolean, default: false },
  connecting: { type: Boolean, default: false },
})

const emit = defineEmits(['reconnect', 'send'])

const terminalContainer = ref(null)
const tabs = ref([{ id: 1, label: 'Terminal 1' }])
const activeTabIndex = ref(0)
const showSearch = ref(false)
const searchQuery = ref('')
let nextTabId = 2

function addTerminalTab() {
  if (tabs.value.length >= 4) return
  tabs.value.push({ id: nextTabId, label: `Terminal ${nextTabId}` })
  nextTabId += 1
  activeTabIndex.value = tabs.value.length - 1
  emit('reconnect')
}

function closeCurrentTab() {
  if (tabs.value.length <= 1) {
    emit('send', 'clear')
    return
  }
  tabs.value.splice(activeTabIndex.value, 1)
  activeTabIndex.value = Math.max(0, activeTabIndex.value - 1)
}

function runHistorySearch() {
  if (!searchQuery.value.trim()) return
  emit('send', `history | grep -i "${searchQuery.value.trim()}" | tail -n 20`)
}

defineExpose({ terminalContainer })
</script>
