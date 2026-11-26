<template>
  <section class="space-y-5 animate-fadeIn">
    <!-- Top Header (1:1 ProxMenux Audit & Report - Imagem 1) -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div class="flex items-center gap-2.5">
        <ClipboardCheck class="w-6 h-6 text-zinc-200" />
        <h1 class="text-2xl font-bold text-white">Audit &amp; Report</h1>
      </div>

      <div class="flex flex-wrap items-center gap-2.5 text-xs">
        <div class="flex items-center gap-2">
          <span class="text-zinc-400">Report</span>
          <select v-model="reportMode" class="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-1.5 text-zinc-200">
            <option value="full">Full audit</option>
            <option value="summary">Resumo executivo</option>
          </select>
        </div>

        <button @click="printReport" class="px-3.5 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-200 font-semibold flex items-center gap-1.5 cursor-pointer">
          <FileText class="w-3.5 h-3.5" /> Gerar relatório
        </button>

        <div class="flex items-center bg-zinc-950 border border-zinc-800 rounded-lg p-1 gap-1">
          <button v-for="t in [{ id: 'report', label: 'Assessment' }, { id: 'changes', label: 'Alterações' }, { id: 'policy', label: 'Política' }]"
            :key="t.id" @click="subTab = t.id"
            class="px-3 py-1 rounded-md font-semibold transition cursor-pointer"
            :class="subTab === t.id ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-white'">
            {{ t.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- TAB 1: Assessment (1:1 ProxMenux) -->
    <template v-if="subTab === 'report'">
      <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div class="space-y-1.5">
            <div class="text-xs font-semibold text-zinc-200">
              Last assessed on {{ auditData.timestamp || currentTimestampBr }}
            </div>
            <p class="text-xs text-zinc-400 max-w-3xl">
              A avaliação inspeciona as configurações e a integridade do host Linux, containers Docker, firewall, armazenamento SMART, rede e cobertura de backups.
            </p>
          </div>
          <button @click="$emit('run-audit')" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold flex items-center gap-1.5 cursor-pointer shrink-0">
            <Play class="w-3.5 h-3.5" /> Run assessment
          </button>
        </div>

        <!-- Status Summary Pills -->
        <div class="flex flex-wrap items-center gap-2 text-xs">
          <button @click="statusFilter = statusFilter === 'observation' ? 'all' : 'observation'"
            class="px-3 py-1 rounded-full border font-semibold flex items-center gap-1.5 cursor-pointer transition"
            :class="statusFilter === 'observation' ? 'bg-blue-600/25 border-blue-500 text-blue-300' : 'bg-blue-500/10 border-blue-500/30 text-blue-400'">
            <Info class="w-3.5 h-3.5" /> Observação {{ auditData.counts?.observation || 0 }}
          </button>
          <button @click="statusFilter = statusFilter === 'compliant' ? 'all' : 'compliant'"
            class="px-3 py-1 rounded-full border font-semibold flex items-center gap-1.5 cursor-pointer transition"
            :class="statusFilter === 'compliant' ? 'bg-emerald-600/25 border-emerald-500 text-emerald-300' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'">
            <CheckCircle2 class="w-3.5 h-3.5" /> Conforme {{ auditData.counts?.compliant || 0 }}
          </button>
          <span class="px-3 py-1 rounded-full border bg-zinc-900 border-zinc-700 text-zinc-400 font-semibold flex items-center gap-1.5">
            <MinusCircle class="w-3.5 h-3.5" /> Não aplicável {{ auditData.counts?.na || 0 }}
          </span>
        </div>

        <div class="space-y-2 pt-1">
          <div class="text-xs text-zinc-400">
            {{ baselineSaved ? `Referência salva em ${baselineTimestamp} para comparação de desvios.` : 'Ainda não foi escolhida uma execução de referência, pelo que não há com que comparar.' }}
          </div>
          <button @click="saveBaseline" class="px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-200 text-xs font-semibold flex items-center gap-1.5 cursor-pointer">
            <Flag class="w-3.5 h-3.5" /> Usar como referência
          </button>
        </div>

        <!-- Category Filter Pills (1:1 ProxMenux adapted for Linux) -->
        <div class="flex flex-wrap gap-1.5 pt-2 border-t border-zinc-800/80 text-xs">
          <button v-for="cat in categories" :key="cat.id" @click="categoryFilter = cat.id"
            class="px-3 py-1.5 rounded-lg font-medium transition cursor-pointer"
            :class="categoryFilter === cat.id ? 'bg-blue-600 text-white font-semibold' : 'bg-zinc-900/70 text-zinc-400 hover:text-white'">
            {{ cat.label }}
          </button>
        </div>
      </div>

      <!-- Expandable Findings List (1:1 ProxMenux) -->
      <div class="space-y-2.5">
        <div v-if="!filteredItems.length" class="p-6 text-center text-xs text-zinc-500 bg-[var(--card)] border border-zinc-800 rounded-xl">
          Nenhum achado para o filtro selecionado. Clique em <strong>Run assessment</strong> para atualizar a auditoria.
        </div>
        <div v-for="item in filteredItems" :key="item.id" class="bg-[var(--card)] border border-zinc-800/90 rounded-xl overflow-hidden">
          <button @click="toggleItem(item.id)" class="w-full px-5 py-3.5 flex items-center justify-between gap-4 text-left hover:bg-zinc-800/30 transition cursor-pointer">
            <div class="flex items-start gap-3 min-w-0">
              <ChevronDown v-if="expandedItems[item.id]" class="w-4 h-4 text-zinc-400 mt-0.5 shrink-0" />
              <ChevronRight v-else class="w-4 h-4 text-zinc-400 mt-0.5 shrink-0" />
              <div class="space-y-1 min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold border flex items-center gap-1"
                    :class="item.status === 'compliant' ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' : 'bg-blue-500/15 text-blue-400 border-blue-500/30'">
                    <CheckCircle2 v-if="item.status === 'compliant'" class="w-3 h-3" />
                    <Info v-else class="w-3 h-3" />
                    {{ item.status === 'compliant' ? 'Conforme' : 'Observação' }}
                  </span>
                  <span class="text-sm font-bold text-white">{{ item.title }}</span>
                  <span class="text-xs px-2 py-0.5 rounded bg-zinc-900 border border-zinc-700 text-zinc-300 font-medium">{{ item.category }}</span>
                </div>
                <p class="text-xs text-zinc-400">{{ item.detail }}</p>
              </div>
            </div>
          </button>
          <div v-if="expandedItems[item.id]" class="px-12 pb-4 pt-2 border-t border-zinc-800/70 text-xs text-zinc-300 space-y-1.5 bg-zinc-950/40">
            <div><strong class="text-zinc-200">ID da verificação:</strong> <span class="font-mono text-zinc-400">{{ item.id }}</span></div>
            <div><strong class="text-zinc-200">Recomendação:</strong> {{ item.status === 'compliant' ? 'Manter configuração atual monitorada.' : 'Revisar e aplicar a correção recomendada na aba correspondente.' }}</div>
          </div>
        </div>
      </div>
    </template>

    <!-- TAB 2: Alterações -->
    <template v-else-if="subTab === 'changes'">
      <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-6 space-y-3 text-xs">
        <div class="font-bold text-base text-white">Histórico &amp; Comparação de Alterações</div>
        <p class="text-zinc-400">
          {{ baselineSaved ? `Comparando estado atual (${auditData.items?.length || 0} verificações) com a referência salva em ${baselineTimestamp}.` : 'Defina uma execução de referência na aba Assessment para rastrear alterações de conformidade ao longo do tempo.' }}
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          <div class="p-4 rounded-xl bg-zinc-950/70 border border-zinc-800">
            <div class="text-zinc-400">Host</div>
            <div class="font-bold text-white mt-0.5">{{ auditData.hostname || 'Linux Host' }}</div>
          </div>
          <div class="p-4 rounded-xl bg-zinc-950/70 border border-zinc-800">
            <div class="text-zinc-400">Verificações</div>
            <div class="font-bold text-blue-400 mt-0.5">{{ (auditData.items || []).length }} ativas</div>
          </div>
          <div class="p-4 rounded-xl bg-zinc-950/70 border border-zinc-800">
            <div class="text-zinc-400">Última Execução</div>
            <div class="font-bold text-emerald-400 mt-0.5">{{ auditData.timestamp || currentTimestampBr }}</div>
          </div>
        </div>
      </div>
    </template>

    <!-- TAB 3: Política -->
    <template v-else>
      <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-6 space-y-3 text-xs text-zinc-300">
        <div class="font-bold text-base text-white">Política de Conformidade Linux Menux - Monitor</div>
        <p class="text-zinc-400">Critérios avaliados automaticamente em cada execução:</p>
        <ul class="list-disc list-inside space-y-1 text-zinc-300">
          <li><strong>Backup:</strong> verificação de backups locais, Borg e Cloudflare R2 configurados.</li>
          <li><strong>Containers:</strong> inspeção de containers Docker/Dokploy em execução e saúde.</li>
          <li><strong>Hardware &amp; Storage:</strong> uso de disco, saúde SMART de SSD/NVMe e temperatura.</li>
          <li><strong>Network &amp; Security:</strong> firewall ativo (UFW/iptables), Fail2Ban, Lynis e atualizações pendentes.</li>
        </ul>
      </div>
    </template>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ClipboardCheck, FileText, Play, Info, CheckCircle2, MinusCircle, Flag, ChevronDown, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  auditData: { type: Object, default: () => ({ items: [], counts: {} }) },
})
defineEmits(['run-audit'])

const subTab = ref('report')
const reportMode = ref('full')
const statusFilter = ref('all')
const categoryFilter = ref('all')
const expandedItems = ref({})
const baselineSaved = ref(false)
const baselineTimestamp = ref('')
const currentTimestampBr = new Date().toLocaleString('pt-BR')

const categories = [
  { id: 'all', label: 'All' },
  { id: 'Backup', label: 'Backup' },
  { id: 'Containers', label: 'Containers' },
  { id: 'Hardware', label: 'Hardware' },
  { id: 'Network', label: 'Network' },
  { id: 'Security', label: 'Security' },
  { id: 'Storage', label: 'Storage' },
  { id: 'System', label: 'System' },
]

const filteredItems = computed(() => {
  const items = props.auditData.items || []
  return items.filter(i => {
    if (statusFilter.value !== 'all' && i.status !== statusFilter.value) return false
    if (categoryFilter.value !== 'all' && String(i.category || '').toLowerCase() !== categoryFilter.value.toLowerCase()) return false
    return true
  })
})

function toggleItem(id) {
  expandedItems.value[id] = !expandedItems.value[id]
}

function saveBaseline() {
  baselineSaved.value = true
  baselineTimestamp.value = new Date().toLocaleString('pt-BR')
}

function printReport() {
  window.print()
}
</script>
