---
name: tecjustica-docx
description: Gera relatórios processuais executivos em DOCX e PDF no padrão de bancas de investimento e consultorias top-tier (paleta navy+ocre, tipografia EB Garamond + IBM Plex Sans/Mono, capa densa institucional, hairlines dourados). Use esta skill sempre que o usuário pedir para criar relatório processual profissional, gerar relatório executivo, elaborar parecer técnico formatado, montar peça para apresentar a magistrado, banco ou conselho, produzir documento em padrão institucional, ou mencionar "relatório", "docx", "pdf", "word", "relatório processual", "tecjustica-docx", "gerar documento", "parecer", "relatório executivo", "minuta formatada". Também dispara quando o usuário quer transformar o resultado de outra análise (como analise-processo-civil ou analise-processo-penal) em um documento formal para compartilhar com magistrados, partes, bancos ou instituições e juntar aos autos.
---

# tecjustica-docx

Gerador de relatórios processuais executivos com padrão visual de bancas de investimento e consultorias top-tier (Goldman, JP Morgan, McKinsey, BCG), adaptado ao contexto judicial brasileiro. Produz DOCX com python-docx e converte para PDF via LibreOffice headless.

## O que esta skill faz

Transforma dados estruturados (JSON) em relatórios executivos com identidade visual "Sobriedade Institucional":

- **Capa densa e preenchida** no padrão banca de investimento
  - Barra superior bipartida: navy profundo + ocre dourado
  - Eyebrow uppercase com tracking amplo + número de documento em mono
  - Hairline dourado separando título
  - Título display EB Garamond 42pt em 1–2 linhas
  - Subtítulo em itálico
  - Metadata grid de até 6 células com labels em caps e valores em serif/mono
  - Bloco "PREPARADO POR" + data em formato romano (MMXXVI)
- **Sumário automático** (TOC) preenchido ao abrir no LibreOffice/Word
- **Cabeçalho e rodapé** institucionais com classificação, número do documento e paginação "01 / 08" em mono
- **Headings** com numeral lateral ("01", "02"...) em mono ocre + divisor dourado
- **KPI cards** com numerais display grandes
- **Data cards** em grid com labels caps e valores mono/serif
- **Tabelas** sem bordas verticais, apenas hairlines horizontais (padrão editorial)
- **Timeline processual** em três colunas: data mono / bullet ocre / descrição
- **Quotes** de jurisprudência com barra lateral ocre e atribuição em caps
- **Callouts** (info navy / warn ocre / ok verde) com barra lateral colorida
- **Bloco de código** com fundo creme e barra ocre
- **Bloco de assinatura** centralizado com nome em serif e cargo em caps
- **Export automático para PDF** via LibreOffice headless

## Dependências

- `python3` com `python-docx` instalado
- `libreoffice` headless para conversão DOCX → PDF
- **Fontes editoriais** (essenciais para o design sair correto):
  - `fonts-ebgaramond` · EB Garamond (display + body)
  - `fonts-ibm-plex` · IBM Plex Sans + IBM Plex Mono (labels + numerais)

Instalação completa no Ubuntu/WSL:

```bash
pip install --user python-docx
sudo apt install -y libreoffice-core libreoffice-writer --no-install-recommends
sudo apt install -y fonts-ebgaramond fonts-ebgaramond-extra fonts-ibm-plex fonts-inconsolata fonts-crosextra-caladea fonts-crosextra-carlito
```

Todas essas dependências são instaladas automaticamente pelo `install.sh` do repositório.

**Sem as fontes editoriais**, o LibreOffice substitui por fallbacks genéricos (Liberation Serif / DejaVu Sans) e o relatório perde sua identidade visual. É essencial instalar as fontes antes de usar a skill.

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
    titulo="Relatório de Análise Processual",
    subtitulo="Parecer técnico sobre cumprimento de sentença",
    eyebrow="RELATÓRIO PROCESSUAL · VOL. I",
    classificacao="DOCUMENTO RESERVADO",
    numero_documento="TJ-CE / 2026 / 024",
    autor="TecJustica · Assessoria Judicial",
    metadata=[
        ("Autos", "0001234-56.2024.8.06.0001"),
        ("Classe", "Cumprimento de sentença"),
        ("Órgão julgador", "4ª Vara Cível · Fortaleza/CE"),
        ("Relator(a)", "Juiz(a) de Direito"),
        ("Valor da causa", "R$ 125.430,00"),
        ("Data de emissão", "14 · Abril · 2026"),
    ],
)
r.add_cover()
r.add_toc()
r.add_heading("Sumário executivo", level=1, numeral="01")
r.add_lead("Parecer técnico elaborado a partir dos autos extraídos via OCR...")
r.add_paragraph("Trata-se de ação de cobrança em fase de cumprimento...")
r.add_kpi([
    ("Prazo restante", "15 dias", "úteis até penhora online"),
    ("Valor atualizado", "R$ 125.430", "sem multa"),
    ("Risco processual", "Baixo", "sentença transitada em julgado"),
])
r.add_heading("Linha do tempo", level=1, numeral="02")
r.add_timeline([
    ("15/03/2024", "Distribuição da ação"),
    ("30/05/2024", "Contestação"),
])
r.add_quote(
    "A prescrição intercorrente começa a correr a partir da ciência inequívoca...",
    "STJ · REsp 1.340.553/RS · Rel. Min. Mauro Campbell",
)
r.add_callout("Prazo de 15 dias úteis em curso.", kind="warn")
r.add_signature("Magistrado(a) de Direito", "4ª Vara Cível · Fortaleza", "Fortaleza, 14/04/2026")

docx = r.save("/tmp/relatorio.docx")
r.export_pdf(docx, "/tmp/relatorio.pdf")
```

## Formato do JSON de entrada

```json
{
  "meta": {
    "titulo": "Relatório de Análise Processual",
    "subtitulo": "Parecer técnico sobre cumprimento de sentença",
    "eyebrow": "RELATÓRIO PROCESSUAL · VOL. I",
    "classificacao": "DOCUMENTO RESERVADO",
    "numero_documento": "TJ-CE / 2026 / 024",
    "autor": "TecJustica · Assessoria Judicial",
    "metadata": [
      ["Autos", "0001234-56.2024.8.06.0001"],
      ["Classe", "Cumprimento de sentença"],
      ["Órgão julgador", "4ª Vara Cível · Fortaleza/CE"],
      ["Relator(a)", "Juiz(a) de Direito"],
      ["Valor da causa", "R$ 125.430,00"],
      ["Data de emissão", "14 · Abril · 2026"]
    ]
  },
  "cover": true,
  "toc": true,
  "sections": [
    {"type": "heading", "level": 1, "numeral": "01", "text": "Sumário executivo"},
    {"type": "lead", "text": "Parecer técnico elaborado..."},
    {"type": "paragraph", "text": "Trata-se de ação..."},
    {"type": "kpi", "items": [["Prazo", "15 dias", "úteis"], ["Valor", "R$ 125.430", "sem multa"], ["Risco", "Baixo", "transitado"]]},
    {"type": "data_cards", "columns": 3, "items": [["Distribuído", "15/03/2024"], ["Fase", "Cumprimento"]]},
    {"type": "table", "headers": ["Col A", "Col B"], "rows": [["x", "y"]], "col_widths_cm": [6, 10]},
    {"type": "timeline", "events": [["15/03/2024", "Distribuição"]]},
    {"type": "quote", "text": "...", "author": "STJ · REsp ..."},
    {"type": "callout", "kind": "warn", "text": "Atenção: prazo em curso"},
    {"type": "bullets", "items": ["Item 1", "Item 2"]},
    {"type": "code", "text": "/plugin install tecjustica@tecjustica-plugins"},
    {"type": "signature", "name": "Juiz(a)", "role": "Vara Cível", "local_data": "Fortaleza, 14/04/2026"}
  ]
}
```

Tipos de seção suportados: `heading`, `lead`, `paragraph`, `bullets`, `kpi`, `data_cards`, `table`, `timeline`, `quote`, `callout`, `code`, `signature`.

Tipos de callout: `info` (navy), `warn` (ocre), `ok` (verde).

Ver `references/tipos-de-secao.md` para a referência completa de cada tipo.

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
│   ├── docx_builder.py               ← biblioteca Report + componentes institucionais
│   ├── gerar_relatorio.py            ← CLI JSON → DOCX/PDF
│   └── docx_para_pdf.sh              ← conversor DOCX → PDF standalone
├── templates/
│   └── relatorio-processual.json     ← exemplo completo
└── references/
    ├── paleta-tecjustica.md          ← paleta + tipografia + justificativas de design
    └── tipos-de-secao.md             ← referência de cada tipo de seção do JSON
```

## Integração com outras skills

Esta skill costuma ser acionada **após** outras análises:

- **analise-processo-civil / analise-processo-penal** → produz análise textual → `tecjustica-docx` formaliza em relatório executivo
- **tecjustica-parse** → extrai texto de PDF → análise → relatório
- **pje-download** → baixa autos → extrai → analisa → relatório

Fluxo completo ideal:

```
pje-download → tecjustica-parse → analise-processo-civil/penal → tecjustica-docx
```

## Limites conhecidos

- **Fontes**: se EB Garamond e IBM Plex não estiverem instalados, o LibreOffice substitui por fallbacks e o design perde sua identidade. Execute o `install.sh` do repositório para garantir que estão presentes.
- **TOC**: o sumário é gerado como campo Word — na primeira abertura do DOCX, o usuário precisa clicar "Atualizar campo" ou abrir no LibreOffice para carregar. O PDF exportado já vem com o TOC preenchido.
- **LibreOffice warmup**: a primeira conversão demora ~3s (inicialização do runtime headless). Conversões subsequentes são ~1s.
- **Tamanho**: o gerador aceita até ~50 páginas de conteúdo sem problemas de performance.
- **Título da capa**: máximo 2 linhas, cerca de 10 palavras. Títulos mais longos devem ser movidos para o subtítulo.
- **Metadata grid da capa**: máximo 6 itens (2 linhas × 3 colunas).

## Solução de problemas

**"libreoffice: command not found"**
Instale: `sudo apt install -y libreoffice-core libreoffice-writer --no-install-recommends`

**"ModuleNotFoundError: No module named 'docx'"**
Instale: `pip install --user python-docx` (no Ubuntu 24+, adicione `--break-system-packages`)

**PDF fica com tipografia errada (serifa feia, letras diferentes do esperado)**
As fontes editoriais não estão instaladas. Execute:
```bash
sudo apt install -y fonts-ebgaramond fonts-ebgaramond-extra fonts-ibm-plex fonts-inconsolata fonts-crosextra-caladea fonts-crosextra-carlito
```
E regere o relatório.

**TOC aparece com "clique para atualizar"**
Normal. Abra no LibreOffice Writer (ou Word) e o campo carrega. O PDF exportado já vem com o TOC renderizado.

**Capa parece vazia ou mal alinhada**
Verifique se a `metadata` no meta está preenchida com 3–6 itens. A capa é projetada para ser densa; sem metadata ela fica excessivamente minimalista.
