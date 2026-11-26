# Changelog

Todas as mudanças notáveis do **Linux Menux - Monitor** serão documentadas neste arquivo (formato baseado em Keep a Changelog, com datas no padrão brasileiro `DD/MM/AAAA`).

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

