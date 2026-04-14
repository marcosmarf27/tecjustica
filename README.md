# Plugin TecJustica para Claude Code

Assessoria judicial inteligente para processos civeis e penais brasileiros. Analise processual, elaboracao de decisoes, pesquisa de jurisprudencia, download de autos do PJE, OCR de PDFs e calculos de prazos — tudo integrado via skills do Claude Code e o MCP Lite TecJustica (DataLake PDPJ/CNJ).

## Plataforma suportada

O plugin e projetado para **Claude Code rodando em Linux ou WSL2**.

- **Linux / macOS:** suportado nativamente. Recomendado.
- **Windows:** use via [WSL2](https://learn.microsoft.com/windows/wsl/install) com Ubuntu (ou distro equivalente). **Nao e suportado Windows nativo** — o MCP e as skills que dependem do `browser-use` CLI nao funcionam fora do ambiente Linux.

```powershell
# Windows: instalar WSL2 (no PowerShell como administrador)
wsl --install
# Reinicie, abra o Ubuntu, e siga o restante deste README de dentro do WSL.
```

## Pre-requisitos

**Sempre necessarios:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado no Linux/WSL
- [Node.js](https://nodejs.org) 18+ (para `npx mcp-remote`)
- Chave de API do MCP TecJustica (prefixo `mcp_...`) — criar em https://tecjusticamcp-lite-production.up.railway.app/registro

**Dependencias por skill (instale apenas as que for usar):**

| Skill | Dependencia externa | Como instalar |
|-------|---------------------|---------------|
| `tecjustica-mcp-lite`, `analise-processo-civil`, `analise-processo-penal` | Chave `mcp_...` (ja listada acima) | — |
| `tecjustica-parse` | `curl`, `python3` (ja vem no Linux) + chave `tjp_...` da TecJustica Parse | Cadastrar em https://tecjustica-dashboard-production.up.railway.app |
| `pje-download` | `browser-use` CLI + Google Chrome + credenciais do PJE TJCE 1o Grau (CPF/CNPJ ou certificado digital) | `curl -fsSL https://browser-use.com/cli/install.sh \| bash` |
| `cjf-jurisprudencia` | `browser-use` CLI + Google Chrome | `curl -fsSL https://browser-use.com/cli/install.sh \| bash` |

Apos instalar o `browser-use`, confirme com:

```bash
export PATH="$HOME/.browser-use-env/bin:$PATH"
browser-use doctor
```

## Instalacao

### Passo 1 — Adicionar o repositorio como marketplace

No Claude Code:

```
/plugin marketplace add marcosmarf27/tecjustica
```

### Passo 2 — Instalar o plugin

```
/plugin install tecjustica@marcosmarf27-tecjustica
```

Para instalar apenas no projeto atual:

```
/plugin install tecjustica@marcosmarf27-tecjustica --scope project
```

### Passo 3 — Configurar as chaves de API

O plugin usa duas variaveis de ambiente distintas. Cada servico TecJustica tem a **propria chave** — nao sao intercambiaveis.

| Variavel | Prefixo | Usada por | Obrigatoria? |
|----------|---------|-----------|--------------|
| `TECJUSTICA_API_KEY` | `mcp_...` | MCP TecJustica (skills de analise) | Sim |
| `TECJUSTICA_PARSE_API_KEY` | `tjp_...` | Skill `tecjustica-parse` (OCR de PDFs) | So se usar a parse |

Adicione ao seu `~/.bashrc` ou `~/.zshrc`:

```bash
export TECJUSTICA_API_KEY=mcp_sua_chave_aqui
export TECJUSTICA_PARSE_API_KEY=tjp_sua_chave_aqui   # opcional
```

Recarregue o shell (`source ~/.bashrc`) ou abra um novo terminal.

> **Alternativa para a chave da Parse:** copiar `skills/tecjustica-parse/config.env.example` para `skills/tecjustica-parse/config.env` e preencher. O `.gitignore` garante que esse arquivo nao va para o repositorio.

### Instalacao local (desenvolvimento)

```bash
git clone https://github.com/marcosmarf27/tecjustica.git
claude --plugin-dir ./tecjustica
```

Durante o desenvolvimento, use `/reload-plugins` para aplicar alteracoes sem reiniciar.

## Skills incluidas

### `tecjustica-mcp-lite` — Acesso ao DataLake PDPJ

Skill base que documenta as 12 tools `pdpj_*` do MCP TecJustica Lite. Pesquisa de processos por CNJ, CPF ou CNPJ, leitura de documentos (peticao inicial, contestacao, sentenca, acordao), linha do tempo, listagem de partes/advogados e busca de precedentes (sumulas, IRDR, repercussao geral, teses) no Banco Nacional de Precedentes. Dispara automaticamente com numeros CNJ ou termos como "processo", "peticao", "sumula".

### `analise-processo-civil` — Assessoria CPC

Assessor especializado em processo civil brasileiro. Identifica rito (comum, especial, execucao, cumprimento de sentenca), analisa fase processual, elabora despachos, decisoes interlocutorias e sentencas civeis, calcula prazos em dias uteis (CPC) e fundamenta com jurisprudencia. Consome dados via `tecjustica-mcp-lite`.

### `analise-processo-penal` — Assessoria CPP

Assessor especializado em processo penal brasileiro. Identifica rito (ordinario, sumario, sumarissimo, juri, especiais), controla prazos com reu preso vs. solto, auxilia na dosimetria trifasica, elabora despachos, decisoes e sentencas penais com atencao a garantias fundamentais. Calcula prazos em dias corridos (CPP). Consome dados via `tecjustica-mcp-lite`.

### `tecjustica-parse` — OCR de PDFs

Extrai texto de PDFs juridicos (escaneados ou digitais) via API TecJustica Parse com PaddleOCR GPU. Suporta enhance com IA Vision para correcao de erros e remocao de ruido (sidebars, rodapes). Processa certidoes, matriculas, peticoes e processos inteiros. Limite: 1GB por upload, 60 req/min.

### `pje-download` — Baixar autos do PJE TJCE

Automatiza o download de autos (PDFs) de processos do PJE TJCE 1o Grau usando `browser-use` CLI. Na primeira execucao abre o Chrome para login manual (CPF/CNPJ + senha ou certificado digital) e salva cookies em `~/.browser-use/pje_cookies.json` para reutilizacao. Traz script `baixar_autos_pje.sh` bundled com fallback manual documentado.

### `cjf-jurisprudencia` — Pesquisa unificada de jurisprudencia

Busca jurisprudencia unificada no Conselho da Justica Federal (STF, STJ, TRF1-5, TNU) via `browser-use` CLI em modo `--headed` (o WAF do CJF bloqueia headless). Suporta operadores logicos (`e`, `ou`, `nao`, `adj`, `prox`, `mesmo`, `com`) para pesquisa avancada.

## Exemplos de uso

Apos instalar o plugin, as skills sao ativadas automaticamente. Basta conversar normalmente:

```
"Analise o processo 3000066-83.2025.8.06.0203"

"Quais processos o CPF 12345678900 tem no TJSP?"

"Busque sumulas do STJ sobre dano moral em emprestimo consignado"

"Baixe os autos do processo 3000066-83.2025.8.06.0203 do PJE"

"Extraia o texto do PDF ./autos_3000066.pdf com OCR"

"Extraia a matricula imovel.pdf com enhance ativado"

"Elabore um despacho de saneamento para o processo X"

"Qual o prazo para contestacao se a citacao foi em 10/03/2025?"

"Faca a dosimetria da pena para o processo Y"

"Busque precedentes sobre tutela antecipada de urgencia no STJ"
```

## Gerenciamento do plugin

```
/plugin marketplace update marcosmarf27-tecjustica   # atualizar
/plugin disable tecjustica@marcosmarf27-tecjustica   # desabilitar
/plugin enable tecjustica@marcosmarf27-tecjustica    # reabilitar
/plugin uninstall tecjustica@marcosmarf27-tecjustica # desinstalar
```

## Licenca

Apache-2.0
