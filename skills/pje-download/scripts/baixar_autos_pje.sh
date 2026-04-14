#!/usr/bin/env bash
# ==============================================================================
# baixar_autos_pje.sh — Baixa os autos de um processo do PJE (TJCE 1º Grau)
#
# Uso:
#   ./baixar_autos_pje.sh NNNNNNN-DD.AAAA.J.TT.OOOO
#   ./baixar_autos_pje.sh NNNNNNN-DD.AAAA.J.TT.OOOO --output ~/Downloads
#
# Primeiro uso: Chrome abre para login. Cookies salvos para próximas vezes.
#
# Fluxo: Login → Painel Usuário → Filtros Tarefas → Número processo →
#        Pesquisar → Tarefa → Processo → Abrir autos → Download → curl
# ==============================================================================

export PATH="$HOME/.browser-use-env/bin:$PATH"
COOKIES_FILE="$HOME/.browser-use/pje_cookies.json"
PJE_URL="https://pje.tjce.jus.br/"

# --- Parâmetros ---
NUMERO="${1:-}"

# Destino padrão: raiz do projeto Claude Code (fallback para CWD quando rodado fora do Claude)
OUTPUT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

if [[ -z "$NUMERO" ]]; then
    echo "Uso: $0 <numero-processo> [--output <dir>]"
    echo "Ex:  $0 NNNNNNN-DD.AAAA.J.TT.OOOO"
    echo ""
    echo "Destino padrao: \$CLAUDE_PROJECT_DIR (raiz do projeto) ou CWD."
    echo "Use --output para forcar outra pasta."
    exit 1
fi

[[ "${2:-}" == "--output" && -n "${3:-}" ]] && { OUTPUT_DIR="$3"; mkdir -p "$OUTPUT_DIR"; }

# Validar formato
if [[ ! "$NUMERO" =~ ^[0-9]{7}-[0-9]{2}\.[0-9]{4}\.[0-9]\.[0-9]{2}\.[0-9]{4}$ ]]; then
    echo "ERRO: Formato inválido: $NUMERO"
    exit 1
fi

OUTPUT_FILE="$OUTPUT_DIR/$NUMERO.pdf"

echo "=== PJE Download Autos ==="
echo "Processo: $NUMERO"
echo ""

# ==========================================================================
# Funções
# ==========================================================================
bu() { browser-use "$@" 2>/dev/null; }

# Busca índice de um elemento pelo padrão no state
idx() {
    bu state | grep "$1" | head -1 | grep -oE '\[[0-9]+' | head -1 | tr -d '['
}

# Espera padrão aparecer no state (max tentativas x 2s)
esperar() {
    local p="$1" max="${2:-15}" i=0
    while [[ $i -lt $max ]]; do
        bu state | grep -q "$p" && return 0
        sleep 2
        i=$((i + 1))
    done
    return 1
}

# Click + select all + type (evita duplicar em campos pré-preenchidos)
preencher() { bu click "$1"; bu keys "Control+a"; bu type "$2"; }

# Fecha tudo ao sair
cleanup() { bu close 2>/dev/null || true; }
trap cleanup EXIT

# Verificação
command -v browser-use &>/dev/null || { echo "ERRO: browser-use não instalado"; exit 1; }

# ==========================================================================
# 1. ABRIR PJE + RESTAURAR SESSÃO
# ==========================================================================
echo "[1/8] Abrindo PJE..."
bu close || true
# --headed só quando precisa login (primeiro uso)
HEADED_FLAG=""
if [[ ! -f "$COOKIES_FILE" ]]; then
    HEADED_FLAG="--headed"
fi
bu --profile "Default" $HEADED_FLAG open "$PJE_URL"
sleep 3

# Importar cookies salvos
if [[ -f "$COOKIES_FILE" ]]; then
    bu cookies import "$COOKIES_FILE" || true
    bu open "$PJE_URL"
    sleep 4
fi

# ==========================================================================
# 2. LOGIN (se necessário)
# ==========================================================================
if bu state | grep -q "id=username\|id=kc-login"; then
    if [[ -z "$HEADED_FLAG" ]]; then
        # Estava headless mas precisa login — reabrir com janela
        echo "    Cookies expiraram. Abrindo Chrome para login..."
        bu close || true
        bu --profile "Default" --headed open "$PJE_URL"
        sleep 3
    fi
    echo ""
    echo "  ┌──────────────────────────────────────────────┐"
    echo "  │  Faça login no Chrome e pressione ENTER aqui │"
    echo "  └──────────────────────────────────────────────┘"
    echo ""
    read -r -p "  > "
    sleep 2
fi

bu state | grep -q "Abrir menu\|Quadro de avisos" || { echo "ERRO: Login falhou"; exit 1; }
bu cookies export "$COOKIES_FILE" || true
echo "    Login OK"

# ==========================================================================
# 3. GARANTIR QUE O PAINEL INTERNO CARREGOU
#
# Após login, a tela mostra "Quadro de avisos" com botão "Painel do usuário".
# Às vezes o iframe ngFrame já carrega (liTarefas aparece).
# Se não carregou, clicar em "Painel do usuário" para forçar.
# ==========================================================================
echo "[2/8] Carregando painel..."

# Tentar 3x esperar o iframe carregar sozinho
PAINEL_OK=false
for tentativa in 1 2 3; do
    if bu state | grep -q "liTarefas"; then
        PAINEL_OK=true
        break
    fi
    sleep 3
done

# Se não carregou, clicar "Painel do usuário"
if [[ "$PAINEL_OK" == "false" ]]; then
    PAINEL_IDX=$(idx "Painel do usu")
    if [[ -n "$PAINEL_IDX" ]]; then
        bu click "$PAINEL_IDX"
        sleep 5
    fi
    if ! esperar "liTarefas" 10; then
        echo "ERRO: Painel não carregou"
        exit 1
    fi
fi
echo "    Painel OK"

# ==========================================================================
# 4. EXPANDIR FILTROS DE TAREFAS
#
# Seção "Tarefas" tem um div aria-expanded=false com texto "Filtros".
# É o SEGUNDO div com Filtros (o primeiro é de "Minhas tarefas").
# Ao clicar, expande campos: itNrProcesso, itCompetencia, itEtiqueta.
# ==========================================================================
echo "[3/8] Abrindo filtros..."

# Pegar o filtro de Tarefas (segundo aria-expanded com Filtros)
FILTRO_IDX=$(bu state | grep "aria-expanded=false" | tail -1 | grep -oE '\[[0-9]+\]' | tr -d '[]' | head -1)
bu click "$FILTRO_IDX"
sleep 2

# Se filtros já estavam abertos, itNrProcesso já deve estar visível
# Se não, tentar de novo
if ! bu state | grep -q "itNrProcesso"; then
    # Tentar o outro filtro
    FILTRO_IDX=$(bu state | grep "aria-expanded" | grep -oE '\[[0-9]+\]' | tr -d '[]' | tail -1)
    bu click "$FILTRO_IDX"
    sleep 2
fi

bu state | grep -q "itNrProcesso" || { echo "ERRO: Campo de filtro não apareceu"; exit 1; }
echo "    Filtros OK"

# ==========================================================================
# 5. PREENCHER NÚMERO E PESQUISAR
#
# Campo itNrProcesso aceita o número completo (ex: NNNNNNN-DD.AAAA.J.TT.OOOO).
# Botão Pesquisar é um <button> logo após os inputs.
# Resultado: aparece uma tarefa com título [Sec], [Gab], [StArq], etc.
# ==========================================================================
echo "[4/8] Pesquisando $NUMERO..."

NR_IDX=$(idx "itNrProcesso")
preencher "$NR_IDX" "$NUMERO"
sleep 1

PESQ_IDX=$(bu state | grep -B1 "Pesquisar" | grep "<button" | head -1 | grep -oE '\[[0-9]+\]' | tr -d '[]' | head -1)
bu click "$PESQ_IDX"
sleep 5

# Verificar se achou tarefa
if ! bu state | grep -q '<a title=\['; then
    # Esperar mais
    esperar '<a title=\[' 10 || { echo "ERRO: Processo não encontrado nas tarefas"; exit 1; }
fi
echo "    Encontrado"

# ==========================================================================
# 6. CLICAR NA TAREFA → PROCESSO → ABRIR AUTOS
#
# A tarefa aparece como <a title="[Sec] - ..."> ou "[Gab] - ..." etc.
# Ao clicar, abre lista com o processo. Clicar no processo abre detalhes.
# Botão "Abrir autos" (ícone de livro) abre autos em nova aba.
# ==========================================================================
echo "[5/8] Abrindo tarefa..."

TAREFA_IDX=$(bu state | grep '<a title=\[' | head -1 | grep -oE '\[[0-9]+\]' | tr -d '[]' | head -1)
bu click "$TAREFA_IDX"
sleep 3

esperar "$NUMERO" 10 || { echo "ERRO: Processo não listado na tarefa"; exit 1; }

echo "[6/8] Abrindo autos..."

# Clicar no processo (span antes do número)
PROC_IDX=$(bu state | grep -B3 "$NUMERO" | grep "<span" | head -1 | grep -oE '\[[0-9]+\]' | tr -d '[]' | head -1)
bu click "$PROC_IDX"
sleep 3

# Clicar "Abrir autos" (ícone do livro)
esperar "title=Abrir autos" 10 || { echo "ERRO: Botão Abrir autos não apareceu"; exit 1; }

AUTOS_IDX=$(idx "title=Abrir autos")
bu click "$AUTOS_IDX"
sleep 5

# Mudar para aba dos autos
bu switch 1 2>/dev/null || true
sleep 2

esperar "Download autos do processo" 15 || { echo "ERRO: Autos não carregaram"; exit 1; }
echo "    Autos OK"

# ==========================================================================
# 7. DOWNLOAD DOS AUTOS
#
# Botão "Download autos do processo" abre painel com opções.
# Botão "Download" (input type=button value=Download) inicia geração do PDF.
# PDF abre em nova aba (index 2) com URL do MinIO (S3):
#   https://minio-pjedocs.tjce.jus.br/...processo.pdf?X-Amz-Expires=120
# A URL expira em 120 segundos — baixar imediatamente com curl.
# ==========================================================================
echo "[7/8] Solicitando download..."

bu click "$(idx 'Download autos do processo')"
sleep 2
bu click "$(idx 'value=Download type=button')"

echo "[8/8] Gerando PDF (até 3 min)..."

TENTATIVAS=0
PDF_URL=""
while [[ $TENTATIVAS -lt 36 ]]; do
    sleep 5
    SWITCH=$(bu switch 2 2>&1 || echo "fail")
    if echo "$SWITCH" | grep -q "switched"; then
        RESULT=$(bu eval "window.location.href" 2>&1 || echo "")
        if echo "$RESULT" | grep -q "\.pdf"; then
            PDF_URL=$(echo "$RESULT" | sed 's/result: //')
            break
        fi
        # Pode ser página "aguarde" — voltar e esperar
        bu switch 1 2>&1 || true
    fi
    TENTATIVAS=$((TENTATIVAS + 1))
    echo -n "."
done
echo ""

[[ -z "$PDF_URL" ]] && { echo "ERRO: PDF não gerado (timeout)"; exit 1; }

echo "    Baixando..."
curl -sL -o "$OUTPUT_FILE" "$PDF_URL"

if [[ -f "$OUTPUT_FILE" ]] && [[ $(wc -c < "$OUTPUT_FILE" | tr -d ' ') -gt 1000 ]]; then
    TAMANHO=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo ""
    echo "=== Concluído ==="
    echo "Arquivo: $OUTPUT_FILE ($TAMANHO)"
else
    echo "ERRO: Download falhou"
    rm -f "$OUTPUT_FILE"
    exit 1
fi
