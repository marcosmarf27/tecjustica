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

## Workflow de Busca

Segue o principio de economia (barato → caro):

### Etapa 1 — Visao geral e mapeamento
- `visao_geral_processo(cnj)` — contexto do processo
- `grep_movimentacoes("audiencia|ata|oitiva|depoimento|interrogat|concilia|media", cnj)` — identificar datas e tipos nas movimentacoes

### Etapa 2 — Localizar documentos de audiencia
- `glob_documentos(cnj, "Ata*")` + `glob_documentos(cnj, "Termo*Audiencia*")` + `glob_documentos(cnj, "Audiencia*")` — encontrar documentos por tipo
- Cruzar com movimentacoes da etapa 1 para lista consolidada sem duplicatas

### Etapa 3 — Analise cirurgica de cada audiencia
- Para cada documento de audiencia identificado, usar `analisar(cnj, "Neste documento de audiencia, identifique: tipo de audiencia, data, quem foi ouvido (nomes e qualificacao: reu, vitima, testemunha de acusacao/defesa, perito, informante), resumo do que aconteceu, e providencias determinadas pelo juiz")`
- Se `analisar()` nao for suficiente, complementar com `read_documento()` para trechos especificos

### Etapa 4 — Consolidacao
- Ordenar audiencias cronologicamente
- Montar tabela estruturada
- Destacar audiencias pendentes/futuras se houver

## Formato de Saida

### Tabela principal

| # | Data | Tipo de Audiencia | Quem foi ouvido | Resumo | Providencias |
|---|------|-------------------|-----------------|--------|--------------|
| 1 | DD/MM/AAAA | Tipo | Nomes e qualificacao | Resumo da audiencia | Providencias determinadas |

### Complementos
- Total de audiencias realizadas e pendentes/futuras
- Alertas: audiencias sem ata, redesignadas, ausencias relevantes

### DOCX (quando solicitado)
- Cabecalho com dados do processo (numero CNJ, vara, partes)
- Mesma tabela formatada
- Gerado via skill docx se instalada

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
