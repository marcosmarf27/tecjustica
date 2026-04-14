# Plugin TecJustica para Claude Code

Assessoria judicial inteligente para processos civeis e penais brasileiros. Analise processual, elaboracao de decisoes, pesquisa de jurisprudencia, download de autos do PJE, OCR de PDFs e calculos de prazos — tudo integrado via skills do Claude Code e o MCP Lite TecJustica (DataLake PDPJ/CNJ).

O plugin reune **6 skills** que trabalham em conjunto para dar ao magistrado, assessor ou advogado um ambiente de trabalho completo dentro do Claude Code.

## Sumario

- [Plataforma suportada](#plataforma-suportada)
- [Pre-requisitos](#pre-requisitos)
- [Passo 1 — Instalar dependencias do sistema](#passo-1--instalar-dependencias-do-sistema)
- [Passo 2 — Obter suas chaves de API](#passo-2--obter-suas-chaves-de-api)
- [Passo 3 — Configurar variaveis de ambiente](#passo-3--configurar-variaveis-de-ambiente)
- [Passo 4 — Instalar o plugin](#passo-4--instalar-o-plugin)
- [Passo 5 — Verificar a instalacao](#passo-5--verificar-a-instalacao)
- [Skills incluidas](#skills-incluidas)
- [Exemplos de uso](#exemplos-de-uso)
- [Fluxo completo de teste](#fluxo-completo-de-teste)
- [Gerenciamento do plugin](#gerenciamento-do-plugin)
- [Troubleshooting](#troubleshooting)
- [Licenca](#licenca)

---

## Plataforma suportada

O plugin e projetado para **Claude Code rodando em Linux ou WSL2**.

| Sistema | Suporte | Observacao |
|---------|:---:|-----------|
| Linux (Ubuntu, Debian, Fedora, etc.) | ✅ Nativo | Recomendado |
| macOS (Intel ou Apple Silicon) | ✅ Nativo | Funciona igual ao Linux |
| Windows via **WSL2** (Ubuntu) | ✅ Suportado | Unica forma suportada em maquinas Windows |
| Windows nativo (fora do WSL) | ❌ Nao suportado | `browser-use` CLI e `mcp-remote` tem limitacoes fora de ambiente Linux |

### Instalando WSL2 no Windows (uma vez)

1. Abra o **PowerShell como administrador** e execute:

   ```powershell
   wsl --install
   ```

2. Reinicie o Windows quando pedido.

3. No primeiro boot, o Ubuntu vai abrir e pedir para voce criar um usuario Linux e uma senha. Esses **nao** precisam ser iguais aos do Windows.

4. Todos os comandos a partir daqui sao executados **dentro do terminal do Ubuntu/WSL**, nunca no PowerShell.

> **Dica:** instale o [Windows Terminal](https://aka.ms/terminal) na Microsoft Store — ele abre abas do Ubuntu/WSL automaticamente e e mais comodo que o console padrao.

---

## Pre-requisitos

A tabela abaixo resume tudo. Os passos detalhados vem na proxima secao.

| Item | Obrigatorio para | Como instalar |
|------|------------------|---------------|
| Claude Code | Tudo | Secao 1.1 |
| Node.js 18+ | MCP TecJustica (todas skills de analise) | Secao 1.2 |
| `curl`, `python3`, `bash` | `tecjustica-parse` | Ja vem no Linux/WSL |
| Google Chrome | `pje-download`, `cjf-jurisprudencia` | Secao 1.3 |
| `browser-use` CLI | `pje-download`, `cjf-jurisprudencia` | Secao 1.4 |
| Chave API MCP (`mcp_...`) | MCP TecJustica | Secao 2.1 |
| Chave API Parse (`tjp_...`) | `tecjustica-parse` | Secao 2.2 (opcional) |
| Credenciais PJE TJCE | `pje-download` | Voce ja deve ter como magistrado/servidor/advogado |

---

## Passo 1 — Instalar dependencias do sistema

Execute no terminal do Linux/WSL (Ubuntu assumido — adapte `apt` para sua distro).

### 1.1 Claude Code

Se voce ainda nao tem:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Depois abra um novo terminal e confirme:

```bash
claude --version
```

### 1.2 Node.js 18+ (necessario para `npx mcp-remote`)

```bash
# Instalar a versao LTS do Node via NodeSource
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# Confirmar
node --version    # deve mostrar v18 ou superior
npm --version
```

### 1.3 Google Chrome (necessario para `pje-download` e `cjf-jurisprudencia`)

```bash
# Baixar o .deb oficial
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Instalar
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# Confirmar
google-chrome --version
```

> **WSL2:** o Chrome instalado dentro do WSL usa o WSLg automaticamente para abrir janelas no Windows. Se a janela nao aparecer, atualize o WSL (`wsl --update` no PowerShell) e tente de novo.

### 1.4 `browser-use` CLI

```bash
# Instalar o CLI
curl -fsSL https://browser-use.com/cli/install.sh | bash

# Adicionar ao PATH permanentemente
echo 'export PATH="$HOME/.browser-use-env/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Validar instalacao
browser-use doctor
```

A saida do `browser-use doctor` deve indicar que Python, dependencias e o binario Chromium/Chrome estao OK. Se algo aparecer como faltando, siga a orientacao do proprio comando.

---

## Passo 2 — Obter suas chaves de API

O plugin usa **duas chaves distintas**. Cada servico TecJustica tem a sua — nao sao intercambiaveis.

| Chave | Prefixo | Usada por | Obrigatoria? |
|-------|---------|-----------|:---:|
| MCP TecJustica | `mcp_...` | `tecjustica-mcp-lite`, `analise-processo-civil`, `analise-processo-penal` | **Sim** |
| TecJustica Parse | `tjp_...` | `tecjustica-parse` | So se usar OCR |

### 2.1 Chave do MCP TecJustica Lite

1. Acesse https://tecjusticamcp-lite-production.up.railway.app/registro
2. Crie uma conta (email + senha)
3. No painel, gere uma API key — o valor comeca com `mcp_` seguido de caracteres alfanumericos
4. **Copie e guarde em local seguro** — a chave nao e exibida de novo

### 2.2 Chave da TecJustica Parse (opcional)

Necessaria apenas se voce quiser usar a skill `tecjustica-parse` para extrair texto de PDFs.

1. Acesse https://tecjustica-dashboard-production.up.railway.app
2. Crie uma conta
3. No painel, gere uma API key — comeca com `tjp_`
4. Copie e guarde

---

## Passo 3 — Configurar variaveis de ambiente

Adicione as chaves ao seu `~/.bashrc` (ou `~/.zshrc` se usar zsh):

```bash
cat >> ~/.bashrc <<'EOF'

# TecJustica — chaves de API
export TECJUSTICA_API_KEY=mcp_SUBSTITUA_PELA_SUA_CHAVE
export TECJUSTICA_PARSE_API_KEY=tjp_SUBSTITUA_PELA_SUA_CHAVE   # opcional

# browser-use CLI no PATH
export PATH="$HOME/.browser-use-env/bin:$PATH"
EOF

# Recarregar o shell
source ~/.bashrc
```

**Confirmar que as variaveis estao definidas:**

```bash
echo "MCP:   $TECJUSTICA_API_KEY"
echo "Parse: $TECJUSTICA_PARSE_API_KEY"
```

Os dois valores devem aparecer. Se aparecer em branco, o Claude Code nao vai conseguir autenticar no MCP.

> **Atencao:** o Claude Code **le as variaveis de ambiente do terminal onde ele e iniciado**. Se voce exportar a variavel depois de abrir o Claude, feche e reabra — a sessao em andamento nao ve a mudanca.

> **Alternativa para a chave Parse:** em vez de usar env var, voce pode copiar `skills/tecjustica-parse/config.env.example` para `skills/tecjustica-parse/config.env` dentro do diretorio do plugin instalado e preencher a chave la. O `.gitignore` garante que esse arquivo nao vai para repositorio.

---

## Passo 4 — Instalar o plugin

Abra o Claude Code em qualquer diretorio:

```bash
cd ~
claude
```

Dentro da sessao, execute os comandos:

### 4.1 Adicionar o marketplace

```
/plugin marketplace add marcosmarf27/tecjustica
```

Esperado: confirmacao de que adicionou o marketplace `tecjustica-plugins`.

### 4.2 Instalar o plugin

```
/plugin install tecjustica@tecjustica-plugins
```

Isso instala o plugin globalmente, incluindo:
- O servidor MCP (`.mcp.json` com `mcp-remote`)
- As 6 skills (`tecjustica-mcp-lite`, `analise-processo-civil`, `analise-processo-penal`, `tecjustica-parse`, `pje-download`, `cjf-jurisprudencia`)

**Escopo de projeto (alternativa):** para instalar apenas no projeto atual, use:

```
/plugin install tecjustica@tecjustica-plugins --scope project
```

### 4.3 Instalacao local (desenvolvimento)

Se voce clonou este repositorio e quer testar localmente sem publicar:

```bash
git clone https://github.com/marcosmarf27/tecjustica.git
cd tecjustica
claude --plugin-dir .
```

Durante o desenvolvimento, `/reload-plugins` dentro da sessao aplica alteracoes sem reiniciar.

---

## Passo 5 — Verificar a instalacao

Dentro da sessao do Claude Code:

### 5.1 Plugin carregado

```
/plugin
```

Esperado: `tecjustica` aparece como **enabled**.

### 5.2 MCP conectado

```
/mcp
```

Esperado: `tecjustica` listado como **connected**.

Se aparecer `failed` ou ficar em `connecting` indefinidamente, consulte [Troubleshooting](#troubleshooting).

### 5.3 Skills descobertas

```
/help
```

Voce deve ver as 6 skills listadas sob o namespace do plugin. Elas sao **model-invoked**, ou seja, o Claude ativa automaticamente a skill correta quando voce faz um pedido que bate com a descricao — voce nao precisa digitar `/tecjustica:analise-processo-civil` manualmente.

### 5.4 Teste rapido

```
Analise o processo 3000066-83.2025.8.06.0203
```

Se tudo estiver configurado, o Claude vai:
1. Ativar a skill `tecjustica-mcp-lite` e/ou `analise-processo-civil`
2. Chamar `pdpj_visao_geral_processo`
3. Retornar metadados do processo (tribunal, classe, partes, assuntos, status)

Se retornar erro 401, a chave `TECJUSTICA_API_KEY` esta invalida ou nao foi lida pelo Claude. Se retornar "tool not found", o MCP nao carregou — veja [Troubleshooting](#troubleshooting).

---

## Skills incluidas

### `tecjustica-mcp-lite` — Acesso ao DataLake PDPJ

Skill base que documenta as **12 tools `pdpj_*`** do MCP TecJustica Lite. Pesquisa de processos por CNJ, CPF ou CNPJ, leitura de documentos (peticao inicial, contestacao, sentenca, acordao), linha do tempo, listagem de partes/advogados e busca de precedentes (sumulas, IRDR, repercussao geral, teses) no Banco Nacional de Precedentes. Dispara automaticamente com numeros CNJ ou termos como "processo", "peticao", "sumula".

**Tools disponiveis:**
- `pdpj_visao_geral_processo`, `pdpj_buscar_processos`, `pdpj_buscar_precedentes`
- `pdpj_list_partes`, `pdpj_list_movimentos`, `pdpj_list_documentos`
- `pdpj_read_documento`, `pdpj_read_documentos_batch`, `pdpj_get_documento_url`
- `pdpj_mapa_documentos`, `pdpj_analise_essencial`, `pdpj_grep_documentos`

### `analise-processo-civil` — Assessoria CPC

Assessor especializado em processo civil brasileiro. Identifica rito (comum, especial, execucao, cumprimento de sentenca), analisa fase processual, elabora despachos, decisoes interlocutorias e sentencas civeis, calcula prazos em dias uteis (CPC) e fundamenta com jurisprudencia. Consome dados via `tecjustica-mcp-lite`.

### `analise-processo-penal` — Assessoria CPP

Assessor especializado em processo penal brasileiro. Identifica rito (ordinario, sumario, sumarissimo, juri, especiais), controla prazos com reu preso vs. solto, auxilia na dosimetria trifasica (art. 68 CP), elabora despachos, decisoes e sentencas penais com atencao a garantias fundamentais. Calcula prazos em dias corridos (CPP). Consome dados via `tecjustica-mcp-lite`.

### `tecjustica-parse` — OCR de PDFs

Extrai texto de PDFs juridicos (escaneados ou digitais) via API TecJustica Parse com PaddleOCR GPU. Suporta `--enhance` com IA Vision para correcao de erros e remocao de ruido (sidebars, rodapes). Processa certidoes, matriculas, peticoes e processos inteiros. Limite: 1GB por upload, 60 req/min. Exige chave `tjp_...`.

### `pje-download` — Baixar autos do PJE TJCE

Automatiza o download de autos (PDFs) de processos do PJE TJCE 1o Grau usando `browser-use` CLI. Na primeira execucao abre o Chrome para login manual (CPF/CNPJ + senha ou certificado digital) e salva cookies em `~/.browser-use/pje_cookies.json` para reutilizacao. Traz script `baixar_autos_pje.sh` bundled com fallback manual documentado em `references/pje-navegacao.md`.

### `cjf-jurisprudencia` — Pesquisa unificada de jurisprudencia

Busca jurisprudencia unificada no Conselho da Justica Federal (STF, STJ, TRF1-5, TNU) via `browser-use` CLI em modo `--headed` (o WAF do CJF bloqueia headless). Suporta operadores logicos (`e`, `ou`, `nao`, `adj`, `prox`, `mesmo`, `com`, `$`) para pesquisa avancada.

---

## Exemplos de uso

Apos instalar o plugin, as skills sao ativadas automaticamente. Basta conversar normalmente com o Claude:

### Analise processual

```
"Analise o processo 3000066-83.2025.8.06.0203"

"Faca uma visao geral do processo X e me diga em que fase esta"

"Quais processos o CPF 12345678900 tem no TJSP?"

"Liste as partes e advogados do processo X"

"Mostra a linha do tempo do processo X nas ultimas decisoes"
```

### Leitura de documentos

```
"Leia a peticao inicial e a contestacao do processo X"

"Me mostra o laudo pericial do processo X"

"Busca o termo 'tutela antecipada' nos documentos do processo X"
```

### Elaboracao de decisoes

```
"Elabore um despacho de saneamento para o processo X"

"Redija uma decisao sobre o pedido de tutela de urgencia no processo X"

"Qual o prazo para contestacao se a citacao foi em 10/03/2025?"

"Faca a dosimetria da pena para o processo criminal Y"
```

### Jurisprudencia

```
"Busque sumulas do STJ sobre dano moral em emprestimo consignado"

"Tem sumula vinculante do STF sobre prisao preventiva?"

"Procura precedentes sobre usucapiao extraordinaria"
```

### Download e OCR

```
"Baixe os autos do processo 3000066-83.2025.8.06.0203 do PJE"

"Extraia o texto do PDF ./autos_3000066.pdf e salve em processo.md"

"Faz OCR com enhance na matricula imovel.pdf"
```

---

## Fluxo completo de teste

Ordem recomendada para validar que tudo esta funcionando ponta-a-ponta. Use o processo de exemplo `3000066-83.2025.8.06.0203` (TJCE) ou um seu.

### 1. Validar o MCP

```
Analise o processo 3000066-83.2025.8.06.0203
```

Esperado: Claude chama `pdpj_visao_geral_processo`, depois `pdpj_analise_essencial` ou `pdpj_mapa_documentos`, e retorna analise estruturada.

### 2. Validar busca de jurisprudencia via MCP

```
Busque sumulas do STJ sobre tutela antecipada
```

Esperado: Claude chama `pdpj_buscar_precedentes(busca="tutela antecipada", orgaos=["STJ"], tipos=["SUM"])` e retorna as sumulas encontradas.

### 3. Validar download do PJE

```
Baixe os autos do processo 3000066-83.2025.8.06.0203 do PJE
```

Esperado (primeiro uso):
1. Claude executa o script `baixar_autos_pje.sh` via `pje-download`
2. Chrome abre em modo visivel
3. Para na tela de login do PJE TJCE
4. **Voce loga manualmente** (CPF + senha ou certificado digital)
5. Pressiona ENTER no terminal quando pedido
6. Script continua: navega → pesquisa → abre autos → baixa o PDF
7. Arquivo final: `./3000066-83.2025.8.06.0203.pdf` no diretorio atual
8. Nas proximas vezes, o login e pulado (cookies salvos)

### 4. Validar OCR

```
Extraia o texto do PDF ./3000066-83.2025.8.06.0203.pdf e salve em processo.md
```

Esperado: Claude invoca `tecjustica-parse`, faz upload async para a API, faz polling do job, e salva o markdown em `processo.md`.

### 5. Analise completa

```
Atue como assessor de gabinete e analise o processo 3000066-83.2025.8.06.0203, identificando rito, fase, decisoes pendentes e proximos passos
```

Esperado: Claude combina `analise-processo-civil` (ou `-penal`, conforme a classe) com `tecjustica-mcp-lite` para produzir analise completa com rito, fase, prazos, decisoes cabiveis e fundamentacao legal.

---

## Gerenciamento do plugin

```
/plugin                                          # listar plugins instalados
/plugin marketplace update tecjustica-plugins    # atualizar para a ultima versao
/plugin disable tecjustica@tecjustica-plugins    # desabilitar temporariamente
/plugin enable tecjustica@tecjustica-plugins     # reabilitar
/plugin uninstall tecjustica@tecjustica-plugins  # desinstalar
/reload-plugins                                  # recarregar (util em desenvolvimento)
/mcp                                             # ver status dos MCP servers
```

---

## Troubleshooting

### O `/mcp` mostra `tecjustica` como `failed`

- **Causa mais comum:** a variavel `TECJUSTICA_API_KEY` nao esta disponivel no ambiente do Claude Code.
- **Correcao:** feche o Claude, confirme `echo $TECJUSTICA_API_KEY` no mesmo shell, e reabra o Claude no mesmo terminal.
- **Teste manual da chave:**

  ```bash
  npx -y mcp-remote https://tecjusticamcp-lite-production.up.railway.app/mcp \
    --header "Authorization: Bearer $TECJUSTICA_API_KEY"
  ```

  Se a chave estiver errada, o servidor responde 401.

### "Tool not found" ao pedir analise

- **Causa mais comum:** o MCP nao carregou (veja item acima) **ou** as skills de analise estao tentando chamar tools com nomes antigos.
- **Verificar:** rode `/mcp` — deve estar `connected`. Rode `/help` — as skills devem aparecer.
- Se o MCP esta conectado e o erro persiste, reinstale o plugin:

  ```
  /plugin uninstall tecjustica@tecjustica-plugins
  /plugin marketplace update tecjustica-plugins
  /plugin install tecjustica@tecjustica-plugins
  ```

### `browser-use: command not found`

- O PATH nao contem `$HOME/.browser-use-env/bin`. Confirme com `echo $PATH` e adicione a linha em [Secao 1.4](#14-browser-use-cli) ao seu `~/.bashrc`.

### Chrome nao abre ao rodar `pje-download`

- **No WSL2:** verifique se o WSLg esta funcionando. Abra o PowerShell como admin e rode `wsl --update`, depois reinicie o WSL: `wsl --shutdown`.
- **No Linux:** confirme que `google-chrome --version` responde. Se der erro de display, verifique `echo $DISPLAY`.

### `pje-download`: cookies expirados

- Os cookies do PJE tem validade limitada. Quando expiram, o script pede para fazer login de novo. Apague o arquivo `~/.browser-use/pje_cookies.json` e rode de novo para forcar novo login:

  ```bash
  rm ~/.browser-use/pje_cookies.json
  ```

### `tecjustica-parse`: erro 401 ou "API key nao configurada"

- Confirme `echo $TECJUSTICA_PARSE_API_KEY` — se estiver vazio, adicione ao `~/.bashrc` e reabra o terminal.
- Confirme que a chave comeca com `tjp_` (e **nao** com `mcp_`). Elas sao trocadas com frequencia — preste atencao ao prefixo.
- Alternativamente, use `config.env` dentro da pasta da skill (veja [Passo 3](#passo-3--configurar-variaveis-de-ambiente)).

### `cjf-jurisprudencia`: WAF bloqueia a busca

- O CJF tem WAF que detecta automacao headless. A skill ja usa `--headed` por padrao.
- Se mesmo assim bloquear, aguarde alguns minutos (o block costuma ser temporario por IP) ou rode a busca em outro horario.

### Rate limit do MCP (erro 429)

- O servidor MCP Lite tem rate limit por token (aprox 1h para reset). Se aparecer 429, aguarde — a skill `tecjustica-mcp-lite` orienta o Claude a nao insistir automaticamente.

### Windows nativo

- O plugin **nao suporta** Windows nativo. Use WSL2. Veja [Plataforma suportada](#plataforma-suportada).

---

## Licenca

Apache-2.0

---

## Contribuicoes

Abra uma issue ou pull request em https://github.com/marcosmarf27/tecjustica. Feedback dos magistrados e assessores que usam no dia-a-dia e bem-vindo.
