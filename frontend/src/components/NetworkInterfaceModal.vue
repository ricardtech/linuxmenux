<template>
  <BaseModal :open="open" max-width="max-w-2xl" @close="$emit('close')">
    <div class="p-6 space-y-4">
      <div class="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h3 class="text-base font-bold text-white">{{ detail.name }} - Detalhes da Interface</h3>
          <p class="text-xs text-zinc-400">Informações básicas e contadores de pacotes em tempo real</p>
        </div>
        <button @click="$emit('close')" class="text-zinc-400 hover:text-white cursor-pointer text-lg">✕</button>
      </div>
      <div class="grid grid-cols-2 gap-3 text-xs tabular-nums">
        <div class="p-3 bg-zinc-900 rounded-lg border border-zinc-800"><span class="text-zinc-400">Status:</span> <strong class="text-emerald-400 ml-1">{{ detail.status }}</strong></div>
        <div class="p-3 bg-zinc-900 rounded-lg border border-zinc-800"><span class="text-zinc-400">Velocidade:</span> <strong class="text-white ml-1">{{ detail.speed }}</strong></div>
        <div class="p-3 bg-zinc-900 rounded-lg border border-zinc-800"><span class="text-zinc-400">MAC:</span> <strong class="text-white ml-1">{{ detail.mac }}</strong></div>
        <div class="p-3 bg-zinc-900 rounded-lg border border-zinc-800"><span class="text-zinc-400">MTU / Duplex:</span> <strong class="text-white ml-1">{{ detail.mtu }} / {{ detail.duplex }}</strong></div>
        <div class="p-3 bg-zinc-900 rounded-lg border border-zinc-800"><span class="text-zinc-400">Bytes Recebidos:</span> <strong class="text-emerald-400 ml-1">{{ detail.rx_bytes_formatted }}</strong></div>
        <div class="p-3 bg-zinc-900 rounded-lg border border-zinc-800"><span class="text-zinc-400">Bytes Enviados:</span> <strong class="text-blue-400 ml-1">{{ detail.tx_bytes_formatted }}</strong></div>
        <div class="p-3 bg-zinc-900 rounded-lg border border-zinc-800"><span class="text-zinc-400">Pacotes RX / Erros / Descartes:</span> <strong class="text-white ml-1">{{ detail.rx_packets }} / {{ detail.rx_errors }} / {{ detail.rx_dropped }}</strong></div>
        <div class="p-3 bg-zinc-900 rounded-lg border border-zinc-800"><span class="text-zinc-400">Pacotes TX / Erros / Descartes:</span> <strong class="text-white ml-1">{{ detail.tx_packets }} / {{ detail.tx_errors }} / {{ detail.tx_dropped }}</strong></div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'

defineProps({
  open: { type: Boolean, default: false },
  detail: { type: Object, default: () => ({}) },
})
defineEmits(['close'])
</script>
