# PJE — Guia de Navegação Manual com browser-use CLI

Guia completo de fallback para quando o script `baixar_autos_pje.sh` falhar. Documenta todos os elementos DOM, IDs estáveis, e armadilhas do PJE (TJCE 1º Grau).

## Índice
1. [Setup e autenticação](#1-setup)
2. [Dashboard e painel interno](#2-dashboard)
3. [Filtros de tarefas](#3-filtros)
4. [Pesquisa por número](#4-pesquisa)
5. [Abrir tarefa e processo](#5-tarefa)
6. [Abrir autos](#6-autos)
7. [Download do PDF](#7-download)
8. [Armadilhas](#8-armadilhas)
9. [Fluxo alternativo: Consulta Processual](#9-alternativo)

---

## 1. Setup

```bash
export PATH="$HOME/.browser-use-env/bin:$PATH"
browser-use close 2>/dev/null || true
browser-use --profile "Default" --headed open https://pje.tjce.jus.br/
sleep 3

# Restaurar cookies
browser-use cookies import ~/.browser-use/pje_cookies.json 2>/dev/null
browser-use open https://pje.tjce.jus.br/
sleep 4
```

### Detectar login necessário
Se `browser-use state` contém `id=username` ou `id=kc-login` → tela de login.
Pedir ao usuário para logar manualmente no Chrome. Depois:
```bash
browser-use cookies export ~/.browser-use/pje_cookies.json
```

### Confirmar logado
```bash
browser-use state | grep "Abrir menu\|Quadro de avisos"
```

---

## 2. Dashboard

Após login: "Quadro de avisos" com nome do usuário.

O painel interno vive em `iframe#ngFrame`. Verificar se carregou:
```bash
browser-use state | grep "liTarefas"
```

Se NÃO carregou em 10s, clicar em "Painel do usuário":
```bash
IDX=$(browser-use state | grep "Painel do usu" | grep -oE '\[[0-9]+\]' | tr -d '[]' | head -1)
browser-use click $IDX
sleep 5
```

---

## 3. Filtros

Dois "Filtros" existem no painel. O de **Tarefas** é o segundo `div aria-expanded`:
```bash
IDX=$(browser-use state | grep "aria-expanded=false" | tail -1 | grep -oE '\[[0-9]+\]' | tr -d '[]' | head -1)
browser-use click $IDX
sleep 2
```

Campos que aparecem:

| Campo | ID | Uso |
|-------|-----|-----|
| Número processo | `itNrProcesso` | Aceita número completo |
| Competência | `itCompetencia` | Não usado |
| Etiqueta | `itEtiqueta` | Não usado |

Botões: `<button>Pesquisar</button>`, `<button>Limpar</button>`

Verificar: `browser-use state | grep "itNrProcesso"`

---

## 4. Pesquisa

Preencher com select-all para não duplicar:
```bash
IDX=$(browser-use state | grep "itNrProcesso" | grep -oE '\[[0-9]+\]' | tr -d '[]* ' | head -1)
browser-use click $IDX
browser-use keys "Control+a"
browser-use type "NUMERO-COMPLETO"
sleep 1

IDX=$(browser-use state | grep -B1 "Pesquisar" | grep "<button" | head -1 | grep -oE '\[[0-9]+\]' | tr -d '[]')
browser-use click $IDX
sleep 5
```

Resultado: tarefa com título tipo `[Sec] - Prazo - AGUARDAR...` ou `[StArq] - Arquivo Definitivo...`
```bash
browser-use state | grep '<a title=\['
```

---

## 5. Tarefa

Clicar na tarefa:
```bash
IDX=$(browser-use state | grep '<a title=\[' | head -1 | grep -oE '\[[0-9]+\]' | tr -d '[]')
browser-use click $IDX
sleep 3
```

Verificar processo listado, clicar no span:
```bash
IDX=$(browser-use state | grep -B3 "NUMERO" | grep "<span" | head -1 | grep -oE '\[[0-9]+\]' | tr -d '[]')
browser-use click $IDX
sleep 3
```

---

## 6. Autos

Clicar "Abrir autos" (ícone de livro):
```bash
IDX=$(browser-use state | grep "title=Abrir autos" | grep -oE '\[[0-9]+\]' | tr -d '[]')
browser-use click $IDX
sleep 5

browser-use switch 1
sleep 2
browser-use state | grep "Download autos do processo"
```

---

## 7. Download

```bash
# Abrir painel de download
IDX=$(browser-use state | grep "Download autos do processo" | grep -oE '\[[0-9]+\]' | tr -d '[]')
browser-use click $IDX
sleep 2

# Clicar Download
IDX=$(browser-use state | grep 'value=Download type=button' | grep -oE '\[[0-9]+\]' | tr -d '[]')
browser-use click $IDX
```

Polling para PDF (aba 2):
```bash
# Repetir até encontrar .pdf na URL:
browser-use switch 2
browser-use eval "window.location.href"
# Se contém .pdf → baixar com curl
curl -sL -o "NUMERO.pdf" "URL_COMPLETA"
```

URL do MinIO expira em **120 segundos**. Baixar imediatamente.

---

## 8. Armadilhas

| Problema | Causa | Solução |
|----------|-------|---------|
| `eval` não acha elementos | Estão em iframe `#ngFrame` | Usar `state` + `click <index>` |
| Índices diferentes | Mudam a cada load | Buscar por padrão com `grep` |
| Campo duplica valor | Pré-preenchido (ramoJustica=8) | `click` → `Ctrl+A` → `type` |
| PDF não abre | Processo grande (300+ pgs) | Aumentar timeout para 3 min |
| URL do PDF não funciona | Expirou (120s) | Baixar imediato com curl |
| Login perdido | Cookies expiraram | Pedir login manual ao usuário |
| Painel não carrega | iframe lento | Clicar "Painel do usuário" |

---

## 9. Alternativo: Consulta Processual

Para processos que **não estão nas suas tarefas**, usar Consulta Processual:

```bash
IDX=$(browser-use state | grep "title=Consulta processual" | grep -oE '\[[0-9]+\]' | tr -d '[]')
browser-use click $IDX
sleep 3
```

Formulário divide número em 6 campos:

| Campo | ID | Max |
|-------|-----|-----|
| Sequencial | `fPP:numeroProcesso:numeroSequencial` | 7 |
| Dígito | `fPP:numeroProcesso:numeroDigitoVerificador` | 2 |
| Ano | `fPP:numeroProcesso:Ano` | 4 |
| Ramo | `fPP:numeroProcesso:ramoJustica` | 1 (pré: "8") |
| Tribunal | `fPP:numeroProcesso:respectivoTribunal` | 2 (pré: "06") |
| Órgão | `fPP:numeroProcesso:NumeroOrgaoJustica` | 4 |

Botão: `input#fPP:searchProcessos`

Resultado em tabela `processosTable`. Link `a[title="NUMERO"]` abre autos direto em nova aba. Download segue o mesmo fluxo da seção 7.
