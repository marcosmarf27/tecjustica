---
name: tecjustica-docx
description: Gera relatórios processuais profissionais em DOCX e PDF com identidade visual TecJustica (capa, sumário, tabelas, timeline, cards de dados, quotes de jurisprudência, callouts). Use esta skill sempre que o usuário pedir para criar relatório processual, gerar documento Word, exportar análise em PDF, elaborar minuta formatada, montar peça em DOCX, produzir relatório em formato profissional, ou mencionar "relatório", "docx", "pdf", "word", "relatório processual", "tecjustica-docx", "gerar documento". Também dispara quando o usuário quer transformar o resultado de outra análise (como analise-processo-civil ou analise-processo-penal) em um documento formal para compartilhar com magistrados, partes ou juntar aos autos.
---

# tecjustica-docx

Gerador de relatórios processuais profissionais com identidade visual TecJustica. Produz DOCX com python-docx e converte para PDF via LibreOffice headless.

## O que esta skill faz

Transforma dados estruturados (JSON) em relatórios profissionais com:

- **Capa** com barra lateral indigo, título em Georgia, subtítulo, CNJ, autor e data
- **Sumário automático** (TOC) com atualização ao abrir no Word/LibreOffice
- **Cabeçalho e rodapé** com numeração "página X de Y"
- **Headings** com divisores laranja acento
- **Data cards** (grid de informações-chave em destaque)
- **Tabelas** com cabeçalho indigo e linhas alternadas
- **Timeline** processual (coluna de datas + descrição)
- **Quotes** de jurisprudência com borda lateral indigo
- **Callouts** informativos, de aviso e de confirmação
- **Blocos de código** formatados
- **Bloco de assinatura** com linha e cargo
- **Export automático para PDF** via LibreOffice headless

Paleta oficial extraída do substack TecJustica:

| Token | Hex | Uso |
|---|---|---|
| Indigo | `#4F46E5` | Primária · títulos, barras, cabeçalhos de tabela |
| Indigo Dark | `#3A30E2` | Título da capa, H1 |
| Orange | `#FF6719` | Acento · divisores, warn callouts |
| Dark | `#363737` | Corpo de texto |
| Medium | `#757575` | Metadados, legendas |
| Soft BG | `#F5F5FA` | Fundo de data cards |

Tipografia:
- **Georgia** (serifa) — headings e citações (autoridade jurídica)
- **Calibri** — corpo (legibilidade)
- **Consolas** — código e identificadores técnicos

## Dependências

- `python3` com `python-docx` instalado (`pip install --user python-docx`)
- `libreoffice` para conversão DOCX → PDF (`sudo apt install -y libreoffice-core libreoffice-writer --no-install-recommends`)

Ambas são instaladas automaticamente pelo `install.sh` do repositório.

## Como usar

### Opção 1 — Via CLI (recomendado)

Monte o conteúdo do relatório em um arquivo JSON e rode:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/gerar_relatorio.py entrada.json saida.docx --pdf
```

O flag `--pdf` converte automaticamente para PDF no mesmo diretório.

Para salvar o PDF em outro caminho:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/gerar_relatorio.py entrada.json saida.docx --pdf --pdf-path /tmp/saida.pdf
```

### Opção 2 — Só converter DOCX existente para PDF

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/docx_para_pdf.sh entrada.docx saida.pdf
```

### Opção 3 — Via biblioteca Python

Para montar relatórios programaticamente (sem passar por JSON):

```python
import sys
sys.path.insert(0, "${CLAUDE_SKILL_DIR}/scripts")
from docx_builder import Report

r = Report(
    titulo="Relatório Processual",
    subtitulo="Análise do processo 0001234-56.2024.8.06.0001",
    autor="TecJustica · Assessoria Judicial",
    data="14 de abril de 2026",
    cnj="0001234-56.2024.8.06.0001",
)
r.add_cover()
r.add_toc()
r.add_heading("Sumário executivo", level=1)
r.add_lead("Análise técnica do processo extraído do PJE TJCE...")
r.add_paragraph("Trata-se de ação de cobrança em fase de cumprimento...")
r.add_data_cards([
    ("CNJ", "0001234-56.2024.8.06.0001"),
    ("Classe", "Cumprimento de sentença"),
    ("Valor", "R$ 125.430,00"),
])
r.add_table(
    headers=["Data", "Movimento"],
    rows=[["15/03/2024", "Distribuição"], ["02/04/2024", "Citação"]],
)
r.add_timeline([
    ("15/03/2024", "Distribuição da ação"),
    ("30/05/2024", "Contestação"),
])
r.add_quote(
    "A prescrição intercorrente começa a correr a partir da ciência inequívoca...",
    "STJ · REsp 1.340.553/RS",
)
r.add_callout("Prazo de 15 dias úteis em curso.", kind="warn")
r.add_signature("Juiz(a) de Direito", "Vara Cível", "Fortaleza/CE, 14/04/2026")

docx = r.save("/tmp/relatorio.docx")
r.export_pdf(docx, "/tmp/relatorio.pdf")
```

## Formato do JSON de entrada

```json
{
  "meta": {
    "titulo": "Relatório Processual",
    "subtitulo": "Análise técnica assistida por IA",
    "autor": "TecJustica · Assessoria Judicial",
    "data": "14 de abril de 2026",
    "cnj": "0001234-56.2024.8.06.0001",
    "orgao": "TecJustica · Assessoria Judicial com IA"
  },
  "cover": true,
  "toc": true,
  "sections": [
    {"type": "heading", "level": 1, "text": "Sumário executivo"},
    {"type": "lead", "text": "Texto introdutório em destaque"},
    {"type": "paragraph", "text": "Parágrafo comum justificado"},
    {"type": "bullets", "items": ["Item 1", "Item 2"]},
    {"type": "data_cards", "columns": 2, "items": [["CNJ", "..."], ["Valor", "R$..."]]},
    {"type": "table", "headers": ["Col A", "Col B"], "rows": [["x", "y"]], "col_widths_cm": [6, 10]},
    {"type": "timeline", "events": [["15/03/2024", "Distribuição"]]},
    {"type": "quote", "text": "Citação...", "author": "STJ · REsp ..."},
    {"type": "callout", "kind": "warn", "text": "Atenção: prazo em curso"},
    {"type": "code", "text": "/plugin install tecjustica@tecjustica-plugins"},
    {"type": "signature", "name": "Juiz(a)", "role": "Vara Cível", "local_data": "Fortaleza/CE, 14/04/2026"}
  ]
}
```

Tipos de seção suportados: `heading`, `lead`, `paragraph`, `bullets`, `data_cards`, `table`, `timeline`, `quote`, `callout`, `code`, `signature`.

Tipos de callout: `info` (indigo), `warn` (laranja), `ok` (verde).

## Template de exemplo

Um template completo com todos os tipos de seção está em:

```
${CLAUDE_SKILL_DIR}/templates/relatorio-processual.json
```

Para gerar um relatório de demonstração:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/gerar_relatorio.py \
  ${CLAUDE_SKILL_DIR}/templates/relatorio-processual.json \
  /tmp/exemplo.docx --pdf
```

## Arquivos desta skill

```
tecjustica-docx/
├── SKILL.md                          ← este arquivo
├── scripts/
│   ├── docx_builder.py               ← biblioteca com Report e componentes
│   ├── gerar_relatorio.py            ← CLI JSON → DOCX/PDF
│   └── docx_para_pdf.sh              ← conversor DOCX → PDF standalone
├── templates/
│   └── relatorio-processual.json     ← exemplo completo
└── references/
    ├── paleta-tecjustica.md          ← cores e tipografia oficiais
    └── tipos-de-secao.md             ← referência dos tipos de seção
```

## Fluxo interno

1. `gerar_relatorio.py` lê o JSON e valida estrutura
2. Instancia `Report` de `docx_builder.py` com a metadata
3. Chama `add_cover()` e `add_toc()` (se habilitados)
4. Itera pelas `sections` e dispara o handler correspondente
5. `Report.save()` escreve o DOCX
6. Se `--pdf`, chama `libreoffice --headless --convert-to pdf` via subprocess
7. Retorna os caminhos gerados no stdout

## Integração com outras skills

Esta skill costuma ser acionada **após** outras análises:

- **analise-processo-civil / analise-processo-penal** → produz análise textual → `tecjustica-docx` formaliza em relatório
- **tecjustica-parse** → extrai texto de PDF → análise → relatório
- **pje-download** → baixa autos → extrai → analisa → relatório

Fluxo completo ideal:

```
pje-download → tecjustica-parse → analise-processo-civil/penal → tecjustica-docx
```

## Limites conhecidos

- O sumário (TOC) é gerado como campo Word — na primeira abertura do DOCX, o usuário precisa clicar "Atualizar campo" ou abrir no LibreOffice para carregar. O PDF exportado já vem com o TOC preenchido.
- LibreOffice usa Java no warmup (~3s na primeira conversão). Conversões subsequentes são ~1s.
- Fontes Georgia e Calibri precisam estar disponíveis no sistema. No Linux sem Microsoft fonts, o LibreOffice substitui automaticamente por equivalentes (Liberation Serif / Carlito). Para fidelidade total, instale `msttcorefonts` ou `fonts-crosextra-carlito`.
- O gerador aceita até ~50 páginas de conteúdo sem problemas de performance. Acima disso, considerar dividir em volumes.

## Solução de problemas

**"libreoffice: command not found"**
Instale: `sudo apt install -y libreoffice-core libreoffice-writer --no-install-recommends`

**"ModuleNotFoundError: No module named 'docx'"**
Instale: `pip install --user python-docx` (no Ubuntu 24+, pode ser necessário `--break-system-packages`)

**PDF fica com fontes diferentes do DOCX**
Instale as fontes Microsoft core: `sudo apt install -y ttf-mscorefonts-installer fonts-crosextra-carlito`

**TOC aparece com "clique para atualizar"**
Normal. Abra no LibreOffice Writer (ou Word) e o campo carrega. O PDF exportado já vem com o TOC renderizado.
