<template>
  <section class="space-y-6 animate-fadeIn">
    <!-- Top Config Card 1:1 with ProxMenux Backup -->
    <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-5 shadow-sm">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <DatabaseBackup class="w-5 h-5 text-blue-400" />
            Configuração de backup
          </h3>
          <p class="text-xs text-zinc-400 mt-0.5">Gerencie destinos (Local, Borg, Cloudflare R2 / S3), caminhos e restauração.</p>
        </div>
        <button
          @click="destModalOpen = true"
          class="bg-blue-600 hover:bg-blue-500 text-white text-xs px-3.5 py-2 rounded-lg font-semibold flex items-center gap-1.5 cursor-pointer transition-colors"
        >
          <Plus class="w-3.5 h-3.5" /> Configurar destino
        </button>
      </div>

      <!-- Active Destination Summary -->
      <div class="p-4 bg-[#141416] border border-zinc-800 rounded-xl space-y-2.5 text-xs tabular-nums">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="font-mono font-bold text-white">{{ backupData.destination }}</span>
            <span class="px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 font-semibold uppercase text-xs">
              {{ destinations.active_type || 'LOCAL' }}
            </span>
            <span
              v-if="r2Configured"
              class="px-2 py-0.5 rounded bg-orange-500/15 text-orange-400 border border-orange-500/30 font-semibold text-xs"
            >
              Cloudflare R2 Conectado
            </span>
          </div>
          <span class="text-emerald-400 font-semibold">{{ backupData.used_formatted }} / {{ backupData.free_formatted }} livres</span>
        </div>
        <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div class="h-full bg-blue-500" :style="{ width: `${backupData.used_percent || 0}%` }"></div>
        </div>
        <div class="pt-1">
          <button
            @click="$emit('run-backup')"
            :disabled="backupRunning"
            class="w-full sm:w-auto bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs px-5 py-2 rounded-lg font-bold transition cursor-pointer"
          >
            {{ backupRunning ? 'Executando Backup...' : 'Executar Backup Manual Agora' }}
          </button>
        </div>
      </div>

      <!-- Custom Paths -->
      <div class="space-y-3">
        <h4 class="text-xs font-bold uppercase tracking-wider text-zinc-400">Caminhos personalizados</h4>
        <div class="flex gap-2">
          <input
            :value="newPath"
            @input="$emit('update:newPath', $event.target.value)"
            type="text"
            placeholder="/etc/nginx ou /opt/app"
            class="flex-1 bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-xs text-white font-mono"
          />
          <button
            @click="$emit('add-path')"
            class="bg-blue-600 hover:bg-blue-500 text-white text-xs px-4 py-2 rounded-lg font-semibold cursor-pointer"
          >
            + Adicionar caminho
          </button>
        </div>
        <div v-if="!(backupData.custom_paths || []).length" class="text-xs text-zinc-400 py-4 text-center border border-dashed border-zinc-800 rounded-lg">
          Ainda não há caminhos personalizados — usando dados de configuração do Linux Menux.
        </div>
        <div v-else class="space-y-1.5 text-xs tabular-nums">
          <div v-for="p in backupData.custom_paths" :key="p" class="flex items-center justify-between px-3 py-2 bg-[#141416] rounded-lg border border-zinc-800">
            <span class="text-zinc-200 font-mono">{{ p }}</span>
            <button @click="$emit('remove-path', p)" class="text-red-400 hover:text-red-300 cursor-pointer">Remover</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Local Backups Table -->
    <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-bold text-white">Cópias de segurança locais ({{ (backupData.backups || []).length }})</h3>
        <span v-if="statusMsg" class="text-xs text-emerald-400 font-medium">{{ statusMsg }}</span>
      </div>
      <div v-if="!(backupData.backups || []).length" class="text-xs text-zinc-400 py-6 text-center">
        Nenhum arquivo .tar.gz encontrado ainda.
      </div>
      <div v-else class="border border-zinc-800 rounded-lg overflow-hidden">
        <table class="w-full text-left text-xs tabular-nums">
          <thead class="bg-[#141416] text-zinc-400 border-b border-zinc-800">
            <tr>
              <th class="p-3">Arquivo</th>
              <th class="p-3">Data</th>
              <th class="p-3">Tamanho</th>
              <th class="p-3 text-right">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-800 text-zinc-300">
            <tr v-for="b in backupData.backups" :key="b.name" class="hover:bg-white/[0.02]">
              <td class="p-3 font-bold text-white font-mono">{{ b.name }}</td>
              <td class="p-3">{{ b.created_at }}</td>
              <td class="p-3 text-emerald-400">{{ b.size_formatted }}</td>
              <td class="p-3 text-right space-x-3">
                <button
                  v-if="r2Configured"
                  @click="uploadToR2(b.name)"
                  :disabled="busyAction === b.name"
                  class="text-orange-400 hover:text-orange-300 font-semibold cursor-pointer"
                >
                  {{ busyAction === b.name ? 'Enviando...' : 'Enviar p/ R2' }}
                </button>
                <button
                  @click="restoreFrom('local', b.name)"
                  :disabled="busyAction === `restore:${b.name}`"
                  class="text-emerald-400 hover:text-emerald-300 font-semibold cursor-pointer"
                >
                  Restaurar
                </button>
                <a :href="`/api/backup/download/${encodeURIComponent(b.name)}`" class="text-blue-400 hover:text-blue-300">Baixar</a>
                <button @click="$emit('delete-backup', b.name)" class="text-red-400 hover:text-red-300 cursor-pointer">Excluir</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Cloudflare R2 Backups Table (when configured) -->
    <div v-if="r2Configured" class="bg-[#18181b] border border-zinc-800 rounded-xl p-5 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-bold text-white flex items-center gap-2">
          <Cloud class="w-4 h-4 text-orange-400" />
          Backups no Cloudflare R2 ({{ r2Items.length }})
        </h3>
        <button @click="fetchR2List" class="text-xs text-zinc-400 hover:text-white flex items-center gap-1 cursor-pointer">
          <RefreshCw class="w-3.5 h-3.5" /> Atualizar R2
        </button>
      </div>
      <div v-if="r2Error" class="text-xs text-red-400">{{ r2Error }}</div>
      <div v-else-if="!r2Items.length" class="text-xs text-zinc-400 py-5 text-center">
        Nenhum backup encontrado no bucket R2. Clique em "Enviar p/ R2" em um backup local acima.
      </div>
      <div v-else class="border border-zinc-800 rounded-lg overflow-hidden">
        <table class="w-full text-left text-xs tabular-nums">
          <thead class="bg-[#141416] text-zinc-400 border-b border-zinc-800">
            <tr><th class="p-3">Objeto (R2)</th><th class="p-3">Modificado</th><th class="p-3">Tamanho</th><th class="p-3 text-right">Ações</th></tr>
          </thead>
          <tbody class="divide-y divide-zinc-800 text-zinc-300">
            <tr v-for="item in r2Items" :key="item.key">
              <td class="p-3 font-mono text-white">{{ item.key }}</td>
              <td class="p-3">{{ item.last_modified }}</td>
              <td class="p-3 text-orange-400">{{ item.size_formatted }}</td>
              <td class="p-3 text-right">
                <button
                  @click="restoreFrom('r2', item.key)"
                  :disabled="busyAction === `restore:${item.key}`"
                  class="text-emerald-400 hover:text-emerald-300 font-semibold cursor-pointer"
                >
                  {{ busyAction === `restore:${item.key}` ? 'Restaurando...' : 'Restaurar do R2' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal: + Configurar destino (1:1 Image 5 + Cloudflare R2) -->
    <BaseModal :open="destModalOpen" max-width="max-w-2xl" @close="destModalOpen = false">
      <div class="p-6 space-y-5">
        <div class="flex items-start justify-between">
          <div>
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <Plus class="w-4 h-4 text-blue-400" />
              Configurar destino
            </h3>
            <p class="text-xs text-zinc-400 mt-0.5">Escolha onde os backups do host devem ser armazenados.</p>
          </div>
          <button @click="destModalOpen = false" class="text-zinc-400 hover:text-white cursor-pointer text-base px-1.5">✕</button>
        </div>

        <!-- 3 Destination Cards: LOCAL | BORG | CLOUDFLARE R2 / S3 -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <button
            type="button"
            @click="selectedType = 'local'"
            class="text-left p-4 rounded-xl border transition cursor-pointer space-y-1.5"
            :class="selectedType === 'local' ? 'border-blue-500 bg-blue-500/10' : 'border-zinc-800 bg-[#141416] hover:border-zinc-700'"
          >
            <div class="font-bold text-blue-400 flex items-center gap-1.5"><HardDrive class="w-4 h-4" /> LOCAL</div>
            <p class="text-xs text-zinc-400 leading-relaxed">Pasta neste host ou em uma unidade USB montada.</p>
          </button>

          <button
            type="button"
            @click="selectedType = 'borg'"
            class="text-left p-4 rounded-xl border transition cursor-pointer space-y-1.5"
            :class="selectedType === 'borg' ? 'border-purple-500 bg-purple-500/10' : 'border-zinc-800 bg-[#141416] hover:border-zinc-700'"
          >
            <div class="font-bold text-purple-400 flex items-center gap-1.5"><Archive class="w-4 h-4" /> BORG</div>
            <p class="text-xs text-zinc-400 leading-relaxed">Repositório Borg para backups de host desduplicados.</p>
          </button>

          <button
            type="button"
            @click="selectedType = 'r2'"
            class="text-left p-4 rounded-xl border transition cursor-pointer space-y-1.5"
            :class="selectedType === 'r2' ? 'border-orange-500 bg-orange-500/10' : 'border-zinc-800 bg-[#141416] hover:border-zinc-700'"
          >
            <div class="font-bold text-orange-400 flex items-center gap-1.5"><Cloud class="w-4 h-4" /> CLOUDFLARE R2</div>
            <p class="text-xs text-zinc-400 leading-relaxed">Bucket S3-compatível na nuvem para envio e restauração remota.</p>
          </button>
        </div>

        <!-- Config Form for Selected Type -->
        <div v-if="selectedType === 'local'" class="space-y-2 text-xs">
          <label class="block text-zinc-300 font-medium">Diretório local de destino</label>
          <input v-model="destinations.local.path" type="text" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono" />
        </div>

        <div v-else-if="selectedType === 'borg'" class="space-y-3 text-xs">
          <div class="space-y-1">
            <label class="block text-zinc-300 font-medium">Repositório Borg</label>
            <input v-model="destinations.borg.repo" type="text" placeholder="ssh://user@host/repo ou /mnt/borg" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono" />
          </div>
          <div class="space-y-1">
            <label class="block text-zinc-300 font-medium">Passphrase (opcional)</label>
            <input v-model="destinations.borg.passphrase" type="password" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono" />
          </div>
        </div>

        <div v-else-if="selectedType === 'r2'" class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div class="space-y-1">
            <label class="block text-zinc-300 font-medium">Cloudflare Account ID</label>
            <input v-model="destinations.r2.account_id" type="text" placeholder="a1b2c3d4..." class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono" />
          </div>
          <div class="space-y-1">
            <label class="block text-zinc-300 font-medium">Nome do Bucket R2</label>
            <input v-model="destinations.r2.bucket" type="text" placeholder="meu-bucket-backups" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono" />
          </div>
          <div class="space-y-1">
            <label class="block text-zinc-300 font-medium">Access Key ID</label>
            <input v-model="destinations.r2.access_key" type="text" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono" />
          </div>
          <div class="space-y-1">
            <label class="block text-zinc-300 font-medium">Secret Access Key</label>
            <input v-model="destinations.r2.secret_key" type="password" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono" />
          </div>
          <div class="sm:col-span-2 space-y-1">
            <label class="block text-zinc-300 font-medium">Endpoint S3 personalizado (opcional)</label>
            <input v-model="destinations.r2.endpoint" type="text" placeholder="https://<account_id>.r2.cloudflarestorage.com" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono" />
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t border-[#2e2e33]">
          <button @click="destModalOpen = false" class="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold cursor-pointer">
            Cancelar
          </button>
          <button @click="saveDestinations" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold cursor-pointer">
            Salvar Destino
          </button>
        </div>
      </div>
    </BaseModal>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { DatabaseBackup, Plus, HardDrive, Archive, Cloud, RefreshCw } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'

defineProps({
  backupData: { type: Object, required: true },
  backupRunning: { type: Boolean, default: false },
  newPath: { type: String, default: '' },
})

const emit = defineEmits(['run-backup', 'add-path', 'remove-path', 'delete-backup', 'update:newPath', 'refresh'])

const destModalOpen = ref(false)
const selectedType = ref('local')
const destinations = ref({
  active_type: 'local',
  local: { path: '/var/backups/linuxmenux' },
  borg: { repo: '', passphrase: '' },
  r2: { account_id: '', endpoint: '', bucket: '', access_key: '', secret_key: '', prefix: 'linuxmenux/' },
})
const r2Items = ref([])
const r2Error = ref('')
const busyAction = ref('')
const statusMsg = ref('')

const r2Configured = computed(() => {
  const r2 = destinations.value.r2 || {}
  return Boolean((r2.endpoint || r2.account_id) && r2.bucket && r2.access_key && r2.secret_key)
})

async function fetchDestinations() {
  const res = await fetch('/api/backup/destinations')
  if (res.ok) {
    destinations.value = await res.json()
    selectedType.value = destinations.value.active_type || 'local'
    if (r2Configured.value) fetchR2List()
  }
}

async function saveDestinations() {
  destinations.value.active_type = selectedType.value
  const res = await fetch('/api/backup/destinations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(destinations.value),
  })
  if (res.ok) {
    destModalOpen.value = false
    statusMsg.value = 'Destino salvo!'
    setTimeout(() => { statusMsg.value = '' }, 3000)
    if (r2Configured.value) fetchR2List()
  }
}

async function fetchR2List() {
  r2Error.value = ''
  const res = await fetch('/api/backup/r2/list')
  if (res.ok) {
    const j = await res.json()
    r2Items.value = j.items || []
    if (j.error) r2Error.value = j.error
  }
}

async function uploadToR2(filename) {
  busyAction.value = filename
  try {
    const res = await fetch('/api/backup/r2/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename }),
    })
    const j = await res.json()
    statusMsg.value = j.message || (j.success ? 'Enviado ao R2!' : 'Falha ao enviar')
    await fetchR2List()
  } finally {
    busyAction.value = ''
  }
}

async function restoreFrom(source, target) {
  busyAction.value = `restore:${target}`
  try {
    const res = await fetch('/api/backup/restore', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source, target }),
    })
    const j = await res.json()
    statusMsg.value = j.message || (j.success ? 'Restaurado!' : 'Falha na restauração')
    emit('refresh')
  } finally {
    busyAction.value = ''
  }
}

onMounted(fetchDestinations)
</script>
