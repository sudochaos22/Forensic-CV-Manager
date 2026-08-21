from __future__ import annotations

import sys
from datetime import date
from typing import Any
import tkinter as tk
from tkinter import ttk

import database as database_module
import professional_v25 as v25

PATCH_VERSION = "2.5.1"

TRAINING_PROVIDERS = [
    "", "Carnegie Mellon", "CISA", "DC3", "DCSA", "EC-Council",
    "Magnet Forensics", "SANS", "Skillsoft", "Mandiant", "ISC2", "CompTIA",
]

TRAINING_CATEGORIES = [
    "", "Windows Forensics", "Mac Forensics", "iPhone Forensics", "Android Forensics",
    "Linux Forensics", "Cyber", "Cyber Threat Intelligence",
    "Insider Threat", "AI",
]

CASEWORK_COLUMNS = {
    "evidence_size_gb": "REAL",
    "image_date": "TEXT",
    "image_time_minutes": "REAL",
    "process_date": "TEXT",
    "process_time_minutes": "REAL",
    "artifacts_identified": "INTEGER",
}

CASEWORK_NEW_FIELDS = list(CASEWORK_COLUMNS)

_DB_INSTALLED = False
_APP_INSTALLED = False


def _insert_before_sort_order(fields, field):
    if field in fields:
        return
    if "sort_order" in fields:
        fields.insert(fields.index("sort_order"), field)
    else:
        fields.append(field)


def install_database_extensions():
    global _DB_INSTALLED
    if _DB_INSTALLED:
        return

    fields = database_module.TABLE_FIELDS.setdefault("casework", [])
    for field in CASEWORK_NEW_FIELDS:
        _insert_before_sort_order(fields, field)

    Database = database_module.Database
    previous_migrate = Database._migrate_schema

    def migrate(self):
        previous_migrate(self)
        if self._table_exists("casework"):
            existing = set(self._columns("casework"))
            for name, sql_type in CASEWORK_COLUMNS.items():
                if name not in existing:
                    self.conn.execute(f"ALTER TABLE casework ADD COLUMN {name} {sql_type}")
            self.conn.commit()
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO schema_meta(key,value) VALUES('professional_version',?)",
                (PATCH_VERSION,),
            )
            self.conn.commit()
        except Exception:
            pass

    Database._migrate_schema = migrate
    _DB_INSTALLED = True


def _replace_field(config, name, replacement):
    fields = config.get("fields", [])
    for index, field in enumerate(fields):
        if field[0] == name:
            fields[index] = replacement
            return
    fields.append(replacement)


def _insert_after(config, after_name, field_tuple):
    fields = config.get("fields", [])
    if any(field[0] == field_tuple[0] for field in fields):
        return
    for index, field in enumerate(fields):
        if field[0] == after_name:
            fields.insert(index + 1, field_tuple)
            return
    fields.append(field_tuple)


def extend_table_config(table_config, date_fields):
    date_fields.update({"image_date", "process_date"})

    training = table_config.get("training")
    if training:
        _replace_field(training, "provider",
                       ("provider", "Provider", "combo", list(TRAINING_PROVIDERS)))
        _replace_field(training, "category",
                       ("category", "Category", "combo", list(TRAINING_CATEGORIES)))

    casework = table_config.get("casework")
    if not casework:
        return

    fields = casework.get("fields", [])
    for index, field in enumerate(fields):
        if field[0] == "device_type" and len(field) >= 4:
            values = list(field[3])
            if "PST" not in values:
                if "Cloud Account" in values:
                    values.insert(values.index("Cloud Account"), "PST")
                else:
                    values.append("PST")
            fields[index] = (field[0], field[1], field[2], values)
            break

    _insert_after(casework, "device_size",
                  ("evidence_size_gb", "Evidence Size (GB)", "entry"))

    image_anchor = "image_format" if any(f[0] == "image_format" for f in fields) else "acquisition_type"
    _insert_after(casework, image_anchor,
                  ("image_date", "Image Date", "entry"))
    _insert_after(casework, "image_date",
                  ("image_time_minutes", "Image Time (Minutes)", "entry"))

    process_anchor = "data_examined" if any(f[0] == "data_examined" for f in fields) else "image_time_minutes"
    _insert_after(casework, process_anchor,
                  ("process_date", "Process Date", "entry"))
    _insert_after(casework, "process_date",
                  ("process_time_minutes", "Process Time (Minutes)", "entry"))
    _insert_after(casework, "process_time_minutes",
                  ("artifacts_identified", "Artifacts Identified", "entry"))


class V251RecordDialog(v25.EnhancedRecordDialog):
    def __init__(self, parent, table, config, initial=None):
        super().__init__(parent, table, config, initial)
        if table == "training":
            for field in ("provider", "category"):
                widget = self.widgets.get(field)
                if isinstance(widget, ttk.Combobox):
                    widget.configure(state="normal")


def _year(value):
    text = str(value or "").strip()
    if len(text) < 4:
        return None
    try:
        return int(text[:4])
    except ValueError:
        return None


def _number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def current_year_casework_stats(db, year=None):
    year = int(year or date.today().year)
    image_minutes = 0.0
    process_minutes = 0.0
    analyzed_gb = 0.0

    try:
        rows = db.list_rows("casework")
    except Exception:
        rows = []

    for row in rows:
        if _year(row.get("image_date")) == year:
            image_minutes += _number(row.get("image_time_minutes"))
        if _year(row.get("process_date")) == year:
            process_minutes += _number(row.get("process_time_minutes"))
            analyzed_gb += _number(row.get("evidence_size_gb"))

    return {
        "image_minutes": image_minutes,
        "process_minutes": process_minutes,
        "analyzed_gb": analyzed_gb,
    }


def format_minutes(value):
    total = max(0, int(round(float(value or 0))))
    days, remainder = divmod(total, 1440)
    hours, minutes = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m"


def format_gb(value_gb):
    gb = max(0.0, float(value_gb or 0))
    if gb == 0:
        return "0 GB"

    size = gb * (1024 ** 3)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            break
        size /= 1024

    if size >= 100:
        return f"{size:,.0f} {unit}"
    if size >= 10:
        return f"{size:,.1f} {unit}"
    return f"{size:,.2f} {unit}"


def install_app_extensions(App):
    global _APP_INSTALLED
    if _APP_INSTALLED:
        return

    app_module = sys.modules.get(App.__module__)
    if app_module is None:
        raise RuntimeError("Could not resolve the application module.")

    install_database_extensions()
    extend_table_config(app_module.TABLE_CONFIG, app_module.DATE_FIELDS)

    v25.FLOAT_FIELDS.update(
        {"evidence_size_gb", "image_time_minutes", "process_time_minutes"}
    )
    v25.INT_FIELDS.add("artifacts_identified")
    v25.ALL_DATE_FIELDS.update({"image_date", "process_date"})

    v25.EnhancedRecordDialog = V251RecordDialog
    app_module.RecordDialog = V251RecordDialog

    previous_dashboard = App.refresh_dashboard

    def refresh_dashboard(self):
        previous_dashboard(self)

        year = date.today().year
        stats = current_year_casework_stats(self.db, year)
        additions = [
            (f"{year} Imaging Time", format_minutes(stats["image_minutes"])),
            (f"{year} Processing Time", format_minutes(stats["process_minutes"])),
            (f"{year} Data Analyzed", format_gb(stats["analyzed_gb"])),
        ]

        for i, (label, value) in enumerate(additions):
            box = ttk.LabelFrame(self.metrics_frame, text=label, padding=7)
            box.grid(row=2, column=i, padx=4, pady=4, sticky="nsew")
            ttk.Button(
                box,
                text=value,
                command=lambda: v25.navigate_to_record(self, "casework"),
            ).pack(fill="both", expand=True)
            self.metrics_frame.columnconfigure(i, weight=1)

        try:
            self.summary_text.config(state="normal")
            self.summary_text.insert(
                "end",
                "\nCurrent-year forensic processing metrics\n",
                "heading",
            )
            self.summary_text.insert(
                "end",
                f"{year} imaging time: {format_minutes(stats['image_minutes'])}\n"
                f"{year} processing time: {format_minutes(stats['process_minutes'])}\n"
                f"{year} data analyzed: {format_gb(stats['analyzed_gb'])}\n",
            )
            self.summary_text.config(state="disabled")
        except Exception:
            pass

    App.refresh_dashboard = refresh_dashboard

    previous_init = App.__init__

    def init(self, *args, **kwargs):
        previous_init(self, *args, **kwargs)
        try:
            self.title(f"Forensic CV Manager Professional {PATCH_VERSION}")
        except Exception:
            pass

    App.__init__ = init
    _APP_INSTALLED = True
