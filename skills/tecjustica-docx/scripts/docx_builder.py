"""Biblioteca TecJustica DOCX Builder.

Gera relatórios processuais profissionais com identidade visual TecJustica,
usando python-docx e convertendo para PDF via LibreOffice headless.

Paleta oficial (extraída do substack tecjustica.substack.com):
    TECJUSTICA_INDIGO       #4F46E5   primária
    TECJUSTICA_INDIGO_DARK  #3A30E2   títulos de capa
    TECJUSTICA_ORANGE       #FF6719   acento, callouts
    TECJUSTICA_DARK         #363737   corpo de texto
    TECJUSTICA_MEDIUM       #757575   metadados, legendas
    TECJUSTICA_SOFT_BG      #F5F5FA   fundo de blocos

Tipografia:
    Georgia     — headings (serifa: autoridade jurídica)
    Calibri     — corpo (legibilidade)
    Consolas    — código e identificadores técnicos

Uso básico:
    from docx_builder import Report

    r = Report(
        titulo="Relatório Processual",
        subtitulo="Análise do processo 0001234-56.2024.8.06.0001",
        autor="TecJustica · Assessoria Judicial",
        data="14/04/2026",
    )
    r.add_cover()
    r.add_toc()
    r.add_heading("Sumário executivo", level=1)
    r.add_paragraph("Este relatório analisa ...")
    r.add_data_cards([("CNJ", "0001234-56..."), ("Classe", "Ação de cobrança")])
    r.add_table(["Data", "Movimento"], [["01/03", "Distribuído"], ["15/03", "Citação"]])
    r.add_quote("A prescrição intercorrente...", "STJ · REsp 1.340.553")
    r.add_signature("Magistrado(a)", "Juiz(a) de Direito")
    r.save("relatorio.docx")
    r.export_pdf("relatorio.pdf")
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

from docx import Document
from docx.document import Document as _Doc
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.table import _Cell


# ---------- Paleta TecJustica ----------

INDIGO = RGBColor(0x4F, 0x46, 0xE5)
INDIGO_DARK = RGBColor(0x3A, 0x30, 0xE2)
ORANGE = RGBColor(0xFF, 0x67, 0x19)
DARK = RGBColor(0x36, 0x37, 0x37)
MEDIUM = RGBColor(0x75, 0x75, 0x75)
LIGHT = RGBColor(0xB7, 0xB7, 0xB7)

HEX_INDIGO = "4F46E5"
HEX_INDIGO_SOFT = "E8E7FB"
HEX_ORANGE_SOFT = "FFF0E6"
HEX_SOFT_BG = "F5F5FA"
HEX_TABLE_HEADER = "4F46E5"
HEX_TABLE_ROW_ALT = "F5F5FA"
HEX_CODE_BG = "F2F2F7"
HEX_QUOTE_BG = "F8F7FF"
HEX_DIVIDER = "D8D7EE"

FONT_HEADING = "Georgia"
FONT_BODY = "Calibri"
FONT_CODE = "Consolas"


# ---------- Helpers XML ----------

def _set_cell_bg(cell: _Cell, hex_color: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def _set_cell_border(cell: _Cell, color: str = HEX_DIVIDER, sz: int = 4) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{edge}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), str(sz))
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), color)
        tc_borders.append(b)
    tc_pr.append(tc_borders)


def _add_left_border(paragraph, color: str, size: int = 24) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), str(size))
    left.set(qn("w:space"), "6")
    left.set(qn("w:color"), color)
    p_bdr.append(left)
    p_pr.append(p_bdr)


def _insert_field(run, instruction: str, placeholder: str = " ") -> None:
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    placeholder_el = OxmlElement("w:t")
    placeholder_el.text = placeholder
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(placeholder_el)
    run._r.append(fld_end)


# ---------- Core ----------

@dataclass
class Report:
    titulo: str
    subtitulo: str = ""
    autor: str = "TecJustica"
    data: str = ""
    cnj: str = ""
    orgao: str = "TecJustica · Assessoria Judicial com IA"
    doc: _Doc = field(default_factory=Document)

    def __post_init__(self) -> None:
        self._configure_styles()
        self._configure_page()
        self._configure_header_footer()

    def _configure_styles(self) -> None:
        styles = self.doc.styles
        normal = styles["Normal"]
        normal.font.name = FONT_BODY
        normal.font.size = Pt(11)
        normal.font.color.rgb = DARK
        normal.paragraph_format.space_after = Pt(6)
        normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        normal.paragraph_format.line_spacing = 1.25

    def _configure_page(self) -> None:
        section = self.doc.sections[0]
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.8)
        section.right_margin = Cm(2.5)

    def _configure_header_footer(self) -> None:
        section = self.doc.sections[0]
        section.different_first_page_header_footer = True

        header = section.header
        p = header.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(f"{self.titulo}")
        run.font.size = Pt(9)
        run.font.color.rgb = MEDIUM
        run.font.name = FONT_BODY
        run.italic = True

        footer = section.footer
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_label = p.add_run(f"{self.orgao}   ·   página ")
        run_label.font.size = Pt(8)
        run_label.font.color.rgb = MEDIUM
        run_label.font.name = FONT_BODY
        run_num = p.add_run()
        run_num.font.size = Pt(8)
        run_num.font.color.rgb = MEDIUM
        run_num.font.name = FONT_BODY
        _insert_field(run_num, "PAGE")
        run_of = p.add_run(" de ")
        run_of.font.size = Pt(8)
        run_of.font.color.rgb = MEDIUM
        run_of.font.name = FONT_BODY
        run_total = p.add_run()
        run_total.font.size = Pt(8)
        run_total.font.color.rgb = MEDIUM
        run_total.font.name = FONT_BODY
        _insert_field(run_total, "NUMPAGES")

    # ---- Cover ----

    def add_cover(self) -> None:
        section = self.doc.sections[0]
        first_header = section.first_page_header
        first_header.paragraphs[0].clear()
        first_footer = section.first_page_footer
        first_footer.paragraphs[0].clear()

        for _ in range(3):
            self.doc.add_paragraph()

        bar = self.doc.add_paragraph()
        bar.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = bar.add_run("TECJUSTICA")
        run.font.name = FONT_HEADING
        run.font.size = Pt(12)
        run.font.color.rgb = INDIGO
        run.bold = True
        _add_left_border(bar, HEX_INDIGO, size=48)

        self.doc.add_paragraph()

        title_p = self.doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title_p.add_run(self.titulo)
        run.font.name = FONT_HEADING
        run.font.size = Pt(34)
        run.font.color.rgb = INDIGO_DARK
        run.bold = True
        title_p.paragraph_format.space_after = Pt(8)

        if self.subtitulo:
            sub_p = self.doc.add_paragraph()
            sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = sub_p.add_run(self.subtitulo)
            run.font.name = FONT_BODY
            run.font.size = Pt(16)
            run.font.color.rgb = DARK
            sub_p.paragraph_format.space_after = Pt(4)

        accent = self.doc.add_paragraph()
        accent.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = accent.add_run("━━━━━━━━━━━━━━━━━━━━")
        run.font.size = Pt(12)
        run.font.color.rgb = ORANGE

        for _ in range(6):
            self.doc.add_paragraph()

        if self.cnj:
            cnj_p = self.doc.add_paragraph()
            cnj_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            label = cnj_p.add_run("Número CNJ    ")
            label.font.size = Pt(9)
            label.font.color.rgb = MEDIUM
            label.font.name = FONT_BODY
            label.bold = True
            value = cnj_p.add_run(self.cnj)
            value.font.size = Pt(11)
            value.font.color.rgb = DARK
            value.font.name = FONT_CODE

        if self.data:
            data_p = self.doc.add_paragraph()
            data_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            label = data_p.add_run("Elaborado em    ")
            label.font.size = Pt(9)
            label.font.color.rgb = MEDIUM
            label.font.name = FONT_BODY
            label.bold = True
            value = data_p.add_run(self.data)
            value.font.size = Pt(11)
            value.font.color.rgb = DARK
            value.font.name = FONT_BODY

        if self.autor:
            a_p = self.doc.add_paragraph()
            a_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            label = a_p.add_run("Elaborado por    ")
            label.font.size = Pt(9)
            label.font.color.rgb = MEDIUM
            label.font.name = FONT_BODY
            label.bold = True
            value = a_p.add_run(self.autor)
            value.font.size = Pt(11)
            value.font.color.rgb = DARK
            value.font.name = FONT_BODY

        for _ in range(3):
            self.doc.add_paragraph()

        tag = self.doc.add_paragraph()
        tag.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = tag.add_run("Inovação tecnológica para o Judiciário brasileiro")
        run.font.size = Pt(9)
        run.font.color.rgb = MEDIUM
        run.font.name = FONT_BODY
        run.italic = True

        self._page_break()

    # ---- TOC ----

    def add_toc(self) -> None:
        self.add_heading("Sumário", level=1)
        p = self.doc.add_paragraph()
        run = p.add_run()
        _insert_field(
            run,
            'TOC \\o "1-3" \\h \\z \\u',
            placeholder="Clique com o botão direito e escolha 'Atualizar campo' para ver o sumário.",
        )
        self._page_break()

    # ---- Headings ----

    def add_heading(self, text: str, level: int = 1) -> None:
        sizes = {1: 22, 2: 16, 3: 13}
        space_before = {1: 14, 2: 10, 3: 6}
        space_after = {1: 8, 2: 6, 3: 4}

        h = self.doc.add_heading(level=level)
        run = h.add_run(text)
        run.font.name = FONT_HEADING
        run.font.size = Pt(sizes.get(level, 11))
        run.font.color.rgb = INDIGO_DARK if level == 1 else INDIGO
        run.bold = True
        h.paragraph_format.space_before = Pt(space_before.get(level, 4))
        h.paragraph_format.space_after = Pt(space_after.get(level, 4))

        if level == 1:
            bar = self.doc.add_paragraph()
            bar_run = bar.add_run("━" * 14)
            bar_run.font.size = Pt(8)
            bar_run.font.color.rgb = ORANGE
            bar.paragraph_format.space_after = Pt(6)

    # ---- Paragraphs ----

    def add_paragraph(self, text: str, *, justify: bool = True) -> None:
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if justify else WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(text)
        run.font.name = FONT_BODY
        run.font.size = Pt(11)
        run.font.color.rgb = DARK

    def add_lead(self, text: str) -> None:
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(text)
        run.font.name = FONT_HEADING
        run.font.size = Pt(13)
        run.font.color.rgb = MEDIUM
        run.italic = True
        p.paragraph_format.space_after = Pt(10)

    def add_bullets(self, items: Iterable[str]) -> None:
        for item in items:
            p = self.doc.add_paragraph(style="List Bullet")
            for r in p.runs:
                r.clear()
            run = p.add_run(item)
            run.font.name = FONT_BODY
            run.font.size = Pt(11)
            run.font.color.rgb = DARK

    # ---- Blocks ----

    def add_code(self, code: str) -> None:
        table = self.doc.add_table(rows=1, cols=1)
        cell = table.cell(0, 0)
        _set_cell_bg(cell, HEX_CODE_BG)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        for i, line in enumerate(code.strip("\n").splitlines()):
            if i > 0:
                p.add_run().add_break()
            run = p.add_run(line)
            run.font.name = FONT_CODE
            run.font.size = Pt(10)
            run.font.color.rgb = DARK
        self.doc.add_paragraph()

    def add_callout(self, text: str, kind: str = "info") -> None:
        config = {
            "info": ("ℹ", HEX_INDIGO_SOFT, INDIGO),
            "warn": ("⚠", HEX_ORANGE_SOFT, ORANGE),
            "ok": ("✔", "E8F5E9", RGBColor(0x2E, 0x7D, 0x32)),
        }
        icon, bg, color = config.get(kind, config["info"])
        table = self.doc.add_table(rows=1, cols=1)
        cell = table.cell(0, 0)
        _set_cell_bg(cell, bg)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        icon_run = p.add_run(f"{icon}  ")
        icon_run.font.name = FONT_BODY
        icon_run.font.size = Pt(12)
        icon_run.font.color.rgb = color
        icon_run.bold = True
        body = p.add_run(text)
        body.font.name = FONT_BODY
        body.font.size = Pt(10)
        body.font.color.rgb = DARK
        self.doc.add_paragraph()

    def add_quote(self, text: str, author: str = "") -> None:
        table = self.doc.add_table(rows=1, cols=1)
        cell = table.cell(0, 0)
        _set_cell_bg(cell, HEX_QUOTE_BG)
        p = cell.paragraphs[0]
        _add_left_border(p, HEX_INDIGO, size=36)
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(f"\u201C{text}\u201D")
        run.font.name = FONT_HEADING
        run.font.size = Pt(11)
        run.font.color.rgb = DARK
        run.italic = True
        if author:
            attr = cell.add_paragraph()
            attr.paragraph_format.space_after = Pt(8)
            attr_run = attr.add_run(f"— {author}")
            attr_run.font.name = FONT_BODY
            attr_run.font.size = Pt(9)
            attr_run.font.color.rgb = MEDIUM
            attr_run.bold = True
        self.doc.add_paragraph()

    # ---- Data cards ----

    def add_data_cards(self, items: Sequence[tuple[str, str]], columns: int = 2) -> None:
        rows = (len(items) + columns - 1) // columns
        table = self.doc.add_table(rows=rows, cols=columns)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        total_w = Cm(16)
        col_w = Cm(16 / columns)
        for col in table.columns:
            col.width = col_w
        for idx, (label, value) in enumerate(items):
            r, c = divmod(idx, columns)
            cell = table.rows[r].cells[c]
            cell.width = col_w
            _set_cell_bg(cell, HEX_SOFT_BG)
            _set_cell_border(cell, color=HEX_DIVIDER, sz=6)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            label_run = p.add_run(label.upper())
            label_run.font.name = FONT_BODY
            label_run.font.size = Pt(8)
            label_run.font.color.rgb = MEDIUM
            label_run.bold = True
            v_p = cell.add_paragraph()
            v_p.paragraph_format.space_after = Pt(6)
            v_run = v_p.add_run(value)
            v_run.font.name = FONT_HEADING
            v_run.font.size = Pt(13)
            v_run.font.color.rgb = INDIGO_DARK
            v_run.bold = True
        _ = total_w
        self.doc.add_paragraph()

    # ---- Tables ----

    def add_table(
        self,
        headers: Sequence[str],
        rows: Sequence[Sequence[str]],
        *,
        col_widths_cm: Sequence[float] | None = None,
    ) -> None:
        cols = len(headers)
        table = self.doc.add_table(rows=1 + len(rows), cols=cols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        if col_widths_cm:
            widths = [Cm(w) for w in col_widths_cm]
        else:
            widths = [Cm(16 / cols)] * cols

        header_cells = table.rows[0].cells
        for i, text in enumerate(headers):
            cell = header_cells[i]
            cell.width = widths[i]
            _set_cell_bg(cell, HEX_TABLE_HEADER)
            _set_cell_border(cell, color=HEX_TABLE_HEADER, sz=8)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(text)
            run.font.name = FONT_HEADING
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            run.bold = True

        for r_idx, row in enumerate(rows):
            row_cells = table.rows[r_idx + 1].cells
            alt = r_idx % 2 == 1
            for c_idx, value in enumerate(row):
                cell = row_cells[c_idx]
                cell.width = widths[c_idx]
                if alt:
                    _set_cell_bg(cell, HEX_TABLE_ROW_ALT)
                _set_cell_border(cell, color=HEX_DIVIDER, sz=4)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                run = p.add_run(value)
                run.font.name = FONT_BODY
                run.font.size = Pt(10)
                run.font.color.rgb = DARK

        self.doc.add_paragraph()

    # ---- Timeline ----

    def add_timeline(self, events: Sequence[tuple[str, str]]) -> None:
        table = self.doc.add_table(rows=len(events), cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        date_w = Cm(3.5)
        text_w = Cm(12.5)
        for row_idx, (date, desc) in enumerate(events):
            date_cell = table.rows[row_idx].cells[0]
            date_cell.width = date_w
            _set_cell_bg(date_cell, HEX_INDIGO_SOFT)
            _set_cell_border(date_cell, color=HEX_INDIGO, sz=4)
            date_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = date_cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(date)
            run.font.name = FONT_CODE
            run.font.size = Pt(10)
            run.font.color.rgb = INDIGO_DARK
            run.bold = True

            text_cell = table.rows[row_idx].cells[1]
            text_cell.width = text_w
            _set_cell_border(text_cell, color=HEX_DIVIDER, sz=4)
            text_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = text_cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(desc)
            run.font.name = FONT_BODY
            run.font.size = Pt(10)
            run.font.color.rgb = DARK
        self.doc.add_paragraph()

    # ---- Signature ----

    def add_signature(self, name: str, role: str = "", local_data: str = "") -> None:
        self.doc.add_paragraph()
        self.doc.add_paragraph()
        if local_data:
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(local_data)
            run.font.name = FONT_BODY
            run.font.size = Pt(11)
            run.font.color.rgb = DARK
            p.paragraph_format.space_after = Pt(16)

        line = self.doc.add_paragraph()
        line.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = line.add_run("_" * 40)
        run.font.name = FONT_BODY
        run.font.size = Pt(11)
        run.font.color.rgb = DARK

        n = self.doc.add_paragraph()
        n.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = n.add_run(name)
        run.font.name = FONT_HEADING
        run.font.size = Pt(12)
        run.font.color.rgb = INDIGO_DARK
        run.bold = True
        n.paragraph_format.space_after = Pt(0)

        if role:
            r_p = self.doc.add_paragraph()
            r_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = r_p.add_run(role)
            run.font.name = FONT_BODY
            run.font.size = Pt(10)
            run.font.color.rgb = MEDIUM
            run.italic = True

    # ---- Low-level ----

    def _page_break(self) -> None:
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---- Export ----

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(path)
        return path

    def export_pdf(self, docx_path: str | Path, pdf_path: str | Path | None = None) -> Path:
        docx_path = Path(docx_path)
        out_dir = Path(pdf_path).parent if pdf_path else docx_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                str(docx_path),
                "--outdir",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice falhou ao converter {docx_path}:\n{result.stderr}"
            )
        default_pdf = out_dir / f"{docx_path.stem}.pdf"
        if pdf_path:
            target = Path(pdf_path)
            if default_pdf != target:
                default_pdf.rename(target)
            return target
        return default_pdf
