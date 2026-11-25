<template>
  <BaseModal :open="open" max-width="max-w-4xl" @close="$emit('close')">
    <div class="flex flex-col">
      <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
        <h3 class="text-base font-bold text-white">Logs: {{ title }}</h3>
        <button @click="$emit('close')" class="text-zinc-400 hover:text-white cursor-pointer text-lg">✕</button>
      </div>
      <pre class="p-4 bg-black text-zinc-200 font-mono text-xs h-96 overflow-y-auto whitespace-pre-wrap">{{ logs || 'Sem logs disponíveis.' }}</pre>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  logs: { type: String, default: '' },
})
defineEmits(['close'])
</script>
