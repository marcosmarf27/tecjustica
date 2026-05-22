# pje-baixar — referência completa

Detalhes que não cabem no fluxo principal do `SKILL.md`. Nos exemplos, `"$PJE_BAIXAR"`
é o caminho para o binário embutido escolhido no Passo 1 do `SKILL.md`.

## Binários embutidos

A pasta `bin/` desta skill traz um binário por plataforma:

| Arquivo | Sistema |
|---|---|
| `pje-baixar-linux-amd64` | Linux x86-64 |
| `pje-baixar-linux-arm64` | Linux ARM64 |
| `pje-baixar-darwin-amd64` | macOS Intel |
| `pje-baixar-darwin-arm64` | macOS Apple Silicon |
| `pje-baixar-windows-amd64.exe` | Windows x86-64 |

Todos são da versão 1.0.0. Em Linux/macOS, dê `chmod +x` no binário antes de
executá-lo (o bit de execução pode se perder ao clonar o repositório).

## Subcomandos

| Comando | O que faz |
|---|---|
| `pje-baixar <numero>` | Baixa todos os documentos do processo |
| `pje-baixar config` | Configura CPF/senha de forma interativa (exige terminal) |
| `pje-baixar config --mostrar` | Mostra a configuração salva (senha mascarada) |
| `pje-baixar version` | Mostra a versão instalada |
| `pje-baixar help` | Exibe a ajuda |

## Flags do download

| Flag | Padrão | Descrição |
|---|---|---|
| `-out DIR` | `.` | Diretório base; a pasta `<numero>/` é criada dentro dele |
| `-ordem MODO` | `id` | Ordem dos arquivos no nome (`NNN_...`) |

A flag e o número do processo podem vir em qualquer ordem — tanto
`pje-baixar -ordem data <num>` quanto `pje-baixar <num> -ordem data` funcionam.

### Modos de `-ordem`

- `id` — crescente por `idDocumento`. A Petição Inicial costuma ser o menor id, então
  fica em `001`. É a ordem cronológica de juntada e o padrão recomendado.
- `data` — por data/hora do documento.
- `xml` — ordem original devolvida pelo MNI (mais recente primeiro).

A ordem afeta apenas o prefixo numérico `NNN_` do nome do arquivo; todos os
documentos são baixados em qualquer modo.

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `PJE_CPF` | — | CPF/CNPJ do consultante no PJe |
| `PJE_SENHA` | — | Senha do PJe |
| `PJE_MNI_URL` | TJCE 1º grau | Endpoint MNI do tribunal |
| `PJE_CONCURRENCY` | `4` | Downloads em paralelo |
| `PJE_TIMEOUT` | `120` | Timeout por requisição, em segundos |
| `PJE_INSECURE` | — | `1` para não verificar o certificado TLS do servidor |

As variáveis de ambiente têm **prioridade** sobre o arquivo de configuração. Defina
`PJE_CPF`/`PJE_SENHA` quando precisar rodar a CLI em um contexto não-interativo (como
o Claude executando via shell), já que `pje-baixar config` exige um terminal.

## Usar com outros tribunais

Por padrão a CLI consulta o TJCE 1º grau
(`https://pjews.tjce.jus.br/pje1grau/intercomunicacao`). Para outro tribunal, aponte
`PJE_MNI_URL` para o endpoint MNI correspondente:

```bash
export PJE_MNI_URL=https://pje.tjxx.jus.br/pje1grau/intercomunicacao
"$PJE_BAIXAR" 0000000-00.0000.0.00.0000
```

O sufixo `?wsdl` na URL, se presente, é removido automaticamente. Só o TJCE foi
testado de fato; outros tribunais que implementam o MNI 2.2.2 podem funcionar, mas
não há garantia.

## Arquivo de configuração

Criado por `pje-baixar config`, fica em:

- Linux/macOS: `~/.config/pje-baixar/config.json`
- Windows: `%AppData%\pje-baixar\config.json`

Permissão `0600` (só o usuário lê). A senha é guardada **codificada em base64** —
isso **não é criptografia**, apenas evita texto puro. Em máquinas compartilhadas,
prefira as variáveis de ambiente.

## Códigos de saída

| Código | Significado |
|---|---|
| `0` | Sucesso — todos os documentos baixados |
| `1` | Erro fatal. Inclui o caso de **falhas parciais**: alguns documentos não baixaram |
| `2` | Erro de uso (argumento faltando, flag inválida) |

Falhas em documentos individuais **não interrompem** os demais — a CLI tenta todos e,
no fim, lista quais falharam no resumo. Se houver qualquer falha, o código de saída é
`1`, mas os documentos que baixaram já estão gravados na pasta. Vale reinspecionar a
pasta antes de concluir que o download "falhou": normalmente a maioria das peças está
lá.

## Erros comuns

- **`credenciais do PJe não configuradas`** — nenhuma credencial disponível em
  contexto não-interativo. Defina `PJE_CPF`/`PJE_SENHA` ou peça ao usuário para rodar
  `pje-baixar config` no terminal dele.
- **`pje-baixar config precisa de um terminal interativo`** — `config` foi chamado
  sem um TTY. Não dá para configurar credenciais por aqui; use as variáveis de
  ambiente.
- **`Permission denied` ao executar o binário** — falta o bit de execução; rode
  `chmod +x "$PJE_BAIXAR"`.
- **`Nenhum documento encontrado neste processo`** — o número é válido mas o processo
  não retornou documentos (sigiloso, sem acesso para esse CPF, ou inexistente naquele
  tribunal). Confira o número e se o CPF tem habilitação no processo.
- **Timeout / erro de TLS** — processos grandes podem estourar os 120s padrão; suba
  `PJE_TIMEOUT`. Erros de certificado em ambientes específicos podem ser contornados
  com `PJE_INSECURE=1` (use com cautela — desativa a verificação TLS).

## Origem do binário

A CLI `pje-baixar` é um projeto Go mantido no laboratório TecJustica PJe MNI Lab.
Os binários desta skill foram compilados da versão 1.0.0. Para atualizar, recompile
a CLI no projeto de origem e substitua os arquivos em `bin/`.
