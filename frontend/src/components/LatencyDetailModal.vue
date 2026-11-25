<template>
  <BaseModal :open="open" max-width="max-w-2xl" @close="$emit('close')">
    <div class="p-6 space-y-5">
      <div class="flex items-center justify-between border-b border-zinc-800 pb-4">
        <div>
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <Activity class="w-5 h-5 text-blue-400" />
            Latência e Teste de Ping em Tempo Real
          </h3>
          <p class="text-xs text-zinc-400 mt-0.5">Medição ICMP real a partir do host Linux</p>
        </div>
        <button @click="$emit('close')" class="text-zinc-400 hover:text-white cursor-pointer px-2 text-lg">✕</button>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button v-for="host in ['1.1.1.1', '8.8.8.8', '9.9.9.9']" :key="host" @click="runPing(host)"
          class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition cursor-pointer"
          :class="target === host ? 'bg-blue-600 text-white border-blue-500' : 'bg-zinc-900 text-zinc-300 border-zinc-700 hover:bg-zinc-800'">
          {{ host }}
        </button>
        <input v-model="customTarget" @keyup.enter="runPing(customTarget)" type="text" placeholder="Host ou IP customizado"
          class="flex-1 bg-[#141416] border border-zinc-700 rounded-lg px-3 py-1.5 text-xs text-white" />
        <button @click="runPing(customTarget || target)" :disabled="loading"
          class="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold cursor-pointer">
          {{ loading ? 'Testando...' : 'Executar Ping' }}
        </button>
      </div>

      <div class="grid grid-cols-4 gap-3 text-center text-xs tabular-nums">
        <div class="p-3 rounded-xl bg-[#141416] border border-zinc-800">
          <div class="text-zinc-400">Atual</div>
          <div class="text-lg font-bold text-white">{{ result.current_ms ?? '—' }} ms</div>
        </div>
        <div class="p-3 rounded-xl bg-[#141416] border border-zinc-800">
          <div class="text-zinc-400">Média</div>
          <div class="text-lg font-bold text-blue-400">{{ result.avg_ms ?? '—' }} ms</div>
        </div>
        <div class="p-3 rounded-xl bg-[#141416] border border-zinc-800">
          <div class="text-zinc-400">Máxima</div>
          <div class="text-lg font-bold text-amber-400">{{ result.max_ms ?? '—' }} ms</div>
        </div>
        <div class="p-3 rounded-xl bg-[#141416] border border-zinc-800">
          <div class="text-zinc-400">Perda</div>
          <div class="text-lg font-bold" :class="(result.loss_percent || 0) > 0 ? 'text-red-400' : 'text-emerald-400'">{{ result.loss_percent ?? 0 }}%</div>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Activity } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'
import { fetchApi } from '../lib/api-config'

const props = defineProps({
  open: { type: Boolean, default: false },
  initialData: { type: Object, default: () => ({}) },
})
defineEmits(['close'])

const target = ref('1.1.1.1')
const customTarget = ref('')
const loading = ref(false)
const result = ref({})

watch(() => props.open, (val) => {
  if (val) {
    result.value = props.initialData || {}
    runPing(target.value)
  }
})

async function runPing(host) {
  const h = (host || '1.1.1.1').trim()
  target.value = h
  loading.value = true
  try {
    const res = await fetchApi(`/api/network/latency?target=${encodeURIComponent(h)}`)
    if (res.ok) result.value = await res.json()
  } finally {
    loading.value = false
  }
}
</script>
