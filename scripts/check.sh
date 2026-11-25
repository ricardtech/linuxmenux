#!/usr/bin/env bash
# ==============================================================================
# Linux Menux - Fast Verification Script (Fast Feedback Loop)
# Valida sintaxe do backend e compilação do frontend Vue 3 em tempo real.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🔍 [1/3] Validando sintaxe Python do Backend..."
cd "${ROOT_DIR}/backend"
python3 -m py_compile main.py core/*.py services/*.py 2>&1
echo "✅ Backend: Todos os arquivos Python possuem sintaxe 100% válida."

echo "🔍 [2/3] Verificando integridade das dependências do Backend..."
if [ -d "venv" ]; then
    echo "✅ Backend: venv isolado detectado."
else
    echo "ℹ️ Backend: rodando com Python do ambiente."
fi

echo "🔍 [3/3] Validando compilação do Frontend em Vue 3 + Vite (Bun)..."
cd "${ROOT_DIR}/frontend"
if command -v bun &>/dev/null; then
    bun run build
    echo "✅ Frontend: Build estático gerado com sucesso em backend/static/."
else
    echo "❌ Erro: Bun não encontrado no PATH."
    exit 1
fi

echo ""
echo "🎉 [SUCESSO] Todas as checagens do Linux Menux foram aprovadas com sucesso!"
