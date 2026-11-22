#!/usr/bin/env bash
# ==========================================================
# Linux Menux - Uninstaller Script
# Safely and completely removes LinuxMenux without touching Docker,
# user data, Dokploy or system packages.
# ==========================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

INSTALL_DIR="/usr/local/share/linuxmenux"
SERVICE_FILE="/etc/systemd/system/linuxmenux.service"

if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}Este script deve ser executado como root (use sudo).${NC}"
    exit 1
fi

echo -e "${CYAN}Desinstalando LinuxMenux...${NC}"

# 1. Stop and disable systemd service
if systemctl is-active --quiet linuxmenux.service 2>/dev/null; then
    echo "Parando serviço linuxmenux..."
    systemctl stop linuxmenux.service
fi

if systemctl is-enabled --quiet linuxmenux.service 2>/dev/null; then
    echo "Desabilitando serviço linuxmenux..."
    systemctl disable linuxmenux.service
fi

# 2. Remove systemd unit file
if [ -f "${SERVICE_FILE}" ]; then
    rm -f "${SERVICE_FILE}"
    systemctl daemon-reload
fi

# 3. Remove application directory
if [ -d "${INSTALL_DIR}" ]; then
    echo "Removendo diretório ${INSTALL_DIR}..."
    rm -rf "${INSTALL_DIR}"
fi

# 4. Remove temporary lock file if exists
rm -f /run/linuxmenux-update.lock

echo -e "${GREEN}✓ LinuxMenux desinstalado com sucesso! O sistema está intacto.${NC}"
