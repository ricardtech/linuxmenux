<template>
  <BaseModal :open="open" max-width="max-w-4xl" @close="$emit('close')">
    <div class="flex flex-col">
      <div class="px-6 py-4 border-b border-zinc-800 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3.5">
          <DistroLogo :distro-id="distroId" :distro-name="distroName" />
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-base font-bold text-white">Atualização do sistema Linux</h3>
              <span v-if="distroName" class="text-xs px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-300 border border-blue-500/30 font-semibold">
                {{ distroName }}
              </span>
            </div>
            <p class="text-xs text-zinc-400 mt-0.5">Executa atualização segura de pacotes e limpeza no host em tempo real.</p>
          </div>
        </div>
      </div>
      <div class="p-4 bg-black">
        <div ref="updateTerminalContainer" class="w-full h-96 rounded overflow-hidden"></div>
      </div>
      <div class="px-6 py-3 border-t border-zinc-800 flex items-center justify-between bg-[#1f1f23]">
        <div class="flex items-center gap-2 text-xs tabular-nums">
          <span class="text-zinc-400">&gt;_</span>
          <span class="w-2 h-2 rounded-full"
            :class="wsState === 'online' ? 'bg-emerald-400 animate-pulse' : (wsState === 'connecting' ? 'bg-amber-400 animate-pulse' : 'bg-zinc-500')"></span>
          <span :class="wsState === 'online' ? 'text-emerald-400' : (wsState === 'connecting' ? 'text-amber-400' : 'text-zinc-400')">
            {{ wsState === 'online' ? 'On-line' : (wsState === 'connecting' ? 'Conectando...' : 'Off-line') }}
          </span>
        </div>
        <button @click="$emit('close')" :disabled="wsState === 'online' || wsState === 'connecting'"
          class="px-4 py-1.5 rounded-lg text-xs font-bold transition"
          :class="(wsState === 'online' || wsState === 'connecting') ? 'bg-zinc-800 text-zinc-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 text-white cursor-pointer'">
          Fechar
        </button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref } from 'vue'
import BaseModal from './BaseModal.vue'
import DistroLogo from './DistroLogo.vue'

defineProps({
  open: { type: Boolean, default: false },
  wsState: { type: String, default: 'offline' },
  distroId: { type: String, default: '' },
  distroName: { type: String, default: '' },
})
defineEmits(['close'])

const updateTerminalContainer = ref(null)
defineExpose({ updateTerminalContainer })
</script>
