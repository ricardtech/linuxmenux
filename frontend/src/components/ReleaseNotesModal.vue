<template>
  <BaseModal :open="open" max-width="max-w-2xl" @close="dismissForVersion">
    <div class="p-6 space-y-5">
      <div class="flex items-center justify-between border-b border-zinc-800 pb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Sparkles class="w-5 h-5" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-base font-bold text-white">O que há de novo no Linux Menux</h3>
              <span class="text-xs px-2 py-0.5 rounded bg-orange-500/15 text-orange-400 border border-orange-500/30 font-semibold">
                v{{ version }}
              </span>
            </div>
            <p class="text-xs text-zinc-400 mt-0.5">Novidades, melhorias de paridade 1:1 e correções desta versão</p>
          </div>
        </div>
        <button @click="dismissForVersion" class="text-zinc-400 hover:text-white cursor-pointer px-2 text-lg">✕</button>
      </div>

      <div class="space-y-3 max-h-[55vh] overflow-y-auto pr-1 text-xs">
        <div v-for="(item, idx) in highlights" :key="idx" class="p-3.5 rounded-xl bg-[#141416] border border-zinc-800 space-y-1">
          <div class="font-bold text-white flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>{{ item.title }}</span>
          </div>
          <p class="text-zinc-400 leading-relaxed">{{ item.detail }}</p>
        </div>
      </div>

      <div class="flex items-center justify-between pt-3 border-t border-zinc-800">
        <label class="flex items-center gap-2 text-xs text-zinc-400 cursor-pointer">
          <input type="checkbox" v-model="dontShowAgain" class="rounded bg-zinc-900 border-zinc-700" />
          <span>Não mostrar novamente na versão v{{ version }}</span>
        </label>
        <button @click="dismissForVersion" class="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold cursor-pointer">
          Entendido
        </button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref } from 'vue'
import { Sparkles } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'
import { APP_VERSION } from '../lib/version'

defineProps({
  open: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])

const version = APP_VERSION
const dontShowAgain = ref(true)

const highlights = [
  {
    title: 'Paridade 1:1 Completa em Segurança & Configurações',
    detail: 'Abas de Segurança (Autenticação, SSL/Cloudflare Tunnel, Tokens API + Swagger, Firewall, Fail2Ban com jails/IPs banidos e Lynis com PDF) e Configurações (Snippets, Otimizações, GitHub API e Notificações).',
  },
  {
    title: 'Rede Real, Wi-Fi Preciso & Logo Oficial da Distro',
    detail: 'Cabo Ethernet desconectado (sem IP) marcado corretamente como Desativado, velocidade real do Wi-Fi via iw dev, latência ICMP corrigida e logotipo oficial da distribuição.',
  },
  {
    title: 'Atualizações AUR & Auto-Atualização no Modal Info',
    detail: 'Detecção de pacotes AUR (pamac checkupdates), verificação automática de novas releases no GitHub público e botão de atualização com 1 clique no modal Info.',
  },
  {
    title: 'Telemetria 100% Linux/Docker (Sem /api/vms)',
    detail: 'Coleta em lote de estatísticas reais de CPU, Memória, E/S de disco e E/S de rede dos containers Docker e Dokploy sem chamadas de VM.',
  },
]

function dismissForVersion() {
  if (dontShowAgain.value) {
    try {
      localStorage.setItem('linuxmenux-last-seen-version', version)
    } catch {
      // ignore
    }
  }
  emit('close')
}
</script>
