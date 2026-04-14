# Tipos de Seção Disponíveis

Referência completa de todos os tipos de seção que podem ser usados no JSON de entrada do `gerar_relatorio.py` — Edição Executiva.

## Estrutura do JSON

```json
{
  "meta": { ... },
  "cover": true,
  "toc": true,
  "sections": [ ... ]
}
```

### Campos da meta (para a capa)

```json
{
  "meta": {
    "titulo": "Relatório de Análise Processual",
    "subtitulo": "Parecer técnico sobre cumprimento de sentença",
    "eyebrow": "RELATÓRIO PROCESSUAL · VOL. I",
    "classificacao": "DOCUMENTO RESERVADO",
    "numero_documento": "TJ-CE / 2026 / 024",
    "autor": "TecJustica · Assessoria Judicial",
    "orgao": "TecJustica · Assessoria Judicial com IA",
    "metadata": [
      ["Autos", "0001234-56.2024.8.06.0001"],
      ["Classe", "Cumprimento de sentença"],
      ["Órgão julgador", "4ª Vara Cível · Fortaleza/CE"],
      ["Relator(a)", "Juiz(a) de Direito"],
      ["Valor da causa", "R$ 125.430,00"],
      ["Data de emissão", "14 · Abril · 2026"]
    ]
  }
}
```

| Campo | Obrigatório | Descrição |
|---|---|---|
| `titulo` | Sim | Título display em 2 linhas (quebra automática inteligente) |
| `subtitulo` | Não | Subtítulo em itálico abaixo do título |
| `eyebrow` | Não | Label ALL CAPS antes do título, tipo "ANNUAL REPORT · 2026" |
| `classificacao` | Não | Tag no canto superior direito: RESERVADO, CONFIDENCIAL, INTERNO |
| `numero_documento` | Não | ID em mono: `TJ-CE / 2026 / 024` — aparece ao lado do eyebrow e no rodapé |
| `autor` | Não | Aparece em "PREPARADO POR" na capa |
| `metadata` | Não | Grid de até 6 células label/valor na parte central da capa |

## Ordem recomendada para relatórios processuais

1. `heading` (level 1, numeral "01") — Sumário executivo
2. `lead` — Parágrafo em itálico com contexto geral
3. `paragraph` — Contextualização completa
4. `kpi` — 3 números de destaque (prazo, valor, risco)
5. `heading` (level 1, numeral "02") — Dados estruturais dos autos
6. `data_cards` — Grid de 6 metadados
7. `heading` (level 2) — Partes e representação
8. `table` — Grid de partes/advogados
9. `heading` (level 1, numeral "03") — Linha do tempo processual
10. `timeline` — Movimentos processuais
11. `heading` (level 1, numeral "04") — Prazos e providências
12. `bullets` — Lista de pontos de atenção
13. `callout` (warn) — Alerta sobre prazo crítico
14. `heading` (level 1, numeral "05") — Fundamentação jurídica
15. `paragraph` — Análise do caso
16. `quote` — Precedente do STJ/STF
17. `heading` (level 1, numeral "06") — Recomendações
18. `bullets` — Roteiro de ações
19. `callout` (info) — Observação final
20. `signature` — Assinatura formal

## Referência dos tipos

### heading

Título com hierarquia visual. Level 1 suporta numeral lateral ("01", "02"...) e adiciona hairline ocre após o título. Level 2 é itálico navy em tamanho menor. Level 3 é ALL CAPS com tracking.

```json
{"type": "heading", "level": 1, "numeral": "01", "text": "Sumário executivo"}
{"type": "heading", "level": 2, "text": "Partes e representação processual"}
{"type": "heading", "level": 3, "text": "Subseção interna"}
```

Campos:
- `level` (int, 1–3) — hierarquia
- `text` (str) — texto do título
- `numeral` (str, opcional, só level 1) — numeral display antes do título

### lead

Parágrafo de destaque em itálico EB Garamond 14pt navy. Usado para introduzir seções importantes ou apresentar o contexto geral do relatório.

```json
{"type": "lead", "text": "Parecer técnico elaborado a partir dos autos..."}
```

### paragraph

Parágrafo normal justificado. EB Garamond 11pt, body color, line-spacing 1.35.

```json
{"type": "paragraph", "text": "Trata-se de ação de cobrança...", "justify": true}
```

Campos opcionais:
- `justify` (bool, default true) — se false, alinha à esquerda

### bullets

Lista com marcadores. Cada item é um parágrafo com bullet automático do Word.

```json
{"type": "bullets", "items": ["Primeiro item", "Segundo item", "Terceiro item"]}
```

### kpi

Três cards grandes em linha com numerais display. Ideal para destacar métricas críticas do processo.

```json
{
  "type": "kpi",
  "items": [
    ["Prazo restante", "15 dias", "úteis até penhora online"],
    ["Valor atualizado", "R$ 125.430", "sem multa e honorários"],
    ["Risco processual", "Baixo", "sentença transitada em julgado"]
  ]
}
```

Cada item é uma tupla `[label, valor, descritor]`.

### data_cards

Grid de 2 a 3 colunas com label/valor. Ideal para metadados de processo (CNJ, classe, valor da causa, fase, datas). Detecta automaticamente valores numéricos e aplica IBM Plex Mono.

```json
{
  "type": "data_cards",
  "columns": 3,
  "items": [
    ["Distribuído em", "15/03/2024"],
    ["Última movimentação", "02/04/2026"],
    ["Fase atual", "Cumprimento"],
    ["Atos praticados", "42"],
    ["Peças digitalizadas", "187"],
    ["Prazo CPC art. 523", "Em curso"]
  ]
}
```

Campos:
- `columns` (int, default 2) — número de colunas
- `items` (list de `[label, value]`) — pares

### table

Tabela estilizada sem bordas verticais. Apenas 3 hairlines horizontais: topo (2pt navy), abaixo do header (1pt navy), base (1pt navy). Linhas internas em hairline dourado 0.25pt.

```json
{
  "type": "table",
  "headers": ["Qualificação", "Denominação", "Representação jurídica"],
  "rows": [
    ["Exequente", "Construtora Exemplo Ltda.", "Dr. João da Silva · OAB/CE 00.000"],
    ["Executado", "Empresa Fictícia S.A.", "Dra. Maria Souza · OAB/CE 00.000"]
  ],
  "col_widths_cm": [4.5, 5.5, 6.5]
}
```

Campos:
- `headers` (list de str) — cabeçalho da tabela
- `rows` (list de list de str) — dados
- `col_widths_cm` (list de float, opcional) — larguras em cm; soma recomendada: 16.5cm

### timeline

Linha do tempo processual com três colunas: data (mono à direita) · bullet ocre ◆ · descrição. Hairline dourado entre eventos.

```json
{
  "type": "timeline",
  "events": [
    ["15/03/2024", "Distribuição da ação"],
    ["02/04/2024", "Despacho inicial"]
  ]
}
```

### quote

Citação de jurisprudência com barra lateral ocre e atribuição em sans caps abaixo.

```json
{
  "type": "quote",
  "text": "A prescrição intercorrente começa a correr a partir da ciência inequívoca.",
  "author": "STJ · REsp 1.340.553/RS · Rel. Min. Mauro Campbell"
}
```

### callout

Bloco destacado com barra lateral colorida e label em caps. Três variantes:

```json
{"type": "callout", "kind": "info", "text": "Observação neutra ou explicação."}
{"type": "callout", "kind": "warn", "text": "Atenção: prazo crítico em curso."}
{"type": "callout", "kind": "ok", "text": "Requisitos de admissibilidade satisfeitos."}
```

Campos:
- `kind` (str, default "info") — `info` (navy), `warn` (ocre) ou `ok` (verde)
- `text` (str) — mensagem

### code

Bloco de código monoespaçado IBM Plex Mono com barra lateral ocre e fundo creme suave.

```json
{"type": "code", "text": "python3 gerar_relatorio.py entrada.json saida.docx --pdf"}
```

### signature

Bloco de assinatura centralizado no final do documento.

```json
{
  "type": "signature",
  "name": "Magistrado(a) de Direito",
  "role": "4ª Vara Cível · Comarca de Fortaleza · CE",
  "local_data": "Fortaleza, 14 de abril de 2026"
}
```

## Restrições

- Nunca usar `\n` dentro de `paragraph.text` — crie múltiplos `paragraph` em sequência
- Nunca inserir `•`, `·` ou outros bullets manualmente no texto — use `bullets`
- Tabelas grandes (mais de 15 linhas) devem ser quebradas em múltiplas seções
- Quotes não devem ultrapassar 3 linhas — se for texto longo, use `paragraph`
- Metadata grid da capa aceita até 6 itens (2 linhas × 3 colunas); mais que isso vira difícil de ler
- `kpi` aceita no máximo 3 cards — com 4+ o display numeral fica pequeno
- Títulos de capa com mais de 10 palavras viram ilegíveis; prefira subtítulo para detalhes
