#!/usr/bin/env bash
# Wrapper multiplataforma do tjocr.
# Detecta SO/arquitetura, escolhe o binário embutido em bin/, garante permissão de
# execução e repassa TODOS os argumentos para o binário. Funciona em WSL/Linux e no
# Git Bash do Windows. A credencial (API key) é tratada pelo próprio binário.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$SKILL_DIR/bin"

os="$(uname -s 2>/dev/null || echo Windows)"
arch="$(uname -m 2>/dev/null || echo x86_64)"

case "$os" in
  Linux*)
    case "$arch" in
      x86_64 | amd64) b="$BIN/tjocr_linux_amd64" ;;
      *) echo "tjocr: esta skill traz somente amd64 (sua arquitetura: $arch). Peça a build arm64." >&2; exit 2 ;;
    esac
    ;;
  MINGW* | MSYS* | CYGWIN* | Windows*) b="$BIN/tjocr_windows_amd64.exe" ;;
  Darwin*) echo "tjocr: sem binário para macOS; rode em WSL, Linux ou Windows." >&2; exit 2 ;;
  *) b="$BIN/tjocr_linux_amd64" ;;
esac

[ -f "$b" ] || { echo "tjocr: binário não encontrado: $b" >&2; exit 2; }
chmod +x "$b" 2>/dev/null || true

exec "$b" "$@"
