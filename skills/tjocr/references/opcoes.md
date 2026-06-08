# tjocr — opções completas

Leia só quando precisar afinar algo além do uso padrão (`tjocr documento.pdf -o saida.md`).

## Comando de OCR

```bash
bash "SKILL_DIR/scripts/tjocr.sh" <arquivo.pdf> [opções]
```

| Opção | Default | Descrição |
|-------|---------|-----------|
| `-o, --output FILE` | stdout | Salva o markdown em arquivo. Sem isso, vai para o stdout (bom para pipe) |
| `--dpi N` | `150` | Resolução do OCR: `72` (rápido/barato), `150` (padrão), `300` (máximo) |
| `--enhance` | off | Pós-processa com IA (Gemini): corrige erros de OCR e remonta layout. Mais lento (~7–11 s/pg) e pode **reescrever** trechos. Use em documentos degradados onde a fidelidade importa |
| `--pages RANGE` | (todas) | Só algumas páginas, ex: `1-5,10,15-20` |
| `--lang CODE` | `pt` | Idioma do OCR (ISO 639-1) |
| `--engine NAME` | `paddle` | `paddle` (GPU, melhor qualidade PT-BR), `tesseract`, `none` (sem OCR) |
| `--key KEY` | — | API key avulsa (sobrepõe env/config) |
| `--quiet` | off | Não mostra progresso/resumo no stderr |

As flags funcionam em **qualquer posição**: `tjocr doc.pdf -o out.md` ou `tjocr -o out.md doc.pdf`.

## Comandos de config

| Comando | O que faz |
|---------|-----------|
| `config set` | Lê a API key do **stdin** (não fica no histórico). Aceita pipe ou digitação |
| `config set-key KEY` | Salva a key passada como argumento (fica no histórico — prefira `set`) |
| `config set-url URL` | Aponta para outra base URL da API (raro) |
| `config show` | Mostra config atual (key mascarada) e o caminho do arquivo |

Config fica em `~/.config/tjocr/config.json` (Linux) ou `%AppData%\tjocr\config.json`
(Windows), com permissão `0600`.

**Precedência da key:** `--key` > env `TJOCR_API_KEY` > config salvo > env `TECJUSTICA_API_KEY` (legado).

## Como funciona (resumo técnico)

1. `POST /parse/async` com o PDF. Trata o **303 de cold start** reenviando o POST.
2. Duas respostas possíveis, tratadas automaticamente:
   - **cache hit** → o markdown vem direto, uso imediato;
   - **async** → vem um `job_id` → polling em `/parse/status` a cada 2 s (respeita o rate
     limit de 60/min) até concluir.
3. Entrega o markdown.

## Outras plataformas

A skill traz `linux_amd64` e `windows_amd64.exe`. Para macOS ou arm64, recompile a partir do
fonte (`cli-go/` no repo liteparser):

```bash
GOOS=darwin GOARCH=arm64 go build -ldflags "-s -w" -o tjocr_darwin_arm64 .
```
