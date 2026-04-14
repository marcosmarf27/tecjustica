# Tipos de Seção Disponíveis

Referência completa de todos os tipos de seção que podem ser usados no JSON de entrada do `gerar_relatorio.py`.

## Ordem recomendada para relatórios processuais

1. `heading` (level 1) — Sumário executivo
2. `lead` — Resumo em destaque
3. `paragraph` — Contextualização
4. `data_cards` — Grid com metadados-chave (CNJ, classe, valor, fase)
5. `heading` (level 1) — Partes e representação
6. `table` — Grid de partes/advogados
7. `heading` (level 1) — Linha do tempo processual
8. `timeline` — Movimentos processuais cronológicos
9. `heading` (level 1) — Prazos e providências
10. `bullets` — Lista de pontos de atenção
11. `callout` (warn) — Alerta sobre prazo crítico
12. `heading` (level 1) — Fundamentação jurídica
13. `paragraph` — Análise do caso
14. `quote` — Precedente do STJ/STF
15. `heading` (level 1) — Próximos passos sugeridos
16. `bullets` — Roteiro de ações
17. `callout` (info) — Observação final
18. `signature` — Assinatura formal

## Referência dos tipos

### heading

Título com hierarquia visual. Level 1 tem divisor laranja abaixo.

```json
{"type": "heading", "level": 1, "text": "Sumário executivo"}
```

Campos:
- `level` (int, 1–3) — hierarquia
- `text` (str) — texto do título

### lead

Parágrafo de destaque em itálico, para introduzir seções. Georgia 13pt cinza.

```json
{"type": "lead", "text": "Análise técnica do processo extraído via OCR."}
```

### paragraph

Parágrafo normal justificado. Calibri 11pt Dark.

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

### data_cards

Grid de 1 a N colunas com label/valor. Ideal para metadados de processo (CNJ, classe, valor da causa, fase, datas).

```json
{
  "type": "data_cards",
  "columns": 2,
  "items": [
    ["CNJ", "0001234-56.2024.8.06.0001"],
    ["Classe", "Cumprimento de sentença"],
    ["Valor da causa", "R$ 125.430,00"],
    ["Fase atual", "Cumprimento"]
  ]
}
```

Campos:
- `columns` (int, default 2) — número de colunas
- `items` (list de `[label, value]`) — pares

### table

Tabela estilizada com cabeçalho indigo e linhas alternadas.

```json
{
  "type": "table",
  "headers": ["Qualificação", "Nome", "Representação"],
  "rows": [
    ["Exequente", "Construtora X Ltda.", "OAB/CE 00000"],
    ["Executado", "Empresa Y S.A.", "OAB/CE 00000"]
  ],
  "col_widths_cm": [4.0, 7.0, 5.0]
}
```

Campos:
- `headers` (list de str) — cabeçalho da tabela
- `rows` (list de list de str) — dados
- `col_widths_cm` (list de float, opcional) — larguras em cm; soma recomendada: 16cm

### timeline

Linha do tempo processual. Coluna esquerda mostra data em fundo indigo soft, coluna direita mostra descrição.

```json
{
  "type": "timeline",
  "events": [
    ["15/03/2024", "Distribuição da ação"],
    ["02/04/2024", "Despacho inicial"],
    ["30/05/2024", "Contestação"]
  ]
}
```

Use para movimentos processuais em ordem cronológica.

### quote

Citação de jurisprudência com borda lateral indigo. Inclui autoria formatada.

```json
{
  "type": "quote",
  "text": "A prescrição intercorrente começa a correr a partir da ciência inequívoca do credor.",
  "author": "STJ · REsp 1.340.553/RS · Rel. Min. Mauro Campbell"
}
```

### callout

Bloco destacado com ícone. Três variantes:

```json
{"type": "callout", "kind": "info", "text": "Observação neutra ou explicação."}
{"type": "callout", "kind": "warn", "text": "Atenção: prazo crítico em curso."}
{"type": "callout", "kind": "ok", "text": "Requisitos de admissibilidade satisfeitos."}
```

Campos:
- `kind` (str, default "info") — `info`, `warn` ou `ok`
- `text` (str) — mensagem

### code

Bloco de código monoespaçado em Consolas com fundo cinza-lavanda.

```json
{"type": "code", "text": "python3 gerar_relatorio.py entrada.json saida.docx --pdf"}
```

Suporta múltiplas linhas se separadas por `\n`.

### signature

Bloco de assinatura no final do documento. Inclui linha, nome (Georgia bold) e cargo (Calibri itálico).

```json
{
  "type": "signature",
  "name": "Juiz(a) de Direito",
  "role": "Vara Cível da Comarca de Fortaleza",
  "local_data": "Fortaleza/CE, 14 de abril de 2026"
}
```

Campos:
- `name` (str) — nome que aparece acima da linha
- `role` (str, opcional) — cargo/função abaixo
- `local_data` (str, opcional) — local e data, posicionado acima da linha

## Restrições

- Nunca usar `\n` dentro de `paragraph.text` — crie múltiplos `paragraph` em sequência
- Nunca inserir `•`, `·` ou outros bullets manualmente no texto — use `bullets`
- Tabelas grandes (mais de 15 linhas) devem ser quebradas em múltiplas seções
- Quotes não devem ultrapassar 3 linhas — se for texto longo, use `paragraph` com prefixo de abertura
- O `data_cards` com mais de 8 itens vira difícil de ler — prefira tabela
