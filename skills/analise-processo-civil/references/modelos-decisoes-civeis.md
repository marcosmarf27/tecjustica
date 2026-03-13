# Modelos de Decisoes Civeis

Templates e estruturas para despachos, decisoes interlocutorias e sentencas civeis.
Ao gerar documentos, use a skill `docx` para criar arquivos `.docx` profissionais.

---

## 1. Despacho de Mero Expediente

Ato judicial sem conteudo decisorio, que apenas impulsiona o processo (art. 203, §3o CPC).

### Estrutura

```
[CABECALHO COM DADOS DO PROCESSO]

Processo nº [CNJ]
Classe: [classe processual]
Autor(a): [nome]
Reu/Re: [nome]

DESPACHO

[Conteudo — determinacao simples]

Intimem-se.

[Localidade], [data].

[Nome do Juiz]
Juiz(a) de Direito
```

### Exemplos comuns

**Citar o reu:**
```
Cite-se o reu para, querendo, contestar no prazo legal.
Intimem-se.
```

**Designar audiencia:**
```
Designo audiencia de conciliacao para o dia [data], as [hora], na sala [X] deste Juizo.
Intimem-se as partes e seus advogados.
```

**Intimar para manifestacao:**
```
Intime-se o(a) autor(a) para se manifestar sobre a contestacao, no prazo de 15 (quinze) dias.
```

**Determinar emenda:**
```
Intime-se o(a) autor(a) para emendar a peticao inicial, no prazo de 15 (quinze) dias, a fim de [especificar o que falta], sob pena de indeferimento (art. 321, CPC).
```

**Abrir vista ao MP:**
```
Abra-se vista ao Ministerio Publico para parecer, no prazo legal.
```

---

## 2. Decisao Interlocutoria

Ato judicial que resolve questao incidental no curso do processo, sem por fim ao procedimento (art. 203, §2o CPC).

### Estrutura

```
[CABECALHO COM DADOS DO PROCESSO]

Processo nº [CNJ]
Classe: [classe processual]
Autor(a): [nome]
Reu/Re: [nome]

DECISAO

[Relatorio breve — o que foi pedido]

[Fundamentacao — por que decide assim, com base legal]

Ante o exposto, [dispositivo — o que decide].

[Providencias: intimacoes, prazos, etc.]

[Localidade], [data].

[Nome do Juiz]
Juiz(a) de Direito
```

### Modelos especificos

**Tutela de urgencia antecipada (art. 300 CPC):**
```
DECISAO

Trata-se de pedido de tutela de urgencia formulado por [autor], em face de [reu], nos autos da [classe processual] acima referenciada.

Alega o(a) requerente que [resumo dos fatos e do pedido de tutela].

DECIDO.

[DEFERIMENTO]
Estao presentes os requisitos do art. 300 do CPC. Ha probabilidade do direito, pois [fundamentar]. Ha perigo de dano, uma vez que [fundamentar]. A medida e reversivel, nao havendo prejuizo irreparavel ao reu caso a tutela seja posteriormente revogada.

Ante o exposto, DEFIRO a tutela de urgencia para [especificar a medida], devendo [providencias].

[OU INDEFERIMENTO]
Nao estao presentes os requisitos do art. 300 do CPC. [Fundamentar o que falta — probabilidade do direito OU perigo de dano OU irreversibilidade].

Ante o exposto, INDEFIRO o pedido de tutela de urgencia.

Cite-se o reu para audiencia de conciliacao/mediacao, na forma do art. 334 do CPC.
Intimem-se.
```

**Saneamento do processo (art. 357 CPC):**
```
DECISAO DE SANEAMENTO E ORGANIZACAO DO PROCESSO

Vistos.

1. QUESTOES PROCESSUAIS PENDENTES
[Resolver preliminares, questoes de legitimidade, interesse, etc.]

2. QUESTOES DE FATO CONTROVERTIDAS
As questoes de fato sobre as quais recaira a atividade probatoria sao:
a) [questao 1]
b) [questao 2]
c) [questao 3]

3. QUESTOES DE DIREITO RELEVANTES
a) [questao juridica 1]
b) [questao juridica 2]

4. DISTRIBUICAO DO ONUS DA PROVA
O onus da prova fica distribuido na forma do art. 373, I e II, do CPC, cabendo ao autor provar [fatos constitutivos] e ao reu provar [fatos impeditivos, modificativos ou extintivos].

[OU, se houver inversao:]
Inverto o onus da prova quanto a [especificar], nos termos do art. 373, §1o, do CPC, diante de [justificar — maior facilidade de prova, vulnerabilidade, etc.].

5. PROVAS DEFERIDAS
Defiro a producao de prova [pericial/testemunhal/documental].
[Se pericial: nomear perito, fixar honorarios, prazo para quesitos]
[Se testemunhal: designar AIJ]

6. AUDIENCIA DE INSTRUCAO E JULGAMENTO
Designo audiencia de instrucao e julgamento para [data], as [hora].
As partes deverao apresentar rol de testemunhas em [prazo] dias.

Intimem-se.
```

**Gratuidade de justica (art. 98 CPC):**
```
DECISAO

Trata-se de pedido de gratuidade de justica formulado por [parte].

[DEFERIMENTO]
A parte requerente declarou hipossuficiencia, conforme [declaracao/documentos], sendo presumida a veracidade da alegacao (art. 99, §3o, CPC).

DEFIRO o beneficio da gratuidade de justica a [parte].

[OU INDEFERIMENTO]
Os elementos dos autos contradizem a presuncao de hipossuficiencia, pois [fundamentar — renda, patrimonio, movimentacao bancaria].

INDEFIRO o pedido de gratuidade. Intime-se a parte para recolher as custas em [prazo] dias, sob pena de [cancelamento da distribuicao / extincao sem resolucao do merito].
```

---

## 3. Sentenca

Ato judicial que poe fim a fase cognitiva ou extingue a execucao (art. 203, §1o CPC).

### Estrutura obrigatoria (art. 489 CPC)

```
[CABECALHO COM DADOS DO PROCESSO]

Processo nº [CNJ]
Classe: [classe processual]
Autor(a): [nome]
Reu/Re: [nome]

SENTENCA

I — RELATORIO

[Nome completo das partes], [qualificacoes].

[Autor] ajuizou a presente [classe processual] em face de [reu], alegando, em sintese, que [resumo dos fatos e pedidos].

Juntou documentos (fls./IDs [referencia]).

[Citado(a) / Intimado(a)], o(a) reu(re) apresentou contestacao (ID [ref]), arguindo [preliminares, se houver] e, no merito, sustentando que [resumo da defesa].

[Replica as fls./ID [ref].]

[Saneamento: fls./ID [ref].]

[Instrucao: audiencia realizada em [data]. Ouvidas [X] testemunhas do autor e [Y] do reu.]

[Alegacoes finais: autor sustentou [resumo]; reu sustentou [resumo].]

[Parecer do MP, se houver.]

E o relatorio. DECIDO.

II — FUNDAMENTACAO

[1. Preliminares — se houver]

[2. Merito]

[Analise de cada pedido com fundamentacao especifica.]

[Citar dispositivos legais, jurisprudencia, sumulas.]

[Enfrentar todos os argumentos relevantes das partes — art. 489, §1o.]

III — DISPOSITIVO

Ante o exposto, [JULGO PROCEDENTE / IMPROCEDENTE / PARCIALMENTE PROCEDENTE] o(s) pedido(s) formulado(s) por [autor] em face de [reu], [com resolucao do merito, nos termos do art. 487, I, do CPC], para:

a) [especificar cada condenacao/declaracao/constituicao];
b) [especificar];
c) [fixar honorarios — art. 85 CPC];
d) [custas].

[Se procedente:]
Condeno o(a) reu(re) ao pagamento de custas processuais e honorarios advocaticios, que fixo em [X]% sobre o valor da condenacao/causa, nos termos do art. 85, §2o, do CPC.

[Se improcedente:]
Condeno o(a) autor(a) ao pagamento de custas processuais e honorarios advocaticios, que fixo em [X]% sobre o valor da causa, nos termos do art. 85, §2o, do CPC. [Se beneficiario(a) da gratuidade: suspensa a exigibilidade, nos termos do art. 98, §3o, do CPC.]

[Se parcialmente procedente:]
Ante a sucumbencia reciproca, cada parte arcara com [distribuicao proporcional] das custas. Fixo honorarios advocaticios de [parte 1] em favor do patrono de [parte 2] em [X]% e de [parte 2] em favor do patrono de [parte 1] em [Y]%, vedada a compensacao (art. 85, §14, CPC).

Publique-se. Registre-se. Intimem-se.

[Localidade], [data].

[Nome do Juiz]
Juiz(a) de Direito
```

### Honorarios advocaticios (art. 85 CPC)

| Faixa sobre condenacao/proveito | Minimo | Maximo |
|-------------------------------|:------:|:------:|
| Ate 200 salarios minimos | 10% | 20% |
| De 200 a 2.000 SM | 8% | 10% |
| De 2.000 a 20.000 SM | 5% | 8% |
| De 20.000 a 100.000 SM | 3% | 5% |
| Acima de 100.000 SM | 1% | 3% |

**Contra a Fazenda Publica (art. 85, §3o):** mesmas faixas, calculadas sobre o valor da condenacao ou proveito economico.

### Sentencas especificas

**Extincao sem resolucao do merito (art. 485):**
- Nao precisa de fundamentacao de merito
- Nao gera coisa julgada material
- Dispositivo: "JULGO EXTINTO o processo, sem resolucao do merito, nos termos do art. 485, [inciso], do CPC."

**Improcedencia liminar (art. 332):**
- Dispensa citacao do reu
- Dispositivo: "JULGO LIMINARMENTE IMPROCEDENTE o pedido, nos termos do art. 332, [inciso], do CPC."

**Julgamento antecipado do merito (art. 355):**
- Dispensa instrucao
- Fundamentar por que nao ha necessidade de provas

**Homologacao de acordo (art. 487, III, "b"):**
- "HOMOLOGO, por sentenca, para que produza seus juridicos e legais efeitos, o acordo celebrado entre as partes (ID [ref]), e JULGO EXTINTO o processo, com resolucao do merito, nos termos do art. 487, III, 'b', do CPC."

---

## 4. Boas Praticas na Redacao Judicial

### Fundamentacao (art. 489, §1o CPC)

A decisao NAO sera considerada fundamentada se:
1. Limitar-se a indicacao, reproducao ou parafraseamento de ato normativo
2. Empregar conceitos juridicos indeterminados sem explicar o motivo concreto
3. Invocar motivos que se prestariam a justificar qualquer outra decisao
4. Nao enfrentar todos os argumentos deduzidos que, em tese, seriam capazes de infirmar a conclusao
5. Limitar-se a invocar precedente ou sumula sem identificar fundamentos determinantes nem demonstrar ajuste ao caso
6. Deixar de seguir precedente vinculante sem demonstrar distincao ou superacao (distinguishing/overruling)

### Linguagem

- Preferir frases curtas e diretas
- Evitar jargao desnecessario
- Fundamentar cada ponto com dispositivo legal especifico
- Citar jurisprudencia com numero do julgado, orgao julgador e data
- Enfrentar os argumentos principais de cada parte

### Formatacao DOCX

Ao gerar o documento via skill `docx`:
- **Fonte:** Times New Roman 12pt ou Arial 12pt
- **Espacamento:** 1,5 entre linhas
- **Margens:** superior 3cm, inferior 2cm, esquerda 3cm, direita 2cm
- **Alinhamento:** justificado
- **Cabecalho:** dados do juizo (comarca, vara)
- **Rodape:** paginacao
- **Paragrafos:** recuo de 2cm na primeira linha
