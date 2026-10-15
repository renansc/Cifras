#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

printf '\n=== NanotechSoft-Cifras: verificação de dependências ===\n'

# Tenta instalar um pacote do sistema. Se não for root, usa sudo quando disponível.
apt_install() {
    local pkg="$1"
    echo "Tentando instalar: $pkg"
    if ! command -v apt-get >/dev/null 2>&1; then
        return 1
    fi
    if [ "$(id -u)" -eq 0 ]; then
        apt-get update && apt-get install -y "$pkg"
    elif command -v sudo >/dev/null 2>&1; then
        echo "O sistema pode pedir sua senha do sudo."
        sudo apt-get update && sudo apt-get install -y "$pkg"
    else
        return 1
    fi
}

# Python é obrigatório.
if ! command -v python3 >/dev/null 2>&1; then
    echo "FALTA: python3"
    apt_install python3 || {
        echo "ERRO: não consegui instalar python3 automaticamente."
        echo "Instale manualmente: sudo apt install python3"
        exit 1
    }
fi

PYTHON=python3

# Verifica módulo Python; tenta APT e depois ambiente virtual local como alternativa.
ensure_module() {
    local module="$1"
    local apt_pkg="$2"
    local pip_pkg="$3"

    if "$PYTHON" -c "import $module" >/dev/null 2>&1; then
        echo "OK: módulo $module"
        return 0
    fi

    echo "FALTA: módulo Python '$module'"
    if apt_install "$apt_pkg" && python3 -c "import $module" >/dev/null 2>&1; then
        echo "INSTALADO: $module ($apt_pkg)"
        PYTHON=python3
        return 0
    fi

    echo "APT não resolveu '$module'. Tentando ambiente virtual local .venv..."
    if [ ! -x .venv/bin/python ]; then
        python3 -m venv .venv >/dev/null 2>&1 || {
            echo "FALTA: suporte a venv (python3-venv)."
            apt_install python3-venv || true
            python3 -m venv .venv >/dev/null 2>&1 || return 1
        }
    fi
    .venv/bin/python -m pip install --upgrade pip >/dev/null 2>&1 || true
    .venv/bin/python -m pip install "$pip_pkg"
    PYTHON=.venv/bin/python
    "$PYTHON" -c "import $module" >/dev/null 2>&1
}

# Se uma dependência cair no .venv, garante que as demais também existam no Python escolhido.
ensure_module bs4 python3-bs4 beautifulsoup4 || {
    echo "ERRO: não consegui instalar BeautifulSoup (bs4)."
    echo "Tente: sudo apt install python3-bs4"
    exit 1
}
ensure_module reportlab python3-reportlab reportlab || {
    echo "ERRO: não consegui instalar ReportLab."
    echo "Tente: sudo apt install python3-reportlab"
    exit 1
}

# Caso PYTHON tenha mudado para .venv no segundo módulo, confira bs4 nesse mesmo ambiente.
if ! "$PYTHON" -c 'import bs4' >/dev/null 2>&1; then
    echo "FALTA: bs4 no ambiente virtual. Instalando..."
    "$PYTHON" -m pip install beautifulsoup4
fi

printf '\n=== Dependências OK ===\n'
echo "Python usado: $PYTHON"
printf '\n=== Gerando NanotechSoft-Cifras ===\n'
"$PYTHON" app/gerar_multi.py
"$PYTHON" app/aplicar_carrossel_giratorio.py
"$PYTHON" app/aplicar_menu3d.py
"$PYTHON" app/aplicar_v14.py
"$PYTHON" app/gerar_pdf.py

echo
printf '=== CONCLUÍDO ===\n'
echo "Aplicação: saida/NanotechSoft-Cifras.html"
echo "PDFs: saida/pdf/"
