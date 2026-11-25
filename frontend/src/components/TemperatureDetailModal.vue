<template>
  <BaseModal :open="open" max-width="max-w-3xl" @close="$emit('close')">
    <div class="p-5 sm:p-6 space-y-4">
      <!-- Header -->
      <div class="flex items-center justify-between gap-3">
        <h3 class="text-base font-bold text-white flex items-center gap-2">
          <Thermometer class="w-5 h-5 text-zinc-300" />
          Temperatura da CPU
        </h3>
        <div class="flex items-center gap-2">
          <select
            v-model="timeframe"
            @change="fetchHistory"
            class="bg-[#262629] border border-[#3a3a3f] rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 cursor-pointer"
          >
            <option value="1h">1 hora</option>
            <option value="24h">24 horas</option>
            <option value="7d">7 dias</option>
            <option value="30d">30 dias</option>
          </select>
          <button
            @click="$emit('close')"
            class="text-zinc-400 hover:text-white cursor-pointer text-base px-1.5 py-1 rounded-md hover:bg-zinc-800 transition-colors"
            title="Fechar (Esc)"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- 4 KPI cards matching ProxMenux TemperatureDetailModal -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3 tabular-nums">
        <div :class="['rounded-lg p-3 text-center', currentCardClass]">
          <div class="text-xs opacity-80 mb-1">Atual</div>
          <div class="text-lg font-bold">{{ currentTemp }}°C</div>
        </div>
        <div class="bg-zinc-800/50 rounded-lg p-3 text-center">
          <div class="text-xs text-zinc-400 mb-1 flex items-center justify-center gap-1">
            <TrendingDown class="w-3 h-3" /> Mínimo
          </div>
          <div class="text-lg font-bold text-emerald-400">{{ stats.min }}°C</div>
        </div>
        <div class="bg-zinc-800/50 rounded-lg p-3 text-center">
          <div class="text-xs text-zinc-400 mb-1 flex items-center justify-center gap-1">
            <Minus class="w-3 h-3" /> Média
          </div>
          <div class="text-lg font-bold text-white">{{ stats.avg }}°C</div>
        </div>
        <div class="bg-zinc-800/50 rounded-lg p-3 text-center">
          <div class="text-xs text-zinc-400 mb-1 flex items-center justify-center gap-1">
            <TrendingUp class="w-3 h-3" /> Máx.
          </div>
          <div class="text-lg font-bold text-red-400">{{ stats.max }}°C</div>
        </div>
      </div>

      <!-- Area Chart -->
      <div class="h-[300px] sm:h-[330px] relative">
        <div v-if="loading" class="h-full flex items-center justify-center text-xs text-zinc-400">
          Carregando histórico térmico...
        </div>
        <div v-else-if="!points.length" class="h-full flex flex-col items-center justify-center text-zinc-400 text-xs">
          <Thermometer class="w-8 h-8 mb-2 opacity-50" />
          <p>Sem dados térmicos históricos ainda.</p>
          <p class="text-xs text-zinc-500 mt-1">As amostras são gravadas automaticamente a cada 10s.</p>
        </div>
        <canvas v-show="!loading && points.length" ref="canvasRef"></canvas>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import { Thermometer, TrendingDown, TrendingUp, Minus } from 'lucide-vue-next'
import Chart from 'chart.js/auto'
import BaseModal from './BaseModal.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  liveTemperature: { type: Number, default: 0 },
})

defineEmits(['close'])

const timeframe = ref('24h')
const loading = ref(false)
const points = ref([])
const stats = ref({ current: 0, min: 0, avg: 0, max: 0 })
const canvasRef = ref(null)
let chartInstance = null

const currentTemp = computed(() => {
  if (props.liveTemperature > 0) return Math.round(props.liveTemperature * 10) / 10
  return stats.value.current || 0
})

const chartColor = computed(() => {
  const t = currentTemp.value
  if (t >= 80) return '#ef4444'
  if (t >= 65) return '#f59e0b'
  return '#22c55e'
})

const currentCardClass = computed(() => {
  const t = currentTemp.value
  if (t >= 80) return 'bg-red-500/15 text-red-400 border border-red-500/20'
  if (t >= 65) return 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
  return 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
})

function formatTimeLabel(tsMs) {
  const d = new Date(tsMs)
  if (timeframe.value === '1h' || timeframe.value === '24h') {
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) + ' ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

async function fetchHistory() {
  loading.value = true
  try {
    const res = await fetch(`/api/temperature/history?timeframe=${timeframe.value}`)
    if (res.ok) {
      const json = await res.json()
      points.value = json.data || []
      stats.value = json.stats || { current: 0, min: 0, avg: 0, max: 0 }
    }
  } finally {
    loading.value = false
    await nextTick()
    renderChart()
  }
}

function renderChart() {
  if (!canvasRef.value || !points.value.length) return
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
  const ctx = canvasRef.value.getContext('2d')
  const color = chartColor.value
  const gradient = ctx.createLinearGradient(0, 0, 0, 320)
  gradient.addColorStop(0, `${color}4d`)
  gradient.addColorStop(1, `${color}05`)

  const values = points.value.map(p => p.value)
  const yMin = Math.max(0, Math.floor(Math.min(...values) - 3))
  const yMax = Math.ceil(Math.max(...values) + 3)

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: points.value.map(p => formatTimeLabel(p.time)),
      datasets: [{
        label: 'Temperatura (°C)',
        data: values,
        borderColor: color,
        backgroundColor: gradient,
        borderWidth: 2,
        fill: true,
        tension: 0.3,
        pointRadius: 0,
        pointHoverRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#18181b',
          borderColor: '#3f3f46',
          borderWidth: 1,
          titleColor: '#a1a1aa',
          bodyColor: '#ffffff',
          callbacks: {
            label: (ctx) => `${ctx.parsed.y}°C`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.06)' },
          ticks: { color: '#a1a1aa', maxTicksLimit: 8, font: { size: 11 } },
        },
        y: {
          min: yMin,
          max: yMax,
          grid: { color: 'rgba(255,255,255,0.06)' },
          ticks: {
            color: '#a1a1aa',
            font: { size: 11 },
            callback: (v) => `${v}°`,
          },
        },
      },
    },
  })
}

watch(() => props.open, (val) => {
  if (val) {
    fetchHistory()
  } else if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
})
</script>
