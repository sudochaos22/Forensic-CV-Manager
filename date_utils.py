from __future__ import annotations

from datetime import datetime
import re

PRESENT_WORDS = {"present", "current", "ongoing", "now"}

# Ordered from unambiguous/specific to more general formats.
DATE_FORMATS = (
    "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
    "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y",
    "%m/%d/%y", "%m-%d-%y", "%m.%d.%y",
    "%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y",
    "%d %B %Y", "%d %b %Y",
)
MONTH_FORMATS = (
    "%Y-%m", "%Y/%m", "%Y.%m",
    "%m/%Y", "%m-%Y", "%m.%Y",
    "%m/%y", "%m-%y", "%m.%y",
    "%B %Y", "%b %Y",
)


def normalize_date(value: object, *, allow_present: bool = False, allow_year_only: bool = True) -> str:
    """Normalize common user-entered date formats to ISO text.

    Full dates become YYYY-MM-DD, month/year values become YYYY-MM, and years
    remain YYYY. Present/current terms become ``Present`` when permitted.
    Empty values remain empty.
    """
    text = "" if value is None else str(value).strip()
    if not text:
        return ""

    lowered = text.lower().rstrip(".")
    if allow_present and lowered in PRESENT_WORDS:
        return "Present"

    # Tolerate commas and repeated whitespace in written dates.
    cleaned = re.sub(r"\s+", " ", text.replace(",", ", ")).strip()
    cleaned = re.sub(r",\s+", ", ", cleaned)

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    for fmt in MONTH_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m")
        except ValueError:
            pass

    if allow_year_only and re.fullmatch(r"(?:19|20)\d{2}", cleaned):
        return cleaned

    raise ValueError(
        f'"{text}" is not a recognized date. Examples: 3/5/2026, '
        "03-05-2026, 2026-03-05, March 5, 2026, March 2026, or 2026."
    )


def date_sort_key(value: object, *, present_is_latest: bool = False) -> tuple[int, int, int, str]:
    text = "" if value is None else str(value).strip()
    if not text:
        return (0, 0, 0, "")
    if text.lower() in PRESENT_WORDS or text.lower() == "present":
        return (9999, 12, 31, text) if present_is_latest else (0, 0, 0, text)
    try:
        normalized = normalize_date(text, allow_present=present_is_latest)
    except ValueError:
        return (0, 0, 0, text.lower())
    if normalized == "Present":
        return (9999, 12, 31, normalized)
    parts = normalized.split("-")
    year = int(parts[0])
    month = int(parts[1]) if len(parts) > 1 else 1
    day = int(parts[2]) if len(parts) > 2 else 1
    return (year, month, day, normalized)


def display_date(value: object, *, month_only: bool = False) -> str:
    """Return a readable date while preserving partial-date precision."""
    text = "" if value is None else str(value).strip()
    if not text:
        return ""
    if text.lower() in PRESENT_WORDS or text.lower() == "present":
        return "Present"
    try:
        normalized = normalize_date(text)
    except ValueError:
        return text
    parts = normalized.split("-")
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return datetime.strptime(normalized, "%Y-%m").strftime("%B %Y")
    dt = datetime.strptime(normalized, "%Y-%m-%d")
    return dt.strftime("%B %Y" if month_only else "%B %-d, %Y") if __import__('os').name != 'nt' else dt.strftime("%B %#d, %Y" if not month_only else "%B %Y")
