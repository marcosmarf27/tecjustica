#!/usr/bin/env bash
# ==============================================================================
# TecJustica Plugin — install.sh
#
# Instala todas as dependencias necessarias para usar o plugin TecJustica
# no Claude Code (Linux / WSL2).
#
# Dependencias cobertas:
#   - Node.js 18+ (para npx mcp-remote)
#   - Google Chrome (para pje-download / cjf-jurisprudencia)
#   - browser-use CLI (para pje-download / cjf-jurisprudencia)
#   - LibreOffice headless (para tecjustica-docx converter DOCX -> PDF)
#   - python-docx (para tecjustica-docx gerar DOCX)
#   - Variaveis de ambiente TECJUSTICA_API_KEY e TECJUSTICA_PARSE_API_KEY
#
# O que NAO instala (por design):
#   - Claude Code (https://claude.ai/install.sh) — voce instala separado
#   - O plugin em si (se faz via /plugin marketplace add marcosmarf27/tecjustica
#     dentro de uma sessao do Claude)
#
# Uso basico:
#   curl -fsSL https://raw.githubusercontent.com/marcosmarf27/tecjustica/main/install.sh | bash
#
# Ou clone o repositorio e rode:
#   bash install.sh
#
# Flags:
#   --check-only          Apenas diagnostica o que esta instalado
#   --no-interactive      Nao pede chaves (usa TECJUSTICA_API_KEY/TECJUSTICA_PARSE_API_KEY do ambiente)
#   --skip-node           Nao instala Node.js
#   --skip-chrome         Nao instala Google Chrome
#   --skip-browser-use    Nao instala browser-use CLI
#   --skip-libreoffice    Nao instala LibreOffice (necessario para tecjustica-docx)
#   --skip-python-docx    Nao instala python-docx (necessario para tecjustica-docx)
#   --skip-env            Nao configura variaveis no ~/.bashrc
#   -h, --help            Mostra esta ajuda
# ==============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Cores e helpers de log
# -----------------------------------------------------------------------------
if [ -t 1 ] && command -v tput >/dev/null 2>&1; then
  BOLD=$(tput bold)
  GREEN=$(tput setaf 2)
  YELLOW=$(tput setaf 3)
  RED=$(tput setaf 1)
  BLUE=$(tput setaf 4)
  DIM=$(tput dim 2>/dev/null || echo)
  RESET=$(tput sgr0)
else
  BOLD=""; GREEN=""; YELLOW=""; RED=""; BLUE=""; DIM=""; RESET=""
fi

info()  { echo "${BLUE}[info]${RESET}  $*"; }
ok()    { echo "${GREEN}[ ok ]${RESET}  $*"; }
warn()  { echo "${YELLOW}[warn]${RESET}  $*"; }
error() { echo "${RED}[erro]${RESET}  $*" >&2; }
step()  { echo; echo "${BOLD}==> $*${RESET}"; }

# -----------------------------------------------------------------------------
# Flags
# -----------------------------------------------------------------------------
CHECK_ONLY=0
SKIP_INTERACTIVE=0
SKIP_NODE=0
SKIP_CHROME=0
SKIP_BROWSER_USE=0
SKIP_LIBREOFFICE=0
SKIP_PYTHON_DOCX=0
SKIP_ENV=0

usage() {
  sed -n '/^# Flags:/,/^# =====/p' "$0" | sed 's/^# //; s/^#//' | sed '$d'
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --check-only)       CHECK_ONLY=1; shift ;;
    --no-interactive)   SKIP_INTERACTIVE=1; shift ;;
    --skip-node)        SKIP_NODE=1; shift ;;
    --skip-chrome)      SKIP_CHROME=1; shift ;;
    --skip-browser-use) SKIP_BROWSER_USE=1; shift ;;
    --skip-libreoffice) SKIP_LIBREOFFICE=1; shift ;;
    --skip-python-docx) SKIP_PYTHON_DOCX=1; shift ;;
    --skip-env)         SKIP_ENV=1; shift ;;
    -h|--help)          usage; exit 0 ;;
    *) error "Opcao desconhecida: $1"; usage; exit 1 ;;
  esac
done

# -----------------------------------------------------------------------------
# Cabecalho
# -----------------------------------------------------------------------------
cat <<BANNER

${BOLD}TecJustica Plugin — Instalador de dependencias${RESET}
${DIM}https://github.com/marcosmarf27/tecjustica${RESET}

BANNER

# -----------------------------------------------------------------------------
# 0. Sanity checks de plataforma
# -----------------------------------------------------------------------------
step "Verificando plataforma"

OS_NAME="$(uname -s)"
if [[ "$OS_NAME" != "Linux" && "$OS_NAME" != "Darwin" ]]; then
  error "Plataforma nao suportada: $OS_NAME"
  error "Use Linux, macOS, ou WSL2 (em Windows)."
  exit 1
fi

if [[ "$OS_NAME" == "Linux" ]]; then
  if grep -qi microsoft /proc/version 2>/dev/null; then
    ok "Rodando em WSL2 (Linux dentro do Windows) — suportado."
  else
    ok "Rodando em Linux nativo — suportado."
  fi
elif [[ "$OS_NAME" == "Darwin" ]]; then
  ok "Rodando em macOS — suportado."
fi

# Detectar gerenciador de pacotes
PKG_MANAGER=""
if command -v apt-get >/dev/null 2>&1; then
  PKG_MANAGER="apt"
elif command -v dnf >/dev/null 2>&1; then
  PKG_MANAGER="dnf"
elif command -v brew >/dev/null 2>&1; then
  PKG_MANAGER="brew"
else
  warn "Nenhum gerenciador de pacote conhecido encontrado (apt/dnf/brew)."
  warn "Voce precisara instalar Node.js e Chrome manualmente."
fi
[[ -n "$PKG_MANAGER" ]] && info "Gerenciador de pacotes detectado: $PKG_MANAGER"

# -----------------------------------------------------------------------------
# 1. Checar / instalar Node.js 18+
# -----------------------------------------------------------------------------
install_node() {
  if [[ "$CHECK_ONLY" == "1" ]]; then return 0; fi
  case "$PKG_MANAGER" in
    apt)
      info "Instalando Node.js LTS via NodeSource..."
      curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
      sudo apt-get install -y nodejs
      ;;
    dnf)
      info "Instalando Node.js LTS via NodeSource..."
      curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
      sudo dnf install -y nodejs
      ;;
    brew)
      info "Instalando Node.js via brew..."
      brew install node
      ;;
    *)
      error "Instale Node.js 18+ manualmente (https://nodejs.org)."
      return 1
      ;;
  esac
}

check_node() {
  if ! command -v node >/dev/null 2>&1; then return 1; fi
  local major
  major=$(node --version | sed 's/^v//' | cut -d. -f1)
  [[ "$major" -ge 18 ]]
}

step "1. Node.js 18+"
if [[ "$SKIP_NODE" == "1" ]]; then
  warn "Pulando instalacao de Node.js (--skip-node)"
elif check_node; then
  ok "Node.js $(node --version) ja instalado."
else
  if [[ "$CHECK_ONLY" == "1" ]]; then
    warn "Node.js nao instalado ou versao < 18"
  else
    install_node
    if check_node; then
      ok "Node.js $(node --version) instalado com sucesso."
    else
      error "Falha ao instalar Node.js. Instale manualmente."
      exit 1
    fi
  fi
fi

# -----------------------------------------------------------------------------
# 2. Checar / instalar Google Chrome
# -----------------------------------------------------------------------------
install_chrome() {
  if [[ "$CHECK_ONLY" == "1" ]]; then return 0; fi
  case "$PKG_MANAGER" in
    apt)
      info "Baixando Google Chrome stable..."
      local tmp="/tmp/google-chrome-stable.deb"
      wget -q "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" -O "$tmp"
      sudo apt-get install -y "$tmp"
      rm -f "$tmp"
      ;;
    dnf)
      info "Instalando Google Chrome via dnf..."
      sudo dnf install -y fedora-workstation-repositories
      sudo dnf config-manager --set-enabled google-chrome
      sudo dnf install -y google-chrome-stable
      ;;
    brew)
      info "Instalando Google Chrome via brew cask..."
      brew install --cask google-chrome
      ;;
    *)
      error "Instale Google Chrome manualmente (https://www.google.com/chrome/)."
      return 1
      ;;
  esac
}

check_chrome() {
  command -v google-chrome >/dev/null 2>&1 || \
  command -v google-chrome-stable >/dev/null 2>&1 || \
  command -v chromium >/dev/null 2>&1 || \
  [[ -d "/Applications/Google Chrome.app" ]]
}

step "2. Google Chrome"
if [[ "$SKIP_CHROME" == "1" ]]; then
  warn "Pulando instalacao do Chrome (--skip-chrome)"
elif check_chrome; then
  if command -v google-chrome >/dev/null 2>&1; then
    ok "Google Chrome $(google-chrome --version 2>/dev/null | head -1) ja instalado."
  else
    ok "Google Chrome ja instalado."
  fi
else
  if [[ "$CHECK_ONLY" == "1" ]]; then
    warn "Google Chrome nao instalado"
  else
    install_chrome
    if check_chrome; then
      ok "Google Chrome instalado com sucesso."
    else
      warn "Chrome nao detectado apos instalacao — pode precisar reiniciar o shell."
    fi
  fi
fi

# -----------------------------------------------------------------------------
# 3. Checar / instalar browser-use CLI
# -----------------------------------------------------------------------------
step "3. browser-use CLI"

BROWSER_USE_BIN="$HOME/.browser-use-env/bin/browser-use"
BROWSER_USE_PATH_LINE='export PATH="$HOME/.browser-use-env/bin:$PATH"'

check_browser_use() {
  [[ -x "$BROWSER_USE_BIN" ]] || command -v browser-use >/dev/null 2>&1
}

if [[ "$SKIP_BROWSER_USE" == "1" ]]; then
  warn "Pulando instalacao do browser-use (--skip-browser-use)"
elif check_browser_use; then
  ok "browser-use ja instalado em $BROWSER_USE_BIN"
else
  if [[ "$CHECK_ONLY" == "1" ]]; then
    warn "browser-use nao instalado"
  else
    info "Instalando browser-use CLI..."
    curl -fsSL https://browser-use.com/cli/install.sh | bash
    if check_browser_use; then
      ok "browser-use instalado com sucesso."
    else
      warn "browser-use nao detectado apos instalacao — verifique o log acima."
    fi
  fi
fi

# -----------------------------------------------------------------------------
# 4. Checar / instalar LibreOffice (para tecjustica-docx)
# -----------------------------------------------------------------------------
install_libreoffice() {
  if [[ "$CHECK_ONLY" == "1" ]]; then return 0; fi
  case "$PKG_MANAGER" in
    apt)
      info "Instalando LibreOffice headless (core + writer)..."
      sudo apt-get install -y libreoffice-core libreoffice-writer --no-install-recommends
      ;;
    dnf)
      info "Instalando LibreOffice via dnf..."
      sudo dnf install -y libreoffice-core libreoffice-writer
      ;;
    brew)
      info "Instalando LibreOffice via brew cask..."
      brew install --cask libreoffice
      ;;
    *)
      error "Instale LibreOffice manualmente (https://www.libreoffice.org/download/)."
      return 1
      ;;
  esac
}

check_libreoffice() {
  command -v libreoffice >/dev/null 2>&1 || command -v soffice >/dev/null 2>&1
}

step "4. LibreOffice headless"
if [[ "$SKIP_LIBREOFFICE" == "1" ]]; then
  warn "Pulando instalacao do LibreOffice (--skip-libreoffice)"
elif check_libreoffice; then
  ok "LibreOffice ja instalado ($(libreoffice --version 2>/dev/null | head -1 || echo presente))"
else
  if [[ "$CHECK_ONLY" == "1" ]]; then
    warn "LibreOffice nao instalado — tecjustica-docx nao conseguira gerar PDF"
  else
    install_libreoffice
    if check_libreoffice; then
      ok "LibreOffice instalado com sucesso."
    else
      warn "LibreOffice nao detectado apos instalacao."
    fi
  fi
fi

# -----------------------------------------------------------------------------
# 5. Checar / instalar python-docx (para tecjustica-docx)
# -----------------------------------------------------------------------------
install_python_docx() {
  if [[ "$CHECK_ONLY" == "1" ]]; then return 0; fi
  if ! command -v python3 >/dev/null 2>&1; then
    error "python3 nao encontrado — instale-o antes (geralmente ja vem no Linux)."
    return 1
  fi
  info "Instalando python-docx via pip..."
  if pip3 install --user python-docx 2>/dev/null; then
    return 0
  fi
  warn "pip recusou a instalacao (PEP 668). Tentando --break-system-packages..."
  pip3 install --user --break-system-packages python-docx
}

check_python_docx() {
  python3 -c "import docx" 2>/dev/null
}

step "5. python-docx (skill tecjustica-docx)"
if [[ "$SKIP_PYTHON_DOCX" == "1" ]]; then
  warn "Pulando instalacao do python-docx (--skip-python-docx)"
elif check_python_docx; then
  ok "python-docx ja instalado."
else
  if [[ "$CHECK_ONLY" == "1" ]]; then
    warn "python-docx nao instalado — tecjustica-docx nao conseguira gerar DOCX"
  else
    install_python_docx || warn "Falha ao instalar python-docx."
    if check_python_docx; then
      ok "python-docx instalado com sucesso."
    else
      warn "python-docx nao detectado apos instalacao."
    fi
  fi
fi

# -----------------------------------------------------------------------------
# 6. Checar Claude Code (nao instala — so avisa)
# -----------------------------------------------------------------------------
step "6. Claude Code"
if command -v claude >/dev/null 2>&1; then
  ok "Claude Code $(claude --version 2>/dev/null || echo instalado)"
else
  warn "Claude Code nao encontrado."
  warn "Instale com: curl -fsSL https://claude.ai/install.sh | bash"
fi

# -----------------------------------------------------------------------------
# 7. Configurar variaveis de ambiente
# -----------------------------------------------------------------------------
SHELL_RC="$HOME/.bashrc"
if [[ -n "${ZSH_VERSION:-}" ]] || [[ "${SHELL:-}" == */zsh ]]; then
  SHELL_RC="$HOME/.zshrc"
fi

prompt_key() {
  local label="$1" varname="$2" prefix="$3" current="${!varname:-}"
  local input=""

  if [[ -n "$current" ]]; then
    echo "  ${DIM}(atual: ${current:0:8}...)${RESET}"
    read -p "  Manter a chave atual de $label? [S/n] " -r keep < /dev/tty
    if [[ ! "$keep" =~ ^[Nn]$ ]]; then
      echo "$current"
      return
    fi
  fi

  while true; do
    read -s -p "  Cole sua chave de $label ($prefix...): " input < /dev/tty
    echo
    if [[ -z "$input" ]]; then
      echo "$current"
      return
    fi
    if [[ "$input" == ${prefix}* ]]; then
      echo "$input"
      return
    fi
    warn "  Chave deve comecar com '$prefix'. Tente de novo ou deixe em branco para pular."
  done
}

write_env_block() {
  local mcp_key="$1" parse_key="$2"
  local marker_begin="# >>> TecJustica plugin >>>"
  local marker_end="# <<< TecJustica plugin <<<"

  if grep -q "$marker_begin" "$SHELL_RC" 2>/dev/null; then
    info "Removendo bloco TecJustica anterior de $SHELL_RC..."
    sed -i.bak "/$marker_begin/,/$marker_end/d" "$SHELL_RC"
  fi

  {
    echo ""
    echo "$marker_begin"
    echo "# Variaveis configuradas por install.sh em $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    [[ -n "$mcp_key" ]]   && echo "export TECJUSTICA_API_KEY=$mcp_key"
    [[ -n "$parse_key" ]] && echo "export TECJUSTICA_PARSE_API_KEY=$parse_key"
    echo "$BROWSER_USE_PATH_LINE"
    echo "$marker_end"
  } >> "$SHELL_RC"

  ok "Bloco TecJustica escrito em $SHELL_RC"
}

step "7. Variaveis de ambiente (${SHELL_RC/$HOME/~})"

if [[ "$SKIP_ENV" == "1" ]]; then
  warn "Pulando configuracao de variaveis (--skip-env)"
elif [[ "$CHECK_ONLY" == "1" ]]; then
  if [[ -n "${TECJUSTICA_API_KEY:-}" ]]; then
    ok "TECJUSTICA_API_KEY ja definida (${TECJUSTICA_API_KEY:0:8}...)"
  else
    warn "TECJUSTICA_API_KEY nao definida"
  fi
  if [[ -n "${TECJUSTICA_PARSE_API_KEY:-}" ]]; then
    ok "TECJUSTICA_PARSE_API_KEY ja definida (${TECJUSTICA_PARSE_API_KEY:0:8}...)"
  else
    warn "TECJUSTICA_PARSE_API_KEY nao definida (opcional, so para OCR)"
  fi
else
  MCP_KEY=""
  PARSE_KEY=""

  if [[ "$SKIP_INTERACTIVE" == "1" ]]; then
    MCP_KEY="${TECJUSTICA_API_KEY:-}"
    PARSE_KEY="${TECJUSTICA_PARSE_API_KEY:-}"
    info "Modo nao-interativo: usando chaves do ambiente se definidas."
  else
    cat <<MSG

  Cole as chaves de API nos prompts abaixo. Elas serao escritas em
  $SHELL_RC e carregadas a cada novo terminal.

  * MCP TecJustica Lite (obrigatoria)
    Cadastre-se em: https://tecjusticamcp-lite-production.up.railway.app/registro

  * TecJustica Parse (opcional — OCR de PDFs)
    Cadastre-se em: https://tecjustica-dashboard-production.up.railway.app/
    Deixe em branco se nao for usar OCR.

MSG
    MCP_KEY=$(prompt_key "MCP TecJustica Lite" "TECJUSTICA_API_KEY" "mcp_")
    PARSE_KEY=$(prompt_key "TecJustica Parse" "TECJUSTICA_PARSE_API_KEY" "tjp_")
  fi

  if [[ -z "$MCP_KEY" && -z "$PARSE_KEY" ]]; then
    warn "Nenhuma chave fornecida — pulando escrita em $SHELL_RC."
    warn "Voce podera rodar o install.sh de novo ou editar $SHELL_RC manualmente."
  else
    write_env_block "$MCP_KEY" "$PARSE_KEY"
  fi
fi

# -----------------------------------------------------------------------------
# 8. Verificacao final
# -----------------------------------------------------------------------------
step "Resumo"

verify() {
  local name="$1" check="$2"
  if eval "$check" >/dev/null 2>&1; then
    ok "$name"
  else
    warn "$name"
  fi
}

verify "Node.js 18+"              "check_node"
verify "Google Chrome"            "check_chrome"
verify "browser-use CLI"          "check_browser_use"
verify "LibreOffice headless"     "check_libreoffice"
verify "python-docx"              "check_python_docx"
verify "Claude Code (claude)"     "command -v claude"

# Recarregar $SHELL_RC numa subshell so para o resumo final
if [[ -f "$SHELL_RC" ]]; then
  # shellcheck disable=SC1090
  source "$SHELL_RC" 2>/dev/null || true
fi

if [[ -n "${TECJUSTICA_API_KEY:-}" ]]; then
  ok "TECJUSTICA_API_KEY     (${TECJUSTICA_API_KEY:0:8}...)"
else
  warn "TECJUSTICA_API_KEY NAO configurada — MCP nao funcionara"
fi
if [[ -n "${TECJUSTICA_PARSE_API_KEY:-}" ]]; then
  ok "TECJUSTICA_PARSE_API_KEY (${TECJUSTICA_PARSE_API_KEY:0:8}...)"
else
  info "TECJUSTICA_PARSE_API_KEY nao configurada (opcional — so para OCR)"
fi

# -----------------------------------------------------------------------------
# 9. Proximos passos
# -----------------------------------------------------------------------------
cat <<DONE

${BOLD}${GREEN}✔ Pronto.${RESET}

Proximos passos:

  1. ${BOLD}Abra um novo terminal${RESET} (ou rode ${DIM}source $SHELL_RC${RESET}) para
     carregar as variaveis de ambiente no shell atual.

  2. Inicie o Claude Code:

       ${DIM}\$${RESET} claude

  3. Dentro da sessao do Claude, instale o plugin:

       /plugin marketplace add marcosmarf27/tecjustica
       /plugin install tecjustica@tecjustica-plugins

  4. Verifique que o MCP carregou:

       /mcp

     Esperado: ${GREEN}tecjustica${RESET} listado como ${GREEN}connected${RESET}.

  5. Teste:

       "Analise o processo NNNNNNN-DD.AAAA.J.TT.OOOO"

     (troque pelo CNJ de um processo real ao qual voce tem acesso)

Documentacao completa: https://github.com/marcosmarf27/tecjustica#readme

DONE
