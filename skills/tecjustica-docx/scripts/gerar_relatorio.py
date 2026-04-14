"""CLI para gerar relatórios TecJustica Edição Executiva a partir de JSON.

Uso:
    python3 gerar_relatorio.py entrada.json saida.docx [--pdf] [--pdf-path /tmp/out.pdf]

Formato completo do JSON:

{
  "meta": {
    "titulo": "Relatório de Análise Processual",
    "subtitulo": "Parecer técnico sobre cumprimento de sentença",
    "eyebrow": "RELATÓRIO PROCESSUAL",
    "classificacao": "RESERVADO",
    "numero_documento": "TJ-CE / 2026 / 024",
    "autor": "TecJustica · Assessoria Judicial",
    "orgao": "TecJustica · Assessoria Judicial com IA",
    "metadata": [
      ["AUTOS", "0001234-56.2024.8.06.0001"],
      ["CLASSE", "Cumprimento de sentença"],
      ["ÓRGÃO JULGADOR", "4ª Vara Cível · Fortaleza/CE"],
      ["RELATOR(A)", "Juiz(a) de Direito"],
      ["DATA", "14 de abril de 2026"]
    ]
  },
  "cover": true,
  "toc": true,
  "sections": [
    {"type": "heading", "level": 1, "text": "Sumário executivo", "numeral": "01"},
    {"type": "lead", "text": "Parecer técnico assistido..."},
    {"type": "paragraph", "text": "..."},
    {"type": "kpi", "items": [["CNJ", "0001234-56", "Processo analisado"]]},
    {"type": "data_cards", "columns": 3, "items": [["CNJ", "..."]]},
    {"type": "table", "headers": ["Col A"], "rows": [["valor"]], "col_widths_cm": [16.5]},
    {"type": "timeline", "events": [["01/03", "..."]]},
    {"type": "quote", "text": "...", "author": "STJ · REsp ..."},
    {"type": "callout", "kind": "warn", "text": "..."},
    {"type": "bullets", "items": ["..."]},
    {"type": "code", "text": "comando"},
    {"type": "signature", "name": "...", "role": "...", "local_data": "..."}
  ]
}

Exit codes:
    0 sucesso · 1 erro de JSON · 2 erro na geração · 3 erro na conversão PDF
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from docx_builder import Report  # noqa: E402


SECTION_HANDLERS = {
    "heading": lambda r, s: r.add_heading(
        s["text"], level=s.get("level", 1), numeral=s.get("numeral")
    ),
    "lead": lambda r, s: r.add_lead(s["text"]),
    "paragraph": lambda r, s: r.add_paragraph(s["text"], justify=s.get("justify", True)),
    "bullets": lambda r, s: r.add_bullets(s["items"]),
    "kpi": lambda r, s: r.add_kpi([tuple(x) for x in s["items"]]),
    "data_cards": lambda r, s: r.add_data_cards(
        [tuple(x) for x in s["items"]], columns=s.get("columns", 2)
    ),
    "table": lambda r, s: r.add_table(
        s["headers"], s["rows"], col_widths_cm=s.get("col_widths_cm"),
    ),
    "timeline": lambda r, s: r.add_timeline([tuple(x) for x in s["events"]]),
    "quote": lambda r, s: r.add_quote(s["text"], s.get("author", "")),
    "callout": lambda r, s: r.add_callout(s["text"], s.get("kind", "info")),
    "code": lambda r, s: r.add_code(s["text"]),
    "signature": lambda r, s: r.add_signature(
        s["name"], s.get("role", ""), s.get("local_data", "")
    ),
}


def build_report(data: dict) -> Report:
    meta = data.get("meta", {})
    r = Report(
        titulo=meta.get("titulo", "Relatório TecJustica"),
        subtitulo=meta.get("subtitulo", ""),
        eyebrow=meta.get("eyebrow", "RELATÓRIO PROCESSUAL"),
        classificacao=meta.get("classificacao", "DOCUMENTO RESERVADO"),
        numero_documento=meta.get("numero_documento", ""),
        autor=meta.get("autor", "TecJustica · Assessoria Judicial"),
        orgao=meta.get("orgao", "TecJustica · Assessoria Judicial com IA"),
        metadata=[tuple(x) for x in meta.get("metadata", [])],
    )

    if data.get("cover", True):
        r.add_cover()
    if data.get("toc", True):
        r.add_toc()

    for section in data.get("sections", []):
        handler = SECTION_HANDLERS.get(section.get("type"))
        if not handler:
            print(
                f"[aviso] tipo de seção desconhecido: {section.get('type')!r}",
                file=sys.stderr,
            )
            continue
        try:
            handler(r, section)
        except KeyError as e:
            print(
                f"[erro] seção {section.get('type')!r} sem campo obrigatório: {e}",
                file=sys.stderr,
            )
            raise SystemExit(2)

    return r


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera relatório TecJustica DOCX (e opcionalmente PDF) a partir de JSON."
    )
    parser.add_argument("input_json", help="Arquivo JSON de entrada")
    parser.add_argument("output_docx", help="Arquivo DOCX de saída")
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Também converter para PDF via LibreOffice headless",
    )
    parser.add_argument(
        "--pdf-path",
        help="Caminho específico para o PDF (padrão: mesmo nome do DOCX)",
    )
    args = parser.parse_args()

    input_path = Path(args.input_json)
    if not input_path.exists():
        print(f"[erro] arquivo não encontrado: {input_path}", file=sys.stderr)
        raise SystemExit(1)

    try:
        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[erro] JSON inválido: {e}", file=sys.stderr)
        raise SystemExit(1)

    report = build_report(data)
    docx_path = report.save(args.output_docx)
    print(f"DOCX gerado: {docx_path}")

    if args.pdf:
        try:
            pdf_path = report.export_pdf(docx_path, args.pdf_path)
            print(f"PDF gerado:  {pdf_path}")
        except (FileNotFoundError, RuntimeError) as e:
            print(f"[erro] conversão PDF falhou: {e}", file=sys.stderr)
            print(
                "[dica] verifique se o LibreOffice está instalado: "
                "sudo apt install -y libreoffice-core libreoffice-writer --no-install-recommends",
                file=sys.stderr,
            )
            raise SystemExit(3)


if __name__ == "__main__":
    main()
