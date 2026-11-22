#!/usr/bin/env bash
# ==========================================================
# LinuxMenux - Multi-Distro Server Dashboard & Terminal
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
echo -e "${CYAN}    LinuxMenux - Painel de Controle Multi-Distro     ${NC}"
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
    manjaro|arch|endeavouros)
        pacman -Sy --noconfirm --needed python python-pip
        ;;
    ubuntu|debian|linuxmint|pop)
        apt-get update -qq
        apt-get install -y -qq python3 python3-pip python3-venv curl
        ;;
    fedora|rhel|centos|rocky|almalinux)
        dnf install -y -q python3 python3-pip
        ;;
    opensuse*|sles)
        zypper --non-interactive install python3 python3-pip
        ;;
    *)
        msg_warn "Distribuição não identificada diretamente. Prosseguindo com verificações genéricas."
        ;;
esac

# 3. Setup Project Structure
msg_info "Instalando arquivos em ${INSTALL_DIR}..."
mkdir -p "${INSTALL_DIR}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cp -r "${SCRIPT_DIR}/backend" "${INSTALL_DIR}/"
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
msg_info "Configurando serviço systemd..."
cp "${INSTALL_DIR}/systemd/linuxmenux.service" "${SERVICE_FILE}"
systemctl daemon-reload
systemctl enable --now linuxmenux.service

msg_ok "Serviço linuxmenux.service iniciado com sucesso na porta ${PORT}!"

# 6. Inform user
SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}✔ Instalação concluída com sucesso!${NC}"
echo -e "Acesse o painel web em: ${CYAN}http://${SERVER_IP}:${PORT}${NC}"
echo -e "Para desinstalar de forma limpa a qualquer momento, execute:"
echo -e "${YELLOW}  sudo ${INSTALL_DIR}/uninstall.sh${NC}"
echo -e "${GREEN}=====================================================${NC}"
