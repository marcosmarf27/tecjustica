# Paleta e Tipografia · Edição Executiva

Referência visual oficial da skill `tecjustica-docx`. O design foi calibrado no padrão de relatórios executivos de bancas de investimento (Goldman Sachs, JP Morgan, Morgan Stanley) e consultorias top-tier (McKinsey, BCG, Bain, Deloitte, PwC), adaptado ao contexto judicial brasileiro.

## Conceito visual

**Sobriedade institucional**. A aparência busca transmitir autoridade jurídica, precisão técnica e formalidade executiva — o tipo de documento que você entregaria para um banco, um tribunal superior ou um conselho administrativo. Nada de cores vibrantes, gradientes ou ícones. Apenas navy profundo, acento ocre (dourado envelhecido), fundos creme e hairlines dourados muito finas.

## Paleta oficial

| Token | Hex | Uso |
|---|---|---|
| Navy | `#12223F` | Primária · títulos, numerais de seção, cabeçalhos de tabela |
| Navy Deep | `#0A1428` | Títulos da capa, barras institucionais do topo |
| Ocre | `#A67C2E` | Acento único · linhas, divisórias, quotes, callouts warn |
| Ocre Light | `#C9A96E` | Tagline da capa, hairlines primárias |
| Cream | `#F6F1E6` | Fundo de metadata grid, data cards, callouts |
| Cream Dark | `#ECE4D1` | Linhas alternadas sutis em tabelas |
| Body | `#2B2B2B` | Corpo de texto (nunca preto puro) |
| Muted | `#6B6B6B` | Labels, legendas, paginação, metadata secundária |
| Hairline | `#D4C9A8` | Linhas divisórias internas (0.25pt–0.5pt) |

## Tipografia editorial

Três famílias apenas, com papéis bem definidos:

### EB Garamond — Display + Body

Serifa transicional clássica inspirada no Garamond do século XVI, redesenhada por Georg Duffner com ajustes modernos de contraste e hinting. Transmite autoridade tipográfica sem parecer pesada ou antiquada. É a fonte que dá a alma editorial ao relatório — a diferença imediata entre "parece profissional" e "parece estudante".

| Uso | Tamanho | Peso |
|---|---|---|
| Título da capa | 42pt | Bold |
| Subtítulo da capa | 16pt | Italic |
| Numerais MMXXVI da capa | 24pt | Bold |
| H1 com numeral lateral | 26pt | Bold |
| H2 | 16pt | Bold Italic |
| Lead paragraphs (destaque) | 14pt | Italic |
| Corpo | 11pt | Regular |
| Valores destacados em data cards | 13–14pt | Bold |
| Quote de jurisprudência | 13pt | Italic |
| KPI numerais | 26pt | Bold |
| Nome na assinatura | 13pt | Bold |

### IBM Plex Sans — Labels e Eyebrows

Sans-serif humanista corporativa desenhada pela IBM. Usada exclusivamente em caixa alta com tracking amplo (+160 a +400 units) para labels, eyebrows, classificações e atribuições de quotes. Cria o contraste moderno contra a serifa editorial.

| Uso | Tamanho | Tracking |
|---|---|---|
| Eyebrow da capa ("RELATÓRIO PROCESSUAL · VOL. I") | 9pt | +400 |
| Tag de classificação ("RESERVADO") | 9pt | +200 |
| Labels de metadata grid | 7pt | +220 |
| Labels de data cards | 7pt | +220 |
| Label "PREPARADO POR" | 7pt | +240 |
| Cabeçalhos de tabela | 8pt | +200 |
| H3 | 10pt | +160 |
| Rodapé institucional | 7pt | +160 |
| Atribuição de quotes | 8pt | +160 |
| Cargo na assinatura | 8pt | +200 |
| Label de callout ("NOTA", "ATENÇÃO") | 8pt | +240 |

### IBM Plex Mono — Document ID, numerais, paginação

Monoespaçada institucional da IBM. Usada para identificadores únicos, datas em formato técnico, números de página e valores numéricos que precisam alinhar verticalmente em tabelas. Dá ao documento o ar de "registro oficial" que relatórios corporativos têm.

| Uso | Tamanho | Tracking |
|---|---|---|
| Número do documento na capa ("TJ-CE / 2026 / 024") | 9pt | +80 |
| Numerais de H1 ("01", "02", "03") | 10pt | +120 |
| Datas da timeline | 9pt | +40 |
| Valores numéricos em metadata (CNJ, R$) | 11pt | 0 |
| Paginação do rodapé ("01 / 08") | 7pt | 0 |
| Blocos de código | 9pt | 0 |

## Instalação das fontes

No Ubuntu/Debian/WSL:

```bash
sudo apt install -y fonts-ebgaramond fonts-ebgaramond-extra fonts-ibm-plex fonts-inconsolata fonts-crosextra-caladea fonts-crosextra-carlito
```

Essas são as dependências do `install.sh` para a skill `tecjustica-docx`. Sem elas, o LibreOffice substitui automaticamente por fallbacks como Liberation Serif e Carlito, o que compromete visivelmente a apresentação.

No macOS:

```bash
brew install --cask font-eb-garamond font-ibm-plex font-inconsolata
```

## Regras de uso

1. **EB Garamond no corpo, sempre.** A combinação "sans-serif no corpo + serifa no título" lê como blog corporativo. Relatórios executivos usam serifa no corpo — é a diferença invisível mais importante entre "polido" e "amador".
2. **Labels em caixa alta com tracking amplo.** Nunca misture title case e caps sem tracking. O respiro entre as letras é o que sinaliza cuidado tipográfico.
3. **Datas em formato longo.** Nunca `14/04/26` no corpo ou na capa — use `14 de abril de 2026` ou `14 · Abril · 2026`. Formato curto `14/04/2026` só em tabelas, timelines e metadata técnica.
4. **Hairlines em vez de bordas grossas.** Todas as divisórias são de 0.25–0.5pt em Ocre Light (`#C9A96E`) ou Hairline (`#D4C9A8`). Bordas de 2pt são amadoras.
5. **Navy profundo, nunca preto puro.** `#0A1428` ou `#12223F` para títulos e barras institucionais. `#2B2B2B` para o corpo.
6. **Ocre é acento, nunca estrutura.** Uma página pode ter no máximo 2 pontos de ocre: o hairline após o eyebrow + um callout warn, por exemplo.
7. **Espaço em branco controlado.** A capa é densa, preenchida, institucional. O interior tem margens generosas assimétricas (externa maior que interna).
8. **Numerais de H1 em mono.** "01", "02", "03" em IBM Plex Mono 10pt ocre — nunca em serif, nunca em arábicos grandes.
9. **Line height 1.35 no corpo.** Nem 1.15 (amontoado) nem 1.5 (frouxo). O 1.35 é o que relatórios editoriais usam.
10. **Tabelas sem bordas verticais.** Apenas 3 linhas horizontais: topo (2pt navy), abaixo do header (1pt navy), base (1pt navy). Linhas internas em Hairline 0.25pt.

## Por que essas escolhas

A paleta navy + ocre vem da tradição de relatórios institucionais do século XX: JP Morgan, Coutts, bancos de investimento europeus. É uma combinação que sobrevive décadas sem datar — enquanto purple gradients, corais e tipografias geométricas vêm e vão, navy + ocre permanece.

A escolha de EB Garamond em vez de Georgia ou Cambria é deliberada: Garamond tem contraste mais alto, pernas mais finas, itálicos mais elegantes — lê como livro de direito, não como documento corporativo genérico.

A combinação IBM Plex Sans + Mono em vez de Helvetica ou Arial é uma escolha contemporânea: Plex é a tipografia institucional mais bem desenhada dos últimos 10 anos, livre, com peso, contraste e tracking otimizados para interfaces executivas.
