---
name: liteparse-windows
description: Extrai texto e metadados de autos judiciais do PJe (Processo Judicial Eletrônico) em Windows usando o CLI `lit` do LiteParse. Use SEMPRE que o usuário pedir para parsear, ler, extrair ou processar um PDF de autos/processo já baixado — seja por barra de comando (/liteparse-windows) ou em linguagem natural ("parseia esse processo", "extrai os autos", "lê o PDF do PJe", "processa esses autos do tribunal", "tira o texto desse processo"). Cobre qualquer tribunal do PJe (CE, SP, RS, RJ, BA, TRF, TRT etc.) identificando o padrão CNJ `NNNNNNN-DD.AAAA.J.TR.OOOO`. Não baixa autos — pressupõe que o PDF já está no disco local. Roda offline, sem cloud nem LLM externo.
---

# LiteParse Windows — Autos do PJe

Skill para extrair conteúdo de PDFs de autos do **PJe (Processo Judicial Eletrônico)** em Windows. O LiteParse lida bem com o padrão típico do PJe: capa padronizada + documentos anexados, frequentemente escaneados (OCR), podendo chegar a centenas de páginas.

## Quando disparar

Acione esta skill quando o usuário:

- Invocar a barra de comando `/liteparse-windows`
- Fornecer um caminho de PDF e pedir para parsear/extrair/ler (ex.: "parseia `C:\...\0000001-23.2025.8.06.0203.pdf`")
- Falar em autos, processo, peça, tribunal, réplica, contestação, decisão — no contexto de extrair texto de um PDF local
- Mencionar número no padrão CNJ (`NNNNNNN-DD.AAAA.J.TR.OOOO`) junto com um pedido de extração

Se o usuário pedir para **baixar** os autos, esta skill não cobre isso — redirecione para uma das skills de download (`baixar-autos-pje` via Claude in Chrome, ou `pje-download` via browser-use).

## Pré-requisitos (assume instalado)

Antes de qualquer parse, valide rapidamente:

```bash
lit --version
```

Se o comando falhar, pare e informe o usuário que precisa instalar `@llamaindex/liteparse` globalmente (`npm i -g @llamaindex/liteparse`). Não entre em tutoriais longos de instalação — essa skill pressupõe ambiente pronto.

Dependências opcionais (já esperadas no Windows do usuário):
- **LibreOffice** — necessário se o anexo vier em DOC/DOCX/XLSX/PPTX dentro do processo
- **ImageMagick** — necessário para imagens soltas (JPG/PNG/TIFF)

## Fluxo padrão de um PDF do PJe

### 1. Verificar o arquivo

```bash
ls -la "<caminho-do-pdf>"
```

Anote o tamanho — PDFs do PJe acima de ~5 MB quase sempre têm páginas escaneadas (OCR vai rodar). Abaixo disso costumam ser texto nativo.

### 2. Rodar o parse

Comando padrão, saída em texto, salvando ao lado do PDF:

```bash
lit parse "<caminho-do-pdf>" --format text -o "<caminho-do-pdf-sem-.pdf>.txt"
```

Por padrão o LiteParse:
- Extrai texto nativo quando disponível
- Faz OCR automático (Tesseract.js embutido) nas páginas escaneadas
- Usa DPI 150 (suficiente para autos típicos)

Para processos grandes (>50 páginas com OCR), rode em **background** para não travar a conversa:

```bash
lit parse "<caminho>" --format text -o "<saida.txt>"
# com run_in_background=true no Bash tool
```

Enquanto roda, avise o usuário: "Processando em background (pode levar vários minutos se houver OCR em muitas páginas)."

### 3. Reportar metadados do processo

Assim que o parse terminar, **sempre** leia as primeiras ~120 linhas do `.txt` e extraia os campos da capa padronizada do PJe. Monte uma tabela e apresente ao usuário:

| Campo | Onde encontrar na capa |
|---|---|
| Número | linha "Número: NNNNNNN-DD.AAAA.J.TR.OOOO" |
| Classe | linha "Classe: ..." |
| Órgão julgador | linha "Órgão julgador: ..." |
| Distribuição | linha "Última distribuição:" |
| Valor da causa | linha "Valor da causa: R$ ..." |
| Assuntos | linha "Assuntos: ..." |
| Sigilo | linha "Nível de Sigilo:" |
| Justiça gratuita | "Justiça gratuita? SIM/NÃO" |
| Liminar/tutela | "Pedido de liminar ou antecipação de tutela? SIM/NÃO" |

Depois identifique:

- **Partes e advogados** — seção "Partes ... Advogados"
- **Últimas movimentações** — topo da tabela "Documentos" (Id., Data, Documento, Tipo)

Dica: o número CNJ revela o tribunal pelo código **TR** (posições 15-16):
| TR | Tribunal |
|---|---|
| 06 | TJCE |
| 26 | TJSP |
| 19 | TJRS |
| 02 | TJRJ |
| 05 | TJBA |
| 04 | TRFs (01-06 conforme região) |

Mencione o tribunal detectado no relatório.

### 4. Oferecer próximos passos

Depois do relatório, pergunte ao usuário se quer algum destes:

1. **Extrair peças específicas** em arquivos separados (petição inicial, contestação, réplica, decisão, sentença) — use `--target-pages` quando souber o range
2. **Reprocessar em JSON** com bounding boxes: `lit parse ... --format json` — útil quando a saída vai alimentar um agente/LLM ou extração estruturada
3. **Screenshots de páginas** para inspeção visual: `lit screenshot <pdf> --pages "1,3,5" -o ./screenshots`
4. **Buscar termos** no `.txt` gerado (valores, datas, nomes) — use Grep direto
5. **Abrir no VS Code**: `code "<caminho.txt>"`

## Opções avançadas (quando o padrão não for suficiente)

| Situação | Flag |
|---|---|
| PDF só com texto nativo (sem scans) — parse mais rápido | `--no-ocr` |
| Scan de baixa qualidade (letras borradas) | `--dpi 300` |
| Só algumas páginas | `--target-pages "1-10,45,80-90"` |
| Texto em rodapé/carimbo muito pequeno sumindo | `--preserve-small-text` |
| Documentos com texto em ângulo (assinaturas digitalizadas) | **remover** `--skip-diagonal-text` se estiver setado |
| OCR errando em português | `--ocr-language por` (exige modelo Tesseract `por`) |
| Lote de vários PDFs de um mesmo processo | `lit batch-parse <dir> <out-dir> --extension .pdf --recursive` |

## Particularidades do Windows

### Caminhos

- No **Git Bash** (shell padrão usado pela skill), use aspas duplas e barras normais:
  ```bash
  lit parse "C:/Users/marco/processos/0000001-23.2025.8.06.0203.pdf" ...
  ```
- Barras invertidas `\` funcionam dentro de aspas duplas, mas misture com cuidado
- Espaços no caminho **exigem** aspas

### PowerShell (alternativa)

Se o usuário pedir PowerShell explicitamente:

```powershell
lit parse "C:\Users\marco\processos\0000001-23.2025.8.06.0203.pdf" --format text -o "C:\Users\marco\processos\0000001-23.2025.8.06.0203.txt"
```

A sintaxe das flags do `lit` é idêntica; só muda o shell ao redor.

### Abrir resultado

```bash
code "<caminho.txt>"      # VS Code
notepad "<caminho.txt>"    # Bloco de Notas (fallback)
```

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `lit: command not found` | CLI não instalado ou fora do PATH | `npm i -g @llamaindex/liteparse`, reabrir shell |
| OCR travando em uma página específica | Página com imagem gigante ou corrompida | Pular com `--target-pages` excluindo a página |
| Texto em português saindo embaralhado | Tesseract sem modelo `por` | Instalar modelo ou usar `--ocr-server-url` externo |
| Anexo DOCX não sendo processado | LibreOffice ausente ou fora do PATH | Verificar `soffice --version` |
| Parse muito lento (>30min em 200 páginas) | DPI alto + OCR pesado | Reduzir para `--dpi 150` ou desativar OCR com `--no-ocr` se o PDF for nativo |
| Saída em branco | PDF criptografado/protegido | Avisar o usuário — LiteParse não quebra senha |

## Formato de entrada esperado

PDFs gerados pelo PJe tipicamente contêm:

1. **Capa** (1 página) — texto nativo, metadados padronizados
2. **Sumário de documentos** (1-3 páginas) — texto nativo, tabela com Id./Data/Tipo
3. **Peças anexadas** — mistura de texto nativo (petições digitadas) e scans (procurações, RG, comprovantes)

O LiteParse trata essa mistura automaticamente. Páginas escaneadas aparecem nos logs como `OCR on page N` → `Found X text items`. Poucos `text items` (< 20) costumam indicar páginas de carimbo/assinatura com pouco conteúdo útil — normal.

## Princípio de operação

Esta skill é uma casca fina sobre o CLI `lit`. A inteligência vem de:
1. Escolher flags adequadas ao perfil de PDF do PJe
2. Extrair e **apresentar os metadados** da capa padronizada de forma estruturada — isso transforma um texto bruto de 10k linhas em um resumo acionável
3. Conhecer as armadilhas de Windows (paths, shell) para não travar na parte trivial
4. Oferecer próximos passos que o usuário realmente precisa (busca, extração de peças, JSON pra agentes)

Se em algum momento o usuário quiser um comportamento que diverge — ex.: parsear um PDF que não é do PJe, ou um XLSX qualquer — use a skill genérica `liteparse` no lugar desta.
