#!/usr/bin/env bash
set -euo pipefail
REPO="https://github.com/renansc/Cifras.git"
BRANCH="main"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for command in git rsync; do
  if ! command -v "$command" >/dev/null; then
    echo "Falta o comando $command. Instale: sudo apt install git rsync"
    exit 1
  fi
done
if ! git config --global user.name >/dev/null || ! git config --global user.email >/dev/null; then
  echo "Configure sua identidade uma vez antes de publicar:"
  echo '  git config --global user.name "Seu Nome"'
  echo '  git config --global user.email "seu@email.com"'
  exit 1
fi
TEMP="$(mktemp -d)"
trap 'rm -rf "$TEMP"' EXIT
echo "Clonando $REPO..."
git clone --branch "$BRANCH" "$REPO" "$TEMP/repo"
echo "Copiando aplicativo completo..."
rsync -a --exclude='.git/' \
 --exclude='backup*.json' --exclude='*.bak' --exclude='__pycache__/' \
 --exclude='.venv/' --exclude='venv/' --exclude='*.pyc' \
 "$ROOT/" "$TEMP/repo/"
cd "$TEMP/repo"
cat >> .gitignore <<'IGNORE'

# Backups locais: nunca publicar dados pessoais no repositório público.
backup*.json
**/backup*.json
__pycache__/
*.pyc
.venv/
venv/
IGNORE
git add .
if git diff --cached --quiet; then
  echo "Nada novo para publicar."
  exit 0
fi
git commit -m "feat: publicar NanotechSoft-Cifras V16 completo com modo TV"
echo "Enviando alterações ao GitHub..."
git push origin "$BRANCH"
echo
echo "OK! Projeto publicado em https://github.com/renansc/Cifras"
echo "Verifique no GitHub os arquivos servidor_tv.py, tv.html, saida/, app/."
