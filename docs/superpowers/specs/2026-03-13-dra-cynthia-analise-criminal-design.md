# Design: Skill Dra. Cynthia — Analise Criminal para Magistrado

## Resumo

Skill separada (`dra-cynthia-analise-criminal`) para analisar processo criminal e gerar relatorio estruturado para magistrado com anotacoes por folhas/documentos, facilitando a preparacao para audiencia de instrucao. Organiza dados sem sugestoes automaticas — o magistrado decide.

## Requisitos

- **Relatorio estruturado** — 4 secoes fixas + 4 condicionais
- **Referencias a folhas** — usar fls. quando disponivel, ID do documento como fallback
- **Busca linear** — workflow barato → caro com analisar() focado por tema
- **Contradições destacadas** — entre depoimentos, em negrito
- **Lacunas sinalizadas** — provas faltantes, diligencias pendentes
- **Sem sugestoes automaticas** — apenas dados organizados para o magistrado
- **DOCX opcional** — via skill docx
- **Instalacao por default** — vem incluida no plugin TecJustica

## Identidade da Skill

- **Nome tecnico:** `dra-cynthia-analise-criminal`
- **Persona:** Dra. Cynthia — assessora de gabinete de magistrado criminal, especializada em organizar processos criminais para preparacao de audiencias de instrucao
- **Localizacao:** `skills/dra-cynthia-analise-criminal/SKILL.md`

### Frontmatter YAML (formato exato do SKILL.md)

```yaml
---
name: dra-cynthia-analise-criminal
description: Analisar processo criminal e gerar relatorio estruturado para magistrado com anotacoes por folhas. Use quando o usuario pedir analise criminal detalhada, relatorio para audiencia, preparacao para instrucao, analise por folhas, resumo de processo criminal, cronologia processual, ou mencionar termos como "relatorio para audiencia", "analise por folhas", "preparacao para instrucao", "pontos para audiencia", "fls.", "anotacoes do processo", "relatorio estruturado criminal", "Dra. Cynthia", "analise criminal magistrado", "relatorio criminal", "preparar audiencia de instrucao".
---
```

## Ferramentas Disponiveis

O SKILL.md deve incluir secao completa de ferramentas:

### MCP TecJustica

- **`listar_processos()`** — descobrir processos disponiveis
- **`visao_geral_processo(cnj)`** — SEMPRE o primeiro passo
- **`grep_documentos(padrao, numero_processo)`** — buscar termos nos documentos
- **`grep_movimentacoes(padrao, numero_processo)`** — buscar nas movimentacoes
- **`glob_documentos(cnj, padrao_tipo)`** — filtrar docs por tipo
- **`localizar_no_documento(document_id, termo)`** — posicoes exatas de um termo
- **`read_documento(document_id, offset, max_chars)`** — leitura cirurgica de trechos
- **`analisar(cnj, pergunta, perspectiva)`** — analise semantica com LLM
- **`stats_documentos(cnj)`** — volume e distribuicao dos documentos
- **`buscar_precedentes(busca, orgaos, tipos)`** — sumulas, temas repetitivos, IRDR
- **`data_hora_atual()`** — data/hora atual

### Skill DOCX (instalacao separada)

Para gerar documentos DOCX. Se nao instalada, oferecer saida em Markdown.

### Skill Relatorio de Audiencias (instalada por default)

Para detalhamento completo de audiencias, invocar `relatorio-audiencias` como recurso complementar.

## Workflow de Busca

Fluxo linear seguindo principio de economia (barato → caro):

### Etapa 0 — Identificar o processo
- CNJ informado → usar diretamente
- Nao informado → `listar_processos()` e pedir escolha

### Etapa 1 — Contexto e dimensionamento
- `visao_geral_processo(cnj)` — metadados, partes, classe, assuntos
- `stats_documentos(cnj)` — volume e tipos de documentos

### Etapa 2 — Cronologia processual
- `grep_movimentacoes(".*", cnj)` — todas as movimentacoes para montar cronologia
- Identificar marcos: data do fato, registro, denuncia, citacao, audiencias, decisoes

### Etapa 3 — Mapear documentos por tipo
- `glob_documentos(cnj, "Denuncia*")` — denuncia/queixa
- `glob_documentos(cnj, "Resposta*|Defesa*")` — resposta a acusacao
- `glob_documentos(cnj, "Ata*|Termo*|Audiencia*")` — termos de audiencia/depoimentos
- `glob_documentos(cnj, "Laudo*|Peric*|Exame*")` — pericias
- `glob_documentos(cnj, "Alega*")` — alegacoes finais
- `glob_documentos(cnj, "Sentenc*|Decisao*|Despacho*")` — decisoes

### Etapa 4 — Analise tematica com analisar()
- `analisar(cnj, "Identifique a tipificacao penal, elementos do tipo, data e circunstancias do fato")`
- `analisar(cnj, "Liste todos os depoimentos e oitivas: nome, qualificacao, resumo do que disse, e contradicoes entre depoimentos")`
- `analisar(cnj, "Identifique todas as provas documentais e periciais, com descricao e relevancia")`
- `analisar(cnj, "Quais as teses da acusacao e da defesa? Quais os pontos controvertidos?")`
- `analisar(cnj, "Existem preliminares, nulidades ou questoes procedimentais pendentes?")`
- `analisar(cnj, "Quais diligencias, pericias ou oitivas estao pendentes?")`

### Etapa 5 — Leitura cirurgica
- `read_documento()` para trechos que precisam de citacao exata ou referencia a folhas/IDs
- Mapear folhas quando disponivel, usar ID do documento como fallback

### Etapa 6 — Consolidacao
- Montar relatorio nas secoes estruturais (fixas + condicionais)

## Estrutura do Relatorio

### Secoes fixas (sempre presentes)

1. **Resumo Executivo** — numero, tipo penal, reu(s), vitima(s), data do fato, fase atual
2. **Cronologia Processual** — marcos em ordem cronologica com datas e referencias
3. **Questoes Juridicas Relevantes** — preliminares, merito, pontos controvertidos
4. **Pontos para Audiencia de Instrucao** — pendencias (checklist com [ ]), teses em confronto (acusacao vs defesa)

### Secoes condicionais (so se houver dados)

5. **Anotacoes por Folhas/Documentos** — para cada documento relevante: referencia (fls. ou ID), tipo, data, resumo, pontos relevantes, impacto processual
6. **Provas Documentais** — pericias, laudos, documentos com referencias
7. **Depoimentos e Oitivas** — testemunhas de acusacao, defesa, interrogatorio do reu, com resumo e pontos-chave. Contradicoes entre depoimentos destacadas em **negrito**
8. **Manifestacoes das Partes** — teses do MP e da defesa com referencias

### Formatacao
- Referencias como `Fls. X` quando folhas disponiveis, `Doc. ID` como fallback
- Contradicoes entre depoimentos destacadas em **negrito**
- Lacunas probatorias sinalizadas
- Checklist com `[ ]` para pendencias
- Sem secao de "Sugestoes para o Magistrado"

### DOCX (quando solicitado)
- Cabecalho com dados do processo
- Relatorio completo formatado
- Gerado via skill docx se instalada; se nao, oferecer Markdown

## Regras de Ouro

1. **SEMPRE comece com `visao_geral_processo`** — nunca analise sem contexto
2. **Identifique o processo primeiro** — se o usuario nao informou o CNJ, use `listar_processos()`
3. **Principio de economia** — barato primeiro (grep/glob), caro depois (analisar/read)
4. **Pagine resultados** — quando `has_more: true`, use offset para ver tudo
5. **Nao leia docs inteiros** — use grep → localizar → read (cadeia eficiente)
6. **Verifique campo `fonte` e `confianca`** — dados de `segmentation` podem ter confianca baixa
7. **Referencie por folhas quando possivel** — usar fls., fallback para Doc. ID
8. **Destaque contradicoes** — entre depoimentos, em negrito
9. **Sinalize lacunas** — provas faltantes, diligencias pendentes
10. **Sem sugestoes** — organizar dados, nao sugerir perguntas ou conclusoes
11. **Use `relatorio-audiencias`** — para detalhamento completo de audiencias quando necessario

## Integracao

### Referencia cruzada em analise-processo-penal
Adicionar secao referenciando a Dra. Cynthia:

```markdown
### Skill Dra. Cynthia — Relatorio Criminal para Magistrado (instalada por default)
Para relatorio estruturado de processo criminal com anotacoes por folhas, preparacao para audiencia de instrucao, e organizacao de provas e depoimentos, invoque a skill `dra-cynthia-analise-criminal`.
```

### Referencia interna a relatorio-audiencias
O SKILL.md da Dra. Cynthia menciona `relatorio-audiencias` como recurso complementar para detalhamento de audiencias.

## Estrutura de Arquivos

```
skills/dra-cynthia-analise-criminal/
└── SKILL.md
```

### Alteracoes em arquivos existentes
- `skills/analise-processo-penal/SKILL.md` — adicionar secao referenciando a skill
- `README.md` — adicionar secao descrevendo a nova skill

### Sem alteracao
- `marketplace.json` — skill distribuida dentro do plugin `tecjustica`
