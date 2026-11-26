<template>
  <BaseModal :open="open" max-width="max-w-4xl" @close="$emit('close')">
    <div class="flex flex-col">
      <div class="px-6 py-4 border-b border-zinc-800 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3.5">
          <div class="w-10 h-10 rounded-xl bg-orange-500/15 border border-orange-500/30 flex items-center justify-center shrink-0">
            <ArrowUpCircle class="w-5 h-5 text-orange-400" />
          </div>
          <div>
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="text-base font-bold text-white">Atualização do Linux Menux - Monitor</h3>
              <span v-if="targetVersion" class="text-xs px-2 py-0.5 rounded-full bg-orange-500/15 text-orange-300 border border-orange-500/30 font-semibold">
                v{{ targetVersion }}
              </span>
            </div>
            <p class="text-xs text-zinc-400 mt-0.5">Baixa a release oficial, aplica o instalador e reinicia o serviço com confirmação da nova versão.</p>
          </div>
        </div>
      </div>

      <div class="p-4 bg-black">
        <pre
          ref="logBox"
          class="w-full h-96 overflow-y-auto rounded p-3 font-mono text-xs leading-relaxed text-zinc-200 whitespace-pre-wrap break-words"
        >{{ cleanLogContent || ':: Conectando ao processo de atualização...' }}</pre>
      </div>

      <div class="px-6 py-3 border-t border-zinc-800 flex items-center justify-between bg-[#1f1f23]">
        <div class="flex items-center gap-2 text-xs tabular-nums">
          <span class="text-zinc-400">&gt;_</span>
          <span
            class="w-2 h-2 rounded-full"
            :class="status === 'done' ? 'bg-emerald-400' : (status === 'error' ? 'bg-red-400' : 'bg-amber-400 animate-pulse')"
          ></span>
          <span :class="status === 'done' ? 'text-emerald-400' : (status === 'error' ? 'text-red-400' : 'text-amber-300')">
            {{ statusMessage }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <button
            v-if="status === 'done'"
            @click="$emit('reload')"
            class="px-4 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white cursor-pointer transition"
          >
            Recarregar Agora
          </button>
          <button
            @click="$emit('close')"
            :disabled="status === 'running' || status === 'restarting'"
            class="px-4 py-1.5 rounded-lg text-xs font-bold transition"
            :class="(status === 'running' || status === 'restarting') ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 text-white cursor-pointer'"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ArrowUpCircle } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  targetVersion: { type: String, default: '' },
  logContent: { type: String, default: '' },
  status: { type: String, default: 'running' },
  statusMessage: { type: String, default: 'Atualizando em tempo real...' },
})

defineEmits(['close', 'reload'])

const logBox = ref(null)

const cleanLogContent = computed(() =>
  String(props.logContent || '').replace(/\x1b\[[0-9;]*m/g, '')
)

watch(() => props.logContent, async () => {
  await nextTick()
  if (logBox.value) {
    logBox.value.scrollTop = logBox.value.scrollHeight
  }
})
</script>
