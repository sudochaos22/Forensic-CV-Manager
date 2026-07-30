from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from database import Database
from date_utils import date_sort_key, display_date

NAVY = RGBColor(31, 78, 121)
DARK = RGBColor(45, 45, 45)


def full_text(value: Any) -> str:
    """Return the complete stored value without clipping or abbreviation."""
    return "" if value is None else str(value)


def date_key(value: Any, present_is_latest: bool = False) -> tuple[int, int, int, str]:
    """Create a stable descending sort key for accepted date formats."""
    return date_sort_key(value, present_is_latest=present_is_latest)


def sorted_by_date(rows: Iterable[dict[str, Any]], field: str, *, present_is_latest: bool = False) -> list[dict[str, Any]]:
    """Sort newest-to-oldest, using sort_order and id only as tie breakers."""
    return sorted(
        rows,
        key=lambda row: (
            date_key(row.get(field), present_is_latest),
            -int(row.get("sort_order") or 0),
            -int(row.get("id") or 0),
        ),
        reverse=True,
    )


def add_complete_text(doc: Document, text: Any, *, bullet: bool = False) -> None:
    """Write all stored characters, preserving user-entered line breaks."""
    value = full_text(text)
    lines = value.splitlines() or [value]
    for line in lines:
        if bullet:
            add_bullet(doc, line)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(1)
            p.add_run(line)


def pretty_date(value: str | None, month_only: bool = False) -> str:
    return display_date(value, month_only=month_only)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), fill)
    tc_pr.append(shd)


def add_section_heading(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text.upper())
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = NAVY
    p_pr = p._p.get_or_add_pPr()
    bottom = OxmlElement('w:pBdr')
    border = OxmlElement('w:bottom')
    border.set(qn('w:val'), 'single')
    border.set(qn('w:sz'), '8')
    border.set(qn('w:space'), '1')
    border.set(qn('w:color'), '1F4E79')
    bottom.append(border)
    p_pr.append(bottom)


def add_bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.first_line_indent = Inches(-0.15)
    p.add_run(text)


def generate_cv(db: Database, output_path: str | Path, options: dict[str, Any] | None = None) -> Path:
    options = options or {}
    output_path = Path(output_path)
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)

    styles = doc.styles
    styles['Normal'].font.name = 'Aptos'
    styles['Normal'].font.size = Pt(9.5)
    styles['Normal'].font.color.rgb = DARK

    profile = db.get_profile()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(profile.get('full_name', ''))
    r.bold = True
    r.font.size = Pt(18)
    r.font.color.rgb = NAVY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(profile.get('title', ''))
    r.bold = True
    r.font.size = Pt(11)

    contact = " | ".join(x for x in [profile.get('agency'), profile.get('email'), profile.get('phone')] if x)
    p = doc.add_paragraph(contact)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(5)

    if options.get('summary', True) and profile.get('summary'):
        add_section_heading(doc, "Professional Summary")
        add_complete_text(doc, profile['summary'])

    if options.get('core_training', True):
        core = sorted_by_date([x for x in db.list_rows('training') if x.get('core_training')], 'attended_date')
        if core:
            add_section_heading(doc, "Core Training")
            for x in core:
                attended = pretty_date(full_text(x.get('attended_date')))
                provider = f" ({full_text(x.get('provider'))})" if x.get('provider') else ''
                add_bullet(doc, f"{full_text(x.get('course_name'))}{provider}, {attended}".strip(', '))

    if options.get('employment', True):
        rows = sorted(db.list_rows('employment'), key=lambda x: (date_key(x.get('end_date'), True), date_key(x.get('start_date'))), reverse=True)
        if rows:
            add_section_heading(doc, "Work Experience")
            for x in rows:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(1)
                period = " to ".join(filter(None, [pretty_date(x.get('start_date'), True), pretty_date(x.get('end_date'), True)]))
                r = p.add_run(f"{period} - {x.get('employer')} ({x.get('title')})")
                r.bold = True
                add_complete_text(doc, x.get('description'), bullet=True)

    if options.get('teaching', True):
        rows = sorted_by_date(db.list_rows('teaching'), 'start_date')
        if rows:
            add_section_heading(doc, "Teaching Experience")
            for x in rows:
                period = "-".join(filter(None, [x.get('start_date'), x.get('end_date')]))
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(1)
                r = p.add_run(f"{x.get('organization')} - {x.get('role')}: {x.get('course_name')} ({period})")
                r.bold = True
                if x.get('description'):
                    add_complete_text(doc, x['description'], bullet=True)

    if options.get('organizations', True):
        rows = sorted_by_date(db.list_rows('organizations'), 'start_year')
        if rows:
            add_section_heading(doc, "Professional Organizations")
            for x in rows:
                years = "-".join(filter(None, [x.get('start_year'), x.get('end_year')]))
                role = f" - {x.get('role')}" if x.get('role') else ''
                add_bullet(doc, f"{years} {x.get('organization')}{role}")

    if options.get('certifications', True):
        rows = sorted_by_date(db.list_rows('certifications'), 'earned_date')
        if rows:
            add_section_heading(doc, "Digital Forensic Certifications")
            for x in rows:
                earned = pretty_date(full_text(x.get('earned_date')))
                expires = f" (expires {pretty_date(full_text(x.get('expiration_date')))})" if x.get('expiration_date') else ''
                add_bullet(doc, f"{full_text(x.get('certification'))}, {full_text(x.get('issuing_organization'))} {earned}{expires}".strip())

    if options.get('skills', True):
        rows = db.list_rows('skills')
        if rows:
            add_section_heading(doc, "Relevant Skills and Tools")
            by_cat: dict[str, list[str]] = {}
            for x in rows:
                by_cat.setdefault(x.get('category') or 'Other', []).append(x.get('skill', ''))
            for cat, values in by_cat.items():
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(1)
                r = p.add_run(f"{cat}: ")
                r.bold = True
                p.add_run('; '.join(values))

    if options.get('education', True):
        rows = sorted_by_date(db.list_rows('education'), 'graduation_date')
        if rows:
            add_section_heading(doc, "Education")
            for x in rows:
                honors = f" ({x.get('honors')})" if x.get('honors') else ''
                add_bullet(doc, f"{x.get('degree')} - {x.get('institution')}, {x.get('graduation_date')}{honors}")

    if options.get('testimony', True):
        rows = sorted_by_date(db.list_rows('testimony'), 'testimony_date')
        if rows:
            add_section_heading(doc, "Courtroom Testimony")
            for kind in ('Expert Witness', 'Fact Witness'):
                subset = [x for x in rows if x.get('witness_type') == kind]
                if not subset:
                    continue
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(1)
                r = p.add_run(kind)
                r.bold = True
                for x in subset:
                    add_bullet(doc, f"SA# {x.get('case_number')}, {x.get('court')} {x.get('jurisdiction')}, {pretty_date(x.get('testimony_date'))}")

    if options.get('full_training', False):
        rows = sorted_by_date(db.list_rows('training'), 'attended_date')
        if rows:
            doc.add_section(WD_SECTION.NEW_PAGE)
            add_section_heading(doc, "Training Courses")
            total = sum(float(x.get('hours') or 0) for x in rows)
            p = doc.add_paragraph(f"Documented training hours in database: {total:,.2f}")
            p.runs[0].bold = True
            table = doc.add_table(rows=1, cols=4)
            table.style = 'Table Grid'
            headers = ['Date', 'Course', 'Provider', 'Hours']
            for i, h in enumerate(headers):
                table.rows[0].cells[i].text = h
                set_cell_shading(table.rows[0].cells[i], 'D9EAF7')
                for run in table.rows[0].cells[i].paragraphs[0].runs:
                    run.bold = True
            for x in rows:
                cells = table.add_row().cells
                vals = [full_text(x.get('attended_date')), full_text(x.get('course_name')), full_text(x.get('provider')), '' if x.get('hours') is None else full_text(x.get('hours'))]
                for i, val in enumerate(vals):
                    cells[i].text = val

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer.add_run(f"Generated {date.today().strftime('%B %d, %Y')}").font.size = Pt(8)

    doc.save(output_path)
    return output_path
