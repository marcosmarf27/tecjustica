# Seletores e armadilhas do PJE (Consulta Processual)

Referência completa dos IDs JSF, seletores estáveis e comportamentos observados em produção. Consulte quando algo no fluxo principal não casar com o que você está vendo.

O conteúdo deste arquivo foi levantado em produção no **TJCE** mas descreve o DOM do PJE unificado (CNJ), que é compartilhado entre tribunais (TJs estaduais, TRFs, TRTs). Os IDs JSF (`fPP:*`) e seletores (`input[value="Download"]`) são os mesmos em qualquer instalação — só a URL base muda.

## URL de entrada

```
<PJE_BASE>/Processo/ConsultaProcesso/listView.seam
```

Onde `<PJE_BASE>` é a URL base do tribunal escolhido (ex.: `https://pje.tjce.jus.br/pje1grau`, `https://pje1g.trf1.jus.br/pje`, `https://pje.tjrn.jus.br/pje1grau`).

Essa é a página da Consulta Processual. Não há `iframe#ngFrame` nela — o DOM do topo é o DOM real. Isso é **diferente** do painel do usuário (`/ng2/dev.seam`), que roda Angular dentro de iframe e exige `page.frameLocator('#ngFrame')` em ferramentas tipo Playwright.

Se você vir um `iframe#ngFrame` nessa tela, você foi redirecionado por engano — volte pra URL canônica.

## Os 6 campos do CNJ

Formulário JSF `<h:form id="fPP">`. Todos os IDs têm o prefixo `fPP:`.

| Campo                    | ID completo                                      | Tipo   | Pré-preenchido? | maxlength |
|--------------------------|--------------------------------------------------|--------|-----------------|-----------|
| Sequencial               | `fPP:numeroProcesso:numeroSequencial`            | text   | não             | 7         |
| Dígito verificador       | `fPP:numeroProcesso:numeroDigitoVerificador`     | text   | não             | 2         |
| Ano                      | `fPP:numeroProcesso:Ano`                         | text   | não             | 4         |
| Ramo da Justiça          | `fPP:numeroProcesso:ramoJustica`                 | text   | **sim** (valor = ramo do tribunal, ex: `8` no TJCE, `4` no TRF1, `5` no TRT)  | 1 |
| Tribunal                 | `fPP:numeroProcesso:respectivoTribunal`          | text   | **sim** (valor = código do tribunal, ex: `06` no TJCE, `01` no TRF1) | 2 |
| Órgão de Justiça         | `fPP:numeroProcesso:NumeroOrgaoJustica`          | text   | não             | 4         |

### Armadilha #1 — pré-preenchidos duplicam

Simplesmente chamar `element.value = "8"` num campo que já tem `"8"` não duplica nada. O problema é `type("8")` via automação de input simulado: muitas ferramentas (Playwright, browser-use) interpretam `type` como "append keystrokes", concatenando com o que já existe.

Regra: **sempre `focus → select → clear → set value`**, não importa o método. O snippet `assets/preencher_cnj.js` faz isso corretamente.

## Submit da pesquisa

```
#fPP:searchProcessos          (input type=button)
```

Após `click()`, aguarde **≥3 segundos** antes de inspecionar a tabela — o RichFaces dispara um AJAX Submit (`A4J.AJAX.Submit`) que repopula o painel.

Botão de limpar (não usado no fluxo padrão): `#fPP:clearButtonProcessos`.

## Tabela de resultados

### Armadilha #2 — o ID não é `processosTable`

O ID correto é `fPP:processosTable` (com o prefixo do form). Isso quebra várias documentações antigas e prompts de automação que mandam procurar `#processosTable`. Sempre:

```js
document.getElementById('fPP:processosTable')
// ou, com escape de dois-pontos no seletor CSS:
document.querySelector('#fPP\\:processosTable')
```

### Link do processo

Cada linha tem um link com o número do processo. O seletor estável é pelo `title`:

```js
document.querySelector('#fPP\\:processosTable a[title="<CNJ>"]')
```

O `href` é `#` e o clique dispara um `A4J.AJAX.Submit` com parâmetros tipo `idProcessoSelecionado=<numero>`. O servidor responde abrindo uma nova aba na URL:

```
/pje1grau/Processo/ConsultaProcesso/Detalhe/listAutosDigitais.seam?idProcesso=<ID>&ca=<token>&aba=
```

O `<ID>` interno é diferente do CNJ — é um inteiro curto tipo `1526285`. O `<token>` é um hash de autorização por sessão.

## Aba dos autos

### Botão "Download autos do processo"

```
a[title="Download autos do processo"]
```

É um `<a>` com ícone de download. O clique não abre modal — injeta um `<iframe id="frameHtml">` apontando pra `/seam/resource/rest/pje-legacy/documento/download/<docId>` que, em background, aciona a compilação do PDF completo.

### Botão "Download" (confirm)

```
input[value="Download"]
```

ID dinâmico observado: `navbar:j_id213` (pode variar — `j_idXXX` é gerado pelo JSF em cada deploy). **Nunca** dependa do ID. Use `input[value="Download"]` filtrado pela toolbar.

Alternativa robusta:

```js
Array.from(document.querySelectorAll('input[type="button"], input[type="submit"]'))
  .filter(b => (b.value || '').trim() === 'Download')[0]
  ?.click();
```

## A aba do storage (MinIO / S3)

Após o clique de confirm, o PJE abre uma nova aba num storage S3-compatible. O host varia por tribunal, mas a assinatura é AWS padrão:

```
<STORAGE_HOST>/<bucket>/<CNJ>-<epoch>-<id>-processo.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...&X-Amz-Date=...&X-Amz-Expires=120&X-Amz-SignedHeaders=host&X-Amz-Signature=...
```

Hosts observados:
- TJCE: `minio-pjedocs.tjce.jus.br`
- Outros tribunais: nomes similares (`minio.<trib>.jus.br`, `s3-pje.<trib>.jus.br`, `pje-docs.<trib>.jus.br`). Não memorize o domínio — **detecte pela presença do query param `X-Amz-Signature=`**, que é o marcador estável em qualquer MinIO/S3 assinado.

### Detalhes importantes

- **`X-Amz-Expires=120`** é literalmente 120 segundos. Marcado a partir de `X-Amz-Date` (o timestamp na própria URL). Depois disso, GET retorna `403 SignatureDoesNotMatch`.
- **`window.location.href` via `javascript_tool`** vem bloqueado como "Cookie/query string data" por segurança do MCP. Use o campo `url` do retorno de `tabs_context_mcp` — ele expõe a URL completa.
- **Título da aba** é do tipo `"PROCESSO: <CNJ> - <CLASSE JUDICIAL>"`. Pode ser usado como sanity check de que a aba certa foi identificada.
- O storage é interno do tribunal, não responde a `OPTIONS`, não aceita range requests em chunks, e não tem fallback público. Sempre baixar com `curl -sS -o` direto.

## Login / sessão

A skill assume sessão logada. Indicadores de que o usuário está logado:

- Presença de `a[href]` com texto ou title `"Abrir menu"` no header da aplicação.
- Botão de usuário visível (ex.: `<button>marcos fonseca</button>`).
- URL `/painel-usuario-interno` acessível sem redirecionamento pro Keycloak.

Indicadores de que **não** está logado:

- Redirecionamento para um host `auth.<trib>.jus.br` ou tela do Keycloak (`#kc-login`).
- Tela com o card "Processo Judicial Eletrônico" e botões "Certificado Digital" / "CPF/Senha".

Se não estiver logado, a skill **não** tenta logar. Avise o usuário e pare. Login automatizado precisa de credenciais que não temos e o PJE tem MFA/captcha em alguns cenários.

## Cookies que precisam estar ativos

Se um dia for preciso transportar a sessão para outra ferramenta (curl, Playwright headless), estes cookies devem ser copiados:

- `JSESSIONID` do domínio do PJE (`pje.<trib>.jus.br`)
- Cookies do Keycloak do domínio de auth do tribunal (`auth.<trib>.jus.br` — `KEYCLOAK_SESSION`, `KC_RESTART`, `AUTH_SESSION_ID`)
- Cookie `Pje-Simultaneidade` do PJE (controla bloqueio de sessão duplicada)

Na extensão Claude in Chrome isso não é um problema — você usa a aba onde o usuário já está logado.

## Tempos de referência (medidos)

| Operação                                      | Tempo típico    | Tempo máximo observado |
|-----------------------------------------------|-----------------|------------------------|
| Navegação → tela Consulta carregada           | 1–2s            | 5s                     |
| Submit AJAX → tabela atualizada               | 2–3s            | 8s                     |
| Clique no processo → aba autos aberta         | 1–2s            | 4s                     |
| Clique Download → clique Confirm              | 1s              | 2s                     |
| Geração PDF no servidor (processo pequeno)    | 5–10s           | 30s                    |
| Geração PDF no servidor (processo grande)     | 60–120s         | 180s+ (300+ páginas)   |
| Download via curl (2–3 MB)                    | 1–2s            | 10s                    |

Use esses números como guia para polling e timeouts. Polling da aba de storage: 5s de intervalo, 180s de teto total.
