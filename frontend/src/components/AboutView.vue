<template>
  <section class="space-y-6 animate-fadeIn">
    <!-- Hero Card (1:1 ProxMenux about.tsx) -->
    <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <img src="/logo.svg" alt="Linux Menux Monitor" class="w-12 h-12 rounded-xl shadow-lg shadow-orange-500/20 shrink-0" />
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-lg font-bold text-white">Linux Menux Monitor</h2>
            <span class="text-xs px-2 py-0.5 rounded bg-orange-500/15 text-orange-400 border border-orange-500/30 font-semibold">v{{ version }}</span>
          </div>
          <p class="text-xs text-zinc-400 mt-0.5">
            Painel completo de monitoramento e gestão para servidores Linux, Docker, Swarm &amp; Dokploy.
          </p>
        </div>
      </div>
      <span class="text-xs px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 font-semibold self-start sm:self-auto">
        100% Linux Nativo
      </span>
    </div>

    <!-- 4 Project Links Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
      <a href="https://github.com/ricardtech/linuxmenux" target="_blank" class="bg-[#18181b] border border-zinc-800 hover:border-blue-500/40 rounded-xl p-4 space-y-1 transition block">
        <div class="font-bold text-white flex items-center justify-between">
          <span>Repositório GitHub</span>
          <span class="text-blue-400">↗</span>
        </div>
        <p class="text-zinc-400">Código-fonte, releases e histórico de versões.</p>
      </a>
      <a href="/docs" target="_blank" class="bg-[#18181b] border border-zinc-800 hover:border-blue-500/40 rounded-xl p-4 space-y-1 transition block">
        <div class="font-bold text-white flex items-center justify-between">
          <span>Documentação API (Swagger)</span>
          <span class="text-blue-400">↗</span>
        </div>
        <p class="text-zinc-400">Endpoints REST e autenticação Bearer JWT / Tokens `lmx_*`.</p>
      </a>
      <a href="https://github.com/ricardtech/linuxmenux/issues" target="_blank" class="bg-[#18181b] border border-zinc-800 hover:border-blue-500/40 rounded-xl p-4 space-y-1 transition block">
        <div class="font-bold text-white flex items-center justify-between">
          <span>Rastreador de Bugs</span>
          <span class="text-blue-400">↗</span>
        </div>
        <p class="text-zinc-400">Reporte falhas ou acompanhe melhorias em andamento.</p>
      </a>
      <div class="bg-[#18181b] border border-zinc-800 rounded-xl p-4 space-y-1">
        <div class="font-bold text-white">Licença &amp; Stack</div>
        <p class="text-zinc-400">GPL v2.0 · FastAPI + Vue 3 + Vite + Bun + Tailwind CSS.</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { APP_VERSION } from '../lib/version'

const version = APP_VERSION
</script>
