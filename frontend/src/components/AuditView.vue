<template>
  <section class="space-y-4 animate-fadeIn">
    <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-4">
      <!-- Header + Actions -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h4 class="text-base font-bold text-white">Auditoria de Conformidade &amp; Relatórios (Linux / Docker)</h4>
          <p class="text-xs text-zinc-400">Verificação contínua de segurança, backups, rede e integridade do host.</p>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <button @click="printReport" class="bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 text-xs px-3 py-1.5 rounded-lg font-semibold cursor-pointer">
            Imprimir / PDF
          </button>
          <button @click="$emit('run-audit')" class="bg-blue-600 hover:bg-blue-500 text-white text-xs px-3.5 py-1.5 rounded-lg font-semibold cursor-pointer">
            Executar relatório
          </button>
        </div>
      </div>

      <!-- Sub-tabs (1:1 ProxMenux Audit Report) -->
      <div class="flex flex-wrap gap-1.5 border-b border-zinc-800 pb-3 text-xs">
        <button v-for="t in ['report', 'inventory', 'policy']" :key="t" @click="subTab = t"
          class="px-3 py-1.5 rounded-lg font-medium transition cursor-pointer"
          :class="subTab === t ? 'bg-blue-600 text-white' : 'bg-zinc-900 text-zinc-400 hover:text-zinc-200'">
          {{ t === 'report' ? 'Relatório' : (t === 'inventory' ? 'Inventário do Host' : 'Política & Critérios') }}
        </button>
      </div>

      <!-- TAB 1: Report -->
      <template v-if="subTab === 'report'">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="flex flex-wrap gap-2 text-xs tabular-nums">
            <span class="px-2.5 py-1 rounded bg-emerald-500/15 text-emerald-400 font-semibold">Conforme: {{ auditData.counts?.compliant || 0 }}</span>
            <span class="px-2.5 py-1 rounded bg-amber-500/15 text-amber-400 font-semibold">Observações: {{ auditData.counts?.observation || 0 }}</span>
            <span class="px-2.5 py-1 rounded bg-zinc-800 text-zinc-300 font-semibold">Não aplicável: {{ auditData.counts?.na || 0 }}</span>
          </div>
          <div class="flex gap-1.5 text-xs">
            <button v-for="f in ['all', 'compliant', 'observation']" :key="f" @click="statusFilter = f"
              class="px-2.5 py-1 rounded border transition cursor-pointer"
              :class="statusFilter === f ? 'bg-blue-600/20 border-blue-500/40 text-blue-300 font-semibold' : 'bg-zinc-900 border-zinc-800 text-zinc-400'">
              {{ f === 'all' ? 'Todos' : (f === 'compliant' ? 'Conformes' : 'Observações') }}
            </button>
          </div>
        </div>

        <div class="space-y-2 text-xs">
          <div v-for="item in filteredItems" :key="item.id" class="p-3.5 bg-[#141416] border border-zinc-800 rounded-xl flex justify-between items-center gap-3">
            <div>
              <div class="font-bold text-white">{{ item.title }} <span class="text-zinc-400 font-mono text-xs">[{{ item.category }}]</span></div>
              <div class="text-zinc-400 mt-0.5">{{ item.detail }}</div>
            </div>
            <span class="px-2.5 py-0.5 rounded-full font-semibold shrink-0" :class="item.status === 'compliant' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-amber-500/15 text-amber-400'">
              {{ item.status === 'compliant' ? 'Conforme' : 'Observação' }}
            </span>
          </div>
        </div>
      </template>

      <!-- TAB 2: Host Inventory -->
      <template v-else-if="subTab === 'inventory'">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
          <div class="p-4 rounded-xl bg-[#141416] border border-zinc-800 space-y-1">
            <div class="text-zinc-400">Sistema Operacional</div>
            <div class="font-bold text-white">{{ auditData.hostname || 'Host Linux' }}</div>
            <div class="text-zinc-500">Auditoria contínua Linux / Docker</div>
          </div>
          <div class="p-4 rounded-xl bg-[#141416] border border-zinc-800 space-y-1">
            <div class="text-zinc-400">Verificações Ativas</div>
            <div class="font-bold text-blue-400">{{ (auditData.items || []).length }} itens avaliados</div>
            <div class="text-zinc-500">Sem dependência de VM/LXC</div>
          </div>
          <div class="p-4 rounded-xl bg-[#141416] border border-zinc-800 space-y-1">
            <div class="text-zinc-400">Última Execução</div>
            <div class="font-bold text-emerald-400">{{ auditData.timestamp || 'Atualizado agora' }}</div>
            <div class="text-zinc-500">Formato BR</div>
          </div>
        </div>
      </template>

      <!-- TAB 3: Policy -->
      <template v-else>
        <div class="p-4 rounded-xl bg-[#141416] border border-zinc-800 text-xs text-zinc-300 space-y-2">
          <div class="font-bold text-white">Política de Conformidade Linux Menux</div>
          <p class="text-zinc-400">Avalia automaticamente cobertura de backup local/remoto, firewall ativo, acesso SSH root, proteção Fail2Ban, atualizações pendentes e capacidade das partições.</p>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  auditData: { type: Object, default: () => ({ items: [], counts: {} }) },
})
defineEmits(['run-audit'])

const subTab = ref('report')
const statusFilter = ref('all')

const filteredItems = computed(() => {
  const list = props.auditData?.items || []
  if (statusFilter.value === 'all') return list
  return list.filter((i) => i.status === statusFilter.value)
})

function printReport() {
  if (typeof window !== 'undefined') window.print()
}
</script>
