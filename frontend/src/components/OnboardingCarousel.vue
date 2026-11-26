<template>
  <BaseModal :open="open" max-width="max-w-2xl" @close="finishOnboarding">
    <div class="p-6 space-y-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <img src="/logo.svg" alt="Linux Menux - Monitor" class="w-10 h-10 rounded-xl shadow-lg shrink-0" />
          <div>
            <h3 class="text-base font-bold text-white">Bem-vindo ao Linux Menux - Monitor</h3>
            <p class="text-xs text-zinc-400">Passo {{ step + 1 }} de {{ slides.length }}</p>
          </div>
        </div>
        <button @click="finishOnboarding" class="text-zinc-400 hover:text-white cursor-pointer px-2 text-lg">✕</button>
      </div>

      <div class="bg-[#141416] border border-zinc-800 rounded-xl p-6 space-y-3 min-h-[190px] flex flex-col justify-center">
        <div class="flex items-center gap-2.5 text-blue-400 font-bold text-base">
          <component :is="slides[step].icon" class="w-5 h-5" />
          <span>{{ slides[step].title }}</span>
        </div>
        <p class="text-sm text-zinc-300 leading-relaxed">{{ slides[step].description }}</p>
        <ul class="space-y-1.5 text-xs text-zinc-400 pt-1">
          <li v-for="(pt, idx) in slides[step].bullets" :key="idx" class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>{{ pt }}</span>
          </li>
        </ul>
      </div>

      <div class="flex items-center justify-between pt-2 gap-3 flex-wrap">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-1.5">
            <button
              v-for="(s, idx) in slides"
              :key="idx"
              @click="step = idx"
              class="h-2 rounded-full transition-all cursor-pointer"
              :class="step === idx ? 'w-6 bg-blue-500' : 'w-2 bg-zinc-700 hover:bg-zinc-600'"
            ></button>
          </div>
          <label class="flex items-center gap-2 text-xs text-zinc-400 cursor-pointer select-none">
            <input type="checkbox" v-model="dontShowAgain" class="rounded bg-zinc-900 border-zinc-700 accent-blue-600" />
            <span>Não mostrar novamente ao fazer login</span>
          </label>
        </div>

        <div class="flex items-center gap-2">
          <button
            v-if="step > 0"
            @click="step--"
            class="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold cursor-pointer"
          >
            Anterior
          </button>
          <button
            v-if="step < slides.length - 1"
            @click="step++"
            class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold cursor-pointer"
          >
            Próximo
          </button>
          <button
            v-else
            @click="finishOnboarding"
            class="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold cursor-pointer"
          >
            Começar a usar
          </button>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref } from 'vue'
import { Activity, Boxes, HardDrive, ShieldCheck } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'

defineProps({
  open: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])

const step = ref(0)
const dontShowAgain = ref(true)
const slides = [
  {
    icon: Activity,
    title: 'Telemetria Real & Histórico em Tempo Real',
    description: 'Acompanhe CPU, RAM, ZRAM, temperatura de sensores, discos e tráfego de rede real com vnstat e SQLite persistente.',
    bullets: [
      'Detecção automática de BigLinux, Manjaro, Arch, Ubuntu, Debian e Fedora',
      'Alertas inteligentes de saúde e atualizações do sistema com terminal em tempo real',
    ],
  },
  {
    icon: Boxes,
    title: 'Containers Docker, Compose, Swarm & Dokploy',
    description: 'Gerencie todos os seus containers, stacks e domínios Traefik com métricas ao vivo de CPU, memória, rede e E/S de disco.',
    bullets: [
      'Catálogo de Apps e links personalizados integrados',
      'Inspeção completa de logs, variáveis de ambiente e atualizações de imagem',
    ],
  },
  {
    icon: HardDrive,
    title: 'Armazenamento SMART, Rede & Backup em Nuvem',
    description: 'Monitore saúde SMART de SSD/NVMe, topologia de rede SVG ao vivo e backups locais, Borg ou Cloudflare R2.',
    bullets: [
      'Restauração direta a partir de buckets Cloudflare R2 (S3)',
      'Terminal PTY interativo diretamente no navegador',
    ],
  },
  {
    icon: ShieldCheck,
    title: 'Segurança, Auditoria & Notificações',
    description: 'Proteja o host com Firewall, Fail2Ban, auditoria Lynis, tokens de API e alertas via Telegram, Discord ou IA.',
    bullets: [
      'Documentação interativa da API integrada (/docs)',
      'Personalização completa de limiares e canais em Configurações',
    ],
  },
]

function finishOnboarding() {
  try {
    if (dontShowAgain.value) {
      localStorage.setItem('linuxmenux-onboarding-done', '1')
    }
  } catch {
    // ignore
  }
  emit('close')
}
</script>
