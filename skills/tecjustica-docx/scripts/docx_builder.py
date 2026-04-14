"""Biblioteca TecJustica DOCX Builder — padrão institucional.

Gera relatórios processuais no padrão visual de bancas de investimento e
consultorias top-tier (Goldman, JP Morgan, McKinsey, BCG), adaptado para o
contexto judicial brasileiro. Usa python-docx para escrever o DOCX e
LibreOffice headless para conversão DOCX -> PDF.

Design system — Sobriedade Institucional
=========================================

Paleta oficial TecJustica · Edição Executiva:
    NAVY          #12223F   primária (deep navy jurídico)
    NAVY_DEEP     #0A1428   topo de capa, barras institucionais
    OCRE          #A67C2E   acento único (dourado envelhecido)
    OCRE_LIGHT    #C9A96E   linhas divisórias sutis, hairlines
    CREAM         #F6F1E6   fundo de capa, metadata grid
    CREAM_DARK    #ECE4D1   linhas alternadas sutis
    BODY          #2B2B2B   corpo (nunca preto puro)
    MUTED         #6B6B6B   labels, legendas, paginação
    HAIRLINE      #D4C9A8   hairlines dourados 0.25pt

Tipografia editorial:
    EB Garamond     — display + body (serifa transicional clássica)
    IBM Plex Sans   — labels, eyebrows, metadata em CAPS com tracking
    IBM Plex Mono   — document ID, datas, numerais, paginação

Regras tipográficas:
    - Labels em UPPERCASE com character spacing amplo (tracking +200)
    - Corpo sempre em serifa, nunca sans
    - Datas em formato longo: "14 de abril de 2026"
    - Numerais de página em mono: "01 / 48"
    - Quebras de linha manuais no título da capa (nunca deixar o Word quebrar)

Uso:
    from docx_builder import Report

    r = Report(
        titulo="Relatório de Análise Processual",
        subtitulo="Parecer técnico sobre cumprimento de sentença",
        classificacao="RESERVADO",
        numero_documento="TJ-CE / 2026 / 024",
        metadata=[
            ("AUTOS", "0001234-56.2024.8.06.0001"),
            ("CLASSE", "Cumprimento de sentença"),
            ("ÓRGÃO JULGADOR", "4ª Vara Cível · Fortaleza/CE"),
            ("RELATOR(A)", "Juiz(a) de Direito"),
            ("DATA", "14 de abril de 2026"),
        ],
        autor="TecJustica · Assessoria Judicial",
    )
    r.add_cover()
    r.add_toc()
    r.add_heading("Sumário executivo", level=1, numeral="01")
    r.add_paragraph("...")
    r.save("relatorio.docx")
    r.export_pdf("relatorio.docx", "relatorio.pdf")
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
from docx.shared import Cm, Mm, Pt, RGBColor
from docx.table import _Cell


# =========================================================================
# Paleta institucional
# =========================================================================

NAVY = RGBColor(0x12, 0x22, 0x3F)
NAVY_DEEP = RGBColor(0x0A, 0x14, 0x28)
OCRE = RGBColor(0xA6, 0x7C, 0x2E)
OCRE_LIGHT = RGBColor(0xC9, 0xA9, 0x6E)
CREAM = RGBColor(0xF6, 0xF1, 0xE6)
BODY = RGBColor(0x2B, 0x2B, 0x2B)
MUTED = RGBColor(0x6B, 0x6B, 0x6B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CREAM_DARK = RGBColor(0xEC, 0xE4, 0xD1)

HEX_NAVY = "12223F"
HEX_NAVY_DEEP = "0A1428"
HEX_OCRE = "A67C2E"
HEX_OCRE_LIGHT = "C9A96E"
HEX_CREAM = "F6F1E6"
HEX_CREAM_DARK = "ECE4D1"
HEX_HAIRLINE = "D4C9A8"
HEX_WHITE = "FFFFFF"
HEX_ROW_ALT = "FBF8F0"
HEX_CODE_BG = "F4EFE2"

FONT_DISPLAY = "EB Garamond"
FONT_BODY = "EB Garamond"
FONT_SANS = "IBM Plex Sans"
FONT_MONO = "IBM Plex Mono"


# =========================================================================
# Helpers XML de baixo nível
# =========================================================================

def _set_cell_bg(cell: _Cell, hex_color: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def _set_cell_borders(
    cell: _Cell,
    *,
    top: tuple[str, int] | None = None,
    bottom: tuple[str, int] | None = None,
    left: tuple[str, int] | None = None,
    right: tuple[str, int] | None = None,
) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    existing = tc_pr.find(qn("w:tcBorders"))
    if existing is not None:
        tc_pr.remove(existing)
    borders = OxmlElement("w:tcBorders")
    sides = {"top": top, "left": left, "bottom": bottom, "right": right}
    for side, value in sides.items():
        b = OxmlElement(f"w:{side}")
        if value is None:
            b.set(qn("w:val"), "nil")
        else:
            color, sz = value
            b.set(qn("w:val"), "single")
            b.set(qn("w:sz"), str(sz))
            b.set(qn("w:space"), "0")
            b.set(qn("w:color"), color)
        borders.append(b)
    tc_pr.append(borders)


def _set_cell_margins(cell: _Cell, top: int = 100, bottom: int = 100, left: int = 140, right: int = 140) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement("w:tcMar")
    for side, value in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(value))
        el.set(qn("w:type"), "dxa")
        tc_mar.append(el)
    tc_pr.append(tc_mar)


def _add_left_border(paragraph, color: str, size: int = 24) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), str(size))
    left.set(qn("w:space"), "12")
    left.set(qn("w:color"), color)
    p_bdr.append(left)
    p_pr.append(p_bdr)


def _tracking(run, value: int) -> None:
    r_pr = run._r.get_or_add_rPr()
    existing = r_pr.find(qn("w:spacing"))
    if existing is not None:
        r_pr.remove(existing)
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:val"), str(value))
    r_pr.append(spacing)


def _set_run_font(run, name: str) -> None:
    run.font.name = name
    r_pr = run._r.get_or_add_rPr()
    rfonts = r_pr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        r_pr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)


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


def _styled_run(
    paragraph,
    text: str,
    *,
    font: str = FONT_BODY,
    size: int = 11,
    color: RGBColor = BODY,
    bold: bool = False,
    italic: bool = False,
    tracking: int = 0,
    uppercase: bool = False,
):
    run = paragraph.add_run(text.upper() if uppercase else text)
    _set_run_font(run, font)
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.bold = bold
    run.italic = italic
    if tracking:
        _tracking(run, tracking)
    return run


# =========================================================================
# Report
# =========================================================================

@dataclass
class Report:
    titulo: str
    subtitulo: str = ""
    classificacao: str = "DOCUMENTO RESERVADO"
    numero_documento: str = ""
    autor: str = "TecJustica · Assessoria Judicial"
    metadata: Sequence[tuple[str, str]] = field(default_factory=list)
    eyebrow: str = "RELATÓRIO PROCESSUAL"
    orgao: str = "TecJustica · Assessoria Judicial com IA"
    doc: _Doc = field(default_factory=Document)

    def __post_init__(self) -> None:
        self._configure_styles()
        self._configure_page()
        self._configure_header_footer()

    # ---- Setup ----

    def _configure_styles(self) -> None:
        styles = self.doc.styles
        normal = styles["Normal"]
        normal.font.name = FONT_BODY
        normal.font.size = Pt(11)
        normal.font.color.rgb = BODY
        normal.paragraph_format.space_after = Pt(6)
        normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        normal.paragraph_format.line_spacing = 1.35

    def _configure_page(self) -> None:
        section = self.doc.sections[0]
        section.top_margin = Mm(28)
        section.bottom_margin = Mm(24)
        section.left_margin = Mm(26)
        section.right_margin = Mm(32)

    def _configure_header_footer(self) -> None:
        section = self.doc.sections[0]
        section.different_first_page_header_footer = True

        header = section.header
        p = header.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        tab_stops = p.paragraph_format.tab_stops
        tab_stops.add_tab_stop(Cm(15.5), WD_ALIGN_PARAGRAPH.RIGHT)
        left = _styled_run(p, "TECJUSTICA", font=FONT_SANS, size=8, color=NAVY, bold=True, tracking=200, uppercase=True)
        _ = left
        p.add_run("\t")
        right_label = _styled_run(p, self.classificacao, font=FONT_SANS, size=7, color=MUTED, tracking=120, uppercase=True)
        _ = right_label

        footer = section.footer
        p = footer.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        tab_stops = p.paragraph_format.tab_stops
        tab_stops.add_tab_stop(Cm(7.75), WD_ALIGN_PARAGRAPH.CENTER)
        tab_stops.add_tab_stop(Cm(15.5), WD_ALIGN_PARAGRAPH.RIGHT)

        left_run = _styled_run(
            p, self.numero_documento or "TECJUSTICA · ASSESSORIA JUDICIAL",
            font=FONT_MONO, size=7, color=MUTED, tracking=60, uppercase=True,
        )
        _ = left_run
        p.add_run("\t")
        _styled_run(p, "TECJUSTICA · EDIÇÃO EXECUTIVA", font=FONT_SANS, size=7, color=MUTED, tracking=160, uppercase=True)
        p.add_run("\t")

        page_run = p.add_run()
        _set_run_font(page_run, FONT_MONO)
        page_run.font.size = Pt(7)
        page_run.font.color.rgb = NAVY
        page_run.bold = True
        _insert_field(page_run, "PAGE")
        sep = _styled_run(p, " / ", font=FONT_MONO, size=7, color=MUTED)
        _ = sep
        total_run = p.add_run()
        _set_run_font(total_run, FONT_MONO)
        total_run.font.size = Pt(7)
        total_run.font.color.rgb = NAVY
        total_run.bold = True
        _insert_field(total_run, "NUMPAGES")

    # ---- Cover ----

    def add_cover(self) -> None:
        section = self.doc.sections[0]
        section.first_page_header.paragraphs[0].clear()
        section.first_page_footer.paragraphs[0].clear()

        self._cover_top_band()
        self._cover_eyebrow_and_id()
        self._cover_title()
        self._cover_metadata_grid()
        self._cover_bottom_band()
        self._page_break()

    def _cover_top_band(self) -> None:
        table = self.doc.add_table(rows=1, cols=2)
        table.autofit = False
        table.columns[0].width = Cm(10)
        table.columns[1].width = Cm(6.5)

        left = table.cell(0, 0)
        left.width = Cm(10)
        _set_cell_bg(left, HEX_NAVY_DEEP)
        _set_cell_margins(left, top=180, bottom=180, left=240, right=120)
        _set_cell_borders(left)
        p = left.paragraphs[0]
        _styled_run(p, "TECJUSTICA", font=FONT_SANS, size=12, color=WHITE, bold=True, tracking=240, uppercase=True)
        p2 = left.add_paragraph()
        p2.paragraph_format.space_before = Pt(2)
        _styled_run(p2, "Assessoria Judicial com IA", font=FONT_BODY, size=9, color=OCRE_LIGHT, italic=True)

        right = table.cell(0, 1)
        right.width = Cm(6.5)
        _set_cell_bg(right, HEX_OCRE)
        _set_cell_margins(right, top=180, bottom=180, left=140, right=240)
        _set_cell_borders(right)
        p = right.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        _styled_run(p, self.classificacao, font=FONT_SANS, size=9, color=NAVY_DEEP, bold=True, tracking=200, uppercase=True)
        p2 = right.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.paragraph_format.space_before = Pt(2)
        _styled_run(p2, "circulação restrita", font=FONT_BODY, size=8, color=NAVY_DEEP, italic=True)

        self._vertical_space(Pt(18))

    def _cover_eyebrow_and_id(self) -> None:
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        _styled_run(p, self.eyebrow, font=FONT_SANS, size=9, color=OCRE, bold=True, tracking=400, uppercase=True)
        if self.numero_documento:
            p.add_run("   ")
            _styled_run(p, "·", font=FONT_SANS, size=9, color=MUTED)
            p.add_run("   ")
            _styled_run(p, self.numero_documento, font=FONT_MONO, size=9, color=NAVY, tracking=80, uppercase=True)

        self._hairline(width_cm=16.5)

    def _cover_title(self) -> None:
        self._vertical_space(Pt(18))

        title_lines = self._smart_split_title(self.titulo)
        for line in title_lines:
            p = self.doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            _styled_run(p, line, font=FONT_DISPLAY, size=42, color=NAVY_DEEP, bold=True)

        if self.subtitulo:
            p = self.doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            _styled_run(p, self.subtitulo, font=FONT_DISPLAY, size=16, color=BODY, italic=True)

        self._vertical_space(Pt(22))
        self._hairline(width_cm=16.5)
        self._vertical_space(Pt(6))

    @staticmethod
    def _smart_split_title(title: str) -> list[str]:
        words = title.split()
        if len(words) <= 3:
            return [title]
        mid = len(words) // 2
        for offset in range(3):
            idx = mid + offset
            if 0 < idx < len(words) and words[idx - 1][-1] not in ".,;:":
                return [" ".join(words[:idx]), " ".join(words[idx:])]
        return [title]

    def _cover_metadata_grid(self) -> None:
        if not self.metadata:
            return
        items = list(self.metadata)
        cols = min(len(items), 3)
        rows = (len(items) + cols - 1) // cols
        table = self.doc.add_table(rows=rows, cols=cols)
        table.autofit = False
        col_w = Cm(16.5 / cols)
        for col in table.columns:
            col.width = col_w

        for idx, (label, value) in enumerate(items):
            r, c = divmod(idx, cols)
            cell = table.rows[r].cells[c]
            cell.width = col_w
            _set_cell_bg(cell, HEX_CREAM)
            _set_cell_margins(cell, top=200, bottom=180, left=200, right=160)
            is_last_row = r == rows - 1
            is_last_col = c == cols - 1
            _set_cell_borders(
                cell,
                top=(HEX_HAIRLINE, 6),
                bottom=(HEX_HAIRLINE, 6) if not is_last_row else (HEX_OCRE, 8),
                left=None,
                right=None if is_last_col else (HEX_HAIRLINE, 4),
            )

            label_p = cell.paragraphs[0]
            label_p.paragraph_format.space_after = Pt(4)
            _styled_run(
                label_p, label, font=FONT_SANS, size=7,
                color=MUTED, bold=True, tracking=240, uppercase=True,
            )

            value_p = cell.add_paragraph()
            value_p.paragraph_format.space_after = Pt(2)
            is_mono = any(ch.isdigit() for ch in value) and any(ch in value for ch in ".-/")
            _styled_run(
                value_p, value,
                font=FONT_MONO if is_mono and len(value) <= 35 else FONT_DISPLAY,
                size=11 if is_mono else 13,
                color=NAVY_DEEP, bold=not is_mono,
            )

        self._vertical_space(Pt(24))

    def _cover_bottom_band(self) -> None:
        self._vertical_space(Pt(30))

        self._hairline(width_cm=16.5)
        self._vertical_space(Pt(4))

        table = self.doc.add_table(rows=1, cols=2)
        table.autofit = False
        table.columns[0].width = Cm(10.5)
        table.columns[1].width = Cm(6)

        left = table.cell(0, 0)
        left.width = Cm(10.5)
        _set_cell_margins(left, top=40, bottom=40, left=0, right=80)
        _set_cell_borders(left)
        p = left.paragraphs[0]
        _styled_run(p, "PREPARADO POR", font=FONT_SANS, size=7, color=MUTED, bold=True, tracking=240, uppercase=True)
        p2 = left.add_paragraph()
        p2.paragraph_format.space_before = Pt(2)
        _styled_run(p2, self.autor, font=FONT_DISPLAY, size=12, color=NAVY_DEEP, bold=True)
        p3 = left.add_paragraph()
        p3.paragraph_format.space_before = Pt(1)
        _styled_run(p3, "Inovação tecnológica para o Judiciário brasileiro", font=FONT_DISPLAY, size=9, color=MUTED, italic=True)

        right = table.cell(0, 1)
        right.width = Cm(6)
        _set_cell_margins(right, top=40, bottom=40, left=80, right=0)
        _set_cell_borders(right)
        p = right.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        _styled_run(p, "Abril", font=FONT_DISPLAY, size=11, color=BODY, italic=True)
        p2 = right.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.paragraph_format.space_before = Pt(0)
        _styled_run(p2, "MMXXVI", font=FONT_DISPLAY, size=24, color=NAVY_DEEP, bold=True)

    # ---- TOC ----

    def add_toc(self) -> None:
        self.add_heading("Sumário", level=1, numeral="—")
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run()
        _set_run_font(run, FONT_BODY)
        run.font.size = Pt(10)
        run.font.color.rgb = BODY
        _insert_field(
            run,
            'TOC \\o "1-3" \\h \\z \\u',
            placeholder="Clique com o botão direito e escolha 'Atualizar campo' para carregar o sumário.",
        )
        self._page_break()

    # ---- Headings ----

    def add_heading(self, text: str, level: int = 1, numeral: str | None = None) -> None:
        if level == 1:
            self._heading_level_1(text, numeral=numeral or "")
        elif level == 2:
            self._heading_level_2(text)
        else:
            self._heading_level_3(text)

    def _heading_level_1(self, text: str, numeral: str = "") -> None:
        self._vertical_space(Pt(14))

        if numeral:
            p = self.doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            _styled_run(p, numeral, font=FONT_MONO, size=10, color=OCRE, bold=True, tracking=120)

        p = self.doc.add_heading(level=1)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        _set_run_font(run, FONT_DISPLAY)
        run.font.size = Pt(26)
        run.font.color.rgb = NAVY_DEEP
        run.bold = True

        self._hairline(width_cm=6, color=HEX_OCRE)
        self._vertical_space(Pt(4))

    def _heading_level_2(self, text: str) -> None:
        p = self.doc.add_heading(level=2)
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        _set_run_font(run, FONT_DISPLAY)
        run.font.size = Pt(16)
        run.font.color.rgb = NAVY
        run.bold = True
        run.italic = True

    def _heading_level_3(self, text: str) -> None:
        p = self.doc.add_heading(level=3)
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        _styled_run(p, text, font=FONT_SANS, size=10, color=NAVY, bold=True, tracking=160, uppercase=True)

    # ---- Paragraphs ----

    def add_paragraph(self, text: str, *, justify: bool = True) -> None:
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if justify else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Pt(0)
        _styled_run(p, text, font=FONT_BODY, size=11, color=BODY)

    def add_lead(self, text: str) -> None:
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(10)
        _styled_run(p, text, font=FONT_DISPLAY, size=14, color=NAVY, italic=True)

    def add_bullets(self, items: Iterable[str]) -> None:
        for item in items:
            p = self.doc.add_paragraph(style="List Bullet")
            for r in p.runs:
                r.clear()
            run = p.add_run(item)
            _set_run_font(run, FONT_BODY)
            run.font.size = Pt(11)
            run.font.color.rgb = BODY

    # ---- Blocks ----

    def add_code(self, code: str) -> None:
        table = self.doc.add_table(rows=1, cols=1)
        cell = table.cell(0, 0)
        _set_cell_bg(cell, HEX_CODE_BG)
        _set_cell_margins(cell, top=120, bottom=120, left=200, right=200)
        _set_cell_borders(cell, left=(HEX_OCRE, 18))
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        for i, line in enumerate(code.strip("\n").splitlines()):
            if i > 0:
                p.add_run().add_break()
            run = p.add_run(line)
            _set_run_font(run, FONT_MONO)
            run.font.size = Pt(9)
            run.font.color.rgb = NAVY_DEEP
        self.doc.add_paragraph()

    def add_callout(self, text: str, kind: str = "info") -> None:
        palette = {
            "info": (HEX_NAVY, "NOTA", NAVY),
            "warn": (HEX_OCRE, "ATENÇÃO", OCRE),
            "ok": ("046A38", "CONFIRMADO", RGBColor(0x04, 0x6A, 0x38)),
        }
        bar_hex, label, color = palette.get(kind, palette["info"])
        table = self.doc.add_table(rows=1, cols=1)
        cell = table.cell(0, 0)
        _set_cell_bg(cell, HEX_CREAM)
        _set_cell_margins(cell, top=160, bottom=160, left=200, right=200)
        _set_cell_borders(cell, left=(bar_hex, 24), top=(HEX_HAIRLINE, 4), bottom=(HEX_HAIRLINE, 4))

        label_p = cell.paragraphs[0]
        label_p.paragraph_format.space_after = Pt(2)
        _styled_run(label_p, label, font=FONT_SANS, size=8, color=color, bold=True, tracking=240, uppercase=True)

        body_p = cell.add_paragraph()
        body_p.paragraph_format.space_after = Pt(0)
        _styled_run(body_p, text, font=FONT_BODY, size=10, color=BODY)
        self.doc.add_paragraph()

    def add_quote(self, text: str, author: str = "") -> None:
        self._vertical_space(Pt(6))

        quote_p = self.doc.add_paragraph()
        quote_p.paragraph_format.left_indent = Cm(0.8)
        quote_p.paragraph_format.right_indent = Cm(0.8)
        quote_p.paragraph_format.space_after = Pt(4)
        _add_left_border(quote_p, HEX_OCRE, size=18)
        _styled_run(quote_p, f"\u201C{text}\u201D", font=FONT_DISPLAY, size=13, color=NAVY_DEEP, italic=True)

        if author:
            attr_p = self.doc.add_paragraph()
            attr_p.paragraph_format.left_indent = Cm(0.8)
            attr_p.paragraph_format.space_before = Pt(2)
            attr_p.paragraph_format.space_after = Pt(8)
            _styled_run(attr_p, "— ", font=FONT_SANS, size=8, color=MUTED, tracking=80)
            _styled_run(attr_p, author, font=FONT_SANS, size=8, color=MUTED, bold=True, tracking=160, uppercase=True)

        self._vertical_space(Pt(4))

    # ---- Data cards ----

    def add_data_cards(self, items: Sequence[tuple[str, str]], columns: int = 2) -> None:
        rows = (len(items) + columns - 1) // columns
        table = self.doc.add_table(rows=rows, cols=columns)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        col_w = Cm(16.5 / columns)
        for col in table.columns:
            col.width = col_w

        for idx, (label, value) in enumerate(items):
            r, c = divmod(idx, columns)
            cell = table.rows[r].cells[c]
            cell.width = col_w
            _set_cell_bg(cell, HEX_CREAM)
            _set_cell_margins(cell, top=200, bottom=200, left=220, right=160)
            is_last_row = r == rows - 1
            is_last_col = c == columns - 1
            _set_cell_borders(
                cell,
                top=(HEX_HAIRLINE, 6),
                bottom=(HEX_OCRE, 8) if is_last_row else (HEX_HAIRLINE, 4),
                left=None,
                right=None if is_last_col else (HEX_HAIRLINE, 4),
            )

            label_p = cell.paragraphs[0]
            label_p.paragraph_format.space_after = Pt(4)
            _styled_run(label_p, label, font=FONT_SANS, size=7, color=MUTED, bold=True, tracking=220, uppercase=True)

            value_p = cell.add_paragraph()
            value_p.paragraph_format.space_after = Pt(0)
            is_mono = any(ch.isdigit() for ch in value) and any(ch in value for ch in "./-R$")
            _styled_run(
                value_p, value,
                font=FONT_MONO if is_mono and len(value) <= 30 else FONT_DISPLAY,
                size=11 if is_mono else 14,
                color=NAVY_DEEP,
                bold=not is_mono,
            )

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
            widths = [Cm(16.5 / cols)] * cols

        header_cells = table.rows[0].cells
        for i, text in enumerate(headers):
            cell = header_cells[i]
            cell.width = widths[i]
            _set_cell_margins(cell, top=140, bottom=140, left=120, right=120)
            _set_cell_borders(
                cell,
                top=(HEX_NAVY, 12),
                bottom=(HEX_NAVY, 6),
                left=None,
                right=None,
            )
            cell.vertical_alignment = WD_ALIGN_VERTICAL.BOTTOM
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            _styled_run(p, text, font=FONT_SANS, size=8, color=NAVY_DEEP, bold=True, tracking=200, uppercase=True)

        for r_idx, row in enumerate(rows):
            row_cells = table.rows[r_idx + 1].cells
            is_last = r_idx == len(rows) - 1
            for c_idx, value in enumerate(row):
                cell = row_cells[c_idx]
                cell.width = widths[c_idx]
                _set_cell_margins(cell, top=110, bottom=110, left=120, right=120)
                _set_cell_borders(
                    cell,
                    top=None,
                    bottom=(HEX_NAVY, 8) if is_last else (HEX_HAIRLINE, 4),
                    left=None,
                    right=None,
                )
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                _styled_run(p, value, font=FONT_BODY, size=10, color=BODY)

        self.doc.add_paragraph()

    # ---- Timeline ----

    def add_timeline(self, events: Sequence[tuple[str, str]]) -> None:
        table = self.doc.add_table(rows=len(events), cols=3)
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        table.autofit = False
        date_w = Cm(3.2)
        bullet_w = Cm(0.9)
        text_w = Cm(12.4)

        for row_idx, (date, desc) in enumerate(events):
            is_last = row_idx == len(events) - 1

            date_cell = table.rows[row_idx].cells[0]
            date_cell.width = date_w
            _set_cell_margins(date_cell, top=80, bottom=80, left=0, right=120)
            _set_cell_borders(date_cell, bottom=(HEX_HAIRLINE, 4) if not is_last else None)
            p = date_cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            _styled_run(p, date, font=FONT_MONO, size=9, color=NAVY, bold=True, tracking=40)

            bullet_cell = table.rows[row_idx].cells[1]
            bullet_cell.width = bullet_w
            _set_cell_margins(bullet_cell, top=80, bottom=80, left=60, right=60)
            _set_cell_borders(bullet_cell, bottom=(HEX_HAIRLINE, 4) if not is_last else None)
            bp = bullet_cell.paragraphs[0]
            bp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            bp.paragraph_format.space_before = Pt(0)
            bp.paragraph_format.space_after = Pt(0)
            _styled_run(bp, "◆", font=FONT_DISPLAY, size=10, color=OCRE, bold=True)

            text_cell = table.rows[row_idx].cells[2]
            text_cell.width = text_w
            _set_cell_margins(text_cell, top=80, bottom=80, left=120, right=0)
            _set_cell_borders(text_cell, bottom=(HEX_HAIRLINE, 4) if not is_last else None)
            tp = text_cell.paragraphs[0]
            tp.paragraph_format.space_before = Pt(0)
            tp.paragraph_format.space_after = Pt(0)
            _styled_run(tp, desc, font=FONT_BODY, size=10, color=BODY)

        self.doc.add_paragraph()

    # ---- KPI ----

    def add_kpi(self, items: Sequence[tuple[str, str, str]]) -> None:
        """Cards de KPI grandes: label em caps + numeral display + descritor."""
        cols = len(items)
        table = self.doc.add_table(rows=1, cols=cols)
        table.autofit = False
        col_w = Cm(16.5 / cols)
        for col in table.columns:
            col.width = col_w

        for idx, (label, value, desc) in enumerate(items):
            cell = table.rows[0].cells[idx]
            cell.width = col_w
            _set_cell_margins(cell, top=200, bottom=200, left=160, right=160)
            _set_cell_borders(
                cell,
                top=(HEX_OCRE, 12),
                bottom=(HEX_HAIRLINE, 4),
                left=None if idx == 0 else (HEX_HAIRLINE, 4),
                right=None,
            )

            label_p = cell.paragraphs[0]
            label_p.paragraph_format.space_after = Pt(4)
            _styled_run(label_p, label, font=FONT_SANS, size=7, color=MUTED, bold=True, tracking=240, uppercase=True)

            value_p = cell.add_paragraph()
            value_p.paragraph_format.space_after = Pt(2)
            _styled_run(value_p, value, font=FONT_DISPLAY, size=26, color=NAVY_DEEP, bold=True)

            desc_p = cell.add_paragraph()
            desc_p.paragraph_format.space_after = Pt(0)
            _styled_run(desc_p, desc, font=FONT_BODY, size=9, color=MUTED, italic=True)

        self.doc.add_paragraph()

    # ---- Signature ----

    def add_signature(self, name: str, role: str = "", local_data: str = "") -> None:
        self._vertical_space(Pt(20))

        if local_data:
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(18)
            _styled_run(p, local_data, font=FONT_BODY, size=11, color=BODY, italic=True)

        line = self.doc.add_paragraph()
        line.alignment = WD_ALIGN_PARAGRAPH.CENTER
        line.paragraph_format.space_after = Pt(2)
        _styled_run(line, "_" * 50, font=FONT_BODY, size=10, color=BODY)

        n = self.doc.add_paragraph()
        n.alignment = WD_ALIGN_PARAGRAPH.CENTER
        n.paragraph_format.space_after = Pt(0)
        _styled_run(n, name, font=FONT_DISPLAY, size=13, color=NAVY_DEEP, bold=True)

        if role:
            r_p = self.doc.add_paragraph()
            r_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_p.paragraph_format.space_before = Pt(0)
            _styled_run(r_p, role, font=FONT_SANS, size=8, color=MUTED, bold=True, tracking=200, uppercase=True)

    # ---- Layout utilities ----

    def _hairline(self, width_cm: float = 16.5, color: str = HEX_OCRE_LIGHT) -> None:
        table = self.doc.add_table(rows=1, cols=1)
        table.autofit = False
        table.columns[0].width = Cm(width_cm)
        cell = table.cell(0, 0)
        cell.width = Cm(width_cm)
        _set_cell_margins(cell, top=0, bottom=0, left=0, right=0)
        _set_cell_borders(cell, top=(color, 6))
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run("")
        run.font.size = Pt(1)

    def _vertical_space(self, size: Pt) -> None:
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = size
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run("")
        run.font.size = Pt(1)

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
