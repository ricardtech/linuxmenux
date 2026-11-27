<template>
  <div class="space-y-5 animate-fadeIn">
    <!-- Top 4 KPI Cards (1:1 Image 7) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 tabular-nums">
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 flex flex-col justify-between">
        <div class="flex items-center justify-between text-xs text-zinc-400">
          <span>Total de entradas</span>
          <FileText class="w-4 h-4 text-zinc-500" />
        </div>
        <div class="mt-2">
          <div class="text-3xl font-black text-white">{{ logsData.total || 0 }}</div>
          <div class="text-xs text-zinc-500 mt-0.5">No intervalo selecionado</div>
        </div>
      </div>

      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 flex flex-col justify-between">
        <div class="flex items-center justify-between text-xs text-zinc-400">
          <span>Erros</span>
          <XCircle class="w-4 h-4 text-red-400" />
        </div>
        <div class="mt-2">
          <div class="text-3xl font-black text-red-400">{{ logsData.errors || 0 }}</div>
          <div class="text-xs text-zinc-500 mt-0.5">Requer atenção</div>
        </div>
      </div>

      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 flex flex-col justify-between">
        <div class="flex items-center justify-between text-xs text-zinc-400">
          <span>Avisos</span>
          <AlertTriangle class="w-4 h-4 text-amber-400" />
        </div>
        <div class="mt-2">
          <div class="text-3xl font-black text-amber-400">{{ logsData.warnings || 0 }}</div>
          <div class="text-xs text-zinc-500 mt-0.5">Monitore de perto</div>
        </div>
      </div>

      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 flex flex-col justify-between">
        <div class="flex items-center justify-between text-xs text-zinc-400">
          <span>Cópias de segurança</span>
          <Database class="w-4 h-4 text-blue-400" />
        </div>
        <div class="mt-2">
          <div class="text-3xl font-black text-blue-400">{{ logsData.backups_count ?? (backupData.backups || []).length }}</div>
          <div class="text-xs text-zinc-500 mt-0.5">{{ logsData.backups_size_formatted || '0 B' }}</div>
        </div>
      </div>
    </div>

    <!-- Main Logs & Events Card (1:1 Image 7) -->
    <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-base font-bold text-white flex items-center gap-2">
          <Activity class="w-4 h-4 text-zinc-300" />
          Logs e eventos do sistema
        </h3>
        <button
          @click="$emit('refresh')"
          class="bg-[#141416] hover:bg-zinc-800 border border-zinc-700 text-zinc-200 text-xs px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 cursor-pointer"
        >
          <RefreshCw class="w-3.5 h-3.5" /> Atualizar
        </button>
      </div>

      <!-- 3 Sub-tabs: Registros | Cópias de segurança | Notificações -->
      <div class="grid grid-cols-3 bg-[#141416] border border-zinc-800 rounded-lg p-1 text-xs font-semibold">
        <button
          @click="subTab = 'logs'"
          class="py-1.5 rounded-md transition cursor-pointer flex items-center justify-center gap-1.5"
          :class="subTab === 'logs' ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white'"
        >
          <Terminal class="w-3.5 h-3.5" /> Registros
        </button>
        <button
          @click="subTab = 'backups'"
          class="py-1.5 rounded-md transition cursor-pointer flex items-center justify-center gap-1.5"
          :class="subTab === 'backups' ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white'"
        >
          <Database class="w-3.5 h-3.5" /> Cópias de segurança
        </button>
        <button
          @click="subTab = 'notifications'"
          class="py-1.5 rounded-md transition cursor-pointer flex items-center justify-center gap-1.5"
          :class="subTab === 'notifications' ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white'"
        >
          <Bell class="w-3.5 h-3.5" /> Notificações
        </button>
      </div>

      <!-- Sub-tab 1: Registros -->
      <template v-if="subTab === 'logs'">
        <div class="flex flex-wrap items-center gap-2">
          <div class="relative flex-1 min-w-[200px]">
            <Search class="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              :value="search"
              @input="$emit('update:search', $event.target.value)"
              @keyup.enter="$emit('refresh')"
              type="text"
              placeholder="Pesquisar registros e eventos..."
              class="w-full bg-[#141416] border border-zinc-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <select
            :value="since"
            @change="$emit('update:since', $event.target.value); $emit('refresh')"
            class="bg-[#141416] border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200"
          >
            <option value="1h">1 hora atrás</option>
            <option value="24h">1 dia atrás</option>
            <option value="7d">7 dias atrás</option>
          </select>
          <select
            :value="level"
            @change="$emit('update:level', $event.target.value); $emit('refresh')"
            class="bg-[#141416] border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200"
          >
            <option value="all">Todos os níveis</option>
            <option value="error">Erros</option>
            <option value="warning">Avisos</option>
          </select>
          <select
            :value="unit"
            @change="$emit('update:unit', $event.target.value); $emit('refresh')"
            class="bg-[#141416] border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 max-w-[180px]"
          >
            <option value="all">Todos os serviços</option>
            <option v-for="s in (logsData.services || [])" :key="s" :value="s">{{ s }}</option>
          </select>
          <button
            @click="$emit('export')"
            class="bg-[#141416] hover:bg-zinc-800 border border-zinc-700 text-zinc-200 text-xs px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 cursor-pointer"
          >
            <Download class="w-3.5 h-3.5" /> Exportar registros
          </button>
        </div>

        <div class="max-h-[460px] overflow-y-auto space-y-2 text-xs tabular-nums">
          <div v-for="(entry, idx) in (logsData.entries || [])" :key="idx" class="p-3 bg-[#141416] border border-zinc-800/90 rounded-lg space-y-1">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2 min-w-0">
                <span
                  class="px-2 py-0.5 rounded font-semibold shrink-0"
                  :class="entry.level === 'Erro' ? 'bg-red-500/15 text-red-400' : (entry.level === 'Aviso' ? 'bg-amber-500/15 text-amber-400' : 'bg-blue-500/15 text-blue-400')"
                >
                  {{ entry.level }}
                </span>
                <span class="text-white font-bold truncate">{{ entry.unit }}</span>
              </div>
              <span class="text-zinc-500 shrink-0">{{ entry.timestamp }}</span>
            </div>
            <div class="text-zinc-300 font-mono text-xs break-all">{{ entry.message }}</div>
            <div class="text-xs text-zinc-500">journal · Unidade: {{ entry.unit }} · PID: {{ entry.pid }}</div>
          </div>
        </div>
      </template>

      <!-- Sub-tab 2: Cópias de segurança -->
      <template v-else-if="subTab === 'backups'">
        <div v-if="!(backupData.backups || []).length" class="py-8 text-center text-xs text-zinc-500">
          Nenhuma cópia de segurança registrada ainda.
        </div>
        <div v-else class="space-y-2 text-xs tabular-nums">
          <div v-for="b in backupData.backups" :key="b.name" class="p-3 bg-[#141416] border border-zinc-800 rounded-lg flex items-center justify-between">
            <div>
              <div class="font-bold text-white font-mono">{{ b.name }}</div>
              <div class="text-zinc-500 text-xs">{{ b.created_at }}</div>
            </div>
            <span class="text-emerald-400 font-semibold">{{ b.size_formatted }}</span>
          </div>
        </div>
      </template>

      <!-- Sub-tab 3: Notificações -->
      <template v-else>
        <div class="py-8 text-center text-xs text-zinc-400">
          Histórico de notificações enviadas via Telegram e Discord será exibido aqui após configurar seus canais em Configurações.
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { FileText, XCircle, AlertTriangle, Database, Activity, RefreshCw, Terminal, Bell, Search, Download } from 'lucide-vue-next'

defineProps({
  logsData: { type: Object, required: true },
  backupData: { type: Object, default: () => ({ backups: [] }) },
  search: { type: String, default: '' },
  level: { type: String, default: 'all' },
  since: { type: String, default: '24h' },
  unit: { type: String, default: 'all' },
})

defineEmits(['refresh', 'export', 'update:search', 'update:level', 'update:since', 'update:unit'])

const subTab = ref((() => { try { return localStorage.getItem('linuxmenux-logs-subtab') || 'logs' } catch { return 'logs' } })())
watch(subTab, (v) => { try { localStorage.setItem('linuxmenux-logs-subtab', v) } catch {} })
</script>
