# 🗺️ Cronograma & Roadmap do Linux Menux

Este documento define os marcos técnicos, evolução arquitetural e entregas planejadas para o **Linux Menux**.

---

## 🚀 Em Andamento / Próxima Entrega Prioritária

### [LNXMENU-7] Topologia Visual de Rede & Diagnóstico com IA (AIOps / Smart Traffic Inspector)
- **Status**: Planejado / Em Andamento
- **Prioridade**: Alta (4)
- **Previsão**: 2026-11-23T18:00:00-03:00
- **Responsável**: AlaxRicard (`user_id: 1`)
- **Escopo Técnico**:
  1. **Topologia Gráfica com Pulsos de Luz (Neon Glow Flow)**:
     - Renderização em Canvas/SVG a 60 FPS com linhas fluidas animadas.
     - 4 Camadas de Topologia:
       - Placas Físicas WAN/LAN (`wlp3s0`, `enp2s0`, `eth0`)
       - Host Linux Central com tráfego agregado (KB/s)
       - Bridges Virtuais (`docker0`, `br-dokploy`, `traefik`)
       - Containers e Stacks Ativos (`traefik`, `dokploy`, `adguard`, etc.)
  2. **Mecanismo AIOps Sob Demanda (Zero-RAG)**:
     - **Detecção de Gargalos (Bottlenecks)**: Correlacionar capacidade nominal da placa física com consumo individual dos containers.
     - **Detecção de Anomalias & Ataques (AppSec / NetSec)**: Alerta imediato sobre picos anômalos de exfiltração contínua ou rajadas de pacotes SYN sem resposta.
     - **Auditoria de Portas e Firewall (iptables)**: Verificação de portas expostas diretamente em `0.0.0.0` e geração automática de regras de isolamento na cadeia `DOCKER-USER`.
     - **Diagnóstico em Linguagem Natural**: Clique sobre qualquer nó para exibir parecer técnico em português do Brasil com portas abertas e saúde de conexão.

---

## ✅ Marcos Já Concluídos

- [x] **[LNXMENU-5] Padronização de Regras & Validador Rápido**:
  - Criação do `AGENTS.md` com matriz de desacoplamento Proxmox -> Linux Standalone.
  - Criação do script `scripts/check.sh` para validação em menos de 5 segundos.
- [x] **[LNXMENU-6] Migração do Frontend para Vue 3 + Vite e Sanitização Real do Backend**:
  - Eliminação de 100% dos dados falsos e mocks do backend.
  - Implementação do `host_inspector.py` lendo dados reais do kernel, discos físicos (`lsblk`), temperatura (`hwmon`) e rede dinâmica.
  - Reconstrução do frontend em **Vue 3.5**, **Vite 8.3**, **Tailwind CSS 4.3** e **Lucide Icons 1.0**.
