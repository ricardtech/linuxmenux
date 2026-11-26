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

      <!-- 5. Firewall Completo -->
      <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-center justify-between gap-4 flex-wrap">
          <div class="flex items-start gap-3">
            <Shield class="w-5 h-5 text-orange-400 mt-0.5 shrink-0" />
            <div>
              <h3 class="text-base font-semibold text-white flex items-center gap-2">
                Firewall ({{ securityData.firewall?.engine || 'UFW / iptables' }})
                <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold border"
                  :class="securityData.firewall?.active ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/15 text-amber-400 border-amber-500/30'">
                  {{ securityData.firewall?.active ? 'Ativo' : 'Inativo' }}
                </span>
              </h3>
              <p class="text-xs text-zinc-400 mt-0.5">Gerencie regras de entrada e saída do host diretamente pela interface web.</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button @click="toggleFirewall(!securityData.firewall?.active)" class="px-3 py-1.5 rounded-lg border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 text-xs text-zinc-200 font-medium cursor-pointer">
              {{ securityData.firewall?.active ? 'Desativar Firewall' : 'Ativar Firewall' }}
            </button>
          </div>
        </div>

        <!-- Regras de acesso rápido (1:1 ProxMenux) -->
        <div class="space-y-2">
          <div class="text-xs font-semibold text-zinc-400">Regras de acesso rápido</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div class="flex items-center justify-between p-3 rounded-lg bg-zinc-950/70 border border-zinc-800">
              <div>
                <div class="font-semibold text-white flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-emerald-400"></span> Linux Menux - Monitor</div>
                <div class="text-zinc-400 mt-0.5">Monitorar porta 8008 (TCP)</div>
              </div>
              <button @click="$emit('update:newFwPort', '8008'); $emit('update:newFwProto', 'tcp'); $emit('update:newFwAction', 'allow'); $emit('add-fw-rule')"
                class="px-3 py-1 rounded bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/30 text-emerald-300 font-semibold cursor-pointer">
                Permitir
              </button>
            </div>
            <div class="flex items-center justify-between p-3 rounded-lg bg-zinc-950/70 border border-zinc-800">
              <div>
                <div class="font-semibold text-white flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-blue-400"></span> Acesso SSH</div>
                <div class="text-zinc-400 mt-0.5">Porta padrão SSH 22 (TCP)</div>
              </div>
              <button @click="$emit('update:newFwPort', '22'); $emit('update:newFwProto', 'tcp'); $emit('update:newFwAction', 'allow'); $emit('add-fw-rule')"
                class="px-3 py-1 rounded bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 font-semibold cursor-pointer">
                Permitir
              </button>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between gap-2 flex-wrap">
          <div class="flex gap-1 bg-zinc-950 border border-zinc-800 rounded-lg p-1 text-xs">
            <button v-for="f in ['all', 'allow', 'deny']" :key="f" @click="fwFilter = f"
              class="px-3 py-1 rounded-md cursor-pointer transition"
              :class="fwFilter === f ? 'bg-blue-600 text-white font-semibold' : 'text-zinc-400 hover:text-white'">
              {{ f === 'all' ? 'Todas' : (f === 'allow' ? 'Permitidas' : 'Bloqueadas') }}
            </button>
          </div>
          <input v-model="fwSearch" type="text" placeholder="Filtrar regras..." class="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-1.5 text-xs text-white w-48" />
        </div>

        <div class="max-h-52 overflow-y-auto bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-xs font-mono space-y-1.5">
          <div v-if="!filteredFwRules.length" class="text-zinc-500 font-sans text-center py-4">Nenhuma regra listada para o filtro selecionado.</div>
          <div v-for="(r, idx) in filteredFwRules" :key="idx" class="flex items-center justify-between gap-2 py-1 border-b border-zinc-900 last:border-0 text-zinc-300">
            <span class="truncate">{{ r }}</span>
            <button @click="deleteFwRule(idx + 1)" class="text-red-400 hover:text-red-300 text-xs font-sans shrink-0 cursor-pointer">Remover</button>
          </div>
        </div>

        <div class="flex flex-wrap gap-2 pt-2 border-t border-zinc-800 text-xs">
          <input :value="newFwPort" @input="$emit('update:newFwPort', $event.target.value)" type="text" placeholder="Porta (ex: 8008)" class="w-36 bg-zinc-900 border border-zinc-700 rounded-md px-3 py-1.5 text-white" />
          <select :value="newFwProto" @change="$emit('update:newFwProto', $event.target.value)" class="bg-zinc-900 border border-zinc-700 rounded-md px-3 py-1.5 text-white">
            <option value="tcp">TCP</option>
            <option value="udp">UDP</option>
          </select>
          <select :value="newFwAction" @change="$emit('update:newFwAction', $event.target.value)" class="bg-zinc-900 border border-zinc-700 rounded-md px-3 py-1.5 text-white">
            <option value="allow">Permitir (ALLOW)</option>
            <option value="deny">Bloquear (DENY)</option>
          </select>
          <button @click="$emit('add-fw-rule')" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-1.5 rounded-md font-semibold cursor-pointer">+ Adicionar Regra</button>
        </div>
      </div>

      <!-- 6. Fail2Ban Completo -->
      <div class="bg-[var(--card)] border border-zinc-800/90 rounded-xl p-5 sm:p-6 space-y-4">
        <div class="flex items-center justify-between gap-4 flex-wrap">
          <div class="flex items-start gap-3">
            <ShieldAlert class="w-5 h-5 text-red-400 mt-0.5 shrink-0" />
            <div>
              <h3 class="text-base font-semibold text-white flex items-center gap-2">
                Fail2Ban
                <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold border"
                  :class="securityData.fail2ban?.installed ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' : 'bg-zinc-800 text-zinc-400 border-zinc-700'">
                  {{ securityData.fail2ban?.installed ? 'Instalado' : 'Não instalado' }}
                </span>
              </h3>
              <p class="text-xs text-zinc-400 mt-0.5">Bloqueio automático de IPs com múltiplas falhas de autenticação SSH e serviços.</p>
            </div>
          </div>
          <button v-if="!securityData.fail2ban?.installed" @click="$emit('install-tool', 'fail2ban')" :disabled="secInstalling === 'fail2ban'"
            class="bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-xs px-4 py-1.5 rounded-lg font-semibold cursor-pointer">
            {{ secInstalling === 'fail2ban' ? 'Instalando...' : 'Instalar e Configurar' }}
          </button>
        </div>

        <div v-if="!securityData.fail2ban?.installed" class="p-4 rounded-xl bg-blue-950/30 border border-blue-800/40 text-xs text-blue-200 space-y-1.5">
          <div class="font-semibold text-blue-300">O instalador irá configurar automaticamente:</div>
          <ul class="list-disc list-inside text-zinc-300 space-y-0.5">
            <li>Proteção SSH (sshd) contra força bruta</li>
            <li>Monitoramento de proteção de login do painel</li>
            <li>Configurações básicas de banimento e whitelist</li>
          </ul>
        </div>

        <div class="grid grid-cols-3 gap-3 text-center">
          <div class="bg-zinc-950/60 border border-zinc-800 rounded-lg p-3">
            <div class="text-lg font-bold text-white">{{ (securityData.fail2ban?.jails || []).length }}</div>
            <div class="text-xs text-zinc-400">Jails Ativos</div>
          </div>
          <div class="bg-zinc-950/60 border border-zinc-800 rounded-lg p-3">
            <div class="text-lg font-bold text-amber-400">{{ securityData.fail2ban?.currently_banned || 0 }}</div>
            <div class="text-xs text-zinc-400">IPs Banidos Agora</div>
          </div>
          <div class="bg-zinc-950/60 border border-zinc-800 rounded-lg p-3">
            <div class="text-lg font-bold text-red-400">{{ securityData.fail2ban?.total_banned || 0 }}</div>
            <div class="text-xs text-zinc-400">Total Banido</div>
          </div>
        </div>

        <div v-if="(securityData.fail2ban?.jail_details || []).length" class="space-y-2 text-xs">
          <div v-for="j in securityData.fail2ban.jail_details" :key="j.name" class="p-3 rounded-lg bg-zinc-950/70 border border-zinc-800 space-y-2">
            <div class="flex items-center justify-between">
              <span class="font-bold text-white">Jail: <span class="font-mono text-orange-400">{{ j.name }}</span></span>
              <span class="text-zinc-400">Banidos agora: <strong class="text-amber-400">{{ j.currently_banned }}</strong> · Total: <strong class="text-red-400">{{ j.total_banned }}</strong></span>
            </div>
            <div v-if="(j.banned_ips || []).length" class="flex flex-wrap gap-1.5">
              <span v-for="bip in j.banned_ips" :key="bip" class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-red-500/15 border border-red-500/30 font-mono text-red-300">
                {{ bip }}
                <button @click="unbanFail2banIp(j.name, bip)" class="text-white hover:text-emerald-300 font-sans cursor-pointer">Desbanir</button>
              </span>
            </div>
          </div>
        </div>

        <div class="bg-zinc-950/60 border border-zinc-800 rounded-lg p-3.5 space-y-2.5 text-xs">
          <div class="font-semibold text-zinc-200">Redes Confiáveis (Whitelist / ignoreip)</div>
          <div class="flex gap-2">
            <input v-model="f2bTrustedInput" type="text" placeholder="Ex: 192.168.16.0/24 ou 10.0.0.5" class="flex-1 bg-zinc-900 border border-zinc-700 rounded-md px-3 py-1.5 text-white font-mono" />
            <button @click="addTrustedIp" class="px-3 py-1.5 rounded-md bg-orange-600 hover:bg-orange-500 text-white font-semibold cursor-pointer">+ Adicionar IP</button>
          </div>
          <div v-if="trustedIps.length" class="flex flex-wrap gap-1.5 pt-1">
            <span v-for="ip in trustedIps" :key="ip" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-900 border border-zinc-700 font-mono text-zinc-200">
              {{ ip }}
              <button @click="removeTrustedIp(ip)" class="text-red-400 hover:text-red-300 cursor-pointer">×</button>
            </span>
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
import { Lock, Key, Eye, EyeOff, ShieldCheck, Shield, ShieldAlert, Globe, FileSearch, Copy } from 'lucide-vue-next'
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
defineEmits(['update:newFwPort', 'update:newFwProto', 'update:newFwAction', 'update:newTokenName', 'add-fw-rule', 'generate-token', 'revoke-token', 'install-tool', 'run-lynis'])

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
const f2bTrustedInput = ref('')
const trustedIps = ref([])

const filteredFwRules = computed(() => {
  const rules = props.securityData?.firewall?.rules || []
  return rules.filter((r) => {
    const text = String(r).toLowerCase()
    if (fwFilter.value === 'allow' && !text.includes('allow')) return false
    if (fwFilter.value === 'deny' && !text.includes('deny') && !text.includes('reject')) return false
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

async function toggleFirewall(enable) {
  await fetchApi('/api/security/firewall/toggle', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enable }),
  })
}

async function deleteFwRule(number) {
  await fetchApi('/api/security/firewall/rule', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ number }),
  })
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
