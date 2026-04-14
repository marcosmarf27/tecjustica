"""CLI para gerar relatórios TecJustica a partir de JSON.

Uso:
    python3 gerar_relatorio.py entrada.json saida.docx [--pdf]

Formato do JSON de entrada:
{
  "meta": {
    "titulo": "Relatório Processual",
    "subtitulo": "Análise do processo ...",
    "autor": "TecJustica",
    "data": "14/04/2026",
    "cnj": "0001234-56.2024.8.06.0001",
    "orgao": "TecJustica · Assessoria Judicial"
  },
  "cover": true,
  "toc": true,
  "sections": [
    {"type": "heading", "level": 1, "text": "Sumário executivo"},
    {"type": "lead", "text": "Este relatório analisa..."},
    {"type": "paragraph", "text": "..."},
    {"type": "bullets", "items": ["Item 1", "Item 2"]},
    {"type": "data_cards", "items": [["CNJ", "..."], ["Classe", "..."]]},
    {"type": "table", "headers": ["Coluna"], "rows": [["Valor"]]},
    {"type": "timeline", "events": [["01/03/2026", "Distribuído"]]},
    {"type": "quote", "text": "...", "author": "STJ · REsp ..."},
    {"type": "callout", "text": "...", "kind": "info"},
    {"type": "code", "text": "comando --flag"},
    {"type": "signature", "name": "Magistrado(a)", "role": "Juiz(a)", "local_data": "..."}
  ]
}

Exit codes:
    0 = sucesso
    1 = erro de argumento / JSON inválido
    2 = erro na geração
    3 = erro na conversão PDF
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
    "heading": lambda r, s: r.add_heading(s["text"], level=s.get("level", 1)),
    "lead": lambda r, s: r.add_lead(s["text"]),
    "paragraph": lambda r, s: r.add_paragraph(s["text"], justify=s.get("justify", True)),
    "bullets": lambda r, s: r.add_bullets(s["items"]),
    "data_cards": lambda r, s: r.add_data_cards(
        [tuple(x) for x in s["items"]], columns=s.get("columns", 2)
    ),
    "table": lambda r, s: r.add_table(
        s["headers"],
        s["rows"],
        col_widths_cm=s.get("col_widths_cm"),
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
        autor=meta.get("autor", "TecJustica"),
        data=meta.get("data", ""),
        cnj=meta.get("cnj", ""),
        orgao=meta.get("orgao", "TecJustica · Assessoria Judicial com IA"),
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
