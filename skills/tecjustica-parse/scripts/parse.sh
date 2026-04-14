#!/usr/bin/env bash
# TecJustica Parse — Extrair texto de PDF via API OCR
# Uso: bash parse.sh <arquivo.pdf> [--enhance] [--key KEY] [--output FILE] [--dpi N] [--pages RANGE]

set -euo pipefail

API_URL="https://marcosmarf27--tecjustica-parse-parseservice-serve.modal.run"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load config.env if exists (user's API key)
if [[ -f "$SKILL_DIR/config.env" ]]; then
  source "$SKILL_DIR/config.env"
fi

# Defaults
PDF_PATH=""
API_KEY="${TECJUSTICA_PARSE_API_KEY:-${TECJUSTICA_API_KEY:-}}"
ENHANCE="false"
OUTPUT=""
DPI="150"
PAGES=""

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --enhance) ENHANCE="true"; shift ;;
    --key) API_KEY="$2"; shift 2 ;;
    --output|-o) OUTPUT="$2"; shift 2 ;;
    --dpi) DPI="$2"; shift 2 ;;
    --pages) PAGES="$2"; shift 2 ;;
    --help|-h)
      echo "Uso: bash parse.sh <arquivo.pdf> [--enhance] [--key KEY] [--output FILE] [--dpi N] [--pages RANGE]"
      echo ""
      echo "  --enhance     Ativar IA Vision (corrige erros, remove ruido)"
      echo "  --key KEY     API key (ou setar TECJUSTICA_PARSE_API_KEY)"
      echo "  --output FILE Salvar resultado em arquivo"
      echo "  --dpi N       Resolucao: 72 (rapido), 150 (padrao), 300 (maximo)"
      echo "  --pages RANGE Paginas: '1-5,10,15-20'"
      exit 0
      ;;
    -*) echo "Opcao desconhecida: $1" >&2; exit 1 ;;
    *) PDF_PATH="$1"; shift ;;
  esac
done

# Validacoes
if [[ -z "$PDF_PATH" ]]; then
  echo "Erro: informe o caminho do PDF" >&2
  echo "Uso: bash parse.sh <arquivo.pdf> [--enhance] [--key KEY]" >&2
  exit 1
fi

if [[ ! -f "$PDF_PATH" ]]; then
  echo "Erro: arquivo nao encontrado: $PDF_PATH" >&2
  exit 1
fi

if [[ -z "$API_KEY" ]]; then
  echo "Erro: API key nao configurada. Use --key ou export TECJUSTICA_PARSE_API_KEY" >&2
  exit 1
fi

# Resolve para caminho absoluto ANTES de qualquer operacao
PDF_PATH="$(cd "$(dirname "$PDF_PATH")" && pwd)/$(basename "$PDF_PATH")"

FILE_SIZE=$(stat -c%s "$PDF_PATH" 2>/dev/null || stat -f%z "$PDF_PATH" 2>/dev/null)
FILE_MB=$(python3 -c "print(f'{$FILE_SIZE/1048576:.1f}')")
FILENAME=$(basename "$PDF_PATH")

echo "Processando: $FILENAME ($FILE_MB MB)" >&2
[[ "$ENHANCE" == "true" ]] && echo "Enhance: ativado (IA Vision)" >&2

FORM_ARGS=(
  -F "file=@${PDF_PATH}"
  -F "ocr_engine=paddle"
  -F "language=pt"
  -F "dpi=$DPI"
  -F "enhance=$ENHANCE"
)
[[ -n "$PAGES" ]] && FORM_ARGS+=(-F "target_pages=$PAGES")

# Enviar PDF
RESPONSE=$(curl -s -X POST "$API_URL/parse/async" \
  -H "X-API-Key: $API_KEY" \
  "${FORM_ARGS[@]}")

# Check if response is a cache hit (direct result), async job, or error
IS_CACHE=$(echo "$RESPONSE" | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
    if 'markdown' in d:
        print('cache')
    elif 'job_id' in d:
        print(d['job_id'])
    elif 'detail' in d:
        print('api_error:' + str(d['detail']))
    else:
        print('error')
except:
    print('parse_error')
" 2>/dev/null)

if [[ "$IS_CACHE" == parse_error ]]; then
  echo "Erro: resposta invalida da API" >&2
  echo "$RESPONSE" | head -200 >&2
  exit 1
elif [[ "$IS_CACHE" == api_error:* ]]; then
  echo "Erro da API: ${IS_CACHE#api_error:}" >&2
  exit 1
elif [[ "$IS_CACHE" == "cache" ]]; then
  echo "Cache hit!" >&2
  RESULT=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin)['markdown'])")
  echo "$RESPONSE" | python3 -c "
import json,sys
r = json.load(sys.stdin)
print(f'Concluido (cache) | {r[\"num_paginas\"]} pgs ({r[\"paginas_texto\"]} texto + {r[\"paginas_ocr\"]} OCR) | {len(r[\"markdown\"]):,} chars', file=sys.stderr)
" 2>&1 >&2
  if [[ -n "$OUTPUT" ]]; then
    echo "$RESULT" > "$OUTPUT"
    echo "Salvo em: $OUTPUT" >&2
  else
    echo "$RESULT"
  fi
  exit 0
elif [[ "$IS_CACHE" == "error" || -z "$IS_CACHE" ]]; then
  echo "Erro ao enviar PDF:" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

JOB_ID="$IS_CACHE"
echo "Job: $JOB_ID" >&2

# Polling
START_TIME=$(date +%s)
while true; do
  sleep 5
  STATUS_RESP=$(curl -s -H "X-API-Key: $API_KEY" "$API_URL/parse/status/$JOB_ID")
  STATUS=$(echo "$STATUS_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])" 2>/dev/null)

  ELAPSED=$(( $(date +%s) - START_TIME ))

  if [[ "$STATUS" == "done" ]]; then
    RESULT=$(echo "$STATUS_RESP" | python3 -c "
import json,sys
d = json.load(sys.stdin)
r = d['result']
print(r['markdown'])
" 2>/dev/null)

    echo "$STATUS_RESP" | python3 -c "
import json,sys
d = json.load(sys.stdin)
r = d['result']
print(f'Concluido em {r[\"tempo_segundos\"]:.1f}s | {r[\"num_paginas\"]} pgs ({r[\"paginas_texto\"]} texto + {r[\"paginas_ocr\"]} OCR) | {len(r[\"markdown\"]):,} chars', file=sys.stderr)
if r.get('enhance_usado'):
    vision = sum(1 for p in r['paginas'] if p['metodo'] == 'ocr+vision')
    print(f'Enhance: {vision} paginas corrigidas com IA Vision', file=sys.stderr)
" 2>&1 >&2

    if [[ -n "$OUTPUT" ]]; then
      echo "$RESULT" > "$OUTPUT"
      echo "Salvo em: $OUTPUT" >&2
    else
      echo "$RESULT"
    fi
    exit 0

  elif [[ "$STATUS" == "failed" ]]; then
    ERROR=$(echo "$STATUS_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('error','erro desconhecido'))" 2>/dev/null)
    echo "Falhou: $ERROR" >&2
    exit 1

  else
    echo "Processando... ${ELAPSED}s" >&2
  fi

  if [[ $ELAPSED -gt 1800 ]]; then
    echo "Timeout: processamento excedeu 30 minutos" >&2
    exit 1
  fi
done
