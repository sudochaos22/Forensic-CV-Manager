from __future__ import annotations

import html
import re
from datetime import date
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, KeepTogether, PageTemplate, Paragraph,
    Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem,
)

from cv_data import build_cv_data, full_text, pretty_date
from database import Database

PDF_THEMES = {
    "Professional": {"primary": colors.HexColor("#1F4E79"), "accent": colors.HexColor("#D9EAF7"), "font": "Helvetica", "title": 18},
    "Court Testimony": {"primary": colors.HexColor("#202020"), "accent": colors.HexColor("#E8E8E8"), "font": "Times-Roman", "title": 17},
    "Executive": {"primary": colors.HexColor("#30343B"), "accent": colors.HexColor("#DDE2E7"), "font": "Helvetica", "title": 20},
    "Academic": {"primary": colors.HexColor("#4A285F"), "accent": colors.HexColor("#EAE0EF"), "font": "Times-Roman", "title": 18},
    "Law Enforcement": {"primary": colors.HexColor("#17365D"), "accent": colors.HexColor("#DCE6F1"), "font": "Helvetica", "title": 18},
}


def _safe(value: Any) -> str:
    return html.escape(full_text(value)).replace("\n", "<br/>")


def _linkify_contact(value: str) -> str:
    escaped = html.escape(value)
    if "@" in value and " " not in value:
        return f'<link href="mailto:{escaped}" color="#1F4E79">{escaped}</link>'
    if re.match(r"^https?://", value, re.I):
        return f'<link href="{escaped}" color="#1F4E79">{escaped}</link>'
    return escaped


class NumberedDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, *, theme: dict[str, Any], metadata: dict[str, str]):
        super().__init__(filename, pagesize=LETTER, rightMargin=.62*inch, leftMargin=.62*inch,
                         topMargin=.58*inch, bottomMargin=.58*inch,
                         title=metadata.get("title", "Curriculum Vitae"),
                         author=metadata.get("author", ""), subject=metadata.get("subject", ""),
                         keywords=metadata.get("keywords", ""))
        self.theme = theme
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates(PageTemplate(id="cv", frames=frame, onPage=self._on_page))

    def _on_page(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(self.leftMargin, .32*inch, f"Generated {date.today().strftime('%B %d, %Y')}")
        canvas.drawRightString(LETTER[0] - self.rightMargin, .32*inch, f"Page {doc.page}")
        canvas.restoreState()


def _styles(theme: dict[str, Any]):
    base = getSampleStyleSheet()
    body_font = theme["font"]
    bold_font = "Helvetica-Bold" if body_font == "Helvetica" else "Times-Bold"
    return {
        "name": ParagraphStyle("Name", parent=base["Normal"], fontName=bold_font, fontSize=theme["title"], leading=theme["title"]+2, alignment=TA_CENTER, textColor=theme["primary"], spaceAfter=2),
        "title": ParagraphStyle("Title", parent=base["Normal"], fontName=bold_font, fontSize=11, leading=13, alignment=TA_CENTER, spaceAfter=2),
        "contact": ParagraphStyle("Contact", parent=base["Normal"], fontName=body_font, fontSize=9, leading=11, alignment=TA_CENTER, spaceAfter=7),
        "section": ParagraphStyle("Section", parent=base["Normal"], fontName=bold_font, fontSize=11, leading=13, textColor=theme["primary"], spaceBefore=7, spaceAfter=3),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontName=body_font, fontSize=9.3, leading=12, alignment=TA_LEFT, spaceAfter=2),
        "bold": ParagraphStyle("Bold", parent=base["Normal"], fontName=bold_font, fontSize=9.3, leading=12, spaceBefore=3, spaceAfter=1),
        "small": ParagraphStyle("Small", parent=base["Normal"], fontName=body_font, fontSize=8.3, leading=10),
    }


def _section(story, title: str, styles, theme):
    story.append(Paragraph(html.escape(title.upper()), styles["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=theme["primary"], spaceAfter=4))


def _bullets(lines, styles):
    items = [ListItem(Paragraph(_safe(line), styles["body"]), leftIndent=10) for line in lines if full_text(line).strip()]
    return ListFlowable(items, bulletType="bullet", leftIndent=18, bulletFontName="Helvetica", bulletFontSize=7, spaceAfter=2)


def generate_pdf(db: Database, output_path: str | Path, options: dict[str, Any] | None = None, *, theme_name: str = "Professional") -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    data = build_cv_data(db, options)
    profile = data["profile"]
    sections = data["sections"]
    theme = PDF_THEMES.get(theme_name, PDF_THEMES["Professional"])
    styles = _styles(theme)
    author = full_text(profile.get("full_name"))
    metadata = {
        "title": f"Curriculum Vitae - {author}" if author else "Curriculum Vitae",
        "author": author,
        "subject": "Professional curriculum vitae and qualifications",
        "keywords": "curriculum vitae, digital forensics, training, certifications, testimony",
    }
    doc = NumberedDocTemplate(str(output), theme=theme, metadata=metadata)
    story = []

    story.append(Paragraph(_safe(profile.get("full_name")), styles["name"]))
    if profile.get("title"):
        story.append(Paragraph(_safe(profile.get("title")), styles["title"]))
    contact_parts = [_linkify_contact(full_text(x)) for x in [profile.get("agency"), profile.get("email"), profile.get("phone")] if x]
    story.append(Paragraph(" &nbsp;|&nbsp; ".join(contact_parts), styles["contact"]))

    if sections.get("summary"):
        _section(story, "Professional Summary", styles, theme)
        story.append(Paragraph(_safe(sections["summary"]), styles["body"]))

    rows = sections.get("core_training", [])
    if rows:
        _section(story, "Core Training", styles, theme)
        story.append(_bullets([
            f"{full_text(x.get('course_name'))}{' (' + full_text(x.get('provider')) + ')' if x.get('provider') else ''}, {pretty_date(full_text(x.get('attended_date')))}".strip(", ")
            for x in rows
        ], styles))

    rows = sections.get("employment", [])
    if rows:
        _section(story, "Work Experience", styles, theme)
        for x in rows:
            period = " to ".join(filter(None, [pretty_date(x.get("start_date"), True), pretty_date(x.get("end_date"), True)]))
            heading = f"{period} - {full_text(x.get('employer'))} ({full_text(x.get('title'))})"
            block = [Paragraph(_safe(heading), styles["bold"])]
            desc_lines = full_text(x.get("description")).splitlines()
            if desc_lines:
                block.append(_bullets(desc_lines, styles))
            story.append(KeepTogether(block))

    rows = sections.get("teaching", [])
    if rows:
        _section(story, "Teaching Experience", styles, theme)
        for x in rows:
            period = "-".join(filter(None, [full_text(x.get("start_date")), full_text(x.get("end_date"))]))
            heading = f"{full_text(x.get('organization'))} - {full_text(x.get('role'))}: {full_text(x.get('course_name'))} ({period})"
            story.append(Paragraph(_safe(heading), styles["bold"]))
            if x.get("description"):
                story.append(_bullets(full_text(x["description"]).splitlines(), styles))

    rows = sections.get("organizations", [])
    if rows:
        _section(story, "Professional Organizations", styles, theme)
        story.append(_bullets([
            f"{'-'.join(filter(None, [full_text(x.get('start_year')), full_text(x.get('end_year'))]))} {full_text(x.get('organization'))}{' - ' + full_text(x.get('role')) if x.get('role') else ''}"
            for x in rows
        ], styles))

    rows = sections.get("certifications", [])
    if rows:
        _section(story, "Digital Forensic Certifications", styles, theme)
        story.append(_bullets([
            f"{full_text(x.get('certification'))}, {full_text(x.get('issuing_organization'))} {pretty_date(full_text(x.get('earned_date')))}{' (expires ' + pretty_date(full_text(x.get('expiration_date'))) + ')' if x.get('expiration_date') else ''}".strip()
            for x in rows
        ], styles))

    skill_groups = sections.get("skills", {})
    if skill_groups:
        _section(story, "Relevant Skills and Tools", styles, theme)
        for cat, values in skill_groups.items():
            text = "; ".join(full_text(v.get("skill")) for v in values)
            story.append(Paragraph(f"<b>{html.escape(cat)}:</b> {_safe(text)}", styles["body"]))

    rows = sections.get("education", [])
    if rows:
        _section(story, "Education", styles, theme)
        story.append(_bullets([
            f"{full_text(x.get('degree'))} - {full_text(x.get('institution'))}, {full_text(x.get('graduation_date'))}{' (' + full_text(x.get('honors')) + ')' if x.get('honors') else ''}"
            for x in rows
        ], styles))

    testimony = sections.get("testimony", {})
    if any(testimony.values()) if testimony else False:
        _section(story, "Courtroom Testimony", styles, theme)
        for kind in ("Expert Witness", "Fact Witness"):
            subset = testimony.get(kind, [])
            if subset:
                story.append(Paragraph(html.escape(kind), styles["bold"]))
                story.append(_bullets([
                    f"SA# {full_text(x.get('case_number'))}, {full_text(x.get('court'))} {full_text(x.get('jurisdiction'))}, {pretty_date(x.get('testimony_date'))}"
                    for x in subset
                ], styles))

    stats = sections.get("casework_summary", {})

    if stats and stats.get("examinations", 0):
        _section(
            story,
            "Digital Forensic Case Work",
            styles,
            theme
        )

        summary_lines = [
            f"Unique cases documented: {stats.get('unique_cases', 0):,}",
            f"Forensic examinations performed: {stats.get('examinations', 0):,}",
            f"Total documented examination hours: {stats.get('total_hours', 0):,.1f}",
            f"Reports written: {stats.get('reports_written', 0):,}",
            f"Examinations involving testimony: {stats.get('testified', 0):,}",
        ]

        story.append(_bullets(summary_lines, styles))

        device_types = stats.get("device_types", {})

        if device_types:
            story.append(
                Paragraph(
                    "<b>Device Types</b>",
                    styles["bold"]
                )
            )

            story.append(
                _bullets(
                    [
                        f"{name}: {count:,}"
                        for name, count in device_types.items()
                    ],
                    styles
                )
            )

        case_types = stats.get("case_types", {})

        if case_types:
            story.append(
                Paragraph(
                    "<b>Case Types</b>",
                    styles["bold"]
                )
            )

            story.append(
                _bullets(
                    [
                        f"{name}: {count:,}"
                        for name, count in case_types.items()
                    ],
                    styles
                )
            )

        tools = stats.get("tools", {})

        if tools:
            story.append(
                Paragraph(
                    "<b>Forensic Tools Utilized</b>",
                    styles["bold"]
                )
            )

            story.append(
                _bullets(
                    [
                        f"{name}: {count:,} examination(s)"
                        for name, count in tools.items()
                    ],
                    styles
                )
            )

    rows = sections.get("achievements", [])
    if rows:
        _section(story, "Professional Achievements", styles, theme)
        for x in rows:
            line = f"{pretty_date(x.get('achievement_date'))} - {full_text(x.get('achievement'))}"
            if x.get("organization"):
                line += f", {full_text(x.get('organization'))}"
            story.append(Paragraph(_safe(line), styles["bold"]))
            if x.get("description"):
                story.append(Paragraph(_safe(x.get("description")), styles["body"]))

    training = sections.get("full_training")
    if training and training.get("rows"):
        story.append(PageBreak())
        _section(story, "Training Courses", styles, theme)
        story.append(Paragraph(f"<b>Documented training hours in database:</b> {training['total_hours']:,.2f}", styles["body"]))
        table_data = [[Paragraph("<b>Date</b>", styles["small"]), Paragraph("<b>Course</b>", styles["small"]), Paragraph("<b>Provider</b>", styles["small"]), Paragraph("<b>Hours</b>", styles["small"])]]
        for x in training["rows"]:
            table_data.append([
                Paragraph(_safe(x.get("attended_date")), styles["small"]),
                Paragraph(_safe(x.get("course_name")), styles["small"]),
                Paragraph(_safe(x.get("provider")), styles["small"]),
                Paragraph("" if x.get("hours") is None else _safe(x.get("hours")), styles["small"]),
            ])
        table = Table(table_data, colWidths=[.95*inch, 3.65*inch, 1.55*inch, .6*inch], repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), theme["accent"]),
            ("TEXTCOLOR", (0,0), (-1,0), theme["primary"]),
            ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#A0A0A0")),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        story.append(table)

    doc.build(story)
    return output


# Backward-compatible alias for callers introduced before native PDF support.
def convert_docx_to_pdf(*args, **kwargs):
    raise RuntimeError("DOCX conversion is no longer used. Generate PDF directly with generate_pdf().")
