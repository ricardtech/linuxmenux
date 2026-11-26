<div align="left">
  <img src="./frontend/public/logo.svg" alt="Linux Menux - Monitor" width="56" height="56" />
</div>

# Linux Menux - Monitor `v1.3.3`

[![Versão](https://img.shields.io/badge/versão-1.3.3-orange.svg)](./CHANGELOG.md)
[![Forgejo](https://img.shields.io/badge/Forgejo-Self--Hosted-ea580c?logo=forgejo)](https://git.ricardtech.top/RicardTech/linuxmenux)
[![GitLab](https://img.shields.io/badge/GitLab-Triplo--Push-fc6d26?logo=gitlab)](https://gitlab.com/ricard-tech/linuxmenux)
[![Métricas](https://img.shields.io/badge/RicardTech-Metrics-0ea5e9)](https://git.ricardtech.top/RicardTech/ricardtech-metrics)
[![Licença](https://img.shields.io/badge/licença-GPLv2-blue.svg)](./LICENSE)

📊 **Métricas do Ecossistema Ricard Tech**: [https://git.ricardtech.top/RicardTech/ricardtech-metrics](https://git.ricardtech.top/RicardTech/ricardtech-metrics)

[![Métricas do Linux Menux - Monitor](https://git.ricardtech.top/RicardTech/ricardtech-metrics/raw/branch/main/charts/linuxmenux.svg)](https://git.ricardtech.top/RicardTech/ricardtech-metrics)

> Dashboard Web e Terminal Interativo para servidores Linux com suporte nativo a **Docker Swarm, Compose, Dokploy, Traefik, Firewall, Cloudflare R2 e Multi-Distro (BigLinux, Manjaro, Arch, Ubuntu, Debian, RHEL, Rocky, Alma, openSUSE, Fedora)**.

Inspirado na usabilidade do [ProxMenux](https://github.com/MacRimi/ProxMenux), porém projetado do zero para servidores de aplicação e clusters Docker sem acoplamento a Proxmox VE.

---

## 🚀 Recursos Principais

- **Docker Swarm & Dokploy Stacks**: Visualização em tempo real de réplicas, serviços, nós do swarm e containers avulsos via socket Unix `/var/run/docker.sock`.
- **Traefik & Iptables**: Monitoramento de roteamento, certificados SSL Let's Encrypt e regras de firewall em `INPUT` e `DOCKER-USER`.
- **Motor Multi-Distro de Atualizações**:
  - `pacman` (Manjaro / Arch)
  - `apt` (Debian / Ubuntu)
  - `dnf` (RHEL / Rocky / Alma / Fedora / CentOS)
  - `zypper` (openSUSE Leap / Tumbleweed)
- **Detecção Inteligente de Reboot**:
  - Verifica marcadores do sistema e discrepâncias entre o Kernel ativo na memória e os módulos instalados no disco.
- **Web Terminal Integrado (xterm.js + PTY)**:
  - Terminal interativo no navegador protegido por tickets de uso único com TTL de 5 segundos.
- **Central Completa de Notificações**:
  - Telegram, Discord, Gotify, E-mail SMTP, Pushover e Apprise.
- **Acesso Seguro via Cloudflare Tunnel**:
  - Zero portas abertas no roteador ou firewall. Protegido por Cloudflare Zero Trust e SSL automático.
- **Pronto para Aplicativo Móvel (Capacitor / Gradle 9.9.2)**:
  - Suporte a distribuição via loja própria em **Cloudflare R2** e telemetria sem Google via **Aptabase self-hosted**.

---

## 📦 Instalação Rápida (Segura e Não-Invasiva)

```bash
git clone https://github.com/ricardtech/linuxmenux.git
cd linuxmenux
sudo ./scripts/install.sh
```

O dashboard estará disponível em:
👉 `http://SEU_IP:8008`

---

## 🗑️ Desinstalação Limpa

Se desejar remover a qualquer momento:

```bash
sudo /usr/local/share/linuxmenux/uninstall.sh
```
*Garantia: O desinstalador não altera seus containers, volumes, Dokploy ou pacotes essenciais do sistema.*

---

## 🛡️ Segurança & Arquitetura

- **Isolamento de Ambiente**: As dependências do backend rodam dentro de um ambiente virtual Python (`venv`) isolado, em total conformidade com a PEP 668.
- **Proteção Anti-SSRF**: Validação rigorosa em todos os canais de webhooks.
- **Lock Concorrente**: Bloqueio de processos concorrentes de atualização (`flock`) para evitar corrupção de pacotes.

---

## 📄 Licença

GPL-3.0 © 2026 Ricard Tech
