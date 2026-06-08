---
name: tjocr
description: >-
  Extrai texto de PDFs (OCR) e devolve Markdown, usando a CLI `tjocr` da TecJustiça com o
  binário já EMBUTIDO para Windows e Linux/WSL — não precisa de Go, Python, curl nem
  compilar nada. Use esta skill SEMPRE que o usuário pedir para extrair texto de um PDF,
  fazer OCR, ler/processar um documento escaneado, converter PDF para texto ou markdown, ou
  analisar um documento jurídico em PDF (petição, certidão, matrícula de imóvel, processo,
  contrato, sentença), mesmo que ele não diga "OCR" explicitamente — por exemplo "lê esse
  PDF pra mim", "o que diz esse documento escaneado", "transforma esse processo em texto",
  "extrai o conteúdo dessa matrícula". Prefira esta skill quando o ambiente for Windows, ou
  quando quiser algo portável e sem dependências. O resultado em markdown alimenta direto a
  skill `tj-mapa` (mapa do processo). NÃO use para gerar o índice/mapa de um .md já extraído
  (isso é a `tj-mapa`) nem para transcrever áudio/vídeo (isso é `tecjustica-transcribe`).
---

# tjocr — OCR de PDF (texto → Markdown)

O `tjocr` recebe um **PDF** e devolve o texto em **Markdown** (uma seção `## Página N` por
página), via a API de OCR da TecJustiça. É o passo que antes era manual no dashboard
(login → upload → baixar o `.md`); aqui é um comando só.

Esta skill traz o binário pronto (não precisa de Go, Python nem compilar) e funciona em
**WSL/Linux** e **Windows**.

## Passo a passo

Nos comandos abaixo, **`SKILL_DIR` é um marcador: substitua-o pelo caminho real desta skill**
— o diretório onde está este `SKILL.md`, informado no cabeçalho "Base directory" quando a skill
abre (por exemplo `~/.claude/skills/tjocr`). Use o caminho real **em cada comando**; não dependa
de uma variável de shell, pois ela não persiste entre comandos executados separadamente.

O wrapper `scripts/tjocr.sh` detecta o sistema operacional e escolhe o binário certo em `bin/`
automaticamente.

### Opcional: deixar `tjocr` no PATH (uma vez por máquina)

Por conveniência, dá para instalar o `tjocr` no PATH do usuário e chamá-lo direto
(`tjocr documento.pdf`) em vez do wrapper. No primeiro uso, ofereça/rode:

```bash
command -v tjocr >/dev/null || bash "SKILL_DIR/scripts/tjocr.sh" install
```

O `install` é multiplataforma (um binário por SO, mesmo comando): no **WSL/Linux** copia para
`~/.local/bin/tjocr`; no **Windows** copia para `%LOCALAPPDATA%\Programs\tjocr\` e adiciona a
pasta ao PATH do usuário (no Windows, reabra o terminal depois — o PATH novo só vale em
terminais abertos a seguir). É **só conveniência**: a skill continua funcionando pelo wrapper
abaixo, que é o caminho oficial (usa sempre o binário embutido, sincronizado com a versão da
skill). Se atualizar a skill, rode `install` de novo para sincronizar o binário do PATH.

### 1. Garantir a credencial (uma vez por máquina)

O `tjocr` precisa de uma API key da TecJustiça (a chave é do usuário; nunca vem na skill).
Cheque o estado:

```bash
bash "SKILL_DIR/scripts/tjocr.sh" config show
```

Se a `api_key` aparecer como "(não configurada)", **peça a chave ao usuário** e salve-a
lendo do stdin (assim ela não fica no histórico do shell):

```bash
bash "SKILL_DIR/scripts/tjocr.sh" config set      # ele cola a chave e tecla Enter
```

A chave é gravada em config do usuário (`~/.config/tjocr/config.json` no Linux,
`%AppData%\tjocr\config.json` no Windows), com permissão restrita. Alternativas: a variável
de ambiente `TJOCR_API_KEY`, ou `--key` no comando. **Precedência:** `--key` > env
`TJOCR_API_KEY` > config salvo > env `TECJUSTICA_API_KEY` (legado).

Não invente nem peça a chave se ela já estiver configurada. Nunca imprima a chave. Se o
usuário não tiver uma, oriente-o a obtê-la no dashboard da TecJustiça.

### 2. Rodar o OCR

```bash
bash "SKILL_DIR/scripts/tjocr.sh" "/caminho/documento.pdf" -o /caminho/documento.md
```

- **Prefira caminhos absolutos** no PDF e no `-o` — é o mais seguro, sobretudo em automação:
  um `-o` relativo é resolvido a partir do diretório de trabalho atual, que pode variar entre
  comandos. (Se usar `-o` relativo, rode o comando já na pasta onde quer o `.md`.)
- O markdown vai para o arquivo de `-o` (ou para o **stdout** se você omitir `-o`). O
  progresso e o resumo vão para o **stderr** — então dá para usar em pipe sem sujar a saída.
- O resumo (stderr) traz `N texto + N OCR`: **texto** = páginas digitais lidas direto (sem OCR);
  **OCR** = páginas escaneadas processadas pelo OCR. Vem também a `qualidade média` (0–100) e um
  aviso quando há páginas de baixa qualidade.
- O primeiro PDF pode demorar alguns segundos (a GPU "esquenta"); PDFs já processados antes
  voltam instantâneos (cache). A skill cuida disso sozinha (cache hit vs processamento
  assíncrono).
- Opções úteis: `--pages 1-5,10` (só algumas páginas), `--dpi 72` (mais rápido/barato),
  `--enhance` (corrige o OCR com IA — mais lento e pode reescrever; use quando a fidelidade
  de números/nomes importa e o documento está degradado). Lista completa em
  `references/opcoes.md`.

### 3. Usar o resultado

Leia o `.md` gerado e responda à pergunta do usuário a partir dele. Se o objetivo for gerar
o **mapa/índice** do processo, passe esse `.md` para a skill `tj-mapa`:

```bash
# fluxo completo: PDF -> markdown (tjocr) -> mapa (tj-mapa)
bash "SKILL_DIR/scripts/tjocr.sh" "processo.pdf" -o processo.md
# depois: tj-mapa processo.md
```

## Qualidade do OCR

O resumo (no stderr) mostra a qualidade média e avisa se houver páginas de baixa qualidade
("⚠ N página(s) com qualidade baixa — revisar"). Documentos datilografados antigos, com
marca d'água ou muito degradados podem sair com erros de transcrição ou layout embaralhado;
nesses casos, `--enhance` costuma recuperar a legibilidade (com a ressalva de que a IA pode
reescrever).

## Windows sem Bash (PowerShell/cmd puro)

O wrapper `tjocr.sh` é Bash — funciona no WSL, no Linux, no macOS e no **Git Bash** do Windows.
Se o ambiente for **PowerShell/cmd sem Bash**, **não precisa de wrapper nem de um `.ps1`**: como
no Windows só existe um binário (`tjocr_windows_amd64.exe`), não há o que "escolher" — chame o
`.exe` direto pelo caminho. Ele tem toda a lógica embutida (inclusive o `install`). Chamar o
`.exe` é melhor que um script `.ps1`, que seria bloqueado pela ExecutionPolicy padrão do Windows.

```powershell
& "SKILL_DIR\bin\tjocr_windows_amd64.exe" install                 # copia p/ o PATH (1ª vez)
& "SKILL_DIR\bin\tjocr_windows_amd64.exe" config show
& "SKILL_DIR\bin\tjocr_windows_amd64.exe" "C:\caminho\documento.pdf" -o documento.md
```

Depois do `install`, em terminais novos você pode chamar `tjocr` direto (sem o caminho).
