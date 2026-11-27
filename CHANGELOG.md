# Changelog

Todas as mudanças notáveis do **Linux Menux - Monitor** serão documentadas neste arquivo (formato baseado em Keep a Changelog, com datas no padrão brasileiro `DD/MM/AAAA`).

## [1.4.8] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **27.645 linhas** de código em **94 arquivos-fonte** (`9.535` `.vue` · `7.542` `.py` · `7.610` `.css` · `2.668` `.js` · `272` `.sh` · `18` `.service`).

### Melhorado
- **Diagnóstico AIOps com contexto real completo (`main.py`)**: o endpoint `/api/ai/network-diagnosis` agora envia para a IA os endereços IP e MTU das interfaces físicas e bridges, rota padrão (`ip route show default`), servidores DNS, estado completo do Firewall (`engine`, `active`, política padrão, contagem de regras em `INPUT`/`FORWARD`/`DOCKER-USER`) e portas/redes dos containers Docker em execução, eliminando análises limitadas e permitindo validar NAT, MTU, DNS e isolamento real.

## [1.4.7] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **27.576 linhas** de código em **94 arquivos-fonte** (`9.535` `.vue` · `7.473` `.py` · `7.610` `.css` · `2.668` `.js` · `272` `.sh` · `18` `.service`).

### Adicionado
- **Suporte Multi-Provedor de IA com Modelos Gratuitos (`main.py` & `SettingsView.vue`)**: adicionados **OpenRouter**, **OpenCode Zen**, **Groq**, **Google Gemini**, **Cerebras**, **Mistral AI**, **GitHub Models**, **OpenAI**, **Anthropic (Claude)** e **Ollama (Local)**.
- **Filtro `free` + botão `Só Free` em Modelos (`SettingsView.vue`)**: após carregar modelos do provedor, permite digitar `free` (ou clicar em `Só Free`) para filtrar instantaneamente os modelos gratuitos.
- **Teste real de conexão IA (`POST /api/ai/test`)**: o botão `Salvar e Testar Conexão IA` agora salva os dados e executa uma chamada real ao provedor/modelo, exibindo modal de confirmação com latência (`ms`) e resposta real da IA (ou erro detalhado).

### Corrigido
- **Persistência de Provedor e Ativação de IA (`App.vue` & `linux_ops.py`)**: corrigido `fetchAdminSettings()` e `saveAdminSettings()` que apagavam `ai_provider` e `ai_enabled` ao salvar ou dar `F5`.
- **Diagnóstico AIOps universal (`main.py`)**: `/api/ai/network-diagnosis` agora lê `_resolve_ai_config(cfg)` e funciona com qualquer provedor configurado (não apenas chave legada OpenRouter).
- **Responsividade do campo Modelo + Carregar (`SettingsView.vue`)**: corrigido o overflow horizontal com grid 12 colunas (`min-w-0`) e `flex-col sm:flex-row`.

## [1.4.6] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **27.270 linhas** de código em **94 arquivos-fonte** (`9.405` `.vue` · `7.297` `.py` · `7.610` `.css` · `2.668` `.js` · `272` `.sh` · `18` `.service`).

### Adicionado
- **Persistência da página atual no `F5` (`App.vue`)**: sincronização bidirecional de `activeTab` com `window.location.hash` (`#overview`, `#containers`, `#network-flow`, `#admin-security`, etc.) e `localStorage`, mantendo a tela exata após recarregar a página e suportando navegação via `hashchange`.
- **Topologia de Rede enriquecida (`NetworkView.vue`)**: portados do `MonitorSystem` os filtros de busca por contêiner/nó, botão **Ativos (N)**, legenda Download/Upload e a lista em grid de **Consumidores & Containers Mapeados** abaixo do diagrama SVG ao vivo + análise por IA.

## [1.4.5] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **27.147 linhas** de código em **94 arquivos-fonte** (`9.282` `.vue` · `7.297` `.py` · `7.610` `.css` · `2.668` `.js` · `272` `.sh` · `18` `.service`).

### Corrigido
- **Erro `Instrução ilegal` do Bun durante atualização pelo painel (`scripts/install.sh`)**: quando o `self-update` rodava via `systemd-run` como `root`, o `install.sh` baixava o Bun padrão (que exige AVX2) e falhava com `SIGILL`. Agora ele localiza qualquer Bun funcional já instalado (incluindo `/home/*/.bun/bin/bun`), baixa automaticamente a variante `bun-linux-x64-baseline` em CPUs sem AVX2 e possui fallback automático para `npm`.
- **Limpeza de códigos ANSI no terminal de auto-atualização (`AppSelfUpdateModal.vue`)**: removidos os caracteres de escape (`[0;32m`, `[0;36m`, `[0m`) na exibição do log ao vivo.

## [1.4.4] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **27.120 linhas** de código em **94 arquivos-fonte** (`9.278` `.vue` · `7.297` `.py` · `7.610` `.css` · `2.668` `.js` · `249` `.sh` · `18` `.service`).

### Corrigido
- **Timeout silencioso no `pamac checkupdates -a -q` (`pkg_manager.py` & `metrics_history.py`)**: aumentado o timeout de `45s` para `120s` (o `pamac` com AUR + checagem de espelhos chegava a levar >45s, estourava `TimeoutExpired` e o cache gravava `0 pacotes pendentes`), impedido que respostas com `error` sobrescrevam o cache válido, e removido o filtro que ocultava pacotes nativos listados pelo próprio Pamac GUI (batendo exatamente as `7` atualizações reais).

### Adicionado
- **Detecção de atualizações Flatpak multi-distro (`pkg_manager.py`)**: adicionado suporte universal a `flatpak remote-ls --updates` somando pacotes Flatpak pendentes em Debian, Ubuntu, Manjaro, BigLinux, Fedora e openSUSE.

## [1.4.3] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **27.094 linhas** de código em **94 arquivos-fonte** (`9.278` `.vue` · `7.271` `.py` · `7.610` `.css` · `2.668` `.js` · `249` `.sh` · `18` `.service`).

### Corrigido
- **Auto-atualização via GitHub (`main.py`)**: removido `LINUXMENUX_SKIP_BUILD=1` quando `backend/static/index.html` não está presente no tarball da release do GitHub (já que `static/` fica no `.gitignore`), garantindo que `install.sh` compile o novo frontend Vue 3 durante a atualização pelo painel.
- **Detecção de atualizações AUR no BigLinux/Manjaro (`pkg_manager.py`)**: adicionado flag `-a` em `pamac checkupdates -a -q` (mantendo o filtro `vercmp` anti-downgrade), passando a detectar atualizações reais do AUR em paridade 1:1 com o escudo do sistema.
- **Texto duplicado no rodapé (`App.vue`)**: removida a linha fixa residual `Linux Menux v1.2.9 · Painel de Controle Linux, Docker Swarm & Dokploy · Multi-Distro` que aparecia repetida antes da versão dinâmica.

## [1.4.2] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **27.093 linhas** de código em **94 arquivos-fonte** (`9.279` `.vue` · `7.269` `.py` · `7.610` `.css` · `2.668` `.js` · `249` `.sh` · `18` `.service`).

### Corrigido
- **Versão dessincronizada no cabeçalho por cache (`main.py` & `App.vue`)**: adicionado middleware `Cache-Control: no-store` para `/` e `index.html` (impedindo cache de navegador/CDN em proxy reverso) e sincronizado o badge de versão do cabeçalho/rodapé com `appUpdateInfo.current_version` retornado pelo backend.

## [1.4.1] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **27.085 linhas** de código em **94 arquivos-fonte** (`9.279` `.vue` · `7.261` `.py` · `7.610` `.css` · `2.668` `.js` · `249` `.sh` · `18` `.service`).

### Adicionado
- **Auto-configuração completa do Fail2Ban (`linux_ops.py` & `main.py`)**: ao instalar o Fail2Ban pelo painel, cria automaticamente `/etc/fail2ban/filter.d/linuxmenux.conf` e `/etc/fail2ban/jail.local` com os jails `sshd` (`backend = systemd`, `maxretry = 3`, `findtime = 10m`, `bantime = 1h`) e `linuxmenux` (portas `8008,80,443`, monitorando `/var/log/linuxmenux-auth.log` com IP real via `CF-Connecting-IP`/`X-Forwarded-For`), preservando os IPs da whitelist (`ignoreip`) cadastrados nas configurações.

## [1.4.0] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **27.010 linhas** de código em **94 arquivos-fonte** (`9.279` `.vue` · `7.186` `.py` · `7.610` `.css` · `2.668` `.js` · `249` `.sh` · `18` `.service`).

### Adicionado
- **Terminal ao vivo na auto-atualização do painel (`AppSelfUpdateModal.vue` & `/api/proxmenux/self-update/log`)**: ao clicar em atualizar o **Linux Menux - Monitor**, abre um modal de terminal em tempo real exibindo download, extração, instalação e reinício do serviço, recarregando a página somente após confirmar a nova versão ativa.
- **Dados completos e atividade do Fail2Ban (`linux_ops.py` & `main.py`)**: detecção automática de versão (`fail2ban-client --version`), parâmetros por jail (`maxretry`, `bantime`, `findtime`), contadores de tentativas falhadas (`currently_failed`, `total_failed`), leitura de eventos reais (`/api/security/fail2ban/activity`), sincronização ao vivo de `ignoreip` (`addignoreip`/`delignoreip`) e endpoint de desinstalação (`/api/security/fail2ban/uninstall`).

### Alterado
- **Fail2Ban idêntico ao ProxMenux Monitor (`SecurityView.vue`)**: redesign completo sem fundo preto (`bg-zinc-950`), mantendo o tamanho de fonte padrão do painel, com card de status do serviço, tabela de *Endereços IP e redes confiáveis* (`127.0.0.0/8` e `::1` como `SISTEMA / Obrigatório` + IPs customizados), 4 KPIs (`PROTEÇÕES`, `IPS BLOQUEADOS`, `TOTAL DE BLOCOS`, `TENTATIVAS FALHADAS`), abas *Proteções e IPs bloqueados* / *Atividade*, cards detalhados por jail e modal de confirmação de instalação.
- **Regra de versionamento semântico (`AGENTS.md`)**: após `.9`, o número de versão incrementa o *minor* e zera o *patch* (`1.3.9 → 1.4.0`, nunca `.10` ou `.11`).

### Corrigido
- **Auto-atualização prematura no Frontend (`App.vue`)**: corrigido o polling de `3s` em `/api/auth/status` que recarregava a página antes do `install.sh` terminar (~29s) e reiniciar o serviço na versão nova.

## [1.3.11] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **26.327 linhas** de código em **93 arquivos-fonte** (`8.777` `.vue` · `7.005` `.py` · `7.610` `.css` · `2.668` `.js` · `249` `.sh` · `18` `.service`).

### Alterado
- **Firewall idêntico ao ProxMenux Monitor (`SecurityView.vue`)**: redesign completo do card de Firewall sem fundo preto (`bg-zinc-950`), utilizando a paleta grafite neutra (`var(--card)` + `bg-white/[0.025]`), com 2 cards de status no topo, banner informativo azul, 2 cards de regras de acesso rápido, contador dinâmico de regras, botão `+ Adicionar regra` com modal dedicado e estado vazio com borda tracejada.

### Adicionado
- **Detecção inteligente multi-motor de Firewall (`linux_ops.py` & `main.py`)**: `_inspect_firewall_smart()` identifica automaticamente todos os motores instalados (`UFW`, `firewalld`, `nftables`, `iptables`), o motor ativo/pronto, política padrão e regras estruturadas (`parsed_rules`), além de suporte multi-motor para habilitar/desabilitar e remover regras.

## [1.3.10] - 26/11/2026

### 📊 Métricas de Código
- **Total**: **25.681 linhas** de código em **93 arquivos-fonte** (`8.492` `.vue` · `6.644` `.py` · `7.610` `.css` · `2.668` `.js` · `249` `.sh` · `18` `.service`).

### Corrigido
- **Detecção real de atualizações (`pkg_manager.py`)**: adicionado filtro com `vercmp <nova_versao> <versao_atual>` para descartar falsos positivos de downgrade retornados pelo `pamac checkupdates` (ex: `26.11.25_1-2026 -> 26.11.25_1-2021`), mantendo apenas atualizações reais.

## [1.3.9] - 26/11/2026

### Corrigido
- **Auto-atualização fora do cgroup (`systemd-run`)**: `POST /api/proxmenux/self-update` agora executa o `install.sh` via `systemd-run --unit=linuxmenux-self-update --collect`, evitando que o `systemctl stop linuxmenux.service` dentro do instalador mate o próprio processo atualizador antes de reiniciar o serviço.

## [1.3.8] - 25/11/2026

### Alterado & Corrigido
- **Streaming em tempo real no terminal de atualização (`/ws/system/update`)**: substituído `readline()` por leitura em chunks (`read(256)`) para exibir imediatamente as barras de progresso (`\r`) do `pacman` sem parecer travado durante downloads grandes.

### 📊 Métricas de Código
- **Total**: **25.662 linhas** de código em **93 arquivos-fonte** (`8.492` `.vue` · `6.625` `.py` · `7.610` `.css` · `2.668` `.js` · `249` `.sh` · `18` `.service`).

## [1.3.7] - 25/11/2026

### Adicionado
- Suporte a login automático via `?token=lmx_...` na URL em `App.vue` (ideal para WebView do **Ricard Hub - Desktop**), além do cabeçalho `Authorization: Bearer lmx_...`.

### Corrigido
- Adicionado `import shutil` em `backend/services/host_inspector.py`, corrigindo o `HTTP 500` em `/api/network`, `/api/network/flow` e `/api/health/full` (que fazia o modal `Estado de saúde do sistema` exibir `0 Total`).
- Removida a tag duplicada `v1.2.9` ao lado de `v1.3.x` no cabeçalho de `App.vue`.
- Melhorada a responsividade mobile do cabeçalho em `App.vue` (`flex-col sm:flex-row`, truncamento limpo e quebra responsiva dos controles em telas `360px`).

## [1.3.6] - 25/11/2026

### Corrigido
- **Versão dinâmica 100% via `version.js`**: removidas as últimas referências fixas `v1.2.9` no cabeçalho/rodapé de `App.vue`, `HealthStatusModal.vue` e `backend/main.py`, passando a usar `APP_VERSION` de `frontend/src/lib/version.js` em todos os lugares (inclusive copiado para `/usr/local/share/linuxmenux/frontend/src/lib/version.js` pelo `install.sh`).

## [1.3.5] - 25/11/2026

### Segurança & Infraestrutura
- **Porta `8008` fechada para a rua (`127.0.0.1`)**: `systemd/linuxmenux.service` alterado de `--host 0.0.0.0` para `--host 127.0.0.1` para impedir acesso direto pelo IP público e operar exclusivamente via Cloudflare Tunnel / localhost.

### Alterado & Corrigido
- **Fonte única de versão (`version.js`)**: `backend/main.py` agora lê `APP_VERSION` diretamente de `frontend/src/lib/version.js`, eliminando versões fixas espalhadas.
- **Modelos de IA dinâmicos (`POST /api/ai/models`)**: adicionado carregamento real de modelos por provedor + chave de API com botão `Carregar` em `SettingsView.vue` (sem modelo fixo).
- **Topologia SVG (`NetworkView.vue`)**: fallback usando `flowData.nics` e `default_ip` para não exibir interface Wi-Fi ativa como `Desativada`.

## [1.3.4] - 25/11/2026

### Corrigido
- **Auto-atualização (`scripts/install.sh` & `POST /api/proxmenux/self-update`)**: corrigido erro de `Instrução ilegal` (`SIGILL`) ao executar `/root/.bun/bin/bun` durante a atualização em segundo plano; agora utiliza `LINUXMENUX_SKIP_BUILD=1` e o build pré-compilado de `backend/static/` quando `bun --version` não estiver funcional para `root`, garantindo atualizações futuras com 1 clique pelo modal `Info`.

## [1.3.3] - 25/11/2026

### Alterado
- **Auditoria & Relatórios (`AuditView.vue`)**: reconstruída 1:1 com o padrão `Audit & Report` do ProxMenux (`Assessment`, `Alterações`, `Política`, `Run assessment`, `Usar como referência`, filtros por categoria e linhas expansíveis).
- **Limites do Monitor de Integridade (`SettingsView.vue`)**: reconstruído em 2 colunas com barras visuais verde/âmbar/vermelho, alças duplas Aviso/Crítico e botão `Redefinir tudo`.
- **Notificações & Aprimoramento de IA (`SettingsView.vue`)**: abas individuais para os 6 canais (`Telegram`, `Gotify`, `Discord`, `Email`, `Pushover`, `Apprise`) com botões de olho, categorias de notificação, Horas tranquilas, Resumo diário e bloco roxo de Aprimoramento de IA.

## [1.3.2] - 25/11/2026

### Adicionado
- Endpoint `GET /api/distro/logo` e logotipo oficial BigLinux (`distro-biglinux.svg`) exibido no modal de atualizações, hardware e topologia de rede SVG.
- Detecção automática de **Cloudflare Tunnel / HTTPS** (`cf-ray`, `cf-connecting-ip`, `x-forwarded-proto`) em `/api/ssl/status` e na aba Segurança.
- Regras de acesso rápido (porta `8008` e SSH `22`), detalhes de jails/IPs banidos no Fail2Ban e botão **Exportar PDF** na auditoria Lynis.
- Caixa **"Não mostrar novamente ao fazer login"** no carrossel de boas-vindas e notas atualizadas em `ReleaseNotesModal.vue`.

### Corrigido
- Removido `--no-aur` do `pamac checkupdates` para detectar atualizações de pacotes AUR (como `visual-studio-code-bin`).
- Forçado `LC_ALL=C` e regex `time|tempo` em `/api/network/latency` para medição ICMP real sem retornar `0 ms`.
- Ethernet física sem IPv4 (`enp2s0`) marcada como `Desconectada` e velocidade real de Wi-Fi (`wlp3s0`) obtida via `iw dev link` (sem mentir `1 Gbps`).
- Removido polling de `/api/vms` em `App.vue` (substituído por `/api/docker/containers`).

## [1.3.1] - 25/11/2026

### Alterado
- Padronizado o nome oficial **`Linux Menux - Monitor`** (com hífen) em toda a interface, cabeçalho, login, setup, sobre, segurança, título HTML, FastAPI e serviço systemd.
- Substituído o emoji no topo do `README.md` pelo logotipo SVG oficial (`frontend/public/logo.svg`) e destacado o link direto de métricas (`https://git.ricardtech.top/RicardTech/ricardtech-metrics`).

## [1.3.0] - 25/11/2026

### Adicionado
- **Paridade 1:1 completa em Segurança (`SecurityView.vue`)**: seções `Linux Menux Monitor` e `Sistema Linux` com Autenticação + olho, status 2FA, Certificado SSL auto-assinado (`POST /api/ssl/self-signed`), Tokens de API + Swagger `/docs`, Tailscale, Firewall (`UFW/iptables`) com filtros e remoção de regras, Fail2Ban com whitelist (`ignoreip`) e Auditoria Lynis com barra de progresso.
- **Paridade 1:1 completa em Configurações (`SettingsView.vue`)**: cabeçalho completo, Token da API do GitHub com botão de olho, Detecção de Atualizações de Containers, Snippets & Comandos Rápidos (`/api/snippets`) e Otimizações & Serviços do Host Linux (`/api/optimizations`).
- **Auto-atualização no modal Info (`HealthStatusModal.vue`)**: verificação automática de novas releases no repositório público `ricardtech/linuxmenux` e botão **Atualizar para vX.Y.Z** (`POST /api/proxmenux/self-update`).

### Corrigido
- Adicionado `import shutil` em `backend/services/pkg_manager.py`, corrigindo o erro `HTTP 500 Internal Server Error` em `/api/system`.
- Corrigida leitura em lote das estatísticas de containers Docker (`_collect_docker_cli_stats`) em `backend/services/docker_swarm.py` para exibir CPU, Memória, E/S de disco e E/S de rede reais.
- Bloqueio de chamadas e pollers de telemetria em `App.vue` antes da autenticação (`authGate === 'ready'`), eliminando erros `401 Unauthorized` no carregamento inicial.
- Removido `Depends(require_auth)` inexistente nas novas rotas de `backend/main.py` (autenticação já aplicada globalmente via middleware).

## [1.2.9] - 25/11/2026

### Adicionado
- Logotipo SVG exclusivo do **Linux Menux Monitor** (`frontend/public/logo.svg`).
- Botão de visualizar/ocultar senha (ícone de olho) nas telas de cadastro de credencial (`AuthSetupView.vue`) e login (`LoginView.vue`).
- Verificação automática de novas versões do **Linux Menux** no repositório GitHub via `/api/proxmenux/update-status`.
- Modal de boas-vindas (`OnboardingCarousel.vue`) e modal *"O que há de novo"* (`ReleaseNotesModal.vue`).
- Documentação interativa da API (`/docs` Swagger UI e `/redoc`) vinculada na aba Segurança.
- Suporte a 6 canais de notificação (`Telegram`, `Discord`, `Gotify`, `Pushover`, `E-mail SMTP`, `Webhook/Apprise`) e múltiplos provedores de IA.

### Corrigido
- Interceptor global de `fetch` em `frontend/src/main.js` anexando `Authorization: Bearer <token>` em todas as requisições `/api/*`, eliminando erros `401 Unauthorized` após login/setup.
- Endpoint `/api/auth/status` retornando `configured`, `enabled`, `declined` e `needs_setup` corretamente para não retornar à tela de cadastro inicial após `Ctrl+Shift+R`.
- Detecção real de interfaces físicas via `operstate`, `LOWER_UP` e `carrier` (evitando marcar `enp2s0` como ativa quando desconectada).
- Diagnóstico AIOps real via OpenRouter (sem retorno simulado quando sem chave configurada) e datas no padrão brasileiro `DD/MM/AAAA HH:mm:ss`.
- Detecção multi-distro de atualizações (`pamac checkupdates`, `checkupdates`, `apt-get update` no botão **Verificar agora**).

## [1.2.8] - 25/11/2026

### Adicionado
- Migração completa e modularização do frontend para **Vue 3 + Vite + Tailwind CSS + Bun v1.4.5** em `frontend/src/components/`.
- Barra de navegação `grid-cols-7` em largura total, tokens OKLCH oficiais e escala tipográfica legível (`16px` base / `14px` `.text-xs`).
- **Containers & Stacks**: métricas ao vivo inline (`CPU %`, `Memória`, `Imagem`, `E/S de disco`, `E/S de rede`) e modal com **7 abas** + confirmação de `Forçar paragem`.
- **Hardware**: CPU + Placa-mãe, Módulos de memória, Monitoramento Térmico agrupado (`CPU`, `NVME`, `Outro`), Placas Gráficas, Consumo Intel RAPL, Dispositivos PCI em 3 colunas, Resumo da rede, Resumo de armazenamento e Dispositivos USB (`lsusb`).
- **Armazenamento & Backup**: detalhes SMART em `DiskDetailModal.vue`, suporte a Backup Local, Borg e **Cloudflare R2 (S3 SigV4)** com envio e restauração remota.
- **Rede & Topologia SVG**: histórico real via `vnstat` + SQLite, detecção real de interfaces e medição ICMP real em `/api/network/latency` + `LatencyDetailModal.vue`.
- **Segurança, Auditoria & Configurações**: seções `Linux Menux Monitor` e `Sistema Linux`, abas de Auditoria (`Relatório`, `Inventário`, `Política`), `SettingsView.vue` com cards independentes (`Editar/Cancelar/Salvar`) e persistência em `/var/lib/linuxmenux`.

