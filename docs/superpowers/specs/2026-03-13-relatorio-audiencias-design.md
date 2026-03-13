# Design: Skill Relatorio de Audiencias

## Resumo

Skill separada (`relatorio-audiencias`) para gerar relatorio estruturado de todas as audiencias de um processo judicial — criminal ou civel. Detecta dinamicamente qualquer tipo de audiencia nos autos, sem lista fixa. Invocavel diretamente pelo usuario ou pelas skills `analise-processo-penal` e `analise-processo-civil`.

## Requisitos

- **Deteccao dinamica** — qualquer evento que seja audiencia, sem lista pre-definida de tipos
- **Busca combinada** — cruzar movimentacoes + documentos + analisar() para cobertura maxima
- **Saida tabular** — tabela com colunas: Data | Tipo de Audiencia | Quem foi ouvido | Resumo | Providencias
- **DOCX opcional** — gerar documento formatado via skill docx quando solicitado
- **Instalacao por default** — vem incluida no plugin TecJustica

## Identidade da Skill

- **Nome:** `relatorio-audiencias`
- **Persona:** Assessor de gabinete especializado em analise de atos processuais, com foco em audiencias judiciais
- **Triggers:** relatorio de audiencias, listar audiencias, resumo de audiencias, audiencia de custodia, audiencia de instrucao, oitiva, depoimento, interrogatorio, conciliacao, mediacao, ata de audiencia, termo de audiencia
- **Localizacao:** `skills/relatorio-audiencias/SKILL.md`

### Frontmatter YAML (formato exato do SKILL.md)

```yaml
---
name: relatorio-audiencias
description: Gerar relatorio estruturado de todas as audiencias de um processo judicial (criminal ou civel). Use esta skill sempre que o usuario pedir relatorio de audiencias, listar audiencias, resumo de audiencias, quem foi ouvido, ou quando outra skill precisar identificar audiencias realizadas. Tambem use quando o usuario mencionar termos como "audiencia de custodia", "audiencia de instrucao", "audiencia de conciliacao", "oitiva", "depoimento", "interrogatorio", "conciliacao", "mediacao", "acareacao", "reconhecimento", "ata de audiencia", "termo de audiencia", "sustentacao oral", ou qualquer referencia a audiencias judiciais.
---
```

## Ferramentas Disponiveis

O SKILL.md deve incluir secao completa de ferramentas, seguindo o padrao das skills existentes:

### MCP TecJustica — Explorar processos

- **`listar_processos()`** — descobrir processos disponiveis
- **`visao_geral_processo(cnj)`** — SEMPRE o primeiro passo. Retorna metadados, partes, stats, catalogo de documentos com IDs, movimentacoes recentes
- **`grep_documentos(padrao, numero_processo)`** — buscar termos nos documentos (fulltext, regex ou ilike)
- **`grep_movimentacoes(padrao, numero_processo)`** — buscar nas movimentacoes
- **`glob_documentos(cnj, padrao_tipo)`** — filtrar docs por tipo (ex: "Ata", "Termo", "Audiencia")
- **`localizar_no_documento(document_id, termo)`** — posicoes exatas de um termo
- **`read_documento(document_id, offset, max_chars)`** — leitura cirurgica de trechos
- **`analisar(cnj, pergunta, perspectiva)`** — analise semantica com LLM (map-reduce automatico)
- **`stats_documentos(cnj)`** — volume e distribuicao dos documentos
- **`data_hora_atual()`** — data/hora atual

### Skill DOCX (instalacao separada)

Para gerar documentos DOCX, orientar o usuario a instalar a skill docx se nao estiver disponivel. Se nao instalada, oferecer saida em Markdown como alternativa.

## Workflow de Busca

Segue o principio de economia (barato → caro):

### Etapa 0 — Identificar o processo
- Se o usuario especificou o CNJ, usar diretamente
- Se nao, usar `listar_processos()` para descobrir processos disponiveis e pedir ao usuario que escolha

### Etapa 1 — Visao geral e mapeamento
- `visao_geral_processo(cnj)` — contexto do processo
- `stats_documentos(cnj)` — dimensionar volume de documentos
- `grep_movimentacoes("audiencia|ata|oitiva|depoimento|interrogat|concilia|mediac|acarea|reconheci|sustenta", cnj)` — identificar datas e tipos nas movimentacoes

### Etapa 2 — Localizar documentos de audiencia
- `glob_documentos(cnj, "Ata*")` + `glob_documentos(cnj, "Termo*Audiencia*")` + `glob_documentos(cnj, "Audiencia*")` — encontrar documentos por tipo
- Cruzar com movimentacoes da etapa 1 para lista consolidada sem duplicatas
- Paginar resultados quando `has_more: true` — usar offset para ver tudo

### Etapa 3 — Analise cirurgica de cada audiencia
- Para cada documento de audiencia identificado, usar `analisar(cnj, "Neste documento de audiencia, identifique: tipo de audiencia, data, quem foi ouvido (nomes e qualificacao: reu, vitima, testemunha de acusacao/defesa, perito, informante), resumo do que aconteceu, e providencias determinadas pelo juiz")`
- Se `analisar()` nao for suficiente, complementar com `read_documento()` para trechos especificos
- Paginar resultados quando `has_more: true`

### Etapa 4 — Consolidacao
- Ordenar audiencias cronologicamente
- Montar tabela estruturada
- Destacar audiencias pendentes/futuras se houver
- Se nenhuma audiencia for encontrada, informar ao usuario e indicar a fase processual atual

## Formato de Saida

### Tabela principal

| # | Data | Tipo de Audiencia | Quem foi ouvido | Resumo | Providencias |
|---|------|-------------------|-----------------|--------|--------------|
| 1 | DD/MM/AAAA | Tipo | Nomes e qualificacao | Resumo da audiencia | Providencias determinadas |

### Complementos
- Total de audiencias realizadas e pendentes/futuras
- Alertas: audiencias sem ata, redesignadas, ausencias relevantes

### Processo sem audiencias
- Informar que nao foram encontradas audiencias
- Indicar a fase processual atual e se audiencias sao esperadas

### DOCX (quando solicitado)
- Cabecalho com dados do processo (numero CNJ, vara, partes)
- Mesma tabela formatada
- Gerado via skill docx se instalada; se nao instalada, sugerir instalacao e oferecer Markdown

## Regras de Ouro

1. **SEMPRE comece com `visao_geral_processo`** — nunca analise sem contexto
2. **Identifique o processo primeiro** — se o usuario nao informou o CNJ, use `listar_processos()`
3. **Principio de economia** — barato primeiro (grep/glob), caro depois (analisar/read)
4. **Pagine resultados** — quando `has_more: true`, use offset para ver tudo
5. **Nao leia docs inteiros** — use grep → localizar → read (cadeia eficiente)
6. **Verifique campo `fonte` e `confianca`** — dados de `segmentation` podem ter confianca baixa
7. **Ordene cronologicamente** — audiencias devem aparecer na ordem em que ocorreram
8. **Destaque alertas** — audiencias sem ata, redesignadas, ausencias sao informacoes criticas
9. **Processos sem audiencias** — informe claramente e indique a fase processual

## Integracao com Outras Skills

As skills `analise-processo-penal` e `analise-processo-civil` recebem uma nova secao referenciando esta skill:

```
### Skill Relatorio de Audiencias (instalada por default)
Para relatorio completo de audiencias realizadas no processo,
invoque a skill `relatorio-audiencias`. Ela retorna tabela
estruturada com todas as audiencias, ouvidos, resumos e providencias.
```

## Estrutura de Arquivos

```
skills/relatorio-audiencias/
└── SKILL.md
```

### Alteracoes em arquivos existentes
- `skills/analise-processo-penal/SKILL.md` — adicionar secao referenciando a skill
- `skills/analise-processo-civil/SKILL.md` — idem

### Sem alteracao
- `marketplace.json` — a skill ja e distribuida dentro do plugin `tecjustica` (source: `./`)
