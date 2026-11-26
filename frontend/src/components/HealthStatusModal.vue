<template>
  <BaseModal :open="open" max-width="max-w-3xl" @close="$emit('close')">
    <div class="flex flex-col max-h-[88vh]">
      <div class="flex items-center justify-between px-6 py-4 border-b border-[#2e2e33]">
        <div>
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <ShieldCheck class="w-5 h-5 text-blue-400" />
            Estado de saúde do sistema
            <span class="text-xs px-2 py-0.5 rounded-full font-semibold"
              :class="healthData.health?.overall === 'OK' ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'">
              {{ healthData.health?.overall || 'OK' }}
            </span>
          </h3>
          <p class="text-xs text-zinc-400 mt-0.5">Verificações detalhadas de todos os componentes do sistema</p>
        </div>
        <button @click="$emit('close')" class="text-zinc-400 hover:text-white cursor-pointer text-lg px-2">✕</button>
      </div>

      <div class="p-6 overflow-y-auto space-y-4">
        <div v-if="loading" class="py-12 flex items-center justify-center">
          <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <template v-else>
          <div class="p-3.5 rounded-xl border text-xs flex items-center justify-between gap-2.5"
            :class="healthData.health?.overall === 'OK' ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-300' : 'bg-amber-500/10 border-amber-500/25 text-amber-300'">
            <div class="flex items-center gap-2.5">
              <Info class="w-4 h-4 shrink-0" />
              <span>{{ healthData.health?.summary }}</span>
            </div>
            <button @click="$emit('refresh-updates')" class="px-2.5 py-1 rounded-md bg-zinc-900/70 hover:bg-zinc-800 border border-zinc-700 text-zinc-200 text-xs font-medium flex items-center gap-1.5 cursor-pointer shrink-0">
              <RefreshCw class="w-3.5 h-3.5" /> Verificar agora
            </button>
          </div>

          <!-- Linux Menux - Monitor Self-Update Card -->
          <div class="p-4 rounded-xl border space-y-2.5"
            :class="appUpdateInfo?.update_available?.stable ? 'bg-blue-500/10 border-blue-500/30' : 'bg-zinc-900/70 border-zinc-800'">
            <div class="flex items-center justify-between gap-3 flex-wrap">
              <div>
                <div class="text-sm font-bold text-white flex items-center gap-2">
                  <span>Linux Menux - Monitor</span>
                  <span class="text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono">v{{ appUpdateInfo?.current_version || APP_VERSION }}</span>
                  <span v-if="appUpdateInfo?.update_available?.stable" class="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 font-semibold">
                    Nova versão v{{ appUpdateInfo.latest_version }} disponível
                  </span>
                  <span v-else class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold">
                    Aplicação atualizada
                  </span>
                </div>
                <p class="text-xs text-zinc-400 mt-0.5">
                  {{ appUpdateInfo?.update_available?.stable ? `Publicada em ${appUpdateInfo.published_at || 'GitHub Releases'}` : 'Verificação automática via repositório público GitHub (ricardtech/linuxmenux).' }}
                </p>
              </div>
              <button v-if="appUpdateInfo?.update_available?.stable"
                @click="$emit('self-update')"
                :disabled="appUpdating"
                class="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold flex items-center gap-1.5 cursor-pointer shadow shrink-0">
                <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': appUpdating }" />
                {{ appUpdating ? 'Atualizando...' : `Atualizar para v${appUpdateInfo.latest_version}` }}
              </button>
            </div>
            <div v-if="appUpdateMsg" class="text-xs text-blue-300 bg-blue-950/50 border border-blue-800/60 rounded-lg px-3 py-2">
              {{ appUpdateMsg }}
            </div>
            <div v-if="appUpdateInfo?.update_available?.stable && appUpdateInfo?.release_notes" class="max-h-28 overflow-y-auto bg-zinc-950/70 border border-zinc-800 rounded-lg p-2.5 text-xs text-zinc-300 whitespace-pre-wrap">
              {{ appUpdateInfo.release_notes }}
            </div>
          </div>
          <div class="grid grid-cols-4 gap-3 text-center">
            <div class="bg-zinc-900/80 border border-zinc-800 rounded-xl p-3">
              <div class="text-lg font-bold text-white">{{ healthData.summary_counts?.total || 0 }}</div>
              <div class="text-xs text-zinc-400">Total</div>
            </div>
            <div class="bg-zinc-900/80 border border-zinc-800 rounded-xl p-3">
              <div class="text-lg font-bold text-emerald-400">{{ healthData.summary_counts?.healthy || 0 }}</div>
              <div class="text-xs text-zinc-400">Saudável</div>
            </div>
            <div class="bg-zinc-900/80 border border-zinc-800 rounded-xl p-3">
              <div class="text-lg font-bold text-amber-400">{{ healthData.summary_counts?.warning || 0 }}</div>
              <div class="text-xs text-zinc-400">Aviso</div>
            </div>
            <div class="bg-zinc-900/80 border border-zinc-800 rounded-xl p-3">
              <div class="text-lg font-bold text-red-400">{{ healthData.summary_counts?.critical || 0 }}</div>
              <div class="text-xs text-zinc-400">Crítico</div>
            </div>
          </div>
          <div class="space-y-2.5">
            <div v-for="cat in (healthData.categories || [])" :key="cat.id" class="bg-zinc-900/70 border border-zinc-800 rounded-xl overflow-hidden">
              <button @click="$emit('update:expandedCat', expandedCat === cat.id ? '' : cat.id)"
                class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-zinc-800/50 transition cursor-pointer">
                <div class="flex items-center gap-2.5">
                  <component :is="categoryIcon(cat.id)" class="w-4 h-4 text-blue-400 shrink-0" />
                  <CheckCircle2 v-if="cat.status === 'OK'" class="w-4 h-4 text-emerald-400 shrink-0" />
                  <AlertTriangle v-else-if="cat.status === 'Advertências'" class="w-4 h-4 text-amber-400 shrink-0" />
                  <XCircle v-else class="w-4 h-4 text-red-400 shrink-0" />
                  <span class="text-sm font-semibold text-zinc-100">{{ cat.title }}</span>
                  <span class="text-xs text-zinc-500">({{ (cat.items || []).length }})</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold border"
                    :class="cat.status === 'OK' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : (cat.status === 'Crítico' ? 'bg-red-500/10 text-red-400 border-red-500/30' : 'bg-amber-500/10 text-amber-400 border-amber-500/30')">
                    {{ cat.status }}
                  </span>
                  <ChevronDown v-if="expandedCat === cat.id" class="w-4 h-4 text-zinc-400" />
                  <ChevronRight v-else class="w-4 h-4 text-zinc-400" />
                </div>
              </button>
              <div v-if="expandedCat === cat.id" class="px-4 pb-4 pt-2 border-t border-zinc-800/70 space-y-2 text-xs">
                <div v-for="(item, idx) in cat.items" :key="idx" class="flex items-center justify-between gap-4 py-1">
                  <div class="flex items-center gap-2.5 min-w-0">
                    <CheckCircle2 v-if="item.ok" class="w-4 h-4 text-emerald-500 shrink-0" />
                    <AlertTriangle v-else class="w-4 h-4 text-amber-400 shrink-0" />
                    <span class="text-zinc-200 font-medium">{{ item.label }}</span>
                    <span class="text-zinc-400 truncate">{{ item.detail }}</span>
                  </div>
                </div>
                <div v-if="cat.id === 'updates' && cat.pending_count > 0" class="pt-3 border-t border-zinc-800 space-y-3">
                  <div class="flex items-center justify-between gap-3 bg-zinc-950/60 border border-zinc-800 rounded-lg p-3">
                    <div class="flex items-center gap-3">
                      <DistroLogo :distro-id="distroId" :distro-name="distroName" />
                      <div>
                        <div class="text-sm font-semibold text-white">{{ distroName || 'Sistema Linux' }}</div>
                        <div class="text-xs text-zinc-400">{{ cat.pending_count }} pacote(s) prontos para atualização</div>
                      </div>
                    </div>
                    <button @click="$emit('open-update')" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold flex items-center gap-2 cursor-pointer shadow shrink-0">
                      <RefreshCw class="w-4 h-4" /> Sistema de atualização
                    </button>
                  </div>
                  <div class="max-h-36 overflow-y-auto bg-zinc-950/70 border border-zinc-800 rounded-lg p-2.5 tabular-nums text-xs space-y-1">
                    <div v-for="pkg in (cat.packages || []).slice(0, 20)" :key="pkg.name" class="flex justify-between text-zinc-300">
                      <span>{{ pkg.name }}</span>
                      <span class="text-zinc-400">{{ pkg.old_version }} → {{ pkg.new_version }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <div class="px-6 py-3 border-t border-[#2e2e33] text-center text-xs text-zinc-400">
        Última atualização: {{ formattedTimestamp }} · Cache de verificação de pacotes: 5 minutos
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import {
  ShieldCheck, Info, RefreshCw, CheckCircle2, AlertTriangle, XCircle,
  Cpu, MemoryStick, HardDrive, Network, Thermometer, ChevronDown, ChevronRight
} from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'
import DistroLogo from './DistroLogo.vue'
import { APP_VERSION } from '../lib/version'

const props = defineProps({
  open: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  healthData: { type: Object, default: () => ({}) },
  expandedCat: { type: String, default: 'updates' },
  distroId: { type: String, default: '' },
  distroName: { type: String, default: '' },
  appUpdateInfo: { type: Object, default: () => ({}) },
  appUpdating: { type: Boolean, default: false },
  appUpdateMsg: { type: String, default: '' },
})
defineEmits(['close', 'open-update', 'refresh-updates', 'self-update', 'update:expandedCat'])

function categoryIcon(id) {
  switch (id) {
    case 'cpu': return Cpu
    case 'memory': return MemoryStick
    case 'storage': return HardDrive
    case 'network': return Network
    case 'temperature': return Thermometer
    case 'updates': return RefreshCw
    default: return ShieldCheck
  }
}

const formattedTimestamp = computed(() => {
  const ts = props.healthData?.health?.timestamp
  if (!ts) return new Date().toLocaleString('pt-BR')
  try {
    const d = typeof ts === 'number' ? new Date(ts > 1e12 ? ts : ts * 1000) : new Date(ts)
    if (Number.isNaN(d.getTime())) return new Date().toLocaleString('pt-BR')
    return d.toLocaleString('pt-BR')
  } catch {
    return new Date().toLocaleString('pt-BR')
  }
})
</script>
