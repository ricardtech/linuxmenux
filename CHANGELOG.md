# Changelog

Todas as mudanças notáveis do **Linux Menux Monitor** serão documentadas neste arquivo (formato baseado em Keep a Changelog, com datas no padrão brasileiro `DD/MM/AAAA`).

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

