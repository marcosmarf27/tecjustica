# Plugin TecJustica para Claude Code

Assessoria judicial inteligente para processos civeis e penais brasileiros. Analise processual, elaboracao de decisoes, jurisprudencia e calculos de prazos usando o MCP TecJustica.

## Pre-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado
- Conta no [TecJustica](https://tecjustica.com) (autenticacao via OAuth)

## Instalacao

### Via Claude Code Plugin Marketplace

```bash
claude plugin install tecjustica
```

### Instalacao local (desenvolvimento)

```bash
git clone https://github.com/tecjustica/skills-tecjustica.git
claude --plugin-dir ./skills-tecjustica
```

## Autenticacao

O plugin usa OAuth para autenticacao com o MCP TecJustica. Na primeira utilizacao, o navegador abrira automaticamente para login. Apos autenticar, o token e armazenado localmente.

## Skills incluidas

### Analise de Processo Civil (`analise-processo-civil`)

Assessoria completa para processos civeis:
- Identificacao automatica do rito (procedimento comum, especial, execucao, cumprimento de sentenca)
- Analise de fase processual e proximos passos
- Elaboracao de despachos, decisoes interlocutorias e sentencas civeis
- Calculo de prazos em dias uteis (CPC)
- Pesquisa de jurisprudencia (sumulas, temas repetitivos, IRDR)
- Visualizacoes: timelines, dashboards, fluxogramas do rito

### Analise de Processo Penal (`analise-processo-penal`)

Assessoria completa para processos criminais:
- Identificacao automatica do rito (ordinario, sumario, sumarissimo, juri, especiais)
- Controle de prazos com reu preso vs. solto
- Dosimetria da pena (sistema trifasico)
- Elaboracao de despachos, decisoes e sentencas penais
- Calculo de prazos em dias corridos (CPP)
- Pesquisa de jurisprudencia penal
- Atencao especial a garantias fundamentais

## Dependencia opcional: Skill DOCX

Para gerar documentos `.docx` formatados (decisoes, despachos, sentencas), instale a skill DOCX oficial da Anthropic separadamente:

1. Baixe de [github.com/anthropics/skills](https://github.com/anthropics/skills) (pasta `skills/docx`)
2. Instale via Settings > Capabilities > Skills > Upload

> **Nota:** A skill DOCX tem licenca source-available restritiva e nao pode ser redistribuida com este plugin.

## Exemplos de uso

```
# Listar processos disponiveis
"Liste meus processos"

# Analisar um processo civel
"Analise o processo 0001234-56.2024.8.26.0100"

# Elaborar uma decisao
"Elabore um despacho de saneamento para o processo X"

# Calcular prazo
"Qual o prazo para contestacao se a citacao foi em 10/03/2025?"

# Buscar jurisprudencia
"Busque sumulas do STJ sobre responsabilidade civil objetiva"
```

## Licenca

Apache-2.0
