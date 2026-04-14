# CJF Jurisprudência — Guia de Navegação

## URL
https://jurisprudencia.cjf.jus.br/unificada/index.xhtml

Site público, sem login.

## Elementos da página principal

### Campo de pesquisa
| Elemento | ID estável |
|----------|-----------|
| Campo texto livre | `formulario:textoLivre` |
| Checkbox informação resumida | `formulario:lista_resumida_input` |
| Checkbox pesquisa avançada | `formulario:ckbAvancada_input` |
| Botão Pesquisar | `formulario:actPesquisar` |
| Botão Limpar | `formulario:actLimpar` |

### Operadores lógicos (botões)
Podem ser clicados ou digitados diretamente no campo:
- `e` (AND), `ou` (OR), `adj` (adjacente), `não` (NOT)
- `prox` (proximidade), `mesmo` (mesmo campo), `com` (mesmo documento), `$` (truncamento)

### Checkboxes de tribunais
| Tribunal | ID | Value |
|----------|-----|-------|
| STF | `formulario:j_idt51:0` | STF |
| STJ | `formulario:j_idt51:1` | STJ |
| TNU | `formulario:j_idt51:2` | TNU (marcado por padrão) |
| TRF1 | `formulario:j_idt51:3` | TRF1 |
| TRF2 | `formulario:j_idt51:4` | TRF2 |
| TRF3 | `formulario:j_idt51:5` | TRF3 |
| TRF4 | `formulario:j_idt51:6` | TRF4 |
| TRF5 | `formulario:j_idt51:7` | TRF5 |
| TR (Turma Recursal) | `formulario:trMarcado_input` | — |
| TRU (Turma Regional) | `formulario:truMarcado_input` | — |
| Todos | `formulario:checkTodos_input` | — |

**ARMADILHA:** Marcar "Todos" NÃO marca TR e TRU automaticamente. Precisa marcar os três: Todos + TR + TRU. Sem TR/TRU marcado, o site retorna erro: "É necessário selecionar pelo menos uma Turma Regional!"

### Navegação dos checkboxes com browser-use

Os checkboxes têm IDs estáveis, então podem ser acessados por `eval`:

```bash
# Marcar Todos (funciona porque NÃO está em iframe)
browser-use eval "document.getElementById('formulario:checkTodos_input').click()"

# Marcar TR
browser-use eval "document.getElementById('formulario:trMarcado_input').click()"

# Marcar TRU
browser-use eval "document.getElementById('formulario:truMarcado_input').click()"
```

Ou via `browser-use click <index>` buscando pelo ID no state.

## Tela de resultados

Após pesquisar, os resultados aparecem na mesma página abaixo do formulário.

### Contagem por tribunal
Aparece a quantidade de documentos encontrados por tribunal:
```
STF: 23 Documento(s) encontrado(s)
STJ: 310 Documento(s) encontrado(s)
...
(Exibindo 1 - 30 de 7861, Página: 1/263)
```

### Estrutura de cada resultado

Cada resultado tem:
| Campo | Descrição |
|-------|-----------|
| Tipo | Acórdão, Decisão Monocrática, Súmula, etc. |
| Classe | APELAÇÃO CÍVEL, RECURSO ESPECIAL, AGRAVO, etc. |
| Processo | Número do processo |
| Relator(a) | Nome do relator |
| Relator convocado | Nome do relator convocado (se houver) |
| Origem | Tribunal de origem (TRF1, STJ, etc.) |
| Órgão julgador | Turma/Seção |
| Data | Data do julgamento |
| Data da publicação | Data de publicação |

### Botões de cada resultado
| Botão | ID pattern | Função |
|-------|-----------|--------|
| Documento (inteiro teor) | `formulario:tabelaDocumentos:N:j_idt255:j_idt258` | Abre o inteiro teor |
| Copiar referência | `formulario:tabelaDocumentos:N:j_idt255:j_idt259` | Copia referência |

Onde `N` é o índice do resultado (0, 1, 2...).

### Paginação
- Dropdown para resultados por página: 10, 30, 50
- ID: `formulario:tabelaDocumentos:j_id44`
- Botões de página no rodapé da tabela

### Leitura dos resultados

Para extrair informações dos resultados, rolar a página e ler o state:

```bash
browser-use scroll down
browser-use state | grep -A2 "Tipo\|Classe\|Relator\|Origem\|Órgão\|Data\|ementa"
```

Para ver o inteiro teor de um resultado específico:
```bash
# Clicar no botão "Documento" do primeiro resultado (índice 0)
IDX=$(browser-use state | grep "tabelaDocumentos:0:j_idt255:j_idt258" | grep -oE '\[[0-9]+\]' | tr -d '[]')
browser-use click $IDX
sleep 3
```

## Pesquisa avançada

Marcar `formulario:ckbAvancada_input` expande campos adicionais:
- Número do processo
- Data de julgamento (de/até)
- Data de publicação (de/até)
- Órgão julgador
- Relator
- Legislação citada

## Exemplo completo de busca

```bash
export PATH="$HOME/.browser-use-env/bin:$PATH"
browser-use close 2>/dev/null || true
browser-use --profile "Default" --headed open https://jurisprudencia.cjf.jus.br/unificada/index.xhtml
sleep 5

# Marcar todos os tribunais (via eval — site não usa iframes)
browser-use eval "document.getElementById('formulario:checkTodos_input').click()"
browser-use eval "document.getElementById('formulario:trMarcado_input').click()"
browser-use eval "document.getElementById('formulario:truMarcado_input').click()"
sleep 1

# Digitar busca
browser-use eval "
  var campo = document.getElementById('formulario:textoLivre');
  campo.value = 'dano moral e bancário';
  campo.dispatchEvent(new Event('change', {bubbles: true}));
"

# Pesquisar
browser-use eval "document.getElementById('formulario:actPesquisar').click()"
sleep 8

# Ler resultados
browser-use scroll down
browser-use state
```
