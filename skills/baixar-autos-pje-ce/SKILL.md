---
name: baixar-autos-pje-ce
description: Baixa os autos completos em PDF de um ou mais processos do PJE 1º grau do TJCE (Tribunal de Justiça do Ceará) usando a extensão Claude in Chrome. Dispare SEMPRE que o usuário servidor/advogado/magistrado pedir para "baixar os autos", "pegar o PDF do processo", "puxar os autos", "baixa esse CNJ pra mim", "salva o processo em PDF", ou simplesmente mandar um número CNJ no formato NNNNNNN-DD.AAAA.8.06.NNNN (ramo=8 Justiça Estadual, tribunal=06 TJCE) sozinho ou em lista. Usa o caminho "Consulta Processual" do PJE (pje.tjce.jus.br/pje1grau) — preenche os 6 campos do CNJ, aciona a geração do PDF consolidado no servidor e salva o arquivo no workspace folder da sessão Cowork. Requer sessão ativa logada no PJE na aba do Chrome controlada pela extensão Claude. NÃO use para processos do TJCE 2º grau (pje2grau), outros tribunais, ou quando o usuário só quer ler movimentos/documentos isolados — para isso existe a skill tecjustica-mcp-lite.
---

# Baixar autos do PJE-CE (1º grau) via Claude in Chrome

Você está atuando como operador do PJE-CE. A tarefa é pegar o PDF consolidado dos autos de um ou mais processos e entregar pro Marcos no workspace folder. O caminho é a **Consulta Processual** do PJE — ele funciona pra qualquer processo público e tem IDs JSF estáveis, ao contrário do caminho via Tarefas.

Esse fluxo foi medido em ~15 segundos end-to-end pra processos pequenos (2–3 MB). Processos grandes (300+ páginas) podem levar até 3 minutos na etapa de geração do PDF — tenha paciência no polling.

## Pré-requisitos de ambiente

Antes de começar, confirme que:

1. **Claude in Chrome está disponível.** Você vai usar `mcp__Claude_in_Chrome__*` (navigate, javascript_tool, tabs_context_mcp, find). Se não tem essas ferramentas, a skill não é aplicável — avise o usuário que precisa da extensão.
2. **Há uma aba Chrome controlável.** Chame `tabs_context_mcp({ createIfEmpty: true })` e capture o `tabId` da aba ativa.
3. **Sessão PJE está logada.** Navegue para `https://pje.tjce.jus.br/` e confirme pela **presença** de "Abrir menu" ou "Quadro de avisos" (use `find` com essa query). Nunca confirme pela ausência de `#username` — carregamentos intermediários dão falso positivo. Se não estiver logado, pare e peça pro usuário fazer login manualmente na aba controlada (a skill não lida com credenciais).

## Inputs que você recebe

O usuário manda um ou mais números CNJ no formato `NNNNNNN-DD.AAAA.8.06.NNNN`. Exemplos válidos:
- Um só: `3000029-27.2023.8.06.0203`
- Em lista: `0123456-12.2024.8.06.0001, 9876543-21.2023.8.06.0145`
- Numa frase: "baixa os autos desse aí 3000029-27.2023.8.06.0203"

Extraia os CNJs do input com o regex `\d{7}-\d{2}\.\d{4}\.8\.06\.\d{4}`. Se algum número não bater no ramo `8` e tribunal `06`, avise que a skill só suporta TJCE e pergunte se é pra seguir só com os compatíveis.

## Fluxo principal (para cada CNJ)

Faça **em série**, um CNJ por vez. Paralelizar quebra o PJE: a sessão é stateful, o mesmo formulário é reutilizado, e abas simultâneas geram conflitos de `idProcessoSelecionado`.

### 1. Navegue direto para Consulta Processual

```
mcp__Claude_in_Chrome__navigate({
  tabId, url: "https://pje.tjce.jus.br/pje1grau/Processo/ConsultaProcesso/listView.seam"
})
```

Essa URL evita clicar no menu lateral e cai direto no formulário. Não há iframe nessa página — `document.querySelector` no topo enxerga tudo.

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

Se a tabela não existir ou estiver vazia, o processo não foi encontrado nessa base. Reporte "CNJ não localizado no PJE-CE 1º grau" e passe pro próximo CNJ da lista (não tente fallback — foi decisão de design).

### 4. Clique no link do processo

Dentro de `#fPP:processosTable`, localize `a[title="<CNJ>"]` (o title é o próprio número do processo) e clique. O PJE abre uma **nova aba** em `listAutosDigitais.seam?idProcesso=<ID>&ca=...`. Descubra o tabId dessa aba via `tabs_context_mcp`.

### 5. Na aba dos autos: acione o download

Dois cliques em sequência, ambos na nova aba:

1. `a[title="Download autos do processo"]` — dispara a geração no backend. Não abre modal visível; injeta um `<iframe id="frameHtml">` apontando pra `/seam/resource/rest/pje-legacy/documento/download/<docId>`.
2. `input[value="Download"]` — é o confirm. **Não procure por ID fixo** — o ID é JSF-gerado (`navbar:j_idXXX`) e muda entre deploys. O seletor estável é pelo `value`.

### 6. Capture a URL assinada do MinIO

Após o segundo clique, o PJE abre uma **terceira aba** num domínio externo: `minio-pjedocs.tjce.jus.br/...?X-Amz-Algorithm=...&X-Amz-Expires=120&X-Amz-Signature=...`.

Polling recomendado: chame `tabs_context_mcp` em loop a cada 5 segundos, até 180s (3 min), procurando uma aba com `url` começando em `https://minio-pjedocs.tjce.jus.br/`. Processos pequenos aparecem em 5–10s; processos gigantes podem demorar.

**Não use `javascript_tool` para ler `window.location.href` na aba do MinIO** — a URL contém dados de query string que o tool bloqueia por segurança. Pegue a URL direto do retorno do `tabs_context_mcp` (campo `url`).

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

### 8. Feche a aba do MinIO (opcional)

Boa prática pra não poluir o navegador do usuário. Use `tabs_close_mcp` na aba `minio-pjedocs.tjce.jus.br`.

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
- **Tabela vazia** → CNJ não está no PJE-CE 1º grau público (pode ser 2º grau, segredo de justiça, outro tribunal, ou dígito errado).
- **URL do MinIO não aparece em 3 min** → provavelmente o clique 2 não foi registrado; refaça a partir do passo 5.
- **curl retorna 403** → URL expirou; gere nova assinatura refazendo o passo 5.
- **PDF com 0 bytes ou HTML** → o servidor devolveu erro; olhe o body da resposta.

## Para detalhes de IDs e seletores

Veja `references/seletores.md`. Traz a tabela completa de IDs JSF, comportamentos observados em produção e armadilhas que não estão no fluxo principal.
