<template>
  <section class="space-y-6 animate-fadeIn">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-lg font-bold text-white">Catálogo de Apps &amp; Serviços</h2>
        <p class="text-xs text-zinc-400">Acesso rápido aos serviços reais dos containers e links web personalizados (editáveis).</p>
      </div>
      <button
        @click="$emit('open-add')"
        class="bg-blue-600 hover:bg-blue-500 text-white text-xs px-3.5 py-2 rounded-lg font-medium flex items-center gap-1.5 shadow transition cursor-pointer self-start sm:self-auto"
      >
        <Plus class="w-3.5 h-3.5" />
        <span>Adicionar Link Personalizado</span>
      </button>
    </div>

    <!-- Filter & Search Toolbar -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-[#202024] border border-[#2e2e33] p-3 rounded-xl shadow-sm">
      <div class="flex items-center gap-2 overflow-x-auto no-scrollbar">
        <button
          @click="selectedCategory = '__all__'"
          class="px-3 py-1 rounded-lg text-xs font-medium transition cursor-pointer shrink-0"
          :class="selectedCategory === '__all__' ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-400 hover:text-white'"
        >
          Todos ({{ visibleApps.length }})
        </button>
        <button
          v-for="cat in categoriesList"
          :key="cat"
          @click="selectedCategory = cat"
          class="px-3 py-1 rounded-lg text-xs font-medium transition cursor-pointer shrink-0"
          :class="selectedCategory === cat ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-400 hover:text-white'"
        >
          {{ cat }}
        </button>
      </div>

      <div class="flex items-center gap-2 w-full sm:w-auto">
        <select v-model="sortBy" class="bg-zinc-900 border border-zinc-700/80 text-xs text-zinc-200 px-2.5 py-1.5 rounded-lg">
          <option value="name">Ordenar: Nome</option>
          <option value="category">Ordenar: Categoria</option>
          <option value="type">Ordenar: Origem</option>
        </select>
        <div class="relative flex-1 sm:w-56">
          <Search class="w-3.5 h-3.5 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            v-model="search"
            type="text"
            placeholder="Buscar apps e links..."
            class="w-full bg-zinc-900 border border-zinc-700/80 text-xs text-zinc-200 pl-8 pr-3 py-1.5 rounded-lg focus:outline-none focus:border-blue-500 font-sans"
          />
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredApps.length === 0" class="flex flex-col items-center justify-center p-12 text-center border border-dashed border-[#2e2e33] rounded-xl bg-[#202024]">
      <Grid3x3 class="w-12 h-12 text-zinc-600 mb-3" />
      <h3 class="text-base font-bold text-white mb-1">Nenhum aplicativo ou link visível</h3>
      <p class="text-xs text-zinc-400 max-w-md mb-4">Adicione links personalizados para acessar rapidamente seus painéis.</p>
      <button @click="$emit('open-add')" class="bg-blue-600 hover:bg-blue-500 text-white text-xs px-4 py-2 rounded-lg font-medium flex items-center gap-1.5 shadow transition cursor-pointer">
        <Plus class="w-4 h-4" /> Adicionar Primeiro Link
      </button>
    </div>

    <!-- Apps Grid (Editable + Removable) -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="app in filteredApps"
        :key="app.id"
        class="bg-[#202024] border border-[#2e2e33] rounded-xl p-5 hover:border-zinc-600 transition flex flex-col justify-between shadow-sm"
      >
        <div>
          <div class="flex items-start justify-between gap-2 mb-3">
            <div class="w-10 h-10 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center font-bold text-lg text-blue-400 shadow overflow-hidden">
              <img v-if="app.logo_url" :src="app.logo_url" :alt="app.name" class="w-full h-full object-contain p-1" />
              <span v-else>{{ (app.name || 'A')[0] }}</span>
            </div>
            <div class="flex items-center gap-1">
              <span
                class="text-xs px-2 py-0.5 rounded-full font-medium mr-1"
                :class="app.running ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-zinc-800 text-zinc-400'"
              >
                {{ app.running ? 'Online' : 'Parado' }}
              </span>
              <button
                @click="openEdit(app)"
                class="text-zinc-400 hover:text-blue-400 p-1 rounded transition cursor-pointer"
                title="Editar nome, URL ou porta"
              >
                <Pencil class="w-3.5 h-3.5" />
              </button>
              <button
                @click="hideOrDelete(app)"
                class="text-zinc-400 hover:text-red-400 p-1 rounded transition cursor-pointer"
                :title="app.isCustom ? 'Excluir link' : 'Ocultar card'"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div class="flex items-center gap-2 mb-1">
            <h3 class="text-base font-bold text-white truncate">{{ app.name }}</h3>
            <span class="text-xs tabular-nums px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700/60">{{ app.category }}</span>
          </div>
          <p class="text-xs text-zinc-400 mb-3 truncate" :title="app.url">{{ app.description || app.url }}</p>
        </div>

        <div class="pt-3 border-t border-[#2e2e33] flex items-center justify-between">
          <span class="text-xs tabular-nums text-zinc-400">{{ app.port }}</span>
          <a :href="app.url" target="_blank" class="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1">
            Abrir Painel
            <ExternalLink class="w-3 h-3" />
          </a>
        </div>
      </div>
    </div>

    <!-- Modal: Editar App / Link -->
    <BaseModal :open="editOpen" max-width="max-w-md" @close="editOpen = false">
      <div class="p-6 space-y-4 text-xs">
        <div class="flex items-center justify-between border-b border-[#2e2e33] pb-3">
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <Pencil class="w-4 h-4 text-blue-400" /> Editar App / Link
          </h3>
          <button @click="editOpen = false" class="text-zinc-400 hover:text-white cursor-pointer text-sm">✕</button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-zinc-400 mb-1 font-medium">Nome</label>
            <input v-model="editForm.name" type="text" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white" />
          </div>
          <div>
            <label class="block text-zinc-400 mb-1 font-medium">URL / Porta de Acesso</label>
            <input v-model="editForm.url" type="text" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono" />
          </div>
          <div>
            <label class="block text-zinc-400 mb-1 font-medium">Categoria</label>
            <input v-model="editForm.category" type="text" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white" />
          </div>
          <div>
            <label class="block text-zinc-400 mb-1 font-medium">Descrição</label>
            <input v-model="editForm.description" type="text" class="w-full bg-[#141416] border border-zinc-700 rounded-lg px-3 py-2 text-white" />
          </div>
        </div>
        <div class="flex justify-end gap-2 pt-2 border-t border-[#2e2e33]">
          <button @click="editOpen = false" class="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-semibold cursor-pointer">Cancelar</button>
          <button @click="saveEdit" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold cursor-pointer">Salvar</button>
        </div>
      </div>
    </BaseModal>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Plus, Search, Grid3x3, Pencil, Trash2, ExternalLink } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'

const props = defineProps({
  apps: { type: Array, default: () => [] },
  overrides: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['open-add', 'delete-custom', 'save-override'])

const readPref = (k, d) => { try { return localStorage.getItem(k) || d } catch { return d } }
const selectedCategory = ref(readPref('linuxmenux-apps-category', '__all__'))
const sortBy = ref(readPref('linuxmenux-apps-sort', 'name'))
watch(selectedCategory, (v) => { try { localStorage.setItem('linuxmenux-apps-category', v) } catch {} })
watch(sortBy, (v) => { try { localStorage.setItem('linuxmenux-apps-sort', v) } catch {} })
const search = ref('')
const editOpen = ref(false)
const editForm = ref({ id: '', name: '', url: '', category: '', description: '' })

const visibleApps = computed(() => {
  return (props.apps || [])
    .filter(a => !props.overrides?.[a.id]?.hidden)
    .map((a) => {
      const ov = props.overrides?.[a.id]
      if (!ov) return a
      return {
        ...a,
        name: ov.name || a.name,
        url: ov.url || a.url,
        category: ov.category || a.category,
        description: ov.description || a.description,
      }
    })
})

const categoriesList = computed(() => {
  const set = new Set(['Geral'])
  for (const a of visibleApps.value) {
    if (a.category) set.add(a.category)
  }
  return Array.from(set)
})

const filteredApps = computed(() => {
  let list = visibleApps.value
  if (selectedCategory.value !== '__all__') {
    list = list.filter(a => a.category === selectedCategory.value)
  }
  const q = search.value.trim().toLowerCase()
  if (q) {
    list = list.filter(a => (a.name || '').toLowerCase().includes(q) || (a.description || '').toLowerCase().includes(q))
  }
  return [...list].sort((a, b) => {
    if (sortBy.value === 'category') return (a.category || '').localeCompare(b.category || '')
    if (sortBy.value === 'type') return Number(Boolean(b.isCustom)) - Number(Boolean(a.isCustom))
    return (a.name || '').localeCompare(b.name || '')
  })
})

function openEdit(app) {
  editForm.value = {
    id: app.id,
    name: app.name,
    url: app.url,
    category: app.category || 'Geral',
    description: app.description || '',
  }
  editOpen.value = true
}

function saveEdit() {
  emit('save-override', { ...editForm.value, hidden: false })
  editOpen.value = false
}

function hideOrDelete(app) {
  if (app.isCustom) {
    emit('delete-custom', app.id)
  } else {
    emit('save-override', {
      id: app.id,
      name: app.name,
      url: app.url,
      category: app.category,
      description: app.description,
      hidden: true,
    })
  }
}
</script>
