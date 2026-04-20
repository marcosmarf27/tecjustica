---
name: baixar-autos-pje
description: Baixa os autos completos em PDF de um ou mais processos do PJE 1º grau de qualquer tribunal brasileiro que use PJE/CNJ (TJCE, TJRN, TJPE, TJMG, TJDFT, TRFs, TRTs etc.) usando a extensão Claude in Chrome. Dispare SEMPRE que o usuário servidor/advogado/magistrado pedir para "baixar os autos", "pegar o PDF do processo", "puxar os autos", "baixa esse CNJ pra mim", "salva o processo em PDF", ou simplesmente mandar um número CNJ no formato NNNNNNN-DD.AAAA.J.TR.OOOO sozinho ou em lista. Usa o caminho "Consulta Processual" do PJE — preenche os 6 campos do CNJ, aciona a geração do PDF consolidado no servidor e salva o arquivo no workspace folder da sessão Cowork. Requer sessão ativa logada no PJE na aba do Chrome controlada pela extensão Claude. Na primeira invocação a skill descobre qual instância do PJE usar (default `pje.tjce.jus.br/pje1grau`, mas aceita qualquer outra que o usuário informe ou que já esteja aberta na aba). NÃO use para processos de 2º grau (pje2grau), sistemas não-PJE (eproc, esaj, PJC, Projudi) ou quando o usuário só quer ler movimentos/documentos isolados — para isso existe a skill tecjustica-mcp-lite.
---

# Baixar autos do PJE (1º grau) via Claude in Chrome

Você está atuando como operador do PJE. A tarefa é pegar o PDF consolidado dos autos de um ou mais processos e entregar pro usuário no workspace folder. O caminho é a **Consulta Processual** do PJE — ele funciona pra qualquer processo público e tem IDs JSF estáveis, ao contrário do caminho via Tarefas.

Esse fluxo foi desenvolvido e validado no **TJCE**, mas funciona em **qualquer instalação do PJE** (TJs estaduais, TRFs, TRTs) porque o sistema é unificado pelo CNJ — o DOM JSF (`fPP:numeroProcesso:*`, `fPP:processosTable`, botão "Download") é compartilhado entre tribunais. A única coisa que muda entre instâncias é a **URL base** (ex.: `pje.tjce.jus.br/pje1grau`, `pje.tjrn.jus.br/pje1grau`, `pje.trf1.jus.br/pje`).

Esse fluxo foi medido em ~15 segundos end-to-end pra processos pequenos (2–3 MB). Processos grandes (300+ páginas) podem levar até 3 minutos na etapa de geração do PDF — tenha paciência no polling.

## Pré-requisitos de ambiente

Antes de começar, confirme que:

1. **Claude in Chrome está disponível.** Você vai usar `mcp__Claude_in_Chrome__*` (navigate, javascript_tool, tabs_context_mcp, find). Se não tem essas ferramentas, a skill não é aplicável — avise o usuário que precisa da extensão.
2. **Há uma aba Chrome controlável.** Chame `tabs_context_mcp({ createIfEmpty: true })` e capture o `tabId` da aba ativa.
3. **Você sabe qual instância do PJE usar.** Veja a próxima seção — determinar a URL base é o primeiro passo concreto.
4. **Sessão PJE está logada.** Navegue para a URL base do PJE escolhida (ex.: `https://pje.tjce.jus.br/`) e confirme pela **presença** de "Abrir menu" ou "Quadro de avisos" (use `find` com essa query). Nunca confirme pela ausência de `#username` — carregamentos intermediários dão falso positivo. Se não estiver logado, pare e peça pro usuário fazer login manualmente na aba controlada (a skill não lida com credenciais).

## Determinar a URL base do PJE

O PJE é multi-tribunal. Cada instância tem sua própria URL. Antes de rodar o fluxo principal, descubra qual usar — nessa ordem de prioridade:

1. **O usuário disse explicitamente?** Ex.: "baixa esse processo do TJRN", "pega do PJE TRF1". Se sim, use a URL correspondente.
2. **Existe alguma aba Chrome já aberta num domínio `pje.*.jus.br`?** Cheque com `tabs_context_mcp` e inspecione as URLs. Se houver uma (idealmente logada), assuma que é a instância do dia e confirme com o usuário em uma frase curta: *"Vi que você já está no `pje.tjce.jus.br/pje1grau`. Posso usar essa instância?"*
3. **Nada disso?** Pergunte ao usuário de forma direta: *"Qual PJE você quer usar? Padrão é TJCE 1º grau (`pje.tjce.jus.br/pje1grau`). Se for outro tribunal, me passa a URL base."*

Mantenha a URL base resolvida numa variável local pra essa conversa — chame de `<PJE_BASE>`. Nos próximos passos, toda URL que usa o PJE substitui `<PJE_BASE>` pelo valor descoberto. Ex.: a Consulta Processual fica em `<PJE_BASE>/Processo/ConsultaProcesso/listView.seam`.

**Default seguro:** se a conversa começou sem contexto e o usuário não se pronunciou, assuma `https://pje.tjce.jus.br/pje1grau` (foi onde o fluxo foi validado). Informe isso de forma transparente na primeira resposta.

### Tabela de URLs conhecidas (não-exaustiva)

| Tribunal              | Ramo.Trib | URL base típica                              |
|-----------------------|-----------|----------------------------------------------|
| TJCE (Ceará)          | 8.06      | `https://pje.tjce.jus.br/pje1grau`           |
| TJRN (Rio G. Norte)   | 8.20      | `https://pje.tjrn.jus.br/pje1grau`           |
| TJPE (Pernambuco)     | 8.17      | `https://pje.tjpe.jus.br/1g`                 |
| TJMG (Minas Gerais)   | 8.13      | `https://pje.tjmg.jus.br/pje`                |
| TJDFT (Distr. Federal)| 8.07      | `https://pje.tjdft.jus.br/pje`               |
| TRF1 (1ª Região)      | 4.01      | `https://pje1g.trf1.jus.br/pje`              |
| TRF5 (5ª Região)      | 4.05      | `https://pje.trf5.jus.br/pje`                |
| TRT genérico (Trab.)  | 5.XX      | `https://pje.trtXX.jus.br/primeirograu`      |

Se o tribunal pedido não está na tabela, **não chute** — pergunte a URL ao usuário. Os subdiretórios variam (`/pje1grau`, `/pje`, `/1g`, `/primeirograu`) e errar só faz perder tempo com 404.

## Inputs que você recebe

O usuário manda um ou mais números CNJ no formato `NNNNNNN-DD.AAAA.J.TR.OOOO`. Exemplos válidos:
- Um só (TJCE): `3000029-27.2023.8.06.0203`
- Em lista (TJCE): `0123456-12.2024.8.06.0001, 9876543-21.2023.8.06.0145`
- Numa frase: "baixa os autos desse aí 3000029-27.2023.8.06.0203"
- Outro tribunal (TRF1): `1012345-67.2023.4.01.3800`

Extraia os CNJs do input com o regex genérico `\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}`. Os dígitos `J.TR` (ramo + tribunal) indicam onde o processo tramita e devem ser **coerentes com a instância PJE escolhida** — se o usuário mandou um CNJ com `.8.06.` (TJCE) mas você está apontando pro TJRN, avise o mismatch e pergunte qual URL ele quer realmente usar.

## Fluxo principal (para cada CNJ)

Faça **em série**, um CNJ por vez. Paralelizar quebra o PJE: a sessão é stateful, o mesmo formulário é reutilizado, e abas simultâneas geram conflitos de `idProcessoSelecionado`.

### 1. Navegue direto para Consulta Processual

```
mcp__Claude_in_Chrome__navigate({
  tabId, url: "<PJE_BASE>/Processo/ConsultaProcesso/listView.seam"
})
```

Onde `<PJE_BASE>` é a URL base resolvida na seção "Determinar a URL base do PJE" (ex.: `https://pje.tjce.jus.br/pje1grau`). Essa URL evita clicar no menu lateral e cai direto no formulário. Não há iframe nessa página — `document.querySelector` no topo enxerga tudo.

Se algum tribunal expôr a Consulta Processual em caminho diferente (raro, mas possível em deploys customizados), o path `/Processo/ConsultaProcesso/listView.seam` pode não existir. Sintoma é 404 ou redirecionamento pro painel. Quando isso acontecer, pare e peça ao usuário pra confirmar a URL da tela de consulta pública daquele tribunal.

### 2. Preencha os 6 campos do CNJ

Use o snippet `assets/preencher_cnj.js` (leia o arquivo e embuta o conteúdo dentro de `javascript_tool`). O snippet recebe as 6 partes do CNJ e faz `focus → select → clear → set value + dispatchEvent(input/change)` em cada campo. Isso é essencial porque **ramoJustica e respectivoTribunal vêm pré-preenchidos** com `8` e `06`; se você só fizer `type`, duplica.

Quebra do CNJ `NNNNNNN-DD.AAAA.J.TR.OOOO`:

| Campo JSF                                            | Fonte do valor         |
|------------------------------------------------------|------------------------|
| `fPP:numeroProcesso:numeroSequencial`                | 7 dígitos iniciais     |
| `fPP:numeroProcesso:numeroDigitoVerificador`         | 2 dígitos após o `-`   |
| `fPP:numeroProcesso:Ano`                             | 4 dígitos              |
| `fPP:numeroProcesso:ramoJustica`                     | sempre `8`             |
| `fPP:numeroProcesso:respectivoTribunal`              | sempre `06`            |
| `fPP:numeroProcesso:NumeroOrgaoJustica`              | 4 dígitos finais       |

### 3. Dispare a pesquisa e aguarde o AJAX

```js
document.getElementById('fPP:searchProcessos').click();
```

A tabela é atualizada via RichFaces AJAX. Aguarde **pelo menos 3 segundos** antes de inspecionar o resultado.

**Armadilha crítica:** a tabela de resultados tem ID `fPP:processosTable`, **não** `processosTable`. O namespace JSF do form (`<h:form id="fPP">`) prefixa todos os IDs internos. Use `document.getElementById('fPP:processosTable')` — `document.querySelector('#processosTable')` retorna `null` e induz ao erro de achar que a pesquisa falhou.

Se a tabela não existir ou estiver vazia, o processo não foi encontrado nessa instância do PJE. Reporte "CNJ não localizado no `<PJE_BASE>`" (trocando `<PJE_BASE>` pela URL real) e passe pro próximo CNJ da lista (não tente fallback — foi decisão de design). Antes de desistir, confirme que o par `ramo.tribunal` do CNJ bate com a instância: um `.8.06.` (TJCE) em `pje.tjrn.jus.br` nunca vai aparecer, mesmo que a sessão esteja logada.

### 4. Clique no link do processo

Dentro de `#fPP:processosTable`, localize `a[title="<CNJ>"]` (o title é o próprio número do processo) e clique. O PJE abre uma **nova aba** em `listAutosDigitais.seam?idProcesso=<ID>&ca=...`. Descubra o tabId dessa aba via `tabs_context_mcp`.

### 5. Na aba dos autos: acione o download

Dois cliques em sequência, ambos na nova aba:

1. `a[title="Download autos do processo"]` — dispara a geração no backend. Não abre modal visível; injeta um `<iframe id="frameHtml">` apontando pra `/seam/resource/rest/pje-legacy/documento/download/<docId>`.
2. `input[value="Download"]` — é o confirm. **Não procure por ID fixo** — o ID é JSF-gerado (`navbar:j_idXXX`) e muda entre deploys. O seletor estável é pelo `value`.

### 6. Capture a URL assinada do MinIO / S3

Após o segundo clique, o PJE abre uma **terceira aba** num domínio externo de storage S3-compatible. O nome do host varia por tribunal, mas o padrão é o mesmo: um MinIO ou S3 assinado com params AWS (`X-Amz-Algorithm`, `X-Amz-Expires=120`, `X-Amz-Signature`, etc.). Exemplos:

- TJCE: `minio-pjedocs.tjce.jus.br/...`
- TJRN: `minio.pjernirn.jus.br/...` (ou similar)
- TRF1: `s3-pje.trf1.jus.br/...`

Polling recomendado: chame `tabs_context_mcp` em loop a cada 5 segundos, até 180s (3 min), procurando uma aba nova cuja URL contenha `X-Amz-Signature=` (assinatura AWS) — esse é o marcador estável, independente do host. Processos pequenos aparecem em 5–10s; processos gigantes podem demorar.

**Não use `javascript_tool` para ler `window.location.href` na aba de storage** — a URL contém dados de query string que o tool bloqueia por segurança. Pegue a URL direto do retorno do `tabs_context_mcp` (campo `url`).

### 7. Baixe imediatamente com curl

Você tem **120 segundos** a partir do timestamp em `X-Amz-Date` antes da assinatura expirar. Use Bash:

```bash
curl -sS -o "/sessions/<session-id>/mnt/<workspace>/<CNJ>.pdf" "<URL_MINIO_COMPLETA>" \
  -w "HTTP:%{http_code} SIZE:%{size_download} TIME:%{time_total}s\n"
```

Onde:
- `<workspace>` é a pasta que o usuário selecionou no Cowork (o caminho exato aparece no system prompt em "WORKSPACE FOLDER").
- `<CNJ>.pdf` — use o próprio número como nome. Fica fácil de achar depois.

Valide o download: `HTTP` deve ser `200`, `SIZE` deve ser > 0, e `file <arquivo>` deve retornar `PDF document`. Se der errado (403, 0 bytes, HTML de erro), a URL pode ter expirado — refaça o passo 5 pra gerar URL nova.

### 8. Feche a aba de storage (opcional)

Boa prática pra não poluir o navegador do usuário. Use `tabs_close_mcp` na aba do MinIO/S3 (aquela capturada no passo 6).

## Entrega ao usuário

Depois de processar todos os CNJs, responda na conversa com:

1. Uma linha de resumo: quantos baixou, quantos falharam.
2. Para cada PDF baixado, um link `computer://` para ele (padrão Cowork). Exemplo:
   ```
   [Autos 3000029-27.2023.8.06.0203](computer:///sessions/.../mnt/.../3000029-27.2023.8.06.0203.pdf)
   ```
3. Para cada falha, uma linha curta com o CNJ e o motivo (não encontrado, URL expirou, etc.).

Não escreva parecer, resumo ou análise dos autos. Essa skill **só baixa**. Se o usuário quiser análise, ele encadeia depois com `pre-audiencia-criminal`, `tecjustica-mcp-lite` ou outra skill.

## Em caso de falha

Veja `references/recovery.md` para diagnóstico passo a passo. Em resumo:

- **Não está logado** → pare e peça login manual, não automatize.
- **Tabela vazia** → CNJ não está na instância PJE atual (pode ser 2º grau, segredo de justiça, tribunal diferente, ou dígito errado — confira o par `ramo.tribunal` do CNJ).
- **404 na URL de Consulta** → o tribunal pode usar path diferente; pergunte ao usuário a URL correta.
- **URL de storage não aparece em 3 min** → provavelmente o clique 2 não foi registrado; refaça a partir do passo 5.
- **curl retorna 403** → URL assinada expirou; gere nova assinatura refazendo o passo 5.
- **PDF com 0 bytes ou HTML** → o servidor devolveu erro; olhe o body da resposta.

## Para detalhes de IDs e seletores

Veja `references/seletores.md`. Traz a tabela completa de IDs JSF, comportamentos observados em produção e armadilhas que não estão no fluxo principal.
