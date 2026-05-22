---
name: pje-baixar
description: >-
  Baixa todos os documentos de um processo do PJe para arquivos locais, documento
  por documento, via protocolo MNI/SOAP — usando a CLI Go pje-baixar embutida nesta
  skill (binários para Linux, macOS e Windows inclusos, não precisa instalar nada).
  Use sempre que o usuário pedir para baixar os autos, baixar os documentos ou PDFs
  de um processo, salvar um processo em disco, ou mencionar "pje-baixar". Dispara
  também quando o usuário manda um número CNJ (NNNNNNN-DD.AAAA.J.TR.OOOO) com a
  intenção de obter os arquivos localmente para depois ler, extrair texto ou montar
  um pipeline de análise dos autos. Diferente das skills de download por navegador
  (pje-download, baixar-autos-pje): aqui não há browser nem PDF consolidado — é
  consulta MNI direta ao tribunal, que devolve cada peça como arquivo separado, sem
  conta, API key ou créditos.
---

# pje-baixar — baixar autos do PJe via MNI

`pje-baixar` é uma CLI que baixa **todos os documentos** de um processo judicial do
PJe e os grava numa pasta local, numerados em ordem. Fala SOAP direto com o MNI
(Modelo Nacional de Interoperabilidade) — o canal oficial do CNJ — usando apenas as
credenciais do PJe do próprio usuário.

Os binários já vêm **embutidos nesta skill** (pasta `bin/`), para Linux, macOS e
Windows. Não há instalação: basta escolher o binário do sistema e executá-lo.

## Quando usar esta skill

Use quando o objetivo for **obter os arquivos do processo no disco**, como peças
separadas (PDF, HTML, RTF, imagens) prontas para um pipeline de leitura/extração:

- "baixa os autos de \<CNJ\>", "baixa esse processo", "pega os PDFs do processo X"
- "salva o processo em disco para eu analisar"
- "preciso dos documentos do processo para rodar uma análise/extração"
- o usuário menciona `pje-baixar` explicitamente

NÃO use esta skill quando:

- O usuário quer um **PDF consolidado** dos autos baixado pela interface web do PJe
  → use `pje-download` ou `baixar-autos-pje` (download por navegador).
- O usuário quer **ler/consultar/sumarizar** o processo via chat sem salvar arquivos
  → use o MCP do TecJustica.
- O alvo não é um processo do PJe identificado por número CNJ.

## Passo 1 — Escolher o binário embutido

Os binários estão na pasta `bin/` **dentro do diretório desta skill** — o caminho
da skill é informado no contexto de ativação ("Base directory for this skill").
Detecte o sistema operacional e a arquitetura, dê permissão de execução e guarde o
caminho numa variável:

```bash
SKILL_DIR="<diretório desta skill>"   # ajuste para o caminho real informado

case "$(uname -s)" in
  Linux)  OS=linux  ;;
  Darwin) OS=darwin ;;
  *)      OS=windows ;;
esac
case "$(uname -m)" in
  x86_64|amd64)  ARCH=amd64 ;;
  arm64|aarch64) ARCH=arm64 ;;
esac

if [ "$OS" = "windows" ]; then
  PJE_BAIXAR="$SKILL_DIR/bin/pje-baixar-windows-amd64.exe"
else
  PJE_BAIXAR="$SKILL_DIR/bin/pje-baixar-$OS-$ARCH"
  chmod +x "$PJE_BAIXAR"
fi

"$PJE_BAIXAR" version   # deve imprimir: pje-baixar 1.0.0
```

Em todos os comandos seguintes, use `"$PJE_BAIXAR"` no lugar de `pje-baixar`. No
Windows nativo (sem `uname`), use diretamente `bin\pje-baixar-windows-amd64.exe`.

## Passo 2 — Garantir as credenciais do PJe

A CLI precisa do CPF/CNPJ e senha do PJe do usuário. **Isto tem uma armadilha:**
quando você (Claude) roda a CLI por um shell, o stdin **não é um terminal
interativo**. O subcomando `config` e os prompts de senha exigem um terminal de
verdade — então **você não consegue configurar as credenciais sozinho**.

Há duas formas válidas de fornecer as credenciais, em ordem de precedência:

1. **Variáveis de ambiente** `PJE_CPF` e `PJE_SENHA` — funcionam em qualquer
   contexto, inclusive não-interativo.
2. **Arquivo de configuração** criado pelo usuário com `pje-baixar config` (rodado
   por ele, no terminal dele).

**Verifique as credenciais antes de tentar baixar:**

```bash
"$PJE_BAIXAR" config --mostrar
```

- Se imprimir um CPF e uma senha mascarada, há config salva — pode baixar.
- Se imprimir `Nenhuma configuração salva` **e** as variáveis `PJE_CPF`/`PJE_SENHA`
  não estiverem definidas, **pare** e peça ao usuário uma das opções:
  - exportar as variáveis antes de você rodar o comando:
    `export PJE_CPF=... PJE_SENHA=...`; ou
  - rodar, no terminal dele, `"$PJE_BAIXAR" config` (interativo, pede CPF e senha).

Nunca tente rodar `config` sem `--mostrar` você mesmo — ele aborta sem um TTY. Sem
credenciais, a CLI falha com `credenciais do PJe não configuradas`.

## Passo 3 — Baixar o processo

Com binário e credenciais prontos:

```bash
"$PJE_BAIXAR" 3000066-83.2025.8.06.0203
```

O número pode vir no formato CNJ pontuado (`NNNNNNN-DD.AAAA.J.TR.OOOO`) ou como 20
dígitos puros. A CLI:

1. consulta o processo e lista todos os documentos;
2. cria a pasta `3000066-83.2025.8.06.0203/` no diretório atual;
3. baixa cada documento em paralelo, gravando arquivos com o nome
   `NNN_<descrição>_<idDocumento>.<ext>` — a Petição Inicial fica em `001`.

O progresso vai para o stderr; ao final, um resumo com quantos baixaram, o tamanho
total e o caminho absoluto da pasta.

**Escolher onde salvar** — `-out` define o diretório base (a pasta `<numero>/` é
criada dentro dele):

```bash
"$PJE_BAIXAR" -out ./autos 3000066-83.2025.8.06.0203
# cria ./autos/3000066-83.2025.8.06.0203/
```

**Ordenação** — `-ordem` aceita `id` (padrão, Petição Inicial primeiro), `data` ou
`xml`. Mantenha o padrão `id` na maioria dos casos. A flag e o número podem vir em
qualquer ordem.

## Depois do download

A pasta resultante contém os arquivos brutos numerados — já é a entrada pronta para
o próximo passo do pipeline:

1. listar os arquivos da pasta para ver o que veio;
2. ler os de texto direto (HTML, RTF, TXT);
3. extrair texto dos PDFs (OCR, se forem digitalizados);
4. sumarizar/analisar conforme o pedido do usuário.

Cada nome de arquivo traz a descrição e o `idDocumento`, o que facilita localizar
peças específicas (petição inicial, sentença, despacho).

## Erros comuns e uso avançado

Para uso com **outros tribunais** (`PJE_MNI_URL`), a tabela completa de variáveis de
ambiente, os modos de `-ordem`, os códigos de saída e o tratamento de falhas
parciais de documentos, consulte `references/referencia.md`.
