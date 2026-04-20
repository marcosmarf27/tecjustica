# Recovery — o que fazer quando algo quebra

Este arquivo é para consulta em tempo de falha. Cada seção começa com o sintoma observado e traz a causa provável + o caminho de recuperação.

## Sintoma: "Redirecionado para tela de login"

A sessão expirou ou nunca existiu. A skill **não** tenta fazer login.

**Faça:**
1. Pare o fluxo. Não preencha credenciais na chat nem nos campos.
2. Avise o usuário: "A sessão do PJE não está ativa nessa aba. Faça login manualmente em `<PJE_BASE>` (a URL do tribunal escolhido — ex.: `https://pje.tjce.jus.br/`) e me avise quando puder."
3. Espere confirmação explícita. Quando ele voltar, reveja a pré-condição (presença de "Abrir menu") e retome do passo 1 do fluxo.

## Sintoma: "Tabela `fPP:processosTable` retornou 0 linhas"

O CNJ não existe na instância PJE atual (`<PJE_BASE>`). Causas prováveis, em ordem de frequência:

1. **Tribunal errado** — o par `ramo.tribunal` do CNJ (quarto e quinto grupos de dígitos) não bate com a instância. Ex.: CNJ `.8.06.` (TJCE) rodando em `pje.tjrn.jus.br`. Confira o mapeamento e, se preciso, resolva uma URL base diferente e refaça.
2. **Segredo de justiça sem permissão** — você consegue ver o processo se estiver como parte/advogado cadastrado, mas a consulta pública nega. Não há como contornar via Consulta Processual; seria necessário o caminho via Tarefas (não implementado por escolha de design).
3. **Processo do 2º grau** — se o processo está em fase recursal, pode estar em `pje2grau` ou equivalente daquele tribunal. Esta skill só cobre 1º grau.
4. **CNJ digitado errado** — especialmente o dígito verificador. Peça ao usuário pra conferir.
5. **Processo arquivado/migrado para sistema legacy** (raro).

**Faça:** reporte "Processo X não encontrado em `<PJE_BASE>`" e siga com os próximos CNJs da lista. Não tente fallback automático para outro tribunal — só se o usuário autorizar explicitamente.

## Sintoma: "Aba de storage (MinIO/S3) não apareceu em 3 minutos"

O clique no "Download" (confirm) não foi registrado, ou a geração do PDF travou no backend.

**Faça:**
1. Confirme que a aba dos autos ainda existe (`tabs_context_mcp`). Se o PJE te deslogou no meio do caminho, você precisa retomar.
2. Inspecione a aba dos autos procurando alertas: `document.querySelectorAll('.rich-messages-label, .alert')`. Às vezes o PJE mostra "Aguarde o processamento" ou "Erro ao gerar PDF".
3. Se não há mensagem de erro, tente refazer os passos 5–6: clique em "Download autos do processo" de novo e depois em "Download". Às vezes o primeiro disparo foi perdido.
4. Se 2ª tentativa também falhar em 3 min, reporte "Tempo esgotado gerando PDF do CNJ X" e siga.

## Sintoma: "curl retornou HTTP 403"

A URL assinada (MinIO/S3 do tribunal) expirou. Você demorou mais de 120s entre capturar a URL e chamar curl. Alternativa: a URL foi copiada errado (faltando um query param).

**Faça:**
1. Valide que a URL completa está presente (precisa ter `X-Amz-Signature` inteiro no final).
2. Se URL está íntegra e deu 403, ela expirou. Gere nova URL refazendo passos 5–7 do fluxo principal. O PDF não fica em cache — a cada clique em "Download" o servidor assina nova URL.
3. Se ficar alternando 403/200, é sinal de que você está demorando no meio do fluxo. Minimize passos entre a detecção da aba de storage e o `curl`: capture a URL e baixe imediatamente, só faça logging/verificação depois.

## Sintoma: "curl retornou HTTP 200 mas o arquivo tem 0 bytes"

Muito raro. Indica que o storage (MinIO/S3) aceitou a requisição mas o objeto tem tamanho zero — bug no servidor do tribunal.

**Faça:** refazer passos 5–7. Se repetir, avise ao usuário que tem algo estranho com esse processo específico e peça pra ele tentar baixar manualmente pra validar.

## Sintoma: "PDF abre mas dá erro de estrutura / 'não é um PDF válido'"

O `curl` pegou um HTML de erro do storage (MinIO/S3), não o PDF.

**Faça:**
1. Rode `file <arquivo>` pra confirmar. Se disser `HTML document` em vez de `PDF document`, é isso.
2. Leia o conteúdo: `head -c 500 <arquivo>`. Normalmente vai ter um `<Error><Code>AccessDenied</Code>...` ou similar do S3.
3. Trate como se fosse 403 (URL expirou ou inválida) — regenere.

## Sintoma: "Duas abas do mesmo PJE abertas, sessões conflitam"

O PJE tem controle de sessão única por usuário (cookie `Pje-Simultaneidade`). Se você abriu o PJE em duas abas em contextos diferentes, uma delas vai mostrar "Sessão expirada" ou redirecionar.

**Faça:** trabalhe só na aba que a extensão Claude in Chrome controla. Peça pro usuário fechar outras abas do PJE se houver conflito.

## Sintoma: "O `javascript_tool` retorna '[BLOCKED: Cookie/query string data]'"

Comportamento esperado do MCP para URLs com query string considerada sensível (assinaturas, tokens).

**Faça:**
- Para URL do storage (MinIO/S3): pegue do retorno do `tabs_context_mcp` (campo `url`). Não tente contornar com `location.search` ou `atob` — o bloqueio é intencional.
- Para valores de input: use `element.value` diretamente; esse caminho não é bloqueado.

## Sintoma: "Ação trava porque o JSF mostra um modal transparente de loading"

Durante submits AJAX, o RichFaces injeta um overlay quase invisível que bloqueia cliques por 1–3s. Se você clicar rápido demais, os eventos não são processados.

**Faça:** sempre **aguardar 3s após qualquer submit** antes do próximo clique. Isso já está embutido no fluxo do SKILL.md, mas se precisar reforçar: `new Promise(r => setTimeout(r, 3000))`.

## Sintoma: "O ID `navbar:j_id213` do botão Download mudou e ele não é encontrado"

Confirmação de que o ID dinâmico quebrou. Você deveria ter usado o seletor por `value`.

**Faça:** `input[value="Download"]` como seletor principal. Se ainda assim não achar, leia o DOM da toolbar e procure por texto "Download" case-insensitive — é a última rede de segurança.

## Quando todas as recuperações falham

Se você tentou 2 vezes cada passo e continua falhando, **pare**. Reporte pro usuário:

1. Qual CNJ falhou
2. Em qual passo do fluxo
3. O que você observou (última mensagem de erro, screenshot se possível via `computer` tool)

Não tente heroicamente inventar caminhos novos. A skill foi desenhada pra falhar explicitamente, não silenciosamente — um download que não aconteceu é menos ruim que um download de arquivo errado ou de outro processo.
