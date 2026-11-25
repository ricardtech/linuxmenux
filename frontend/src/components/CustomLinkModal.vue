<template>
  <BaseModal :open="open" max-width="max-w-md" @close="$emit('close')">
    <div class="p-6 space-y-4">
      <div class="flex items-center justify-between border-b border-[#2e2e33] pb-3">
        <h3 class="text-base font-bold text-white flex items-center gap-2">
          <Plus class="w-4 h-4 text-blue-400" />
          Adicionar Link Personalizado
        </h3>
        <button @click="$emit('close')" class="text-zinc-400 hover:text-white cursor-pointer text-sm">✕</button>
      </div>
      <div class="space-y-3 text-xs">
        <div>
          <label class="block text-zinc-400 mb-1 font-medium">Nome do App / Serviço *</label>
          <input :value="name" @input="$emit('update:name', $event.target.value)" type="text" placeholder="Ex: Grafana, Portainer..." class="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-white" />
        </div>
        <div>
          <label class="block text-zinc-400 mb-1 font-medium">URL de Acesso *</label>
          <input :value="url" @input="$emit('update:url', $event.target.value)" type="text" placeholder="http://192.168.16.1:3000" class="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-white tabular-nums" />
        </div>
        <div>
          <label class="block text-zinc-400 mb-1 font-medium">Categoria</label>
          <input :value="category" @input="$emit('update:category', $event.target.value)" type="text" placeholder="Geral, Monitoramento, DevOps..." class="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-white" />
        </div>
        <div>
          <label class="block text-zinc-400 mb-1 font-medium">URL do Logo / Ícone (Opcional)</label>
          <input :value="logo" @input="$emit('update:logo', $event.target.value)" type="text" placeholder="https://exemplo.com/logo.png" class="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-white tabular-nums" />
        </div>
      </div>
      <div class="flex items-center justify-end gap-2 pt-3 border-t border-[#2e2e33]">
        <button @click="$emit('close')" class="px-4 py-2 rounded-lg bg-zinc-800 text-zinc-300 hover:bg-zinc-700 text-xs font-medium cursor-pointer">Cancelar</button>
        <button @click="$emit('save')" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow cursor-pointer">Salvar Link</button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { Plus } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'

defineProps({
  open: { type: Boolean, default: false },
  name: { type: String, default: '' },
  url: { type: String, default: '' },
  category: { type: String, default: 'Geral' },
  logo: { type: String, default: '' },
})
defineEmits(['close', 'save', 'update:name', 'update:url', 'update:category', 'update:logo'])
</script>
