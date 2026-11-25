<template>
  <BaseModal :open="open" max-width="max-w-md" @close="$emit('close')">
    <div class="p-6 space-y-4">
      <div class="flex items-center justify-between border-b border-zinc-800 pb-3">
        <h3 class="text-base font-bold text-white">Perfil de usuário</h3>
        <button @click="$emit('close')" class="text-zinc-400 hover:text-white cursor-pointer">✕</button>
      </div>
      <div class="space-y-2 text-xs tabular-nums">
        <div class="flex justify-between py-1 border-b border-zinc-800"><span class="text-zinc-400">Usuário:</span><span class="text-white font-bold">AlaxRicard</span></div>
        <div class="flex justify-between py-1 border-b border-zinc-800"><span class="text-zinc-400">Nome de exibição:</span><span class="text-white">Alax Ricard</span></div>
      </div>
      <button @click="$emit('open-security')" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg text-xs font-bold cursor-pointer">
        Abrir configurações de segurança
      </button>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'

defineProps({ open: { type: Boolean, default: false } })
defineEmits(['close', 'open-security'])
</script>
