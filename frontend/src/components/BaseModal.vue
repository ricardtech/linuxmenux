<template>
  <Teleport to="body">
    <div
      v-if="open"
      @click.self="$emit('close')"
      class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn"
    >
      <div
        :class="['bg-[#1c1c1e] border border-[#2e2e33] rounded-xl w-full shadow-2xl overflow-hidden', maxWidth]"
        @click.stop
      >
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  maxWidth: { type: String, default: 'max-w-3xl' },
})

const emit = defineEmits(['close'])

function onKeyDown(e) {
  if (e.key === 'Escape' && props.open) {
    emit('close')
  }
}

onMounted(() => window.addEventListener('keydown', onKeyDown))
onUnmounted(() => window.removeEventListener('keydown', onKeyDown))
</script>
