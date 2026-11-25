<template>
  <section class="space-y-6 animate-fadeIn">
    <!-- Top 4 Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 tabular-nums">
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
        <span class="text-xs font-semibold uppercase tracking-wider text-zinc-400">Armazenamento Total</span>
        <div class="text-3xl font-black text-white mt-2">{{ totalFormatted }}</div>
        <div class="h-1.5 bg-zinc-800 rounded-full mt-3 overflow-hidden">
          <div class="h-full bg-blue-500" :style="{ width: `${totalPercent}%` }"></div>
        </div>
      </div>

      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
        <span class="text-xs font-semibold uppercase tracking-wider text-zinc-400">Usado Localmente</span>
        <div class="text-3xl font-black text-emerald-400 mt-2">{{ totalPercent }}%</div>
        <p class="text-xs text-zinc-400 mt-2">{{ freeFormatted }} livres</p>
      </div>

      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
        <span class="text-xs font-semibold uppercase tracking-wider text-zinc-400">Remoto Usado</span>
        <div class="text-3xl font-black text-zinc-400 mt-2">Nenhum</div>
        <p class="text-xs text-zinc-400 mt-2">Sem NFS/S3 montado</p>
      </div>

      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 shadow-sm">
        <span class="text-xs font-semibold uppercase tracking-wider text-zinc-400">Discos Físicos</span>
        <div class="text-3xl font-black text-white mt-2">{{ disks.length }} discos</div>
        <div class="flex flex-wrap items-center gap-2 mt-2 text-xs text-zinc-400">
          <span v-for="d in disks" :key="d.device" class="text-emerald-400">
            ● {{ d.model }} ({{ d.size_formatted }})
          </span>
        </div>
      </div>
    </div>

    <!-- Discos físicos e status SMART (1:1 Image 3) -->
    <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-base font-bold text-white flex items-center gap-2">
          <HardDrive class="w-4 h-4 text-zinc-300" />
          Discos físicos e status SMART
        </h3>
        <button @click="$emit('refresh-disks')" class="text-xs text-zinc-400 hover:text-white flex items-center gap-1 cursor-pointer">
          <RefreshCw class="w-3.5 h-3.5" /> Atualizar
        </button>
      </div>

      <div v-if="disks.length === 0" class="text-xs text-zinc-400 py-6 text-center">Nenhum disco físico detectado.</div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <button
          v-for="d in disks"
          :key="d.device"
          @click="$emit('open-disk', d)"
          class="text-left p-4 bg-[#141416] hover:bg-zinc-900/90 border border-zinc-800 hover:border-blue-500/40 rounded-xl transition cursor-pointer space-y-3 tabular-nums"
        >
          <!-- Header row -->
          <div class="space-y-1.5">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2 min-w-0">
                <span class="font-bold text-sm text-white truncate">{{ d.device }}</span>
                <span class="text-xs px-2 py-0.5 rounded bg-purple-500/15 text-purple-400 font-semibold">{{ d.media_type }}</span>
              </div>
              <span
                class="text-xs font-bold flex items-center gap-1 shrink-0"
                :class="d.smart_status === 'APROVADO' ? 'text-emerald-400' : (d.smart_status === 'FALHA' ? 'text-red-400' : 'text-zinc-400')"
              >
                ● {{ d.smart_status }}
              </span>
            </div>

            <div class="flex items-center justify-between gap-2">
              <span
                v-if="d.is_system"
                class="text-xs px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30 font-semibold inline-flex items-center gap-1"
              >
                Sistema
              </span>
              <span v-else class="text-xs text-zinc-500">{{ d.transport }}</span>
            </div>

            <div class="flex items-center justify-between pt-1">
              <span class="text-xs text-zinc-400">{{ d.size_formatted }}</span>
              <span
                v-if="d.temperature !== null && d.temperature !== undefined"
                class="text-sm font-bold"
                :class="d.temperature >= 65 ? 'text-red-400' : (d.temperature >= 50 ? 'text-amber-400' : 'text-emerald-400')"
              >
                {{ d.temperature }}°C
              </span>
            </div>
          </div>

          <!-- Detail rows 1:1 Image 3 -->
          <div class="space-y-2 pt-2 border-t border-zinc-800/80 text-xs">
            <div class="flex justify-between gap-2">
              <span class="text-xs uppercase tracking-wider text-zinc-500">MODELO</span>
              <span class="text-zinc-200 font-medium truncate">{{ d.model }}</span>
            </div>

            <div class="space-y-1">
              <div class="flex justify-between gap-2">
                <span class="text-xs uppercase tracking-wider text-zinc-500">NÍVEL DE DESGASTE</span>
                <span class="text-zinc-200 font-bold">{{ d.wear_percent !== null && d.wear_percent !== undefined ? `${d.wear_percent}%` : 'N/D' }}</span>
              </div>
              <div class="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 rounded-full" :style="{ width: `${Math.min(100, Number(d.wear_percent || 0))}%` }"></div>
              </div>
            </div>

            <div class="flex justify-between gap-2">
              <span class="text-xs uppercase tracking-wider text-zinc-500">CICLOS DE ENERGIA</span>
              <span class="text-zinc-200 font-medium">{{ d.power_cycles ?? 'N/D' }}</span>
            </div>

            <div class="flex justify-between gap-2">
              <span class="text-xs uppercase tracking-wider text-zinc-500">LIGAR</span>
              <span class="text-zinc-200 font-medium">{{ d.power_on_formatted || 'N/D' }}</span>
            </div>

            <div class="flex justify-between gap-2">
              <span class="text-xs uppercase tracking-wider text-zinc-500">ERROS CRC</span>
              <span class="font-semibold" :class="(d.crc_errors || 0) === 0 ? 'text-emerald-400' : 'text-red-400'">● {{ d.crc_errors ?? 0 }}</span>
            </div>

            <div class="flex justify-between items-center gap-2 pt-1 border-t border-zinc-800/60">
              <span class="text-xs font-mono text-zinc-500 truncate">S/N: {{ d.serial }}</span>
              <ArrowRight class="w-3.5 h-3.5 text-blue-400 shrink-0" />
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- Montagens reais -->
    <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-4">
      <h3 class="text-base font-bold text-white">Armazenamento Linux &amp; Montagens Reais</h3>
      <div class="space-y-3">
        <div v-for="m in mounts" :key="m.mountpoint" class="p-3 bg-[#141416] border border-zinc-800 rounded-lg space-y-2">
          <div class="flex justify-between items-center text-xs tabular-nums">
            <div class="flex items-center gap-2">
              <span class="font-bold text-white">{{ m.mountpoint }}</span>
              <span
                class="text-xs px-1.5 py-0.5 rounded font-semibold"
                :class="m.fstype === 'btrfs' ? 'bg-blue-500/10 text-blue-400' : (m.fstype === 'vfat' ? 'bg-amber-500/10 text-amber-400' : 'bg-blue-500/10 text-blue-400')"
              >
                {{ m.fstype }}
              </span>
              <span v-if="m.device" class="text-zinc-400 text-xs hidden sm:inline">({{ m.device }})</span>
            </div>
            <span class="text-emerald-400 font-bold">{{ m.percent }}%</span>
          </div>
          <div class="h-2 bg-zinc-800 rounded-full overflow-hidden">
            <div class="h-full bg-blue-500 rounded-full transition-all duration-500" :style="{ width: `${m.percent}%` }"></div>
          </div>
          <div class="flex justify-between text-xs tabular-nums text-zinc-400">
            <span>Usado: {{ m.used_formatted }}</span>
            <span>Total: {{ m.total_formatted }}</span>
            <span>Disponível: {{ m.available_formatted }}</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { HardDrive, RefreshCw, ArrowRight } from 'lucide-vue-next'

defineProps({
  disks: { type: Array, default: () => [] },
  mounts: { type: Array, default: () => [] },
  totalFormatted: { type: String, default: '0 GB' },
  freeFormatted: { type: String, default: '0 GB' },
  totalPercent: { type: Number, default: 0 },
})

defineEmits(['refresh-disks', 'open-disk'])
</script>
