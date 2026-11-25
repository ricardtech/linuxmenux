<template>
  <BaseModal :open="open" max-width="max-w-lg" @close="$emit('close')">
    <div class="p-6 space-y-4">
      <div class="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h3 class="text-base font-bold text-white">Nós vinculados</h3>
          <p class="text-xs text-zinc-400">Adicione servidores locais, remotos ou via Túnel Cloudflare.</p>
        </div>
        <button @click="$emit('close')" class="text-zinc-400 hover:text-white cursor-pointer">✕</button>
      </div>
      <div class="space-y-2.5 text-xs">
        <input :value="name" @input="$emit('update:name', $event.target.value)" type="text" placeholder="Nome (ex: srv01br)" class="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-white" />
        <input :value="url" @input="$emit('update:url', $event.target.value)" type="text" placeholder="Endereço (ex: https://monitor.exemplo.com)" class="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-white tabular-nums" />
        <label class="flex items-center gap-2 text-zinc-300">
          <input :checked="tunnel" @change="$emit('update:tunnel', $event.target.checked)" type="checkbox" />
          Aponta para túnel externo (Cloudflare / Tailscale)
        </label>
        <button @click="$emit('save')" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg font-bold cursor-pointer">+ Adicionar Nó</button>
      </div>
      <div class="space-y-1.5 text-xs tabular-nums max-h-40 overflow-y-auto">
        <div v-for="n in nodes.filter(x => !x.local)" :key="n.id" class="flex justify-between items-center p-2 bg-zinc-900 rounded border border-zinc-800">
          <span>{{ n.name }} ({{ n.url }})</span>
          <button @click="$emit('remove', n.id)" class="text-red-400 hover:text-red-300 cursor-pointer">Remover</button>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'

defineProps({
  open: { type: Boolean, default: false },
  nodes: { type: Array, default: () => [] },
  name: { type: String, default: '' },
  url: { type: String, default: '' },
  tunnel: { type: Boolean, default: false },
})
defineEmits(['close', 'save', 'remove', 'update:name', 'update:url', 'update:tunnel'])
</script>
