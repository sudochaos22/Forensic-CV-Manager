from __future__ import annotations

from typing import Any, Iterable
from database import Database
from date_utils import date_sort_key, display_date


def full_text(value: Any) -> str:
    return "" if value is None else str(value)


def date_key(value: Any, present_is_latest: bool = False):
    return date_sort_key(value, present_is_latest=present_is_latest)


def sorted_by_date(rows: Iterable[dict[str, Any]], field: str, *, present_is_latest: bool = False) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            date_key(row.get(field), present_is_latest),
            -int(row.get("sort_order") or 0),
            -int(row.get("id") or 0),
        ),
        reverse=True,
    )


def pretty_date(value: str | None, month_only: bool = False) -> str:
    return display_date(value, month_only=month_only)


def build_cv_data(db: Database, options: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build one renderer-neutral representation of the selected CV."""
    options = options or {}
    profile = db.get_profile()
    data: dict[str, Any] = {"profile": profile, "options": options, "sections": {}}
    sections = data["sections"]

    if options.get("summary", True) and profile.get("summary"):
        sections["summary"] = full_text(profile["summary"])

    if options.get("core_training", True):
        sections["core_training"] = sorted_by_date(
            [x for x in db.list_rows("training") if x.get("core_training")], "attended_date"
        )

    if options.get("employment", True):
        sections["employment"] = sorted(
            db.list_rows("employment"),
            key=lambda x: (date_key(x.get("end_date"), True), date_key(x.get("start_date"))),
            reverse=True,
        )

    if options.get("teaching", True):
        sections["teaching"] = sorted_by_date(db.list_rows("teaching"), "start_date")

    if options.get("organizations", True):
        sections["organizations"] = sorted_by_date(db.list_rows("organizations"), "start_year")

    if options.get("certifications", True):
        sections["certifications"] = sorted_by_date(db.list_rows("certifications"), "earned_date")

    if options.get("skills", True):
        by_category: dict[str, list[dict[str, Any]]] = {}
        for row in db.list_rows("skills"):
            by_category.setdefault(row.get("category") or "Other", []).append(row)
        sections["skills"] = by_category

    if options.get("education", True):
        sections["education"] = sorted_by_date(db.list_rows("education"), "graduation_date")

    if options.get("testimony", True):
        rows = sorted_by_date(db.list_rows("testimony"), "testimony_date")
        sections["testimony"] = {
            "Expert Witness": [x for x in rows if x.get("witness_type") == "Expert Witness"],
            "Fact Witness": [x for x in rows if x.get("witness_type") == "Fact Witness"],
        }

    if options.get("achievements", True):
        sections["achievements"] = sorted_by_date(db.list_rows("achievements"), "achievement_date")

    if options.get("full_training", False):
        rows = sorted_by_date(db.list_rows("training"), "attended_date")
        sections["full_training"] = {
            "rows": rows,
            "total_hours": sum(float(x.get("hours") or 0) for x in rows),
        }

    return data
