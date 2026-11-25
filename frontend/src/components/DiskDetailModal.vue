<template>
  <BaseModal :open="open && !!disk" max-width="max-w-3xl" @close="$emit('close')">
    <div v-if="disk" class="flex flex-col max-h-[88vh]">
      <!-- Header 1:1 with ProxMenux Disk Detail Modal -->
      <div class="flex items-start justify-between px-6 pt-5 pb-3">
        <div>
          <div class="flex items-center gap-2.5 flex-wrap">
            <HardDrive class="w-5 h-5 text-zinc-300" />
            <h3 class="text-base font-bold text-white">Detalhes do disco: {{ disk.device }}</h3>
            <span
              v-if="disk.is_system"
              class="text-xs px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30 font-semibold"
            >
              Sistema
            </span>
          </div>
          <p class="text-xs text-zinc-400 mt-0.5">{{ disk.model }} · {{ disk.size_formatted }}</p>
        </div>
        <button
          @click="$emit('close')"
          class="text-zinc-400 hover:text-white cursor-pointer text-base px-1.5 py-1 rounded-md hover:bg-zinc-800"
          title="Fechar (Esc)"
        >
          ✕
        </button>
      </div>

      <!-- 4 Tabs: Visão geral | SMART | História | Agendar -->
      <div class="flex items-center gap-5 px-6 border-b border-[#2e2e33] text-xs font-semibold">
        <button
          v-for="t in tabs"
          :key="t.id"
          @click="$emit('change-tab', t.id)"
          class="pb-2.5 border-b-2 transition cursor-pointer flex items-center gap-1.5"
          :class="activeTab === t.id ? 'border-blue-500 text-blue-400' : 'border-transparent text-zinc-400 hover:text-white'"
        >
          <component :is="t.icon" class="w-3.5 h-3.5" />
          {{ t.label }}
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto space-y-5 text-xs">
        <!-- TAB 1: Visão geral (1:1 Image 4) -->
        <template v-if="activeTab === 'overview'">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 tabular-nums">
            <div class="space-y-1">
              <div class="text-zinc-400">Modelo</div>
              <div class="font-bold text-sm text-white">{{ disk.model }}</div>
            </div>
            <div class="space-y-1">
              <div class="text-zinc-400">Número de série</div>
              <div class="font-bold text-sm text-white font-mono">{{ disk.serial }}</div>
            </div>
            <div class="space-y-1">
              <div class="text-zinc-400">Capacidade</div>
              <div class="font-bold text-sm text-white">{{ disk.size_formatted }}</div>
            </div>
            <div class="space-y-1">
              <div class="text-zinc-400">Estado de saúde</div>
              <div>
                <span
                  class="inline-block text-xs px-2.5 py-0.5 rounded font-semibold"
                  :class="disk.smart_status === 'APROVADO' ? 'bg-emerald-500/15 text-emerald-400' : (disk.smart_status === 'FALHA' ? 'bg-red-500/15 text-red-400' : 'bg-zinc-700 text-zinc-300')"
                >
                  {{ disk.smart_status === 'APROVADO' ? 'Saudável' : disk.smart_status }}
                </span>
              </div>
            </div>
          </div>

          <div class="pt-2 border-t border-[#2e2e33] space-y-1">
            <div class="text-zinc-400">Controlador de armazenamento</div>
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-bold text-sm text-white">{{ disk.controller || disk.transport }}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono uppercase">{{ disk.media_type }}</span>
            </div>
          </div>

          <!-- Desgaste e vida útil -->
          <div class="pt-3 border-t border-[#2e2e33] space-y-3">
            <h4 class="text-sm font-bold text-white">Desgaste e vida útil</h4>
            <div class="flex items-center gap-5">
              <div class="relative w-16 h-16 shrink-0">
                <svg class="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
                  <circle cx="18" cy="18" r="15.5" fill="none" stroke="#27272a" stroke-width="3" />
                  <circle
                    cx="18" cy="18" r="15.5" fill="none"
                    :stroke="lifePercent >= 50 ? '#22c55e' : (lifePercent >= 20 ? '#f59e0b' : '#ef4444')"
                    stroke-width="3" stroke-linecap="round"
                    :stroke-dasharray="`${Math.min(100, lifePercent) * 0.974} 100`"
                  />
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center leading-tight">
                  <span class="text-xs font-bold text-emerald-400">{{ lifePercent }}%</span>
                  <span class="text-xs text-zinc-400">vida</span>
                </div>
              </div>

              <div class="flex-1 space-y-2 tabular-nums">
                <div class="flex justify-between">
                  <span class="text-zinc-400">Desgaste utilizado</span>
                  <span class="font-bold text-white">{{ wearPercent }}%</span>
                </div>
                <div class="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
                  <div class="h-full bg-blue-500 rounded-full" :style="{ width: `${Math.min(100, wearPercent)}%` }"></div>
                </div>
                <div class="grid grid-cols-2 gap-3 pt-1">
                  <div>
                    <div class="text-zinc-400">Tempo ligado</div>
                    <div class="font-bold text-white">{{ disk.power_on_formatted || 'N/D' }}</div>
                  </div>
                  <div>
                    <div class="text-zinc-400">Dados escritos</div>
                    <div class="font-bold text-white">{{ disk.data_written_formatted || 'N/D' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- TAB 2: SMART -->
        <template v-else-if="activeTab === 'smart'">
          <div v-if="!smartDetail.installed" class="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl space-y-3">
            <div class="font-bold text-amber-300">As ferramentas SMART não estão instaladas</div>
            <p class="text-zinc-300">smartmontools / nvme-cli são necessários para executar testes SMART neste host.</p>
            <button @click="$emit('install-smart')" :disabled="smartInstalling" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg font-bold cursor-pointer">
              {{ smartInstalling ? 'Instalando ferramentas SMART...' : 'Instalar ferramentas SMART' }}
            </button>
          </div>
          <template v-else>
            <div class="flex gap-2">
              <button @click="$emit('run-smart', 'short')" class="bg-blue-600 hover:bg-blue-500 text-white px-3.5 py-2 rounded-lg font-semibold cursor-pointer">Teste curto</button>
              <button @click="$emit('run-smart', 'extended')" class="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 px-3.5 py-2 rounded-lg font-semibold cursor-pointer">Teste estendido</button>
            </div>
            <div class="max-h-60 overflow-y-auto border border-[#2e2e33] rounded-lg">
              <table class="w-full text-left tabular-nums text-xs">
                <thead class="bg-[#141416] text-zinc-400">
                  <tr><th class="p-2.5">Atributo</th><th class="p-2.5">Valor</th><th class="p-2.5">Status</th></tr>
                </thead>
                <tbody class="divide-y divide-[#2e2e33] text-zinc-300">
                  <tr v-for="(a, i) in (smartDetail.attributes || [])" :key="i">
                    <td class="p-2.5">{{ a.name }}</td>
                    <td class="p-2.5 font-mono">{{ a.value }}</td>
                    <td class="p-2.5 text-emerald-400">{{ a.status }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </template>

        <!-- TAB 3: História -->
        <template v-else-if="activeTab === 'history'">
          <div v-if="!smartHistory.length" class="text-zinc-400 py-8 text-center">Sem histórico de testes SMART ainda.</div>
          <div v-else class="space-y-2 tabular-nums">
            <div v-for="(h, i) in smartHistory" :key="i" class="p-3 bg-[#141416] rounded-lg border border-[#2e2e33] flex justify-between">
              <span class="font-medium text-white">{{ h.device }} · {{ h.mode }}</span>
              <span class="text-zinc-400">{{ h.timestamp }} ({{ h.status }})</span>
            </div>
          </div>
        </template>

        <!-- TAB 4: Agendar -->
        <template v-else-if="activeTab === 'schedule'">
          <div class="flex gap-2">
            <input
              :value="cronValue"
              @input="$emit('update:cronValue', $event.target.value)"
              type="text"
              placeholder="0 3 * * 0"
              class="flex-1 bg-[#141416] border border-zinc-700 rounded-lg px-3 py-1.5 text-white font-mono"
            />
            <button @click="$emit('add-schedule')" class="bg-blue-600 hover:bg-blue-500 text-white px-3.5 py-1.5 rounded-lg font-semibold cursor-pointer">
              + Adicionar programação
            </button>
          </div>
          <div class="space-y-2">
            <div v-for="s in (smartSchedules.items || [])" :key="s.id" class="p-3 bg-[#141416] rounded-lg border border-[#2e2e33] flex justify-between tabular-nums">
              <span class="text-zinc-200">{{ s.device }} ({{ s.mode }})</span>
              <span class="text-blue-400 font-mono">{{ s.cron }}</span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import { HardDrive, Info, Activity, History, Clock } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  disk: { type: Object, default: null },
  activeTab: { type: String, default: 'overview' },
  smartDetail: { type: Object, default: () => ({}) },
  smartHistory: { type: Array, default: () => [] },
  smartSchedules: { type: Object, default: () => ({ items: [] }) },
  smartInstalling: { type: Boolean, default: false },
  cronValue: { type: String, default: '0 3 * * 0' },
})

defineEmits(['close', 'change-tab', 'install-smart', 'run-smart', 'add-schedule', 'update:cronValue'])

const tabs = [
  { id: 'overview', label: 'Visão geral', icon: Info },
  { id: 'smart', label: 'SMART', icon: Activity },
  { id: 'history', label: 'História', icon: History },
  { id: 'schedule', label: 'Agendar', icon: Clock },
]

const wearPercent = computed(() => {
  const w = Number(props.disk?.wear_percent ?? 0)
  return Number.isFinite(w) ? Math.max(0, Math.min(100, w)) : 0
})

const lifePercent = computed(() => Math.max(0, 100 - wearPercent.value))
</script>
