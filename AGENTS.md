# Regras de Engenharia e Instruções para Agentes de IA - Linux Menux

## Sinalização Obrigatória de Auditoria Sênior Contínua

- **BANNER OBRIGATÓRIO EM TODA E QUALQUER RESPOSTA (SEM EXCEÇÃO)**:
  Em TODA resposta emitida pelo assistente, independentemente do tipo de tarefa, pergunta, status, diagnóstico ou código, a PRIMEIRA linha visível de texto DEVE iniciar obrigatoriamente com:
  > 🛡️ **Auditoria Sênior Ativa [SonarQube & CodeRabbit | Strix Security]**: Varredura de qualidade e segurança executada automaticamente em segundo plano (sem necessidade de intervenção manual).

---

## 🎯 Contexto Crítico de Origem: Migração ProxMenux -> LinuxMenux

> **ATENÇÃO MÁXIMA PARA A IA**: Este projeto nasceu como um fork/clone do **ProxMenux**, mas seu propósito é rodar em **qualquer servidor Linux Standalone ou Cluster Docker Swarm**, sem depender do Proxmox VE!

### Matriz de Substituição Obrigatória (Desacoplamento do Proxmox)

| Recurso no ProxMenux (LEGADO - PROXMOX) | Recurso no LinuxMenux (NOVO - LINUX NATIVO) | O que a IA DEVE fazer |
| :--- | :--- | :--- |
| **APIs Proxmox (`/api2/json/...`)** | **APIs FastAPI nativas (`/api/...`)** | **ELIMINAR** chamadas de API Proxmox (`pvesh`, tickets PVE). |
| **QEMU VMs (`qm`) e LXC Containers (`pct`)** | **Docker Containers & Swarm Services** | Substituir por inspeção via `/var/run/docker.sock`. |
| **Clusters PVE (`pvecm`)** | **Docker Swarm Nodes & Dokploy Stacks** | Listar réplicas, stacks e nós do cluster Swarm. |
| **Storage PVE (ZFS, PBS, LVM-Thin)** | **Discos/Montagens Linux & Volumes Docker** | Coletar dados de `df -h`, `lsblk`, `/proc/mounts`. |
| **Proxmox Firewall** | **Iptables & Traefik Routing** | Monitorar regras nativas de `INPUT` e `DOCKER-USER`. |
| **Terminal de LXC/VM (`pve-xtermjs`)** | **Web Terminal PTY Standalone** | Usar o PTY WebSocket nativo do backend FastAPI. |

⚠️ **NUNCA tente restabelecer comunicação com Proxmox VE, PVE Nodes ou endpoints da porta 8006 neste projeto.**

---

## ⚡ Diretrizes de Ação Rápida e Foco Direto (Zero Enrolação)

Para garantir que correções sejam aplicadas com máxima velocidade e sem regressões:
1. **Foco Cirúrgico**: Nunca reescreva arquivos inteiros com centenas de linhas quando apenas poucas linhas precisam ser corrigidas. Identifique a função ou trecho exato responsável.
2. **Sem Prolixidade**: Responda de forma técnica, direta e resolutiva. Não faça introduções teóricas óbvias ou tutoriais longos antes de entregar o código ou a correção.
3. **Validação Obrigatória Pré-Entrega**: Após qualquer alteração no código, execute **obrigatoriamente** o script de validação rápida:
   ```bash
   ./scripts/check.sh
   ```
   Se houver qualquer erro de sintaxe no backend ou falha de build, corrija-o antes de concluir a resposta ao usuário.

---

## 🏗️ Arquitetura Técnica do Linux Menux

- **Backend (`backend/`)**:
  - Framework: **FastAPI** rodando em **Uvicorn** (porta padrão: `8008`).
  - Ambiente: Python 3.10+ isolado dentro de `backend/venv` (PEP 668).
  - Organização:
    - `backend/main.py`: Ponto de entrada, configuração de middlewares, websockets e inicialização do app.
    - `backend/core/`: Módulos centrais (autenticação JWT, detecção de distro, utilitários de sistema).
    - `backend/services/`: Serviços especializados (`docker_swarm.py`, `system_metrics.py`, `pkg_manager.py`, `firewall_monitor.py`, `traefik_monitor.py`).
  - **Regra de Isolamento**: Todo comando shell executado pelo backend deve usar listas de argumentos (`subprocess.Popen` / `subprocess.run` sem `shell=True`) ou `shlex.quote` para prevenir injeção de comandos.
- **Frontend (`frontend/`)**:
  - Framework: **Vue 3** (`<script setup>`) com **Vite**, **Tailwind CSS** e **Chart.js** (`lucide-vue-next` para ícones).
  - Runtime obrigatório: **100% Bun** (`bun install`, `bun run build`). **Proibido usar ou mencionar `npm`**.
  - Distribuição: Build estático (`bun run build` gerando `frontend/dist/`).
  - Sincronização e Deploy: O backend do FastAPI serve os arquivos estáticos e o serviço roda em `/usr/local/share/linuxmenux/` via `systemd` (`sudo ./scripts/install.sh` publica na porta `8008`).
- **Paridade 1:1 Obrigatória com o ProxMenux (`/home/alaxricard/Documentos/Projetos/ProxMenux/AppImage/`)**:
  - Toda tela, card, gráfico e modal deve espelhar 1:1 o layout, cores, tipografia (`Geist` / `Geist Mono`), largura (`container mx-auto px-4 md:px-6 py-4 md:py-6`) e comportamento do código de referência em `ProxMenux/AppImage/components/`.
  - **Modularização**: Não inflar `App.vue` com novas telas/modais; criar componentes dedicados em `frontend/src/components/` espelhando os nomes do `ProxMenux`.
  - **Modais**: Todo modal deve usar `BaseModal.vue` e fechar obrigatoriamente ao clicar fora (backdrop `@click.self`) e com a tecla `Esc`.
  - **Unidades Automáticas & Dados Limpos**: Tráfego de rede, disco e memória devem converter automaticamente entre `B`/`KB`/`MB`/`GB`/`TB`. Modais específicos (ex: CPU vs Memória) não devem misturar métricas de outros recursos.
- **Serviço de Sistema**:
  - Unidade systemd configurada em `systemd/linuxmenux.service`.

---

## 🛡️ Segurança e Resiliência Operacional

- **Docker Swarm e Dokploy**:
  - Acesso seguro ao socket Unix `/var/run/docker.sock`. Sempre tratar exceções caso o daemon do Docker esteja indisponível ou em reinicialização.
- **Firewall e Atualizações do Sistema**:
  - Bloqueio concorrente (`flock`) obrigatório ao acionar operações de pacotes (`apt`, `pacman`, `dnf`, `zypper`) para evitar quebra da base de dados do sistema.
  - Validação estrita em rotas administrativas (requer autenticação JWT).

---

## 📋 Gerenciamento Automatizado de Tarefas no Vikunja via MCP

Sempre que qualquer desenvolvimento, refatoração, criação, análise, teste ou manutenção for solicitado no Linux Menux:
- **Projeto no Vikunja**: Projeto com ID **27** (`Linux Menux - Dashboard`, slug: `LNXMENU`).
- **Criação de Tarefas (`tasks_create`)**:
  - `project`: 27.
  - `title`: Título objetivo e claro da tarefa.
  - `description`: Detalhes técnicos, checklist e critérios de aceitação em Markdown.
  - `due_date`: Data e hora exata prevista de conclusão em ISO 8601 (ex: `YYYY-MM-DDTHH:mm:ss-03:00`). Proibido enviar data sem horário.
  - `priority`: 1 (Baixa) a 5 (Fazer Agora).
  - `percent_done`: Inicializado em `0.0`.
- **Responsável Obrigatório**: Atribuir `bot-antigravity` (`user_id: 3`) via `task_assignees_create` (pois o agente de IA executa as alterações no repositório).
- **Etiquetas Obrigatórias**: Vincular uma ou mais etiquetas via `do_action` (`task_labels_create`):
  - Oficiais: `Bugs` (`2`), `Criação` (`3`), `Edição` (`4`), `Teste` (`7`), `Configuração` (`8`), `Melhoria` (`9`), `Visual` (`10`), `Documentação` (`11`), `Limpeza` (`12`), `Segurança` (`13`), `Refatoração` (`14`), `Backend` (`16`), `Frontend` (`17`), `Velocidade` (`18`).
- **Conclusão**: Ao finalizar, atualizar `tasks_update` com `done: true`, `percent_done: 1.0` e `end_date` com data e hora exata de término no formato ISO 8601 com horário.

---

## 🔄 Redundância Obrigatória e Triplo-Push Git (GitHub + GitLab + Forgejo)

Ao realizar commits, branches, tags ou releases no repositório `linuxmenux`:
- **Triplo-Push no `origin`**:
  - 1ª URL (GitHub): `https://github.com/ricardtech/linuxmenux.git`
  - 2ª URL (GitLab): `https://gitlab.com/ricard-tech/linuxmenux.git`
  - 3ª URL (Forgejo): `https://git.ricardtech.top/RicardTech/linuxmenux.git`
  - O comando `git push origin <branch>` enviará simultaneamente para os 3 destinos.
- **Releases e Versões**:
  - Atualizar `CHANGELOG.md` e `README.md`.
  - Criar tag anotada (`git tag -a vX.Y.Z -m "..."`).
  - Publicar a release nas três plataformas (GitHub, GitLab e Forgejo).
