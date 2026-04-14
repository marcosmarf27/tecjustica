# Paleta e Tipografia TecJustica

Referência visual oficial da skill `tecjustica-docx`.

## Origem das cores

As cores foram extraídas do substack oficial TecJustica (tecjustica.substack.com) por análise do CSS gerado pelo tema. A paleta do Substack indica uma cor primária configurada pelo autor, que no caso do TecJustica é um indigo vibrante, alinhado ao posicionamento "tecnologia + justiça".

## Cores principais

| Nome | Hex | RGB | Uso |
|---|---|---|---|
| Indigo | `#4F46E5` | 79 · 70 · 229 | Primária. Cabeçalhos de tabela, barras laterais, bordas de quote, cor de ícones de info |
| Indigo Dark | `#3A30E2` | 58 · 48 · 226 | Título da capa, H1. Usado quando precisa mais peso visual |
| Orange | `#FF6719` | 255 · 103 · 25 | Acento. Divisores decorativos, callouts de warn, highlights ocasionais |
| Dark | `#363737` | 54 · 55 · 55 | Corpo de texto. Preferido a preto puro por ser mais suave |
| Medium | `#757575` | 117 · 117 · 117 | Metadados, legendas de tabela, rodapé, placeholder |
| Light | `#B7B7B7` | 183 · 183 · 183 | Bordas muito sutis, separadores |

## Cores de fundo

| Nome | Hex | Uso |
|---|---|---|
| Indigo Soft | `#E8E7FB` | Fundo de callouts info, células de timeline |
| Orange Soft | `#FFF0E6` | Fundo de callouts warn |
| Soft BG | `#F5F5FA` | Fundo de data cards, linhas alternadas de tabela |
| Quote BG | `#F8F7FF` | Fundo de citações de jurisprudência |
| Code BG | `#F2F2F7` | Fundo de blocos de código |
| Divider | `#D8D7EE` | Bordas de tabelas e cards |

## Tipografia

A combinação usada busca equilíbrio entre autoridade jurídica (serifa) e legibilidade moderna (sem serifa).

### Georgia — Headings e citações

Serifa clássica, disponível em todos os sistemas operacionais modernos. Transmite autoridade e tradição, adequada a documentos judiciais. Usada em:

- Títulos da capa (34pt · Indigo Dark)
- Headings nível 1 (22pt · Indigo Dark)
- Headings nível 2 (16pt · Indigo)
- Headings nível 3 (13pt · Indigo)
- Texto de citações (11pt · itálico)
- Valores destacados em data cards (13pt · Indigo Dark)
- Nome na assinatura (12pt · Indigo Dark)

### Calibri — Corpo

Sans-serif humanista, padrão do Microsoft Word desde 2007. Excelente legibilidade em tela e impressão. Usada em:

- Parágrafos comuns (11pt · Dark · justificado · 1.25 line-spacing)
- Listas com bullets (11pt · Dark)
- Labels de metadados (9pt · Medium)
- Labels de data cards (8pt · Medium · maiúsculas)
- Cabeçalho e rodapé (9pt · Medium)

### Consolas — Código e identificadores técnicos

Monoespaçada. Usada em:

- Blocos de código (10pt · Dark)
- Datas da timeline (10pt · Indigo Dark · bold)
- Valores de CNJ na capa (11pt · Dark)

## Fallbacks de fonte (Linux sem Microsoft fonts)

Se as fontes Georgia / Calibri / Consolas não estiverem instaladas, o LibreOffice substitui automaticamente:

| Fonte original | Fallback no LibreOffice |
|---|---|
| Georgia | Liberation Serif ou DejaVu Serif |
| Calibri | Carlito (pacote `fonts-crosextra-carlito`) |
| Consolas | Liberation Mono ou DejaVu Sans Mono |

Para garantir fidelidade total ao design:

```bash
sudo apt install -y ttf-mscorefonts-installer fonts-crosextra-carlito
```

## Regras de uso

1. **Nunca usar preto puro** (`#000000`) — sempre Dark (`#363737`) para corpo e Indigo Dark para títulos
2. **Orange é acento, não estrutura** — nunca preencher grandes áreas em laranja; usar em divisores de até 14 caracteres, bordas finas, ou callouts pequenos
3. **Indigo é a estrutura** — cabeçalhos de tabela, barras de capa, bordas principais
4. **Contraste mínimo 4.5:1** — todas as combinações de texto/fundo foram validadas
5. **Bullet automático**, nunca `•` manual — usar `add_bullets()` da classe `Report`
6. **Justificação no corpo, alinhamento à esquerda em leads** — legibilidade
7. **Line spacing 1.25** — equilíbrio entre densidade e respiração
