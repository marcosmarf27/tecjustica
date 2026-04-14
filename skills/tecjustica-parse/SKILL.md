---
name: tecjustica-parse
description: Extrai texto de PDFs via API TecJustica Parse (OCR com PaddleOCR GPU). Use esta skill sempre que o usuario pedir para extrair texto de PDF, fazer OCR, processar documento escaneado, converter PDF para texto/markdown, ou analisar documento juridico (peticoes, certidoes, matriculas de imoveis, processos judiciais). Tambem use quando o usuario mencionar "parse", "OCR", "extrair PDF", "TecJustica", ou tiver um arquivo .pdf que precisa ser lido/convertido.
---

# TecJustica Parse — Extracao de texto de PDFs

Servico de OCR com PaddleOCR GPU para documentos juridicos brasileiros. Processa PDFs escaneados e digitais, retornando texto em markdown estruturado.

## Dependencias

O sistema precisa ter instalado: `curl`, `python3`, `bash`. Todos ja vem por padrao no Linux e macOS.

## Configuracao

O usuario precisa de uma API key da TecJustica Parse (prefixo `tjp_`). Se nao tiver, orientar a se cadastrar em https://tecjustica-dashboard-production.up.railway.app

> **Atencao:** esta chave e DIFERENTE da chave do MCP TecJustica (prefixo `mcp_`). Cada servico tem sua propria.

Ha tres formas de configurar a API key:

1. **Arquivo config.env** (recomendado): copiar `config.env.example` para `config.env` dentro da pasta da skill e preencher a chave. O script carrega automaticamente. **Nao commitar** — ja esta no `.gitignore`.
2. **Variavel de ambiente**: `export TECJUSTICA_PARSE_API_KEY="tjp_..."`
3. **Inline**: passar `--key tjp_...` no comando

## Como usar

O Claude Code expande `${CLAUDE_SKILL_DIR}` automaticamente para o diretorio absoluto desta skill. Invoque o script assim:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/parse.sh <caminho-do-pdf> [opcoes]
```

O caminho do PDF pode ser absoluto ou relativo ao diretorio de trabalho — o script resolve para absoluto internamente.

### Opcoes

| Opcao | Default | Descricao |
|-------|---------|-----------|
| `--enhance` | off | Ativa pos-processamento com IA Vision. Corrige erros de OCR, remove ruido de layout (sidebars, rodapes). Recomendado para certidoes e documentos com overlays |
| `--key <api_key>` | `$TECJUSTICA_PARSE_API_KEY` | API key (se nao estiver na env) |
| `--output <arquivo>` | stdout | Salvar resultado em arquivo |
| `--dpi <numero>` | 150 | Resolucao de rendering (72=rapido, 150=padrao, 300=maximo) |
| `--pages <range>` | todas | Paginas especificas. Ex: "1-5,10,15-20" |

### Exemplos

```bash
# Basico — extrair texto de um PDF
bash ${CLAUDE_SKILL_DIR}/scripts/parse.sh /caminho/para/documento.pdf

# Com enhance (recomendado para certidoes e matriculas)
bash ${CLAUDE_SKILL_DIR}/scripts/parse.sh matricula.pdf --enhance --output resultado.md

# Paginas especificas
bash ${CLAUDE_SKILL_DIR}/scripts/parse.sh processo.pdf --pages 1-10 --output primeiras_paginas.md

# Com API key inline
bash ${CLAUDE_SKILL_DIR}/scripts/parse.sh doc.pdf --key tjp_sua_chave_aqui
```

## Fluxo interno

1. Envia o PDF para `POST /parse/async` (retorna job_id)
2. Faz polling em `GET /parse/status/{job_id}` ate `status=done`
3. Extrai o markdown do resultado
4. Exibe ou salva o resultado

## Parametros da API

| Parametro | Default | Descricao |
|-----------|---------|-----------|
| `ocr_engine` | `paddle` | PaddleOCR GPU (melhor qualidade PT-BR) |
| `dpi` | `150` | Resolucao. 150=padrao, 72=rapido, 300=maximo |
| `ocr_threshold` | `1500` | Minimo de chars nativos para pular OCR |
| `enhance` | `false` | IA Vision para corrigir erros e remover ruido |
| `language` | `pt` | Idioma OCR |

## Performance tipica

| Documento | Paginas | Tempo (sem enhance) | Tempo (com enhance) |
|-----------|---------|---------------------|---------------------|
| Peticao (5 pgs) | 5 | ~5s | ~50s |
| Certidao imovel (11 pgs) | 11 | ~16s | ~100s |
| Processo judicial (159 pgs) | 159 | ~74s | N/A (usar sem enhance) |

## Quando usar enhance

- **SEM enhance**: Indexacao, busca, volume alto, documentos digitais puros
- **COM enhance**: Auditoria, extracao estruturada, certidoes com overlays/sidebars, documentos onde datas, CPFs e nomes precisam estar 100% corretos

## Limites

- Upload maximo: 1GB
- Formatos: PDF
- Rate limit: 60 requests/minuto
