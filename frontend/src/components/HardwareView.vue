<template>
  <section class="space-y-6 animate-fadeIn">
    <div v-if="loading" class="py-16 flex flex-col items-center justify-center gap-3">
      <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-sm text-zinc-400">Detectando CPU, placa-mãe, memória, GPU, sensores térmicos e dispositivos PCI...</p>
    </div>

    <template v-else>
      <!-- 1. Informações do sistema (CPU + Placa-mãe lado a lado — Imagem 12) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-4">
        <h3 class="text-base font-bold text-white flex items-center gap-2">
          <Cpu class="w-4 h-4 text-zinc-300" />
          Informações do sistema
        </h3>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs tabular-nums">
          <!-- CPU -->
          <div class="space-y-2.5">
            <div class="text-zinc-300 font-semibold flex items-center gap-1.5">
              <Cpu class="w-3.5 h-3.5 text-zinc-400" /> CPU
            </div>
            <div class="flex justify-between py-1 border-b border-zinc-800/60"><span class="text-zinc-400">Modelo</span><span class="text-white font-medium">{{ hardwareData.cpu?.model || 'N/D' }}</span></div>
            <div class="flex justify-between py-1 border-b border-zinc-800/60"><span class="text-zinc-400">Núcleos</span><span class="text-white font-medium">{{ hardwareData.cpu?.cores || 0 }} núcleos</span></div>
            <div class="flex justify-between py-1 border-b border-zinc-800/60"><span class="text-zinc-400">Threads</span><span class="text-white font-medium">{{ hardwareData.cpu?.threads || 0 }}</span></div>
            <div class="flex justify-between py-1 border-b border-zinc-800/60"><span class="text-zinc-400">Cache L3</span><span class="text-white font-medium">{{ hardwareData.cpu?.l3_cache || 'N/D' }}</span></div>
            <div class="flex justify-between py-1"><span class="text-zinc-400">Virtualização</span><span class="text-white font-medium">{{ hardwareData.cpu?.virtualization || 'N/D' }}</span></div>
          </div>

          <!-- Placa-mãe -->
          <div class="space-y-2.5">
            <div class="text-zinc-300 font-semibold flex items-center gap-1.5">
              <Server class="w-3.5 h-3.5 text-zinc-400" /> Placa-mãe
            </div>
            <div class="flex justify-between py-1 border-b border-zinc-800/60"><span class="text-zinc-400">Fabricante</span><span class="text-white font-medium">{{ hardwareData.motherboard?.vendor || 'N/D' }}</span></div>
            <div class="flex justify-between py-1 border-b border-zinc-800/60"><span class="text-zinc-400">Modelo</span><span class="text-white font-medium">{{ hardwareData.motherboard?.model || 'N/D' }}</span></div>
            <div class="flex justify-between py-1 border-b border-zinc-800/60"><span class="text-zinc-400">BIOS</span><span class="text-white font-medium">{{ hardwareData.motherboard?.bios_vendor || 'N/D' }}</span></div>
            <div class="flex justify-between py-1 border-b border-zinc-800/60"><span class="text-zinc-400">Versão</span><span class="text-white font-medium">{{ hardwareData.motherboard?.bios_version || 'N/D' }}</span></div>
            <div class="flex justify-between py-1"><span class="text-zinc-400">Data</span><span class="text-white font-medium">{{ hardwareData.motherboard?.bios_date || 'N/D' }}</span></div>
          </div>
        </div>
      </div>

      <!-- 2. Módulos de memória (Imagem 12) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <HardDrive class="w-4 h-4 text-zinc-300" /> Módulos de memória
          </h3>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-zinc-800 border border-zinc-700 text-zinc-300 font-medium tabular-nums">
            {{ (hardwareData.dimms || []).length }} instalado(s)
          </span>
        </div>
        <div v-if="(hardwareData.dimms || []).length === 0" class="text-xs text-zinc-400 p-4 bg-[#141416] rounded-lg border border-zinc-800">
          Total instalado: <strong class="text-white">{{ hardwareData.memory?.total_gb }} GB</strong> (Detalhes de slots DIMM requerem dmidecode com privilégio root).
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs tabular-nums">
          <div v-for="(dimm, idx) in hardwareData.dimms" :key="idx" class="p-4 bg-[#141416] border border-zinc-800 rounded-xl space-y-2">
            <div class="font-bold text-white">{{ dimm.slot }}</div>
            <div class="flex justify-between"><span class="text-zinc-400">Tamanho</span><span class="font-bold text-emerald-400">{{ dimm.size }}</span></div>
            <div class="flex justify-between"><span class="text-zinc-400">Tipo</span><span class="text-white font-medium">{{ dimm.type }}</span></div>
            <div class="flex justify-between"><span class="text-zinc-400">Velocidade</span><span class="text-amber-400 font-medium">{{ dimm.speed }}</span></div>
            <div class="flex justify-between"><span class="text-zinc-400">Fabricante</span><span class="text-white">{{ dimm.manufacturer }}</span></div>
          </div>
        </div>
      </div>

      <!-- 3. Monitoramento Térmico agrupado por CPU / NVME / Outro (Imagem 13) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-5">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <Thermometer class="w-4 h-4 text-zinc-300" /> Monitoramento Térmico
          </h3>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-zinc-800 border border-zinc-700 text-zinc-300 font-medium tabular-nums">
            {{ (hardwareData.sensors || []).length }} sensores
          </span>
        </div>

        <div v-if="!(hardwareData.sensors || []).length" class="text-xs text-zinc-400">Nenhum sensor hwmon detectado.</div>

        <div v-for="grp in sensorGroups" :key="grp.name" class="space-y-3">
          <div class="flex items-center gap-2 text-xs font-semibold text-zinc-300">
            <span>{{ grp.name }}</span>
            <span class="px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 text-xs">{{ grp.items.length }}</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs tabular-nums">
            <div v-for="(s, idx) in grp.items" :key="idx" class="space-y-1.5">
              <div class="flex justify-between">
                <span class="text-white font-medium">{{ s.label }}</span>
                <span class="font-bold" :class="s.temp_c >= 80 ? 'text-red-400' : (s.temp_c >= 65 ? 'text-amber-400' : 'text-emerald-400')">
                  {{ s.temp_c }}°C
                </span>
              </div>
              <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 rounded-full" :style="{ width: `${Math.min(100, s.temp_c)}%` }"></div>
              </div>
              <div class="text-xs text-zinc-500">{{ s.chip }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. Placas Gráficas (Imagem 14) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <Monitor class="w-4 h-4 text-zinc-300" /> Placas Gráficas
          </h3>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-zinc-800 border border-zinc-700 text-zinc-300 font-medium tabular-nums">
            {{ (hardwareData.gpus || []).length }} GPU
          </span>
        </div>
        <div v-if="!(hardwareData.gpus || []).length" class="text-xs text-zinc-400">Nenhuma GPU detectada via lspci.</div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 text-xs tabular-nums">
          <div v-for="g in (hardwareData.gpus || [])" :key="g.slot" class="p-4 bg-[#141416] border border-zinc-800 rounded-xl space-y-3">
            <div class="flex items-start justify-between gap-2">
              <div class="font-bold text-white">{{ g.description }}</div>
              <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-semibold shrink-0">
                {{ g.description.toLowerCase().includes('intel') ? 'Intel' : (g.description.toLowerCase().includes('amd') ? 'AMD' : 'GPU') }}
              </span>
            </div>
            <div class="space-y-1.5">
              <div class="flex justify-between"><span class="text-zinc-400">Tipo</span><span class="text-white">Integrado / PCIe</span></div>
              <div class="flex justify-between"><span class="text-zinc-400">Slot PCI</span><span class="text-white font-mono">{{ g.slot }}</span></div>
              <div class="flex justify-between"><span class="text-zinc-400">Driver</span><span class="text-emerald-400 font-mono">{{ g.driver }}</span></div>
            </div>
            <div class="pt-2 border-t border-zinc-800/80 flex items-center gap-3 text-zinc-400">
              <span class="px-2 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold">GPU</span>
              <span>→</span>
              <span class="text-blue-400 font-medium">Pronto para contêineres Docker</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 5. Consumo de energia (Imagem 15) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-3">
        <h3 class="text-base font-bold text-white flex items-center gap-2">
          <Zap class="w-4 h-4 text-zinc-300" /> Consumo de energia
        </h3>
        <div class="p-4 bg-[#141416] border border-zinc-800 rounded-xl flex items-center justify-between tabular-nums">
          <div>
            <div class="font-bold text-sm text-white">CPU Power</div>
            <div class="text-xs text-zinc-400">Intel RAPL (CPU only)</div>
          </div>
          <div class="text-right">
            <div class="text-xl font-black text-blue-400">
              {{ hardwareData.power?.cpu_watts !== null && hardwareData.power?.cpu_watts !== undefined ? `${hardwareData.power.cpu_watts} W` : 'N/D' }}
            </div>
            <div class="text-xs text-zinc-400">Consumo Atual</div>
          </div>
        </div>
      </div>

      <!-- 6. Dispositivos PCI (Cards em grid 3 colunas — Imagem 15) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <Layers class="w-4 h-4 text-zinc-300" /> Dispositivos PCI
          </h3>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-zinc-800 border border-zinc-700 text-zinc-300 font-medium tabular-nums">
            {{ (hardwareData.pci_devices || []).length }} dispositivos
          </span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs tabular-nums">
          <div v-for="p in (hardwareData.pci_devices || [])" :key="p.slot" class="p-4 bg-[#141416] border border-zinc-800 rounded-xl space-y-2">
            <div class="flex items-center justify-between gap-2">
              <span class="text-xs px-2 py-0.5 rounded font-semibold" :class="pciBadgeClass(p.category)">
                {{ p.category || 'Dispositivo PCI' }}
              </span>
              <span class="text-xs font-mono text-zinc-500">{{ p.slot }}</span>
            </div>
            <div class="font-semibold text-white leading-snug">{{ p.description }}</div>
            <div class="text-emerald-400 font-mono text-xs">Driver: {{ p.driver }}</div>
          </div>
        </div>
      </div>

      <!-- 7. Resumo da rede (1:1 ProxMenux) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <Network class="w-4 h-4 text-zinc-300" /> Resumo da rede
          </h3>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-zinc-800 border border-zinc-700 text-zinc-300 font-medium tabular-nums">
            {{ (hardwareData.network_summary || []).length }} interfaces
          </span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs tabular-nums">
          <div v-for="nic in (hardwareData.network_summary || [])" :key="nic.name" class="p-4 bg-[#141416] border border-zinc-800 rounded-xl space-y-1.5">
            <div class="flex items-center justify-between gap-2">
              <span class="font-bold text-white">{{ nic.name }}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 font-semibold">
                {{ nic.name.startsWith('wl') ? 'Wi-Fi' : 'Ethernet' }}
              </span>
            </div>
            <div class="text-zinc-400 font-mono">{{ nic.ip || 'Sem IP' }} · {{ nic.speed || 'Link ativo' }}</div>
            <div class="text-emerald-400 font-mono">Status: {{ nic.status || 'UP' }}</div>
          </div>
        </div>
      </div>

      <!-- 8. Resumo de armazenamento (1:1 ProxMenux) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <HardDrive class="w-4 h-4 text-zinc-300" /> Resumo de armazenamento
          </h3>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-zinc-800 border border-zinc-700 text-zinc-300 font-medium tabular-nums">
            {{ (hardwareData.storage_summary || []).length }} dispositivos
          </span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs tabular-nums">
          <div v-for="disk in (hardwareData.storage_summary || [])" :key="disk.device" class="p-4 bg-[#141416] border border-zinc-800 rounded-xl space-y-1.5">
            <div class="flex items-center justify-between gap-2">
              <span class="font-bold text-white font-mono">{{ disk.device }}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-purple-500/15 text-purple-400 font-semibold">
                {{ disk.media_type || disk.transport || 'Disco' }}
              </span>
            </div>
            <div class="text-white font-semibold">{{ disk.size_formatted || disk.size }}</div>
            <div class="text-zinc-400 truncate">{{ disk.model }}</div>
          </div>
        </div>
      </div>

      <!-- 9. Dispositivos USB (1:1 ProxMenux) -->
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <Usb class="w-4 h-4 text-zinc-300" /> Dispositivos USB
          </h3>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-zinc-800 border border-zinc-700 text-zinc-300 font-medium tabular-nums">
            {{ (hardwareData.usb_devices || []).length }} dispositivos
          </span>
        </div>
        <div v-if="!(hardwareData.usb_devices || []).length" class="text-xs text-zinc-400">Nenhum dispositivo USB externo detectado.</div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs tabular-nums">
          <div v-for="u in (hardwareData.usb_devices || [])" :key="`${u.bus}-${u.device}`" class="p-4 bg-[#141416] border border-zinc-800 rounded-xl space-y-1.5">
            <div class="flex items-center justify-between gap-2">
              <span class="font-bold text-white truncate">{{ u.description }}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-semibold shrink-0">USB</span>
            </div>
            <div class="text-zinc-400 font-mono">Bus {{ u.bus }} · Dev {{ u.device }} · ID {{ u.usb_id }}</div>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { Cpu, Server, HardDrive, Thermometer, Monitor, Zap, Layers, Network, Usb } from 'lucide-vue-next'

const props = defineProps({
  hardwareData: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
})

const sensorGroups = computed(() => {
  const groups = { CPU: [], NVME: [], Outro: [] }
  for (const s of (props.hardwareData?.sensors || [])) {
    const g = s.group && groups[s.group] ? s.group : 'Outro'
    groups[g].push(s)
  }
  return Object.entries(groups)
    .filter(([, items]) => items.length > 0)
    .map(([name, items]) => ({ name, items }))
})

function pciBadgeClass(cat) {
  if (cat === 'Placa gráfica') return 'bg-emerald-500/15 text-emerald-400'
  if (cat === 'Controlador USB') return 'bg-purple-500/15 text-purple-400'
  if (cat === 'Controlador de armazenamento') return 'bg-amber-500/15 text-amber-400'
  if (cat === 'Controlador de áudio') return 'bg-teal-500/15 text-teal-400'
  if (cat === 'Controlador de rede') return 'bg-blue-500/15 text-blue-400'
  return 'bg-zinc-800 text-zinc-300'
}
</script>
