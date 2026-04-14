# Licenciamento Comercial — Plugin TecJustica

Este plugin e distribuido sob a [PolyForm Noncommercial License 1.0.0](./LICENSE).
Uso nao-comercial e **gratuito e irrestrito**. Uso comercial requer **licenca
paga** negociada diretamente com a TecJustica.

Este documento esclarece o que conta como cada caso e como obter a licenca
comercial.

---

## Uso nao-comercial — gratuito

Voce pode instalar, usar, modificar e redistribuir o plugin **sem pagar nada
e sem pedir autorizacao** se o uso se enquadrar em qualquer um dos casos
abaixo:

### Pessoa fisica

- **Magistrados, servidores publicos e assessores** usando o plugin no
  exercicio da funcao publica (TJ estadual, TRF, STJ, STF, MP, Defensoria,
  AGU, procuradorias). A licenca PolyForm NC considera explicitamente
  "government institution" como uso nao-comercial permitido, independente
  da fonte de financiamento.
- **Estudantes e pesquisadores** usando em monografias, dissertacoes, teses,
  artigos cientificos ou projetos academicos.
- **Uso pessoal** para estudo, experimentacao, teste ou hobby, sem aplicacao
  comercial prevista.

### Organizacoes

- **Universidades publicas e privadas sem fins lucrativos**, para ensino e
  pesquisa.
- **Orgaos publicos** de qualquer esfera (federal, estadual, municipal).
- **ONGs, associacoes e instituicoes de caridade** sem fins lucrativos.
- **Organizacoes de saude e seguranca publica**.

Se o seu caso se encaixa em qualquer um acima, voce **nao precisa fazer
nada** alem de seguir a licenca PolyForm NC (mantere o aviso de copyright
ao redistribuir, nao remover atribuicoes, etc.).

---

## Uso comercial — requer licenca paga

Voce precisa de uma **licenca comercial** da TecJustica se voce ou sua
organizacao se encaixar em qualquer um dos casos abaixo:

- **Escritorios de advocacia** (de qualquer porte) usando o plugin para
  atender clientes pagantes.
- **Departamentos juridicos de empresas privadas** com fins lucrativos.
- **Legaltechs, startups juridicas e SaaS** que embutam, redistribuam,
  hospedem ou ofertem o plugin (ou qualquer skill dele) como parte de um
  produto ou servico pago.
- **Consultorias juridicas e empresas de assessoria** que cobram clientes
  por servicos baseados no plugin.
- **Integracoes comerciais** em produtos de terceiros (ERPs juridicos,
  plataformas de automacao processual, etc.).
- Qualquer outro uso com **intuito de vantagem comercial ou compensacao
  monetaria** direta ou indireta.

### O que a licenca comercial inclui

- Direito de uso em ambiente comercial sem restricoes de numero de usuarios
  dentro da organizacao contratante.
- Suporte tecnico direto (canal dedicado, SLA a combinar).
- Atualizacoes e correcoes prioritarias.
- Possibilidade de customizacao de skills para o fluxo do escritorio.
- Contrato de licenciamento formal com clausulas de indenizacao e garantia
  compativeis com contratacoes corporativas.

### Como contratar

Entre em contato pelos canais abaixo informando: nome da organizacao, numero
aproximado de usuarios, tipo de uso pretendido e prazo desejado.

- **E-mail:** contato@tecjustica.com.br
- **Site:** https://tecjusticamcp-lite-production.up.railway.app/
- **GitHub:** abra uma issue privada em https://github.com/marcosmarf27/tecjustica

A TecJustica retorna em ate 3 dias uteis com proposta comercial.

---

## Casos duvidosos

Se voce nao tem certeza se seu uso e comercial ou nao, **pergunte antes de
usar em producao**. Abra uma issue publica no repositorio descrevendo o
cenario (sem dados sensiveis) ou envie e-mail para contato@tecjustica.com.br.
A resposta em casos duvidosos costuma ser gratuita e rapida, e evita
discussao depois.

Alguns exemplos comuns:

| Cenario | Classificacao |
|---------|---------------|
| Juiz usando no gabinete para elaborar despachos | Nao-comercial (governo) |
| Assessor de desembargador analisando processos do TJ | Nao-comercial (governo) |
| Advogado autonomo usando para atender clientes pagantes | **Comercial** |
| Mestrando usando para pesquisa academica | Nao-comercial (pesquisa) |
| Escritorio boutique de 3 advogados | **Comercial** |
| Defensoria Publica Estadual | Nao-comercial (governo) |
| Startup embutindo em um SaaS juridico | **Comercial** |
| Professor usando em disciplina de Direito Digital | Nao-comercial (ensino) |
| Procurador do Municipio | Nao-comercial (governo) |

---

## Compatibilidade com servicos da TecJustica

Esta licenca cobre **o codigo do plugin** (skills, scripts, manifestos).
Os servicos de backend consumidos pelo plugin — **MCP TecJustica Lite** e
**TecJustica Parse** — sao servicos hospedados com seus proprios termos de
uso, disponiveis em:

- https://tecjusticamcp-lite-production.up.railway.app/termos
- https://tecjustica-dashboard-production.up.railway.app/termos

As chaves de API (`mcp_...` e `tjp_...`) tem seus proprios planos e limites
de uso, definidos pelos respectivos portais.
