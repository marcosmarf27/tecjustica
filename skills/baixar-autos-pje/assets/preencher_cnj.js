// preencher_cnj.js
// ---------------------------------------------------------------
// Preenche os 6 campos do formulário "Consulta Processual" do PJE
// a partir de um número CNJ no formato NNNNNNN-DD.AAAA.J.TR.OOOO.
//
// Uso: substitua __CNJ__ pelo número do processo e passe o conteúdo
// deste arquivo como argumento do mcp__Claude_in_Chrome__javascript_tool.
//
// Por que existe: os campos ramoJustica (=8) e respectivoTribunal (=06)
// vêm pré-preenchidos pelo servidor. Se só fizer `type`, o valor duplica
// ("86" em vez de "8", "0606" em vez de "06"). A receita é:
//   focus → select → clear (value="") → dispatchEvent input
//         → set new value → dispatchEvent input + change → blur
// Essa sequência cobre o ciclo que o JSF/RichFaces espera para reconhecer
// a edição e não reintroduzir o valor antigo via script do próprio PJE.
// ---------------------------------------------------------------

(function () {
  // __CNJ__ é um placeholder — substitua pelo número completo antes de injetar.
  // Ex.: const cnj = "3000029-27.2023.8.06.0203";
  const cnj = "__CNJ__";

  // Regex quebra o CNJ em: sequencial, dv, ano, ramo, tribunal, orgao
  const m = cnj.match(/^(\d{7})-(\d{2})\.(\d{4})\.(\d)\.(\d{2})\.(\d{4})$/);
  if (!m) {
    return { ok: false, reason: "CNJ invalido: " + cnj };
  }
  const [, sequencial, dv, ano, ramo, tribunal, orgao] = m;

  // Mapeamento campo -> valor. Ordem importa: preencha da esquerda para a
  // direita como se fosse um humano tabulando pelo form.
  const fields = [
    ["fPP:numeroProcesso:numeroSequencial",         sequencial],
    ["fPP:numeroProcesso:numeroDigitoVerificador",  dv],
    ["fPP:numeroProcesso:Ano",                       ano],
    ["fPP:numeroProcesso:ramoJustica",               ramo],
    ["fPP:numeroProcesso:respectivoTribunal",        tribunal],
    ["fPP:numeroProcesso:NumeroOrgaoJustica",        orgao],
  ];

  // Aplica a sequência focus → select → clear → set em cada campo
  function setField(id, value) {
    const el = document.getElementById(id);
    if (!el) return { id, ok: false, reason: "elemento nao encontrado" };

    el.focus();
    el.select();
    // Limpa o conteudo atual (cobre o caso de pre-preenchido do ramo/tribunal)
    el.value = "";
    el.dispatchEvent(new Event("input", { bubbles: true }));
    // Seta o novo valor
    el.value = value;
    el.dispatchEvent(new Event("input",  { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    el.blur();

    return { id, ok: true, final: el.value, expected: value };
  }

  const results = fields.map(([id, v]) => setField(id, v));
  const allOk = results.every(r => r.ok && r.final === r.expected);

  // Retorno estruturado para a skill conferir se tudo bateu antes de
  // disparar o clique em "Pesquisar".
  return { ok: allOk, cnj, results };
})();
