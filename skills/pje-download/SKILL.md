---
name: pje-download
description: Baixa autos (PDFs) de processos do PJE TJCE 1º Grau via browser-use CLI. Dispara com "PJE", "autos", "baixar processo", "download autos", "TJCE", ou números no formato NNNNNNN-DD.AAAA.J.TT.OOOO.
argument-hint: [numero-processo]
allowed-tools: Bash(bash *), Bash(chmod *), Bash(curl *), Bash(export *), Bash(browser-use *), Bash(ls *), Bash(rm *), Bash(cat *)
---

# PJE Download — Baixar Autos de Processos

## Pré-requisitos

Antes de tudo, verificar se o browser-use CLI está instalado:

```bash
export PATH="$HOME/.browser-use-env/bin:$PATH" && command -v browser-use && echo "OK" || echo "NAO_INSTALADO"
```

Se `NAO_INSTALADO`, orientar o usuário a instalar:

```bash
curl -fsSL https://browser-use.com/cli/install.sh | bash
```

Requisitos da máquina: Python 3.11+, Google Chrome instalado.

## Estratégia: Script primeiro, fallback manual depois

### Nível 1 — Script determinístico

Rodar o script bundled. Ele faz tudo sozinho: abre PJE, restaura cookies, navega, baixa o PDF.

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/baixar_autos_pje.sh "$ARGUMENTS"
```

**Destino padrão:** raiz do projeto (`$CLAUDE_PROJECT_DIR`). O PDF sai em `$CLAUDE_PROJECT_DIR/NNNNNNN-DD.AAAA.J.TT.OOOO.pdf`, **nunca** dentro da pasta da skill ou de `scripts/`. Fora do Claude Code, cai no `$PWD` atual.

Para forçar outro destino:
```bash
bash ${CLAUDE_SKILL_DIR}/scripts/baixar_autos_pje.sh "$ARGUMENTS" --output /pasta/destino
```

Se `$ARGUMENTS` estiver vazio, perguntar o número do processo ao usuário.

O número do processo deve estar no formato `NNNNNNN-DD.AAAA.J.TT.OOOO`.

### Login manual (primeira execução ou cookies expirados)

O script autentica com cookies salvos em `~/.browser-use/pje_cookies.json`. Na primeira execução (e sempre que os cookies expirarem), o Chrome precisa abrir com a tela de login para o usuário digitar CPF/CNPJ + senha ou usar certificado digital.

**Como funciona a espera do login (importante — não trava em modo não-interativo):**

O script detecta se está rodando num terminal interativo (TTY) ou sendo invocado pelo Claude Code (sem TTY) e escolhe a estratégia certa de espera:

- **TTY presente** — o script avisa o usuário, aceita ENTER como sinal "já loguei" **e** checa em paralelo o estado do browser a cada 5s. O que vier primeiro encerra a espera.
- **Sem TTY (Claude Code)** — o script não chama `read`. Fica em loop checando o estado do browser a cada 5s (timeout 5 min). Quando detecta os marcadores pós-login (`Abrir menu` / `Quadro de avisos`), segue.

Em ambos os modos, a detecção final é **positiva**: só confirma login quando os marcadores pós-login aparecem no `browser-use state`. Não confia em "tela de login sumiu" (que daria falso positivo em loadings).

**Antes de invocar o script pela primeira vez, avise o usuário:**

> "Vou baixar o processo. Se for sua primeira execução ou os cookies expiraram, uma janela do Chrome vai abrir para você fazer login manual. O script detecta automaticamente quando você concluir."

**Dica para primeira execução limpa:** se você quer só estabelecer a sessão sem baixar nada ainda, rode o script no modo `--login`. Isso é especialmente útil quando o usuário prefere logar de forma deliberada antes de pedir downloads. Instrua-o a rodar no próprio prompt do Claude Code, prefixando com `!` para garantir TTY do shell do usuário:

```
! bash ${CLAUDE_SKILL_DIR}/scripts/baixar_autos_pje.sh --login
```

Esse modo apenas abre o Chrome, espera o login, salva os cookies e sai. Depois o download roda normalmente (sem re-login) até os cookies expirarem.

**Se o script concluir com "=== Concluído ==="**, informe o caminho e tamanho do PDF ao usuário. Trabalho feito.

**Se o script falhar**, vá para o Nível 2.

### Nível 2 — Navegação manual com browser-use CLI

Se o script falhou, leia o guia completo de navegação em [`references/pje-navegacao.md`](${CLAUDE_SKILL_DIR}/references/pje-navegacao.md) e siga os passos manualmente usando browser-use CLI. O guia documenta todos os elementos DOM, IDs estáveis, e armadilhas do PJE.

O fluxo resumido:

1. **Abrir e autenticar:**
   ```bash
   export PATH="$HOME/.browser-use-env/bin:$PATH"
   browser-use close 2>/dev/null || true
   browser-use --profile "Default" --headed open https://pje.tjce.jus.br/
   sleep 3
   browser-use cookies import ~/.browser-use/pje_cookies.json 2>/dev/null
   browser-use open https://pje.tjce.jus.br/
   sleep 4
   ```
   Se `browser-use state` mostrar `id=username` ou `id=kc-login`, pedir ao usuário para logar no Chrome e avisar. Depois: `browser-use cookies export ~/.browser-use/pje_cookies.json`

2. **Esperar painel interno carregar** — verificar `browser-use state | grep "liTarefas"`. Se não aparecer, clicar em "Painel do usuário".

3. **Expandir filtros de Tarefas** — clicar no segundo `div aria-expanded=false` (seção Tarefas, não Minhas tarefas).

4. **Pesquisar** — preencher campo `itNrProcesso` com número completo, clicar `<button>Pesquisar</button>`.

5. **Abrir tarefa** — clicar na tarefa filtrada (`<a title="[Sec] - ...">`).

6. **Selecionar processo** — clicar no `<span>` do número do processo.

7. **Abrir autos** — clicar `button[title="Abrir autos"]` (ícone do livro), mudar para aba 1 (`browser-use switch 1`).

8. **Download** — clicar `a[title="Download autos do processo"]`, depois `input[value="Download"]`. Esperar PDF abrir na aba 2, capturar URL com `browser-use eval "window.location.href"`, baixar com `curl -sL -o arquivo.pdf "URL"`.

## Regras críticas (armadilhas do PJE)

- **`browser-use eval` NÃO enxerga iframes.** Todo o painel interno do PJE está em `iframe#ngFrame`. Use `browser-use state` + `browser-use click <index>` para interagir — os índices do state incluem iframes.

- **Índices mudam a cada carregamento.** Nunca hardcodar índices. Sempre buscar por padrão estável:
  ```bash
  IDX=$(browser-use state | grep "PADRAO" | grep -oE '\[[0-9]+\]' | tr -d '[]' | head -1)
  browser-use click $IDX
  ```

- **Campos pré-preenchidos duplicam valor.** Os campos `ramoJustica` e `respectivoTribunal` já vêm com "8" e "06". Para preencher: `click` → `keys "Control+a"` → `type "valor"`.

- **URL do PDF expira em 120 segundos.** Após capturar com `eval`, baixar imediatamente com curl.

- **Cookies do PJE expiram.** Sempre importar cookies antes e verificar login. Se expirou, pedir login manual ao usuário.
