#!/usr/bin/env bash
# Wrapper de inicializacao do MCP TecJustica Lite.
#
# Chamado pelo .mcp.json do plugin via:
#
#   "command": "bash",
#   "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/start-mcp.sh"]
#
# Existe para dar UX decente: se TECJUSTICA_API_KEY nao estiver definida
# (ou estiver com prefixo errado), o servidor MCP aparece em /mcp como
# `failed` com uma mensagem stderr acionavel explicando exatamente o que
# fazer, em vez de sumir silenciosamente da lista.

set -euo pipefail

if [ -z "${TECJUSTICA_API_KEY:-}" ]; then
  cat >&2 <<'ERR'
================================================================
  TecJustica MCP nao pode iniciar: TECJUSTICA_API_KEY vazia
================================================================

A variavel de ambiente TECJUSTICA_API_KEY nao esta definida no
shell que iniciou o Claude Code. Sem ela, o servidor MCP nao
consegue autenticar no DataLake PDPJ/CNJ.

Como corrigir:

  1. Gere sua chave em:
     https://tecjusticamcp-lite-production.up.railway.app/

  2. Adicione ao ~/.bashrc (ou ~/.zshrc se usa zsh):

       export TECJUSTICA_API_KEY=mcp_SUA_CHAVE_AQUI

  3. Abra um terminal NOVO (o Claude Code le as env vars uma
     unica vez ao iniciar), entre na pasta do projeto e rode
     `claude` de novo.

Apos isso, dentro da sessao, rode /mcp e confirme que
'tecjustica' aparece como `connected`.
================================================================
ERR
  exit 1
fi

if [[ ! "${TECJUSTICA_API_KEY}" =~ ^mcp_ ]]; then
  cat >&2 <<'ERR'
================================================================
  TecJustica MCP: TECJUSTICA_API_KEY com prefixo errado
================================================================

A chave exportada nao comeca com 'mcp_'. O MCP Lite aceita
apenas chaves com prefixo `mcp_` seguidas de 32+ caracteres
hexadecimais.

Voce pode estar usando por engano a chave do outro portal
(TecJustica Parse, prefixo `tjp_`, usada pela skill de OCR).
As duas NAO sao intercambiaveis.

- Chave do MCP Lite (o que voce precisa agora):
    https://tecjusticamcp-lite-production.up.railway.app/
    exporta como TECJUSTICA_API_KEY

- Chave do Parse (opcional, so para OCR de PDFs):
    https://tecjustica-dashboard-production.up.railway.app/
    exporta como TECJUSTICA_PARSE_API_KEY

Corrija o valor de TECJUSTICA_API_KEY no ~/.bashrc, abra um
terminal novo e reinicie o Claude Code.
================================================================
ERR
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  cat >&2 <<'ERR'
================================================================
  TecJustica MCP: npx nao encontrado no PATH
================================================================

O servidor MCP depende de `npx mcp-remote`. Voce precisa
instalar Node.js 18+ antes de usar o plugin.

Instalacao rapida (Ubuntu/Debian/WSL):

  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
  sudo apt install -y nodejs

Depois rode `node --version` para confirmar (tem que ser v18+).
================================================================
ERR
  exit 1
fi

exec npx -y mcp-remote \
  https://tecjusticamcp-lite-production.up.railway.app/mcp \
  --header "Authorization: Bearer ${TECJUSTICA_API_KEY}"
