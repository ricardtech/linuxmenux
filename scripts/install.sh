#!/usr/bin/env bash
# ==========================================================
# Linux Menux - Multi-Distro Server Dashboard & Terminal
# Safe Installer for Arch/Manjaro, Debian/Ubuntu, RHEL/Rocky, openSUSE
# ==========================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

INSTALL_DIR="/usr/local/share/linuxmenux"
SERVICE_FILE="/etc/systemd/system/linuxmenux.service"
PORT="${PORT:-8008}"

msg_info() { echo -e "${CYAN}ℹ ${NC} $1"; }
msg_ok() { echo -e "${GREEN}✓ ${NC} $1"; }
msg_warn() { echo -e "${YELLOW}⚠ ${NC} $1"; }
msg_error() { echo -e "${RED}✖ ${NC} $1"; }

if [ "$(id -u)" -ne 0 ]; then
    msg_error "Este instalador deve ser executado como root (use sudo)."
    exit 1
fi

echo -e "${BLUE}=====================================================${NC}"
echo -e "${CYAN}    Linux Menux - Painel de Controle Multi-Distro     ${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 1. Detect Distribution
msg_info "Detectando distribuição Linux..."
DISTRO="unknown"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO="${ID:-unknown}"
fi
msg_ok "Distribuição detectada: ${PRETTY_NAME:-$DISTRO}"

# 2. Install Python3 and venv dependencies
msg_info "Garantindo dependências básicas do sistema..."
case "$DISTRO" in
    manjaro|arch|endeavouros|biglinux)
        pacman -Sy --noconfirm --needed python python-pip vnstat
        ;;
    ubuntu|debian|linuxmint|pop)
        apt-get update -qq
        apt-get install -y -qq python3 python3-pip python3-venv curl vnstat
        ;;
    fedora|rhel|centos|rocky|almalinux)
        dnf install -y -q python3 python3-pip vnstat
        ;;
    opensuse*|sles)
        zypper --non-interactive install python3 python3-pip vnstat
        ;;
    *)
        msg_warn "Distribuição não identificada diretamente. Prosseguindo com verificações genéricas."
        ;;
esac

# Garante coleta contínua de tráfego de rede persistente entre reinícios
systemctl enable --now vnstat 2>/dev/null || true
if command -v vnstat >/dev/null 2>&1; then
    for iface_path in /sys/class/net/*; do
        iface=$(basename "$iface_path")
        case "$iface" in
            lo|docker*|veth*|br-*|tailscale*|virbr*) continue ;;
            *) vnstat --add -i "$iface" 2>/dev/null || true ;;
        esac
    done
    systemctl restart vnstat 2>/dev/null || true
fi
mkdir -p /var/lib/linuxmenux /etc/linuxmenux /var/backups/linuxmenux

# 3. Setup Project Structure & Build Frontend
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -d "${SCRIPT_DIR}/frontend" ] && [ "${LINUXMENUX_SKIP_BUILD:-0}" != "1" ]; then
    msg_info "Garantindo build atualizado do frontend Vue 3 (Bun)..."
    BUN_BIN=""

    # 1. Procura Bun funcional já instalado (incluindo /home/*/.bun/bin/bun quando rodando via systemd/root)
    for cand in "$(command -v bun 2>/dev/null || true)" "/root/.bun/bin/bun" /home/*/.bun/bin/bun; do
        if [ -n "${cand}" ] && [ -x "${cand}" ] && "${cand}" --version >/dev/null 2>&1; then
            BUN_BIN="${cand}"
            break
        fi
    done

    # 2. Se não encontrou Bun funcional, instala (com fallback automático para baseline se CPU não suportar AVX2)
    if [ -z "${BUN_BIN}" ] && [ ! -f "${SCRIPT_DIR}/backend/static/index.html" ]; then
        msg_info "Bun funcional não encontrado. Instalando Bun v1.4.5..."
        if [ -n "${SUDO_USER:-}" ] && id "${SUDO_USER}" >/dev/null 2>&1; then
            sudo -u "${SUDO_USER}" bash -c 'curl -fsSL https://bun.sh/install | bash -s "bun-v1.4.5"' || true
            [ -x "/home/${SUDO_USER}/.bun/bin/bun" ] && BUN_BIN="/home/${SUDO_USER}/.bun/bin/bun"
        else
            curl -fsSL https://bun.sh/install | bash -s "bun-v1.4.5" || true
            [ -x "/root/.bun/bin/bun" ] && BUN_BIN="/root/.bun/bin/bun"
        fi

        if [ -n "${BUN_BIN}" ] && ! "${BUN_BIN}" --version >/dev/null 2>&1; then
            msg_warn "Bun padrão incompatível com a CPU (sem AVX2). Baixando variante baseline..."
            ARCH="$(uname -m)"
            if [ "${ARCH}" = "x86_64" ] && command -v unzip >/dev/null 2>&1; then
                TMP_BUN="$(mktemp -d)"
                if curl -fsSL "https://github.com/oven-sh/bun/releases/download/bun-v1.4.5/bun-linux-x64-baseline.zip" -o "${TMP_BUN}/bun.zip"; then
                    unzip -qo "${TMP_BUN}/bun.zip" -d "${TMP_BUN}"
                    if [ -f "${TMP_BUN}/bun-linux-x64-baseline/bun" ]; then
                        mkdir -p "$(dirname "${BUN_BIN}")"
                        cp "${TMP_BUN}/bun-linux-x64-baseline/bun" "${BUN_BIN}"
                        chmod +x "${BUN_BIN}"
                    fi
                fi
                rm -rf "${TMP_BUN}"
            fi
        fi
    fi

    if [ -n "${BUN_BIN}" ] && [ -x "${BUN_BIN}" ] && "${BUN_BIN}" --version >/dev/null 2>&1; then
        if [ -n "${SUDO_USER:-}" ]; then
            sudo -u "${SUDO_USER}" bash -c "cd '${SCRIPT_DIR}/frontend' && '${BUN_BIN}' install --frozen-lockfile && '${BUN_BIN}' run build"
        else
            (cd "${SCRIPT_DIR}/frontend" && "${BUN_BIN}" install --frozen-lockfile && "${BUN_BIN}" run build)
        fi
        msg_ok "Frontend compilado com sucesso via Bun!"
    elif command -v npm >/dev/null 2>&1; then
        msg_warn "Bun indisponível; compilando frontend via npm..."
        (cd "${SCRIPT_DIR}/frontend" && npm install --no-audit --no-fund && npm run build)
        msg_ok "Frontend compilado com sucesso via npm!"
    elif [ -f "${SCRIPT_DIR}/backend/static/index.html" ]; then
        msg_warn "Bun/npm indisponíveis; utilizando build pré-compilado de backend/static/."
    else
        msg_error "Falha ao instalar ou localizar o Bun v1.4.5 (e npm ausente)."
        exit 1
    fi
fi

msg_info "Instalando arquivos em ${INSTALL_DIR}..."
mkdir -p "${INSTALL_DIR}"

cp -r "${SCRIPT_DIR}/backend" "${INSTALL_DIR}/"
mkdir -p "${INSTALL_DIR}/frontend/src/lib"
cp "${SCRIPT_DIR}/frontend/src/lib/version.js" "${INSTALL_DIR}/frontend/src/lib/"
cp -r "${SCRIPT_DIR}/systemd" "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/scripts/uninstall.sh" "${INSTALL_DIR}/"
chmod +x "${INSTALL_DIR}/uninstall.sh"

# 4. Create Isolated Python Virtual Environment (PEP 668 Compliant)
msg_info "Criando ambiente isolado Python (venv)..."
if [ ! -d "${INSTALL_DIR}/venv" ]; then
    python3 -m venv "${INSTALL_DIR}/venv"
fi

msg_info "Instalando dependências do backend no venv..."
"${INSTALL_DIR}/venv/bin/pip" install --upgrade pip -q
"${INSTALL_DIR}/venv/bin/pip" install -r "${INSTALL_DIR}/backend/requirements.txt" -q
msg_ok "Ambiente Python configurado com sucesso."

# 5. Setup Systemd Service
msg_info "Garantindo liberação da porta ${PORT}..."
systemctl stop linuxmenux.service 2>/dev/null || true
fuser -k "${PORT}/tcp" 2>/dev/null || true

msg_info "Configurando serviço systemd..."
cp "${INSTALL_DIR}/systemd/linuxmenux.service" "${SERVICE_FILE}"
systemctl daemon-reload
systemctl enable linuxmenux.service
systemctl restart linuxmenux.service

msg_ok "Serviço linuxmenux.service iniciado com sucesso na porta ${PORT}!"

# 6. Inform user
SERVER_IP=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") {print $(i+1); exit}}' || true)
if [ -z "${SERVER_IP}" ]; then
    SERVER_IP=$(hostname -i 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
fi
echo ""
echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}✔ Instalação concluída com sucesso!${NC}"
echo -e "Acesse o painel web em: ${CYAN}http://${SERVER_IP}:${PORT}${NC}"
echo -e "Para desinstalar de forma limpa a qualquer momento, execute:"
echo -e "${YELLOW}  sudo ${INSTALL_DIR}/uninstall.sh${NC}"
echo -e "${GREEN}=====================================================${NC}"
