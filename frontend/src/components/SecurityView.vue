<template>
  <section class="space-y-6 animate-fadeIn">
    <!-- Page Header (1:1 ProxMenux security.tsx) -->
    <div>
      <h1 class="text-3xl font-bold text-white">Segurança</h1>
      <p class="text-sm text-zinc-400 mt-1">Autenticação, certificados SSL, tokens de API, firewall, Fail2Ban e auditoria Lynis</p>
    </div>

    <!-- Section 1: Linux Menux - Monitor -->
    <div class="space-y-4">
      <h2 class="text-sm font-semibold uppercase tracking-wider text-cyan-400">Linux Menux - Monitor</h2>

      <!-- 1. Autenticação & Credenciais + 2FA -->
      <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div class="flex items-start gap-3">
            <Lock class="w-5 h-5 text-cyan-400 mt-0.5 shrink-0" />
            <div>
              <h3 class="text-base font-semibold text-white flex items-center gap-2">
                Autenticação do Painel
                <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold border"
                  :class="authEnabled ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/15 text-amber-400 border-amber-500/30'">
                  {{ authEnabled ? 'Ativada' : 'Desativada' }}
                </span>
              </h3>
              <p class="text-xs text-zinc-400 mt-0.5">Proteja o acesso web com senha PBKDF2-HMAC-SHA256, sessão JWT e 2FA TOTP.</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button @click="showPasswordForm = !showPasswordForm" class="px-3 py-1.5 rounded-lg border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 text-xs text-zinc-200 font-medium cursor-pointer">
              {{ authEnabled ? 'Alterar Senha' : 'Ativar Autenticação' }}
            </button>
            <button v-if="authEnabled" @click="disableAuth" class="px-3 py-1.5 rounded-lg bg-red-600/15 hover:bg-red-600/25 border border-red-500/30 text-red-400 text-xs font-medium cursor-pointer">
              Desativar
            </button>
          </div>
        </div>

        <div v-if="showPasswordForm" class="bg-zinc-950/70 border border-zinc-800 rounded-xl p-4 space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <label class="block text-zinc-400 mb-1">Usuário Administrador</label>
              <input v-model="authUser" type="text" class="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-white" />
            </div>
            <div>
              <label class="block text-zinc-400 mb-1">Nova Senha (mín. 8 chars)</label>
              <div class="relative">
                <input v-model="authPass" :type="showAuthPass ? 'text' : 'password'" placeholder="••••••••" class="w-full bg-zinc-900 border border-zinc-700 rounded-md pl-3 pr-9 py-2 text-white" />
                <button type="button" @click="showAuthPass = !showAuthPass" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer">
                  <EyeOff v-if="showAuthPass" class="w-4 h-4" /><Eye v-else class="w-4 h-4" />
                </button>
              </div>
            </div>
            <div>
              <label class="block text-zinc-400 mb-1">Confirmar Nova Senha</label>
              <div class="relative">
                <input v-model="authPassConfirm" :type="showAuthPassConfirm ? 'text' : 'password'" placeholder="••••••••" class="w-full bg-zinc-900 border border-zinc-700 rounded-md pl-3 pr-9 py-2 text-white" />
                <button type="button" @click="showAuthPassConfirm = !showAuthPassConfirm" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer">
                  <EyeOff v-if="showAuthPassConfirm" class="w-4 h-4" /><Eye v-else class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-between pt-1 text-xs">
            <span :class="authErr ? 'text-red-400' : 'text-emerald-400'">{{ authErr || authMsg }}</span>
            <div class="flex gap-2">
              <button @click="showPasswordForm = false" class="px-3 py-1.5 rounded-md border border-zinc-700 text-zinc-400 hover:text-white cursor-pointer">Cancelar</button>
              <button @click="saveAuthCredentials" class="px-4 py-1.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white font-semibold cursor-pointer">Salvar Credencial</button>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between pt-3 border-t border-zinc-800/70 text-xs">
          <div>
            <span class="text-zinc-300 font-medium">Autenticação em Dois Fatores (2FA / TOTP)</span>
            <p class="text-zinc-500">Camada extra com aplicativo autenticador (Google Authenticator / Authy).</p>
          </div>
          <span class="px-2.5 py-0.5 rounded-full border bg-zinc-900 border-zinc-700 text-zinc-400">SQLite Local · Protegido via JWT</span>
        </div>
      </div>

      <!-- 2. SSL / HTTPS / Cloudflare Tunnel -->
      <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div class="flex items-start gap-3">
            <ShieldCheck class="w-5 h-5 text-emerald-400 mt-0.5 shrink-0" />
            <div>
              <h3 class="text-base font-semibold text-white flex items-center gap-2">
                Certificado SSL / HTTPS
                <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold border"
                  :class="sslInfo.enabled ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' : 'bg-zinc-800 text-zinc-400 border-zinc-700'">
                  {{ sslInfo.mode === 'cloudflare_tunnel' ? 'Cloudflare Tunnel SSL Ativo' : (sslInfo.enabled ? 'SSL Local Configurado' : 'HTTP Local') }}
                </span>
              </h3>
              <p class="text-xs text-zinc-400 mt-0.5">
                {{ sslInfo.mode === 'cloudflare_tunnel' ? 'Domínio protegido automaticamente por TLS Edge via Cloudflare Tunnel (não requer certificado local).' : 'Criptografia TLS para acesso seguro em rede local ou domínio via Reverse Proxy.' }}
              </p>
            </div>
          </div>
          <button v-if="sslInfo.mode !== 'cloudflare_tunnel'" @click="generateSelfSignedSsl" :disabled="sslLoading" class="px-3.5 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/30 text-emerald-300 text-xs font-semibold cursor-pointer">
            {{ sslLoading ? 'Gerando...' : 'Gerar Certificado Auto-Assinado' }}
          </button>
        </div>
        <div v-if="sslMsg" class="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 rounded-lg px-3 py-2">{{ sslMsg }}</div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div class="bg-zinc-950/60 border border-zinc-800 rounded-lg p-3">
            <div class="text-zinc-500">Emissor / CN</div>
            <div class="text-zinc-200 font-mono mt-0.5">{{ sslInfo.issuer || 'linuxmenux.local' }}</div>
          </div>
          <div class="bg-zinc-950/60 border border-zinc-800 rounded-lg p-3">
            <div class="text-zinc-500">Domínio / Origem</div>
            <div class="text-zinc-200 font-mono mt-0.5 truncate">{{ sslInfo.domain || sslInfo.cert_path || '/etc/linuxmenux/ssl/cert.pem' }}</div>
          </div>
          <div class="bg-zinc-950/60 border border-zinc-800 rounded-lg p-3">
            <div class="text-zinc-500">Validade</div>
            <div class="text-zinc-200 font-mono mt-0.5">{{ sslInfo.expires || '365 dias (auto-assinado)' }}</div>
          </div>
        </div>
      </div>

      <!-- 3. Tokens de API & Swagger -->
      <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div class="flex items-start gap-3">
            <Key class="w-5 h-5 text-purple-400 mt-0.5 shrink-0" />
            <div>
              <h3 class="text-base font-semibold text-white">Tokens de API &amp; Documentação</h3>
              <p class="text-xs text-zinc-400 mt-0.5">Chaves <code class="text-purple-300">lmx_*</code> para integrações com N8N, scripts e automações.</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <a href="/docs" target="_blank" class="px-3 py-1.5 rounded-lg bg-blue-600/15 hover:bg-blue-600/25 border border-blue-500/30 text-blue-300 text-xs font-semibold">Swagger /docs ↗</a>
            <a href="/redoc" target="_blank" class="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 text-xs font-semibold">ReDoc ↗</a>
          </div>
        </div>

        <div class="flex flex-wrap gap-2">
          <input :value="newTokenName" @input="$emit('update:newTokenName', $event.target.value)" type="text" placeholder="Nome do token (ex: Home Assistant / N8N)" class="flex-1 min-w-[200px] bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-xs text-white" />
          <button @click="$emit('generate-token')" class="bg-purple-600 hover:bg-purple-500 text-white text-xs px-4 py-2 rounded-lg font-semibold cursor-pointer">+ Gerar Token</button>
        </div>

        <div v-if="lastGeneratedToken" class="p-3.5 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-xs text-emerald-300 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold">Token gerado (copie agora — não será exibido novamente):</span>
            <button @click="copyToken(lastGeneratedToken)" class="px-2.5 py-1 rounded bg-emerald-600/25 hover:bg-emerald-600/40 text-emerald-200 flex items-center gap-1 cursor-pointer">
              <Copy class="w-3.5 h-3.5" /> {{ tokenCopied ? 'Copiado!' : 'Copiar' }}
            </button>
          </div>
          <div class="font-mono break-all bg-black/50 p-2 rounded">{{ lastGeneratedToken }}</div>
          <div class="text-zinc-300 font-mono text-xs">curl -H "Authorization: Bearer {{ lastGeneratedToken }}" {{ originUrl }}/api/system-info</div>
        </div>

        <div class="space-y-2 text-xs">
          <div v-if="!(securityData.api_tokens || []).length" class="text-zinc-500 py-2">Nenhum token ativo. Use <code class="text-zinc-300">Authorization: Bearer &lt;token&gt;</code> nas chamadas à API.</div>
          <div v-for="t in (securityData.api_tokens || [])" :key="t.id" class="flex justify-between items-center p-2.5 bg-zinc-950/60 rounded-lg border border-zinc-800">
            <div>
              <span class="font-semibold text-white">{{ t.name }}</span>
              <span class="text-zinc-400 font-mono ml-2">({{ t.prefix || 'lmx_***' }})</span>
            </div>
            <button @click="$emit('revoke-token', t.id)" class="text-red-400 hover:text-red-300 font-semibold cursor-pointer">Revogar</button>
          </div>
        </div>
      </div>

      <!-- 4. Gateway Seguro (Tailscale) -->
      <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 flex items-center justify-between gap-4 flex-wrap">
        <div class="flex items-start gap-3">
          <Globe class="w-5 h-5 text-blue-400 mt-0.5 shrink-0" />
          <div>
            <h3 class="text-base font-semibold text-white">Security Gateway (Tailscale)</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Acesso remoto criptografado sem abrir portas públicas no roteador.</p>
          </div>
        </div>
        <span class="text-xs px-3 py-1 rounded-full border font-semibold"
          :class="securityData.tailscale?.running ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' : 'bg-zinc-900 text-zinc-400 border-zinc-700'">
          {{ securityData.tailscale?.running ? `Conectado (${securityData.tailscale.ip})` : (securityData.tailscale?.installed ? 'Instalado (Desconectado)' : 'Não instalado') }}
        </span>
      </div>
    </div>

    <!-- Section 2: Sistema Linux (1:1 ProxMenux PVE section) -->
    <div class="space-y-4 pt-2">
      <h2 class="text-sm font-semibold uppercase tracking-wider text-orange-400">Sistema Linux</h2>

      <!-- 5. Firewall Completo (1:1 ProxMenux Monitor) -->
      <div class="bg-[var(--card)] border border-zinc-700/60 rounded-xl p-5 sm:p-6 space-y-4">
        <!-- Cabeçalho -->
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-start gap-2.5">
            <Flame class="w-5 h-5 text-orange-400 mt-0.5 shrink-0" />
            <div>
              <h3 class="text-base font-semibold text-white">Firewall</h3>
              <p class="text-xs text-zinc-400 mt-0.5">Gerencie o estado do firewall do host e regras de acesso simples.</p>
            </div>
          </div>
          <button
            @click="refreshFirewall"
            :disabled="fwRefreshing"
            class="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200 transition cursor-pointer shrink-0 disabled:opacity-50"
          >
            <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': fwRefreshing }" />
            Atualizar
          </button>
        </div>

        <!-- Cards de Status do Motor & Host (2 colunas idênticas ao ProxMenux, sem fundo preto) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <!-- Card 1: Motor detectado -->
          <div class="flex items-center justify-between gap-3 px-4 py-3 rounded-lg bg-white/[0.025] border border-zinc-700/60">
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-8 h-8 rounded-full bg-white/[0.04] border border-zinc-700/60 flex items-center justify-center shrink-0">
                <Globe class="w-4 h-4 text-zinc-400" />
              </div>
              <div class="min-w-0">
                <div class="text-sm font-medium text-white truncate">
                  Motor: {{ firewallEngineName }}
                </div>
                <div class="text-xs text-zinc-400 truncate">
                  {{ firewallInstalledSummary }}
                </div>
              </div>
            </div>
            <span
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-medium shrink-0"
              :class="securityData.firewall?.active
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                : 'bg-white/[0.03] border-zinc-700/60 text-zinc-300'"
            >
              <span class="w-1.5 h-1.5 rounded-full" :class="securityData.firewall?.active ? 'bg-emerald-400' : 'bg-zinc-400'"></span>
              {{ securityData.firewall?.active ? 'Em execução' : (securityData.firewall?.engine_id && securityData.firewall?.engine_id !== 'none' ? 'Detectado' : 'Ausente') }}
            </span>
          </div>

          <!-- Card 2: Firewall do host -->
          <div class="flex items-center justify-between gap-3 px-4 py-3 rounded-lg bg-white/[0.025] border border-zinc-700/60">
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-8 h-8 rounded-full bg-white/[0.04] border border-zinc-700/60 flex items-center justify-center shrink-0">
                <Shield class="w-4 h-4" :class="securityData.firewall?.active ? 'text-emerald-400' : 'text-zinc-400'" />
              </div>
              <div class="min-w-0">
                <div class="text-sm font-medium text-white">Firewall do host</div>
                <div class="text-xs" :class="securityData.firewall?.active ? 'text-emerald-400' : 'text-zinc-400'">
                  {{ securityData.firewall?.active ? 'Habilitado' : 'Desabilitado' }}
                </div>
              </div>
            </div>
            <button
              @click="toggleFirewall(!securityData.firewall?.active)"
              :disabled="fwToggling"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border text-xs font-medium transition cursor-pointer shrink-0 disabled:opacity-50"
              :class="securityData.firewall?.active
                ? 'bg-red-500/10 hover:bg-red-500/20 border-red-500/30 text-red-400'
                : 'bg-emerald-500/10 hover:bg-emerald-500/20 border-emerald-500/30 text-emerald-400'"
            >
              <Power class="w-3.5 h-3.5" />
              {{ fwToggling ? 'Aplicando...' : (securityData.firewall?.active ? 'Desabilitar' : 'Habilitar') }}
            </button>
          </div>
        </div>

        <!-- Banner informativo azul (1:1 ProxMenux) -->
        <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-lg bg-blue-500/10 border border-blue-500/25 text-xs text-blue-300">
          <Info class="w-4 h-4 text-blue-400 shrink-0" />
          <span v-if="!securityData.firewall?.active">
            Libere as portas essenciais (como 8008 e SSH 22) nas regras de acesso rápido antes de habilitar o firewall do host.
          </span>
          <span v-else>
            Firewall <strong>{{ firewallEngineName }}</strong> ativo e protegendo o host{{ securityData.firewall?.default_policy ? ` (${securityData.firewall.default_policy})` : '' }}.
          </span>
        </div>

        <div v-if="fwNotice" class="px-3.5 py-2 rounded-lg text-xs border" :class="fwNoticeError ? 'bg-red-500/10 border-red-500/30 text-red-300' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'">
          {{ fwNotice }}
        </div>

        <!-- Regras de acesso rápido (1:1 ProxMenux) -->
        <div class="space-y-2">
          <div class="text-xs font-medium text-zinc-400">Regras de acesso rápido</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div class="flex items-center justify-between gap-3 px-4 py-3 rounded-lg bg-white/[0.025] border border-zinc-700/60">
              <div class="min-w-0">
                <div class="font-medium text-white flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full shrink-0" :class="securityData.firewall?.has_port_8008 ? 'bg-emerald-400' : 'bg-amber-400'"></span>
                  Linux Menux - Monitor
                </div>
                <div class="text-zinc-400 mt-0.5">Monitorar porta 8008</div>
              </div>
              <span v-if="securityData.firewall?.has_port_8008" class="text-xs text-emerald-400 font-medium shrink-0">Permitida</span>
              <button
                v-else
                @click="allowQuickPort('8008', 'tcp')"
                class="px-3 py-1 rounded-md bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 font-medium cursor-pointer shrink-0 transition"
              >
                Permitir
              </button>
            </div>

            <div class="flex items-center justify-between gap-3 px-4 py-3 rounded-lg bg-white/[0.025] border border-zinc-700/60">
              <div class="min-w-0">
                <div class="font-medium text-white flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 shrink-0"></span>
                  Acesso SSH
                </div>
                <div class="text-zinc-400 mt-0.5">A porta SSH 22 para administração remota.</div>
              </div>
              <span v-if="securityData.firewall?.has_port_22" class="text-xs text-emerald-400 font-medium shrink-0">Permitida</span>
              <button
                v-else
                @click="allowQuickPort('22', 'tcp')"
                class="px-3 py-1 rounded-md bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 font-medium cursor-pointer shrink-0 transition"
              >
                Permitir
              </button>
            </div>
          </div>
        </div>

        <!-- Cabeçalho da lista de regras (1:1 ProxMenux) -->
        <div class="flex items-center justify-between gap-3 flex-wrap pt-1">
          <div class="flex items-center gap-3 flex-wrap">
            <span class="text-xs text-zinc-400 font-medium">
              {{ parsedFwRules.length }} {{ parsedFwRules.length === 1 ? 'regra' : 'regras' }}
            </span>
            <div v-if="parsedFwRules.length > 0" class="flex items-center gap-2">
              <div class="flex gap-1 bg-white/[0.03] border border-zinc-700/60 rounded-lg p-0.5 text-xs">
                <button
                  v-for="f in ['all', 'allow', 'deny']"
                  :key="f"
                  @click="fwFilter = f"
                  class="px-2.5 py-0.5 rounded-md cursor-pointer transition"
                  :class="fwFilter === f ? 'bg-white/[0.1] text-white font-medium' : 'text-zinc-400 hover:text-zinc-200'"
                >
                  {{ f === 'all' ? 'Todas' : (f === 'allow' ? 'Permitidas' : 'Bloqueadas') }}
                </button>
              </div>
              <input
                v-model="fwSearch"
                type="text"
                placeholder="Filtrar regras..."
                class="bg-white/[0.03] border border-zinc-700/60 rounded-lg px-2.5 py-1 text-xs text-white placeholder-zinc-500 w-36 sm:w-44 focus:outline-none focus:border-zinc-500"
              />
            </div>
          </div>

          <button
            @click="showAddFwModal = true"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-orange-500/30 bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 text-xs font-medium cursor-pointer transition"
          >
            <Plus class="w-3.5 h-3.5" />
            Adicionar regra
          </button>
        </div>

        <!-- Lista de regras ou Empty State tracejado (1:1 ProxMenux, zero fundo preto) -->
        <div
          v-if="!filteredFwRules.length"
          class="border border-dashed border-zinc-700/70 rounded-lg py-10 px-4 text-center bg-white/[0.015]"
        >
          <Shield class="w-8 h-8 text-zinc-500 mx-auto mb-2.5" />
          <div class="text-sm font-medium text-zinc-300">
            {{ parsedFwRules.length ? 'Nenhuma regra encontrada para o filtro.' : 'Ainda não há regras de firewall.' }}
          </div>
          <div class="text-xs text-zinc-500 mt-1">
            Adicione uma regra ou use uma predefinição acima.
          </div>
        </div>

        <div
          v-else
          class="max-h-64 overflow-y-auto bg-white/[0.02] border border-zinc-700/60 rounded-lg divide-y divide-zinc-800/70 text-xs"
        >
          <div
            v-for="(r, idx) in filteredFwRules"
            :key="r.number || idx"
            class="flex items-center justify-between gap-3 px-4 py-2.5 hover:bg-white/[0.02] transition"
          >
            <div class="flex items-center gap-3 min-w-0">
              <span class="text-zinc-500 font-mono w-6 shrink-0">#{{ r.number || (idx + 1) }}</span>
              <span
                class="px-2 py-0.5 rounded text-[11px] font-semibold uppercase border shrink-0"
                :class="r.action === 'deny'
                  ? 'bg-red-500/10 border-red-500/30 text-red-400'
                  : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'"
              >
                {{ r.action_label || (r.action === 'deny' ? 'DENY' : 'ALLOW') }}
              </span>
              <span class="font-mono text-zinc-200 truncate">{{ r.target || r.raw }}</span>
              <span v-if="r.from_ip" class="text-zinc-500 hidden sm:inline truncate">← {{ r.from_ip }}</span>
            </div>
            <button
              @click="deleteFwRule(r.number || (idx + 1))"
              class="inline-flex items-center gap-1 text-red-400 hover:text-red-300 text-xs shrink-0 cursor-pointer"
              title="Remover regra"
            >
              <Trash2 class="w-3.5 h-3.5" />
              <span class="hidden sm:inline">Remover</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Modal Adicionar Regra de Firewall -->
      <div
        v-if="showAddFwModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4"
        @click.self="showAddFwModal = false"
      >
        <div class="w-full max-w-md bg-[var(--card)] border border-zinc-700/80 rounded-xl p-5 space-y-4 shadow-2xl">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Flame class="w-4 h-4 text-orange-400" />
              <h4 class="text-sm font-semibold text-white">Adicionar regra de firewall</h4>
            </div>
            <button @click="showAddFwModal = false" class="text-zinc-400 hover:text-white cursor-pointer">
              <X class="w-4 h-4" />
            </button>
          </div>
          <div class="space-y-3 text-xs">
            <div>
              <label class="block text-zinc-400 mb-1">Porta (1 - 65535)</label>
              <input
                :value="newFwPort"
                @input="$emit('update:newFwPort', $event.target.value)"
                type="text"
                placeholder="Ex: 8008, 443, 8080"
                class="w-full bg-white/[0.04] border border-zinc-700 rounded-lg px-3 py-2 text-white placeholder-zinc-500 focus:outline-none focus:border-orange-500/60"
              />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-zinc-400 mb-1">Protocolo</label>
                <select
                  :value="newFwProto"
                  @change="$emit('update:newFwProto', $event.target.value)"
                  class="w-full bg-white/[0.04] border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none"
                >
                  <option value="tcp" class="bg-zinc-900">TCP</option>
                  <option value="udp" class="bg-zinc-900">UDP</option>
                </select>
              </div>
              <div>
                <label class="block text-zinc-400 mb-1">Ação</label>
                <select
                  :value="newFwAction"
                  @change="$emit('update:newFwAction', $event.target.value)"
                  class="w-full bg-white/[0.04] border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none"
                >
                  <option value="allow" class="bg-zinc-900">Permitir (ALLOW)</option>
                  <option value="deny" class="bg-zinc-900">Bloquear (DENY)</option>
                </select>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800/80 text-xs">
            <button
              @click="showAddFwModal = false"
              class="px-3 py-1.5 rounded-lg border border-zinc-700 text-zinc-300 hover:bg-white/[0.04] cursor-pointer"
            >
              Cancelar
            </button>
            <button
              @click="submitNewFwRule"
              class="px-4 py-1.5 rounded-lg bg-orange-500 hover:bg-orange-400 text-white font-semibold cursor-pointer"
            >
              Adicionar regra
            </button>
          </div>
        </div>
      </div>

      <!-- 6. Fail2Ban Completo (1:1 ProxMenux Monitor, zero fundo preto) -->
      <div class="bg-[var(--card)] border border-zinc-700/60 rounded-xl p-5 sm:p-6 space-y-4">
        <!-- Cabeçalho -->
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div class="flex items-start gap-2.5">
            <Bug class="w-5 h-5 text-red-400 mt-0.5 shrink-0" />
            <div>
              <h3 class="text-base font-semibold text-white">Fail2Ban</h3>
              <p class="text-xs text-zinc-400 mt-0.5">Bloqueie tentativas repetidas de login com falha no SSH e no Monitor.</p>
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button
              @click="refreshFail2ban"
              :disabled="f2bRefreshing"
              class="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200 transition cursor-pointer disabled:opacity-50"
            >
              <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': f2bRefreshing }" />
              Atualizar
            </button>
            <button
              v-if="securityData.fail2ban?.installed"
              @click="showF2bUninstallConfirm = true"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-red-500/30 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-medium cursor-pointer transition"
            >
              <Trash2 class="w-3.5 h-3.5" />
              Desinstalar
            </button>
            <button
              v-else
              @click="showF2bInstallModal = true"
              :disabled="secInstalling === 'fail2ban'"
              class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-xs font-semibold cursor-pointer transition"
            >
              {{ secInstalling === 'fail2ban' ? 'Instalando...' : 'Instalar e Configurar' }}
            </button>
          </div>
        </div>

        <!-- Card de Status do Serviço -->
        <div class="flex items-center justify-between gap-3 px-4 py-3 rounded-lg bg-white/[0.025] border border-zinc-700/60">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-9 h-9 rounded-full bg-white/[0.04] border border-zinc-700/60 flex items-center justify-center shrink-0">
              <Bug class="w-4 h-4" :class="securityData.fail2ban?.running ? 'text-emerald-400' : 'text-zinc-400'" />
            </div>
            <div class="min-w-0">
              <div class="text-sm font-medium text-white truncate">
                Fail2Ban {{ securityData.fail2ban?.version || '' }}
              </div>
              <div class="text-xs text-zinc-400">
                {{ securityData.fail2ban?.running ? 'Serviço em execução' : (securityData.fail2ban?.installed ? 'Serviço parado' : 'Não instalado neste sistema') }}
              </div>
            </div>
          </div>
          <span
            class="px-3 py-1 rounded-md border text-xs font-medium shrink-0"
            :class="securityData.fail2ban?.running
              ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
              : 'bg-white/[0.03] border-zinc-700/60 text-zinc-400'"
          >
            {{ securityData.fail2ban?.running ? 'Ativo' : (securityData.fail2ban?.installed ? 'Inativo' : 'Desativado') }}
          </span>
        </div>

        <!-- Endereços IP e redes confiáveis (1:1 ProxMenux, sem fundo preto) -->
        <div class="rounded-lg bg-white/[0.02] border border-zinc-700/60 overflow-hidden">
          <div class="flex items-center justify-between gap-3 px-4 py-3 border-b border-zinc-800/80 flex-wrap">
            <div class="flex items-center gap-2.5 min-w-0">
              <div class="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center shrink-0">
                <Globe class="w-4 h-4 text-emerald-400" />
              </div>
              <div class="min-w-0">
                <div class="text-sm font-medium text-white">Endereços IP e redes confiáveis</div>
                <div class="text-xs text-zinc-400">Fail2Ban nunca bloqueará esses endereços.</div>
              </div>
            </div>
            <button
              @click="showAddTrustedModal = true"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-orange-500/30 bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 text-xs font-medium cursor-pointer transition shrink-0"
            >
              <Plus class="w-3.5 h-3.5" />
              Adicionar endereço/rede
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="border-b border-zinc-800/80 text-zinc-500 uppercase tracking-wider text-[11px]">
                <tr>
                  <th class="px-4 py-2.5 font-medium">STATUS</th>
                  <th class="px-4 py-2.5 font-medium">TIPO</th>
                  <th class="px-4 py-2.5 font-medium">ENDEREÇO/REDE</th>
                  <th class="px-4 py-2.5 font-medium text-right">AÇÕES</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-zinc-800/60">
                <tr>
                  <td class="px-4 py-2.5">
                    <span class="px-2 py-0.5 rounded bg-white/[0.05] border border-zinc-700/60 text-zinc-300 font-medium text-[11px]">SISTEMA</span>
                  </td>
                  <td class="px-4 py-2.5">
                    <span class="px-2 py-0.5 rounded bg-purple-500/15 border border-purple-500/30 text-purple-300 font-mono text-[11px]">CIDR</span>
                  </td>
                  <td class="px-4 py-2.5 font-mono text-zinc-200">127.0.0.0/8</td>
                  <td class="px-4 py-2.5 text-right text-zinc-500">
                    <span class="inline-flex items-center gap-1"><Lock class="w-3 h-3" /> Obrigatório</span>
                  </td>
                </tr>
                <tr>
                  <td class="px-4 py-2.5">
                    <span class="px-2 py-0.5 rounded bg-white/[0.05] border border-zinc-700/60 text-zinc-300 font-medium text-[11px]">SISTEMA</span>
                  </td>
                  <td class="px-4 py-2.5">
                    <span class="px-2 py-0.5 rounded bg-blue-500/15 border border-blue-500/30 text-blue-300 font-mono text-[11px]">IP</span>
                  </td>
                  <td class="px-4 py-2.5 font-mono text-zinc-200">::1</td>
                  <td class="px-4 py-2.5 text-right text-zinc-500">
                    <span class="inline-flex items-center gap-1"><Lock class="w-3 h-3" /> Obrigatório</span>
                  </td>
                </tr>
                <tr v-for="ip in trustedIps" :key="ip">
                  <td class="px-4 py-2.5">
                    <span class="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-medium text-[11px]">CUSTOM</span>
                  </td>
                  <td class="px-4 py-2.5">
                    <span class="px-2 py-0.5 rounded bg-white/[0.05] border border-zinc-700/60 text-zinc-300 font-mono text-[11px]">{{ ip.includes('/') ? 'CIDR' : 'IP' }}</span>
                  </td>
                  <td class="px-4 py-2.5 font-mono text-zinc-200">{{ ip }}</td>
                  <td class="px-4 py-2.5 text-right">
                    <button @click="removeTrustedIp(ip)" class="text-red-400 hover:text-red-300 cursor-pointer font-medium">Remover</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="px-4 py-2.5 bg-amber-500/[0.06] border-t border-amber-500/20 text-xs text-amber-300/90 flex items-center gap-2">
            <AlertTriangle class="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>Confie apenas nos endereços que você controla. Se você confiar em uma rede inteira, o Fail2Ban também ignorará um dispositivo comprometido nessa rede.</span>
          </div>
        </div>

        <!-- 4 Cards de KPI (1:1 ProxMenux) -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 text-center">
          <div class="bg-white/[0.025] border border-zinc-700/60 rounded-lg py-3.5 px-3">
            <div class="text-xl font-bold text-white">{{ (securityData.fail2ban?.jails || []).length }}</div>
            <div class="text-[11px] uppercase tracking-wider text-zinc-400 mt-1">PROTEÇÕES</div>
          </div>
          <div class="bg-white/[0.025] border border-zinc-700/60 rounded-lg py-3.5 px-3">
            <div class="text-xl font-bold text-white">{{ securityData.fail2ban?.currently_banned || 0 }}</div>
            <div class="text-[11px] uppercase tracking-wider text-zinc-400 mt-1">IPS BLOQUEADOS</div>
          </div>
          <div class="bg-orange-500/[0.06] border border-orange-500/25 rounded-lg py-3.5 px-3">
            <div class="text-xl font-bold text-orange-400">{{ securityData.fail2ban?.total_banned || 0 }}</div>
            <div class="text-[11px] uppercase tracking-wider text-orange-400/80 mt-1">TOTAL DE BLOCOS</div>
          </div>
          <div class="bg-amber-500/[0.06] border border-amber-500/25 rounded-lg py-3.5 px-3">
            <div class="text-xl font-bold text-amber-400">{{ securityData.fail2ban?.total_failed || 0 }}</div>
            <div class="text-[11px] uppercase tracking-wider text-amber-400/80 mt-1">TENTATIVAS FALHADAS</div>
          </div>
        </div>

        <!-- Abas Proteções / Atividade (1:1 ProxMenux) -->
        <div class="grid grid-cols-2 rounded-lg overflow-hidden border border-zinc-700/60 bg-white/[0.02] text-xs font-medium">
          <button
            @click="f2bActiveTab = 'jails'"
            class="flex items-center justify-center gap-2 py-2.5 px-3 cursor-pointer transition"
            :class="f2bActiveTab === 'jails' ? 'bg-red-500 text-white font-semibold' : 'text-zinc-400 hover:text-white'"
          >
            <Shield class="w-3.5 h-3.5" />
            Proteções e IPs bloqueados
          </button>
          <button
            @click="loadFail2banActivity()"
            class="flex items-center justify-center gap-2 py-2.5 px-3 cursor-pointer transition"
            :class="f2bActiveTab === 'activity' ? 'bg-red-500 text-white font-semibold' : 'text-zinc-400 hover:text-white'"
          >
            <Clock class="w-3.5 h-3.5" />
            Atividade
          </button>
        </div>

        <!-- Conteúdo Aba: Proteções e IPs bloqueados -->
        <div v-if="f2bActiveTab === 'jails'" class="space-y-3 text-xs">
          <div
            v-if="!(securityData.fail2ban?.jail_details || []).length"
            class="border border-dashed border-zinc-700/70 rounded-lg py-8 px-4 text-center bg-white/[0.015] text-zinc-400"
          >
            {{ securityData.fail2ban?.installed ? 'Nenhum jail ativo encontrado no Fail2Ban.' : 'Instale o Fail2Ban para ativar as proteções automáticas (SSH e Monitor).' }}
          </div>

          <div
            v-for="j in (securityData.fail2ban?.jail_details || [])"
            :key="j.name"
            class="rounded-lg bg-white/[0.025] border border-zinc-700/60 overflow-hidden"
          >
            <div class="flex items-center justify-between gap-3 px-4 py-3 border-b border-zinc-800/70 flex-wrap">
              <div class="flex items-center gap-2 flex-wrap min-w-0">
                <span class="w-2 h-2 rounded-full bg-emerald-400 shrink-0"></span>
                <span class="font-semibold text-white">{{ j.label || j.name }}</span>
                <span class="font-mono text-zinc-400">{{ j.name }}</span>
                <span class="text-zinc-400 truncate">{{ j.description }}</span>
              </div>
              <div class="flex items-center gap-3 text-zinc-400 shrink-0 flex-wrap">
                <span>Limite de tentativas: <strong class="text-white">{{ j.maxretry || 3 }}</strong></span>
                <span>Tempo de bloqueio: <strong class="text-white">{{ j.bantime || '1h' }}</strong></span>
                <span>Período: <strong class="text-white">{{ j.findtime || '10m' }}</strong></span>
              </div>
            </div>

            <div class="flex items-center gap-5 px-4 py-2.5 border-b border-zinc-800/70 flex-wrap text-zinc-400">
              <span>Atualmente bloqueado: <strong class="text-emerald-400">{{ j.currently_banned || 0 }}</strong></span>
              <span>Total de blocos: <strong class="text-orange-400">{{ j.total_banned || 0 }}</strong></span>
              <span>Falha agora: <strong class="text-amber-400">{{ j.currently_failed || 0 }}</strong></span>
              <span>Falha total: <strong class="text-zinc-200">{{ j.total_failed || 0 }}</strong></span>
            </div>

            <div class="px-4 py-3">
              <div v-if="(j.banned_ips || []).length" class="flex flex-wrap gap-1.5">
                <span
                  v-for="bip in j.banned_ips"
                  :key="bip"
                  class="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-red-500/10 border border-red-500/30 font-mono text-red-300"
                >
                  {{ bip }}
                  <button @click="unbanFail2banIp(j.name, bip)" class="text-white hover:text-emerald-300 font-sans font-medium cursor-pointer">Desbanir</button>
                </span>
              </div>
              <div v-else class="text-center text-zinc-500 py-0.5">
                Nenhum endereço IP está bloqueado no momento.
              </div>
            </div>
          </div>
        </div>

        <!-- Conteúdo Aba: Atividade -->
        <div v-else class="rounded-lg bg-white/[0.02] border border-zinc-700/60 overflow-hidden text-xs">
          <div v-if="f2bActivityLoading" class="py-8 text-center text-zinc-400">Carregando atividade recente...</div>
          <div v-else-if="!f2bActivity.length" class="py-8 text-center text-zinc-500">Nenhum evento recente registrado nos logs do Fail2Ban.</div>
          <div v-else class="max-h-64 overflow-y-auto divide-y divide-zinc-800/70">
            <div v-for="(ev, i) in f2bActivity" :key="i" class="flex items-center justify-between gap-3 px-4 py-2.5">
              <div class="flex items-center gap-2.5 min-w-0">
                <span
                  class="px-2 py-0.5 rounded font-semibold uppercase text-[11px] border shrink-0"
                  :class="ev.action === 'Ban' ? 'bg-red-500/10 border-red-500/30 text-red-400' : (ev.action === 'Unban' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-amber-500/10 border-amber-500/30 text-amber-400')"
                >
                  {{ ev.action }}
                </span>
                <span class="font-mono text-zinc-200">{{ ev.ip }}</span>
                <span class="text-zinc-500 font-mono">[{{ ev.jail }}]</span>
              </div>
              <span class="text-zinc-500 font-mono shrink-0">{{ ev.timestamp }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Adicionar IP / Rede Confiável -->
      <div
        v-if="showAddTrustedModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4"
        @click.self="showAddTrustedModal = false"
      >
        <div class="w-full max-w-md bg-[var(--card)] border border-zinc-700/80 rounded-xl p-5 space-y-4 shadow-2xl">
          <div class="flex items-center justify-between">
            <h4 class="text-sm font-semibold text-white">Adicionar endereço/rede confiável</h4>
            <button @click="showAddTrustedModal = false" class="text-zinc-400 hover:text-white cursor-pointer"><X class="w-4 h-4" /></button>
          </div>
          <div class="space-y-2 text-xs">
            <label class="block text-zinc-400">IPv4, IPv6 ou CIDR</label>
            <input
              v-model="f2bTrustedInput"
              type="text"
              placeholder="Ex: 192.168.16.0/24 ou 100.64.0.10"
              class="w-full bg-white/[0.04] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono placeholder-zinc-500 focus:outline-none focus:border-orange-500/60"
            />
          </div>
          <div class="flex justify-end gap-2 pt-2 border-t border-zinc-800/80 text-xs">
            <button @click="showAddTrustedModal = false" class="px-3 py-1.5 rounded-lg border border-zinc-700 text-zinc-300 hover:bg-white/[0.04] cursor-pointer">Cancelar</button>
            <button @click="addTrustedIp" class="px-4 py-1.5 rounded-lg bg-orange-500 hover:bg-orange-400 text-white font-semibold cursor-pointer">Adicionar</button>
          </div>
        </div>
      </div>

      <!-- Modal Confirmação Instalação Fail2Ban (1:1 Imagem 3 ProxMenux) -->
      <div
        v-if="showF2bInstallModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4"
        @click.self="showF2bInstallModal = false"
      >
        <div class="w-full max-w-lg bg-[var(--card)] border border-zinc-700/80 rounded-xl p-6 space-y-4 shadow-2xl">
          <h4 class="text-base font-bold text-white">Instale Fail2Ban</h4>
          <p class="text-xs text-zinc-300">Fail2Ban não está instalado neste sistema.</p>
          <div class="text-xs text-zinc-300 space-y-1.5">
            <div class="font-medium text-zinc-200">Isto irá instalar e configurar o Fail2Ban com:</div>
            <ul class="space-y-1 text-zinc-300 pl-1">
              <li>- Proteção SSH (modo agressivo) (max 2 novas tentativas, 9h proibir)</li>
              <li>- Proteção do Linux Menux - Monitor (porta 8008 + proxy reverso, max 3 novas tentativas, 1h proibir)</li>
              <li>- Back-end de firewall detectado automaticamente (nftables/iptables)</li>
              <li>- Ajusta o nível de log do diário, se necessário, para captura de logs de autenticação</li>
              <li>- Proteção SSH: MaxAuthTries definido como 3 (recomendação Lynis)</li>
            </ul>
          </div>
          <p class="text-xs text-zinc-300 pt-1">Você quer prosseguir?</p>
          <div class="grid grid-cols-2 gap-3 pt-1">
            <button
              @click="confirmInstallFail2ban"
              class="py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold cursor-pointer transition"
            >
              Sim
            </button>
            <button
              @click="showF2bInstallModal = false"
              class="py-2 rounded-lg bg-white/[0.05] hover:bg-white/[0.08] border border-zinc-700 text-zinc-200 text-xs font-medium cursor-pointer transition"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>

      <!-- Modal Confirmação Desinstalação Fail2Ban -->
      <div
        v-if="showF2bUninstallConfirm"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4"
        @click.self="showF2bUninstallConfirm = false"
      >
        <div class="w-full max-w-md bg-[var(--card)] border border-zinc-700/80 rounded-xl p-5 space-y-4 shadow-2xl">
          <h4 class="text-sm font-semibold text-white">Desinstalar Fail2Ban</h4>
          <p class="text-xs text-zinc-300">Deseja realmente parar o serviço e remover o Fail2Ban deste host?</p>
          <div class="grid grid-cols-2 gap-3 pt-1 text-xs">
            <button
              @click="uninstallFail2ban"
              :disabled="f2bUninstalling"
              class="py-2 rounded-lg bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-semibold cursor-pointer"
            >
              {{ f2bUninstalling ? 'Desinstalando...' : 'Confirmar' }}
            </button>
            <button
              @click="showF2bUninstallConfirm = false"
              class="py-2 rounded-lg bg-white/[0.05] hover:bg-white/[0.08] border border-zinc-700 text-zinc-200 font-medium cursor-pointer"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>

      <!-- 7. Auditoria Lynis Completa -->
      <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-center justify-between gap-4 flex-wrap">
          <div class="flex items-start gap-3">
            <FileSearch class="w-5 h-5 text-blue-400 mt-0.5 shrink-0" />
            <div>
              <h3 class="text-base font-semibold text-white">Auditoria de Segurança Lynis</h3>
              <p class="text-xs text-zinc-400 mt-0.5">Varredura profunda de kernel, permissões, SSH, pacotes e compliance Linux.</p>
            </div>
          </div>
          <div class="flex gap-2">
            <button v-if="!securityData.lynis?.installed" @click="$emit('install-tool', 'lynis')" :disabled="secInstalling === 'lynis'"
              class="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs px-4 py-1.5 rounded-lg font-semibold cursor-pointer">
              {{ secInstalling === 'lynis' ? 'Instalando...' : 'Instalar Lynis' }}
            </button>
            <button v-else @click="$emit('run-lynis')" :disabled="lynisRunning"
              class="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs px-4 py-1.5 rounded-lg font-semibold cursor-pointer">
              {{ lynisRunning ? 'Auditando...' : 'Executar Auditoria Completa' }}
            </button>
            <button v-if="(securityData.lynis?.reports || []).length" @click="exportLynisPdf"
              class="bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 text-xs px-3.5 py-1.5 rounded-lg font-semibold cursor-pointer">
              Exportar PDF
            </button>
          </div>
        </div>

        <div v-if="(securityData.lynis?.reports || []).length" class="space-y-3">
          <div class="grid grid-cols-3 gap-3 text-center text-xs">
            <div class="p-3 bg-zinc-950/70 rounded-lg border border-zinc-800">
              <div class="text-xl font-bold text-blue-400">{{ securityData.lynis.reports[0].hardening_index }}/100</div>
              <div class="text-zinc-400 mt-0.5">Índice de Hardening</div>
            </div>
            <div class="p-3 bg-zinc-950/70 rounded-lg border border-zinc-800">
              <div class="text-xl font-bold text-amber-400">{{ securityData.lynis.reports[0].warnings }}</div>
              <div class="text-zinc-400 mt-0.5">Avisos Críticos</div>
            </div>
            <div class="p-3 bg-zinc-950/70 rounded-lg border border-zinc-800">
              <div class="text-xl font-bold text-zinc-200">{{ securityData.lynis.reports[0].suggestions }}</div>
              <div class="text-zinc-400 mt-0.5">Sugestões</div>
            </div>
          </div>
          <div class="w-full h-2 rounded-full bg-zinc-900 overflow-hidden">
            <div class="h-full bg-blue-500 transition-all" :style="{ width: `${Math.min(100, securityData.lynis.reports[0].hardening_index || 0)}%` }"></div>
          </div>
        </div>
        <div v-else class="text-xs text-zinc-500 bg-zinc-950/50 border border-zinc-800 rounded-lg p-4 text-center">
          {{ securityData.lynis?.installed ? 'Clique em "Executar Auditoria Completa" para gerar o primeiro relatório Lynis.' : 'Instale o Lynis para auditar o hardening do sistema.' }}
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Lock, Key, Eye, EyeOff, ShieldCheck, Shield, ShieldAlert, Globe, FileSearch, Copy, Flame, RefreshCw, Power, Info, Plus, Trash2, X, Bug, AlertTriangle, Clock } from 'lucide-vue-next'
import { fetchApi, setAuthToken } from '../lib/api-config'

const props = defineProps({
  securityData: { type: Object, default: () => ({}) },
  newFwPort: { type: String, default: '' },
  newFwProto: { type: String, default: 'tcp' },
  newFwAction: { type: String, default: 'allow' },
  newTokenName: { type: String, default: '' },
  lastGeneratedToken: { type: String, default: '' },
  secInstalling: { type: String, default: '' },
  lynisRunning: { type: Boolean, default: false },
})
const emit = defineEmits(['update:newFwPort', 'update:newFwProto', 'update:newFwAction', 'update:newTokenName', 'add-fw-rule', 'refresh-security', 'generate-token', 'revoke-token', 'install-tool', 'run-lynis'])

const authEnabled = ref(false)
const authUser = ref('admin')
const authPass = ref('')
const authPassConfirm = ref('')
const showAuthPass = ref(false)
const showAuthPassConfirm = ref(false)
const showPasswordForm = ref(false)
const authMsg = ref('')
const authErr = ref('')
const tokenCopied = ref(false)
const originUrl = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8008'

const sslInfo = ref({ enabled: false })
const sslLoading = ref(false)
const sslMsg = ref('')

const fwFilter = ref('all')
const fwSearch = ref('')
const showAddFwModal = ref(false)
const fwRefreshing = ref(false)
const fwToggling = ref(false)
const fwNotice = ref('')
const fwNoticeError = ref(false)
const f2bTrustedInput = ref('')
const trustedIps = ref([])
const f2bActiveTab = ref('jails')
const f2bRefreshing = ref(false)
const showAddTrustedModal = ref(false)
const showF2bInstallModal = ref(false)
const showF2bUninstallConfirm = ref(false)
const f2bUninstalling = ref(false)
const f2bActivity = ref([])
const f2bActivityLoading = ref(false)

const firewallEngineName = computed(() => {
  const eng = props.securityData?.firewall?.engine
  return eng && eng !== 'Nenhum' ? eng : 'Não detectado'
})

const firewallInstalledSummary = computed(() => {
  const list = props.securityData?.firewall?.installed_engines || []
  if (!list.length) return 'Nenhum gerenciador (UFW/firewalld/iptables) instalado.'
  const labels = list.map((e) => (e === 'ufw' ? 'UFW' : e))
  return `Detectado: ${labels.join(' · ')}`
})

const parsedFwRules = computed(() => {
  const fw = props.securityData?.firewall || {}
  if (Array.isArray(fw.parsed_rules) && fw.parsed_rules.length) {
    return fw.parsed_rules
  }
  return (fw.rules || []).map((r, i) => {
    const raw = String(r)
    const lower = raw.toLowerCase()
    const isDeny = lower.includes('deny') || lower.includes('reject') || lower.includes('drop')
    return {
      number: String(i + 1),
      target: raw,
      action: isDeny ? 'deny' : 'allow',
      action_label: isDeny ? 'DENY' : 'ALLOW',
      from_ip: '',
      raw,
    }
  })
})

const filteredFwRules = computed(() => {
  return parsedFwRules.value.filter((r) => {
    const text = `${r.target || ''} ${r.raw || ''} ${r.from_ip || ''}`.toLowerCase()
    if (fwFilter.value === 'allow' && r.action !== 'allow') return false
    if (fwFilter.value === 'deny' && r.action !== 'deny') return false
    if (fwSearch.value.trim() && !text.includes(fwSearch.value.trim().toLowerCase())) return false
    return true
  })
})

onMounted(async () => {
  try {
    const [authRes, sslRes, setRes] = await Promise.all([
      fetch('/api/auth/status'),
      fetch('/api/ssl/status'),
      fetch('/api/settings'),
    ])
    if (authRes.ok) {
      const d = await authRes.json()
      authEnabled.value = Boolean(d.enabled)
      if (d.username) authUser.value = d.username
    }
    if (sslRes.ok) sslInfo.value = await sslRes.json()
    if (setRes.ok) {
      const s = await setRes.json()
      trustedIps.value = s.fail2ban_trusted_ips || []
    }
  } catch {}
})

async function saveAuthCredentials() {
  authMsg.value = ''
  authErr.value = ''
  if (!authPass.value || authPass.value.length < 8) {
    authErr.value = 'Senha deve ter pelo menos 8 caracteres.'
    return
  }
  if (authPass.value !== authPassConfirm.value) {
    authErr.value = 'As senhas não conferem.'
    return
  }
  const res = await fetchApi('/api/auth/setup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: authUser.value.trim() || 'admin', password: authPass.value }),
  })
  if (res.ok) {
    const d = await res.json().catch(() => ({}))
    if (d.token) setAuthToken(d.token)
    authEnabled.value = true
    authPass.value = ''
    authPassConfirm.value = ''
    showPasswordForm.value = false
    authMsg.value = 'Credencial salva e proteção ativada.'
  } else {
    authErr.value = 'Erro ao atualizar credencial.'
  }
}

async function disableAuth() {
  const res = await fetchApi('/api/auth/disable', { method: 'POST' })
  if (res.ok) {
    authEnabled.value = false
    authMsg.value = 'Autenticação desativada.'
  }
}

async function generateSelfSignedSsl() {
  sslLoading.value = true
  sslMsg.value = ''
  try {
    const res = await fetchApi('/api/ssl/self-signed', { method: 'POST' })
    if (res.ok) {
      const d = await res.json()
      sslInfo.value = { enabled: true, cert_path: d.cert_path, issuer: 'linuxmenux.local', expires: '365 dias' }
      sslMsg.value = `Certificado gerado em ${d.cert_path}`
    }
  } finally {
    sslLoading.value = false
  }
}

async function refreshFirewall() {
  fwRefreshing.value = true
  try {
    emit('refresh-security')
  } finally {
    setTimeout(() => { fwRefreshing.value = false }, 400)
  }
}

function allowQuickPort(port, proto = 'tcp') {
  emit('update:newFwPort', String(port))
  emit('update:newFwProto', proto)
  emit('update:newFwAction', 'allow')
  emit('add-fw-rule')
}

function submitNewFwRule() {
  if (!String(props.newFwPort || '').trim()) return
  emit('add-fw-rule')
  showAddFwModal.value = false
}

async function toggleFirewall(enable) {
  fwToggling.value = true
  fwNotice.value = ''
  fwNoticeError.value = false
  try {
    const res = await fetchApi('/api/security/firewall/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enable }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok || data.success === false) {
      fwNoticeError.value = true
      fwNotice.value = data.error || data.output || 'Não foi possível alterar o estado do firewall.'
    } else {
      fwNotice.value = enable ? 'Firewall habilitado com sucesso.' : 'Firewall desabilitado.'
    }
    emit('refresh-security')
  } finally {
    fwToggling.value = false
  }
}

async function deleteFwRule(number) {
  fwNotice.value = ''
  fwNoticeError.value = false
  const res = await fetchApi('/api/security/firewall/rule', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ number: String(number) }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok || data.success === false) {
    fwNoticeError.value = true
    fwNotice.value = data.error || data.output || 'Não foi possível remover a regra.'
  }
  emit('refresh-security')
}

async function refreshFail2ban() {
  f2bRefreshing.value = true
  try {
    emit('refresh-security')
    if (f2bActiveTab.value === 'activity') {
      await loadFail2banActivity()
    }
  } finally {
    setTimeout(() => { f2bRefreshing.value = false }, 400)
  }
}

async function loadFail2banActivity() {
  f2bActiveTab.value = 'activity'
  f2bActivityLoading.value = true
  try {
    const res = await fetchApi('/api/security/fail2ban/activity')
    if (res.ok) {
      const d = await res.json()
      f2bActivity.value = d.events || []
    }
  } finally {
    f2bActivityLoading.value = false
  }
}

function confirmInstallFail2ban() {
  showF2bInstallModal.value = false
  emit('install-tool', 'fail2ban')
}

async function uninstallFail2ban() {
  f2bUninstalling.value = true
  try {
    await fetchApi('/api/security/fail2ban/uninstall', { method: 'POST' })
    showF2bUninstallConfirm.value = false
    emit('refresh-security')
  } finally {
    f2bUninstalling.value = false
  }
}

async function addTrustedIp() {
  const ip = f2bTrustedInput.value.trim()
  if (!ip) return
  const res = await fetchApi('/api/security/fail2ban/ignoreip', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ip, action: 'add' }),
  })
  if (res.ok) {
    const d = await res.json()
    trustedIps.value = d.trusted_ips || []
    f2bTrustedInput.value = ''
    showAddTrustedModal.value = false
  }
}

async function removeTrustedIp(ip) {
  const res = await fetchApi('/api/security/fail2ban/ignoreip', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ip, action: 'remove' }),
  })
  if (res.ok) {
    const d = await res.json()
    trustedIps.value = d.trusted_ips || []
  }
}

function copyToken(tok) {
  navigator.clipboard?.writeText(tok)
  tokenCopied.value = true
  setTimeout(() => { tokenCopied.value = false }, 2000)
}

async function unbanFail2banIp(jail, ip) {
  await fetchApi('/api/security/fail2ban/unban', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jail, ip }),
  })
}

function exportLynisPdf() {
  const rep = props.securityData?.lynis?.reports?.[0]
  if (!rep) return
  const w = window.open('', '_blank', 'width=800,height=650')
  if (!w) return
  w.document.write(`<!doctype html><html><head><title>Relatorio Lynis - Linux Menux - Monitor</title><style>body{font-family:sans-serif;padding:32px;color:#111}h1{margin-bottom:4px}.grid{display:flex;gap:16px;margin:20px 0}.card{border:1px solid #ccc;border-radius:8px;padding:16px;flex:1;text-align:center}</style></head><body><h1>Auditoria de Segurança Lynis — Linux Menux - Monitor</h1><p>Data da auditoria: ${rep.timestamp || new Date().toLocaleString('pt-BR')}</p><div class="grid"><div class="card"><h2>${rep.hardening_index}/100</h2><div>Índice de Hardening</div></div><div class="card"><h2>${rep.warnings}</h2><div>Avisos Críticos</div></div><div class="card"><h2>${rep.suggestions}</h2><div>Sugestões</div></div></div></body></html>`)
  w.document.close()
  w.print()
}
</script>
