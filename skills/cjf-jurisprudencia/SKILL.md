---
name: cjf-jurisprudencia
description: Busca jurisprudência unificada no CJF (STF, STJ, TRFs, TNU) via browser-use CLI. Dispara com "jurisprudência", "precedente", "acórdão", "ementa", "CJF", "STJ", "STF", "TRF", ou pesquisa de tese jurídica.
argument-hint: [termo-busca]
allowed-tools: Bash(bash *), Bash(export *), Bash(browser-use *)
---

# CJF Jurisprudência — Busca Unificada

Busca jurisprudência no site do Conselho da Justiça Federal usando browser-use CLI.

**URL:** https://jurisprudencia.cjf.jus.br/unificada/index.xhtml

## Pré-requisito

```bash
export PATH="$HOME/.browser-use-env/bin:$PATH" && command -v browser-use && echo "OK" || echo "NAO_INSTALADO"
```

Se não instalado: `curl -fsSL https://browser-use.com/cli/install.sh | bash`

## Fluxo de busca

O site é público (sem login). Para navegar, leia [`references/cjf-navegacao.md`](${CLAUDE_SKILL_DIR}/references/cjf-navegacao.md) que documenta todos os elementos DOM e o passo a passo.

O termo de busca é: `$ARGUMENTS`

Se `$ARGUMENTS` estiver vazio, perguntar ao usuário o que deseja pesquisar.

### Resumo dos passos

1. **Abrir o site (OBRIGATÓRIO --headed, WAF bloqueia headless):**
   ```bash
   export PATH="$HOME/.browser-use-env/bin:$PATH"
   browser-use close 2>/dev/null || true
   browser-use --profile "Default" --headed open https://jurisprudencia.cjf.jus.br/unificada/index.xhtml
   sleep 5
   ```

2. **Selecionar tribunais** — marcar os checkboxes desejados (STF, STJ, TRF1-5, TNU, TR, TRU). Para todos: marcar "Todos" E marcar "TR" e "TRU" (obrigatórios, o site dá erro sem eles).

3. **Digitar termo de busca** no campo `input#formulario:textoLivre` e clicar `button#formulario:actPesquisar`.

4. **Ler resultados** — o state mostra tipo, relator, origem, data, ementa. Cada resultado tem botão "Documento" para ver inteiro teor.

5. **Reportar ao usuário** — listar os resultados relevantes com tipo, tribunal, relator, ementa.

### Operadores de busca

O site aceita operadores lógicos entre termos. Existem botões na interface, mas podem ser digitados diretamente:

| Operador | Função | Exemplo |
|----------|--------|---------|
| `e` | AND — ambos os termos | `dano moral e bancário` |
| `ou` | OR — qualquer termo | `dano moral ou material` |
| `não` | NOT — exclui termo | `dano moral não trabalhista` |
| `adj` | Adjacente — termos juntos em ordem | `dano adj moral` |
| `prox` | Proximidade — termos próximos | `dano prox5 moral` |
| `mesmo` | No mesmo campo/parágrafo | `dano mesmo moral` |
| `com` | No mesmo documento | `dano com indenização` |
| `$` | Truncamento — raiz da palavra | `indeniz$` (indenização, indenizar...) |

### Pesquisa avançada

Se o usuário precisar filtrar por data, número de processo, ou outros campos, marcar o checkbox "Pesquisa avançada" (`input#formulario:ckbAvancada_input`) que expande campos adicionais.

## Regras importantes

- **Sempre marcar TR e TRU** quando selecionar "Todos" — o site exige pelo menos uma Turma Regional selecionada, caso contrário mostra erro.
- O site é público, não precisa de login nem cookies.
- Os índices dos elementos mudam a cada carregamento. Buscar por ID estável (`formulario:textoLivre`, `formulario:actPesquisar`, etc.).
- `browser-use eval` funciona aqui (não tem iframes).
- Para ler ementas longas, pode ser necessário fazer `browser-use scroll down` várias vezes.
- Cada resultado tem botão "Documento" que abre o inteiro teor em detalhe.
