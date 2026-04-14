#!/usr/bin/env bash
# ==============================================================================
# baixar_autos_pje.sh — Baixa os autos de um processo do PJE (TJCE 1º Grau)
#
# Uso:
#   ./baixar_autos_pje.sh NNNNNNN-DD.AAAA.J.TT.OOOO
#   ./baixar_autos_pje.sh NNNNNNN-DD.AAAA.J.TT.OOOO --output ~/Downloads
#   ./baixar_autos_pje.sh --login                     # so faz login inicial
#
# Modos:
#   Download: navega e baixa o PDF do processo. Se cookies invalidos, abre
#             Chrome e aguarda login manual (detecta TTY vs non-TTY).
#   Login:    apenas abre Chrome, aguarda login manual, salva cookies e sai.
#             Util para primeira execucao ou quando cookies expiram.
#
# Compatibilidade TTY:
#   - Com TTY (usuario rodando direto): aceita ENTER apos login OU detecta
#     automaticamente quando a tela de login sai (o que vier primeiro).
#   - Sem TTY (Claude Code chamando o script): poll puro do estado do
#     browser-use a cada 5s, timeout 5 min. Nao trava em `read`.
#
# Fluxo download: Login → Painel Usuário → Filtros Tarefas → Numero processo →
#                 Pesquisar → Tarefa → Processo → Abrir autos → Download → curl
# ==============================================================================

export PATH="$HOME/.browser-use-env/bin:$PATH"
COOKIES_FILE="$HOME/.browser-use/pje_cookies.json"
PJE_URL="https://pje.tjce.jus.br/"

# --- Parametros ---
MODE="download"
NUMERO=""
OUTPUT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --login)
            MODE="login"
            shift
            ;;
        --output)
            if [[ -z "${2:-}" ]]; then
                echo "ERRO: --output requer um caminho"
                exit 1
            fi
            OUTPUT_DIR="$2"
            mkdir -p "$OUTPUT_DIR"
            shift 2
            ;;
        -h|--help)
            cat <<HELP
Uso:
  $0 <numero-processo>                   # baixa autos
  $0 <numero-processo> --output <dir>    # baixa para pasta especifica
  $0 --login                             # so faz login (1a execucao ou cookies expirados)

Exemplos:
  $0 NNNNNNN-DD.AAAA.J.TT.OOOO
  $0 NNNNNNN-DD.AAAA.J.TT.OOOO --output ~/Downloads
  $0 --login

Variaveis de ambiente:
  CLAUDE_PROJECT_DIR   destino padrao quando rodado via Claude Code
                       (fallback: PWD atual)
HELP
            exit 0
            ;;
        *)
            if [[ -n "$NUMERO" ]]; then
                echo "ERRO: argumento inesperado '$1' (numero ja informado: $NUMERO)"
                exit 1
            fi
            NUMERO="$1"
            shift
            ;;
    esac
done

if [[ "$MODE" == "download" ]]; then
    if [[ -z "$NUMERO" ]]; then
        echo "Uso: $0 <numero-processo> [--output <dir>]"
        echo "     $0 --login"
        echo ""
        echo "Destino padrao: \$CLAUDE_PROJECT_DIR (raiz do projeto) ou CWD."
        exit 1
    fi

    if [[ ! "$NUMERO" =~ ^[0-9]{7}-[0-9]{2}\.[0-9]{4}\.[0-9]\.[0-9]{2}\.[0-9]{4}$ ]]; then
        echo "ERRO: Formato invalido: $NUMERO"
        echo "Esperado: NNNNNNN-DD.AAAA.J.TT.OOOO"
        exit 1
    fi

    OUTPUT_FILE="$OUTPUT_DIR/$NUMERO.pdf"

    echo "=== PJE Download Autos ==="
    echo "Processo: $NUMERO"
    echo ""
else
    echo "=== PJE Login (manual) ==="
    echo ""
fi

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

# Aguarda o usuario fazer login manual no Chrome ja aberto.
#
# Detecta login por PRESENCA de marcadores pos-login no state do browser-use
# ("Abrir menu" ou "Quadro de avisos") -- os mesmos que o resto do script ja
# usa para confirmar autenticacao. Nao confia em "tela de login sumiu", que
# pode dar falso positivo em loadings intermediarios.
#
# Funciona em dois modos sem precisar sinalizacao externa:
#
#   - TTY (usuario rodando direto no terminal):
#     `read -t 5` aguarda ENTER com timeout de 5s. A cada ciclo (venha ENTER
#     ou venha timeout) checa o state. ENTER funciona como "pular espera" --
#     o detector real continua sendo o state do browser.
#
#   - Sem TTY (Claude Code invocando via Bash tool):
#     `sleep 5` + check de state em loop. Sem read.
#
# Retorna 0 quando os marcadores pos-login aparecem; 1 em timeout (5 min).
aguardar_login() {
    local max_iter=60 interval=5 i=0
    local sucesso_re='Abrir menu\|Quadro de avisos'
    local login_re='id=username\|id=kc-login'
    local state

    if [ -t 0 ]; then
        echo "  Aguardando voce logar no Chrome aberto."
        echo "  ENTER adianta a deteccao; ou espere deteccao automatica."
        echo "  Timeout: 5 minutos."
    else
        echo "  Aguardando login via polling (cada ${interval}s, timeout 5 min)..."
    fi

    while [[ $i -lt $max_iter ]]; do
        state=$(bu state 2>/dev/null || echo "")

        # Sinal positivo: marcadores pos-login presentes
        if echo "$state" | grep -q "$sucesso_re"; then
            echo "    Login confirmado (pos-login visivel em $((i * interval))s)"
            return 0
        fi

        # Nao esta logado -- espera o proximo ciclo
        if [ -t 0 ]; then
            # TTY: read com timeout; ENTER adianta, timeout tambem ok
            if read -r -t "$interval" _ 2>/dev/null; then
                # ENTER recebido -- recheca imediatamente (sem consumir ciclo)
                state=$(bu state 2>/dev/null || echo "")
                if echo "$state" | grep -q "$sucesso_re"; then
                    echo "    Login confirmado apos ENTER"
                    return 0
                fi
                if echo "$state" | grep -q "$login_re"; then
                    echo "    Tela de login ainda visivel. Continue logando..."
                fi
            fi
        else
            sleep "$interval"
        fi

        i=$((i + 1))
    done

    echo "ERRO: Timeout aguardando login (5 min sem tela pos-login)"
    echo "       Verifique a janela do Chrome. Se logou mas nao detectou,"
    echo "       pode ser que o PJE mudou a UI -- abra um issue."
    return 1
}

# Fecha tudo ao sair
cleanup() { bu close 2>/dev/null || true; }
trap cleanup EXIT

# Verificação
command -v browser-use &>/dev/null || { echo "ERRO: browser-use não instalado"; exit 1; }

# ==========================================================================
# MODO LOGIN: abre Chrome, aguarda login, salva cookies, sai.
# ==========================================================================
if [[ "$MODE" == "login" ]]; then
    echo "Abrindo Chrome na tela de login do PJE..."
    bu close || true
    bu --profile "Default" --headed open "$PJE_URL"
    sleep 3

    # Tentar reaproveitar cookies antigos caso ainda sejam parcialmente validos
    if [[ -f "$COOKIES_FILE" ]]; then
        bu cookies import "$COOKIES_FILE" || true
        bu open "$PJE_URL"
        sleep 4
    fi

    # Se ja esta logado, salva e sai feliz
    if bu state | grep -q "Abrir menu\|Quadro de avisos"; then
        echo "    Ja estava logado. Atualizando cookies..."
        bu cookies export "$COOKIES_FILE" || true
        echo "    Cookies salvos em $COOKIES_FILE"
        echo ""
        echo "=== Login OK ==="
        echo "Agora rode: $0 <numero-processo>"
        exit 0
    fi

    cat <<'MSG'

  +------------------------------------------------------------+
  |  LOGIN NO PJE TJCE                                         |
  |                                                            |
  |  Abriu uma janela do Chrome com a tela de login.           |
  |  Entre com CPF/CNPJ + senha ou certificado digital.        |
  |                                                            |
  |  O script detecta automaticamente quando voce concluir.    |
  |  Se estiver em terminal interativo, ENTER tambem funciona. |
  +------------------------------------------------------------+

MSG

    aguardar_login || exit 1
    sleep 2

    if ! bu state | grep -q "Abrir menu\|Quadro de avisos"; then
        echo "ERRO: Tela pos-login nao apareceu. O login pode ter falhado."
        echo "Veja a janela do Chrome e tente de novo."
        exit 1
    fi

    bu cookies export "$COOKIES_FILE" || true
    echo "    Cookies salvos em $COOKIES_FILE"
    echo ""
    echo "=== Login concluido ==="
    echo "Agora rode: $0 <numero-processo>"
    exit 0
fi

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
        # Estava headless mas precisa login — reabrir com janela visivel
        echo "    Cookies expiraram ou primeira execucao. Reabrindo em --headed..."
        bu close || true
        bu --profile "Default" --headed open "$PJE_URL"
        sleep 3
    fi

    cat <<'MSG'

  +--------------------------------------------------------------+
  |  LOGIN NO PJE TJCE NECESSARIO                                |
  |                                                              |
  |  Uma janela do Chrome abriu com a tela de login.             |
  |  Entre com CPF/CNPJ + senha ou certificado digital.          |
  |                                                              |
  |  O script detecta sozinho quando voce concluir o login.      |
  |  Dica: para fazer apenas o login uma vez (sem baixar),       |
  |        rode antes: bash <este script> --login                |
  +--------------------------------------------------------------+

MSG

    aguardar_login || exit 1
    sleep 2
fi

bu state | grep -q "Abrir menu\|Quadro de avisos" || { echo "ERRO: Login falhou (pos-login nao carregou)"; exit 1; }
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
