# Plugin TecJustica para Claude Code

Assessoria judicial inteligente para processos civeis e penais brasileiros. Analise processual, elaboracao de decisoes, jurisprudencia e calculos de prazos usando o MCP TecJustica.

## Pre-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado
- Conta no [TecJustica](https://tecjustica.com) (autenticacao via OAuth)

## Instalacao

### Passo 1 — Adicionar o repositorio como marketplace

No Claude Code, execute:

```
/plugin marketplace add marcosmarf27/tecjustica
```

### Passo 2 — Instalar o plugin

```
/plugin install tecjustica@marcosmarf27-tecjustica
```

Para instalar apenas no projeto atual (ao inves de globalmente):

```
/plugin install tecjustica@marcosmarf27-tecjustica --scope project
```

### Instalacao local (desenvolvimento)

Clone o repositorio e inicie o Claude Code apontando para ele:

```bash
git clone https://github.com/marcosmarf27/tecjustica.git
claude --plugin-dir ./tecjustica
```

Durante o desenvolvimento, use `/reload-plugins` para aplicar alteracoes sem reiniciar.

## Autenticacao

O plugin usa OAuth para autenticacao com o MCP TecJustica. Na primeira utilizacao de qualquer ferramenta do MCP, o navegador abrira automaticamente para login. Apos autenticar, o token e armazenado localmente.

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

### Relatorio de Audiencias (`relatorio-audiencias`)

Relatorio estruturado de todas as audiencias de um processo (criminal ou civel):

- Deteccao dinamica de qualquer tipo de audiencia nos autos
- Busca combinada: movimentacoes + documentos + analise semantica
- Tabela estruturada: Data | Tipo | Quem foi ouvido | Resumo | Providencias
- Alertas: audiencias sem ata, redesignadas, ausencias relevantes
- Exportacao DOCX opcional

## Dependencia opcional: Skill DOCX

Para gerar documentos `.docx` formatados (decisoes, despachos, sentencas), instale a skill DOCX oficial da Anthropic separadamente:

1. Baixe de [github.com/anthropics/skills](https://github.com/anthropics/skills) (pasta `skills/docx`)
2. Instale via Settings > Capabilities > Skills > Upload

> **Nota:** A skill DOCX tem licenca source-available restritiva e nao pode ser redistribuida com este plugin.

## Exemplos de uso

Apos instalar o plugin, as skills sao ativadas automaticamente quando voce faz pedidos relacionados. Basta conversar normalmente:

```
"Liste meus processos"

"Analise o processo 0001234-56.2024.8.26.0100"

"Elabore um despacho de saneamento para o processo X"

"Qual o prazo para contestacao se a citacao foi em 10/03/2025?"

"Busque sumulas do STJ sobre responsabilidade civil objetiva"

"Faca a dosimetria da pena para o processo Y"

"Faca um relatorio de audiencias do processo Z"

"Quem foi ouvido nas audiencias do processo X?"
```

## Gerenciamento do plugin

```
# Atualizar para a versao mais recente
/plugin marketplace update marcosmarf27-tecjustica

# Desabilitar temporariamente
/plugin disable tecjustica@marcosmarf27-tecjustica

# Reabilitar
/plugin enable tecjustica@marcosmarf27-tecjustica

# Desinstalar
/plugin uninstall tecjustica@marcosmarf27-tecjustica
```

## Licenca

Apache-2.0
