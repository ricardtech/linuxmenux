<template>
  <div
    class="w-9 h-9 rounded-lg flex items-center justify-center shadow-lg shrink-0 overflow-hidden"
    :class="badgeClass"
    :title="distroName || 'Linux'"
  >
    <!-- BigLinux Official Logo -->
    <img v-if="distroKey === 'biglinux'" :src="distroLogoUrl" alt="BigLinux" class="w-9 h-9 object-contain p-0.5" onerror="this.src='/distro-biglinux.svg'" />

    <!-- Manjaro -->
    <svg v-else-if="distroKey === 'manjaro'" viewBox="0 0 36 36" class="w-6 h-6" fill="white">
      <path d="M6 6h14v7h-7v17H6V6zm16 0h8v24h-8V6zm-8 9h6v15h-6V15z" />
    </svg>

    <!-- Arch Linux -->
    <svg v-else-if="distroKey === 'arch'" viewBox="0 0 36 36" class="w-6 h-6" fill="white">
      <path d="M18 5c-1.5 3.6-2.4 6-4.1 9.5 1 .9 2.3 2 4.3 3.4-2.2-.9-3.7-1.8-4.8-2.7C11.4 19.3 8.4 24.4 5 31c4.5-2.6 8-4.2 11.2-4.8-.1-.6-.2-1.3-.2-2 0-2.5 1.3-4.6 3-4.6s3 2.1 3 4.6c0 .7-.1 1.4-.2 2 3.2.6 6.7 2.2 11.2 4.8-1-1.9-1.9-3.6-2.8-5.2-1.3-1-2.7-2.4-5.5-3.9 1.9.5 3.3 1.1 4.4 1.8C24.5 14.9 23.8 12.6 18 5z" />
    </svg>

    <!-- Ubuntu -->
    <svg v-else-if="distroKey === 'ubuntu'" viewBox="0 0 36 36" class="w-6 h-6" fill="white">
      <circle cx="18" cy="18" r="7" fill="none" stroke="white" stroke-width="3" />
      <circle cx="18" cy="6" r="2.5" />
      <circle cx="8" cy="24" r="2.5" />
      <circle cx="28" cy="24" r="2.5" />
    </svg>

    <!-- Debian -->
    <svg v-else-if="distroKey === 'debian'" viewBox="0 0 36 36" class="w-6 h-6" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round">
      <path d="M21 25c-4 1-8-2-8-6 0-5 4-9 9-9 4 0 7 3 7 7 0 6-5 11-11 11-6 0-10-4-10-10 0-7 6-12 13-12" />
    </svg>

    <!-- Fedora -->
    <svg v-else-if="distroKey === 'fedora'" viewBox="0 0 36 36" class="w-6 h-6" fill="none" stroke="white" stroke-width="2.6">
      <circle cx="18" cy="18" r="11" />
      <path d="M18 25V13a4 4 0 0 1 4-4h2M14 18h7" stroke-linecap="round" />
    </svg>

    <!-- Fallback Menux M -->
    <span v-else class="text-white font-black text-xl tracking-tighter">M</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const distroLogoUrl = '/api/distro/logo'

const props = defineProps({
  distroId: { type: String, default: '' },
  distroName: { type: String, default: '' },
})

const distroKey = computed(() => {
  const raw = `${props.distroId} ${props.distroName}`.toLowerCase()
  if (raw.includes('biglinux')) return 'biglinux'
  if (raw.includes('manjaro')) return 'manjaro'
  if (raw.includes('arch') || raw.includes('endeavour')) return 'arch'
  if (raw.includes('ubuntu') || raw.includes('pop') || raw.includes('mint')) return 'ubuntu'
  if (raw.includes('debian')) return 'debian'
  if (raw.includes('fedora') || raw.includes('rhel') || raw.includes('rocky')) return 'fedora'
  return 'default'
})

const badgeClass = computed(() => {
  switch (distroKey.value) {
    case 'biglinux': return 'bg-gradient-to-br from-sky-500 to-blue-700 shadow-sky-500/25'
    case 'manjaro': return 'bg-gradient-to-br from-emerald-500 to-teal-700 shadow-emerald-500/25'
    case 'arch': return 'bg-gradient-to-br from-cyan-500 to-blue-600 shadow-cyan-500/25'
    case 'ubuntu': return 'bg-gradient-to-br from-orange-500 to-red-600 shadow-orange-500/25'
    case 'debian': return 'bg-gradient-to-br from-rose-600 to-red-800 shadow-rose-500/25'
    case 'fedora': return 'bg-gradient-to-br from-blue-500 to-indigo-700 shadow-blue-500/25'
    default: return 'bg-gradient-to-br from-orange-500 to-amber-600 shadow-orange-500/20'
  }
})
</script>
