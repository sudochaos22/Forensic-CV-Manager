from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import webbrowser
import json
from datetime import date, datetime
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from database import Database
from seed_data import seed
from sample_data import load_sample_profile
from profile_io import export_profile, import_profile
from pdf_export import generate_pdf
from update_checker import check_github_release
from app_config import APP_NAME, APP_VERSION, GITHUB_REPOSITORY
from cv_generator import generate_cv
from date_utils import normalize_date, date_sort_key
from ui_modern import SplashScreen, PdfPreviewWindow, make_preview_temp_path, resource_path

DATE_FIELDS = {"start_date", "end_date", "graduation_date", "attended_date", "expiration_date", "earned_date", "testimony_date", "achievement_date"}
YEAR_FIELDS = {"start_year", "end_year"}

TABLE_CONFIG = {
    "employment": {
        "label": "Employment",
        "display": ["employer", "title", "start_date", "end_date"],
        "fields": [("employer", "Employer", "entry"), ("title", "Title", "entry"), ("start_date", "Start Date", "entry"), ("end_date", "End Date", "entry"), ("location", "Location", "entry"), ("description", "Description / Duties", "text")],
    },
    "education": {
        "label": "Education",
        "display": ["degree", "institution", "graduation_date", "honors"],
        "fields": [("degree", "Degree / Program", "entry"), ("institution", "Institution", "entry"), ("graduation_date", "Graduation Date", "entry"), ("honors", "Honors", "entry"), ("notes", "Notes", "text")],
    },
    "training": {
        "label": "Training",
        "display": ["attended_date", "course_name", "provider", "hours", "core_training"],
        "fields": [("attended_date", "Date Attended", "entry"), ("course_name", "Course Name", "entry"), ("provider", "Provider", "entry"), ("hours", "Hours", "entry"), ("category", "Category", "entry"), ("certificate_number", "Certificate Number", "entry"), ("expiration_date", "Expiration Date", "entry"), ("core_training", "Include in Core Training", "check"), ("notes", "Notes", "text")],
    },
    "certifications": {
        "label": "Certifications",
        "display": ["certification", "issuing_organization", "earned_date", "expiration_date", "status"],
        "fields": [("certification", "Certification", "entry"), ("issuing_organization", "Issuing Organization", "entry"), ("earned_date", "Earned Date", "entry"), ("expiration_date", "Expiration Date", "entry"), ("credential_number", "Credential Number", "entry"), ("status", "Status", "entry"), ("notes", "Notes", "text")],
    },
    "testimony": {
        "label": "Courtroom Testimony",
        "display": ["testimony_date", "case_number", "court", "witness_type"],
        "fields": [("testimony_date", "Testimony Date", "entry"), ("case_number", "Case Number", "entry"), ("court", "Court", "entry"), ("jurisdiction", "Jurisdiction", "entry"), ("witness_type", "Witness Type", "combo", ["Fact Witness", "Expert Witness"]), ("party", "Party", "entry"), ("subject", "Subject / Discipline", "entry"), ("outcome", "Outcome", "entry"), ("notes", "Notes", "text")],
    },
    "teaching": {
        "label": "Teaching",
        "display": ["organization", "role", "course_name", "start_date", "end_date"],
        "fields": [("organization", "Organization", "entry"), ("role", "Role", "entry"), ("course_name", "Course", "entry"), ("start_date", "Start Date", "entry"), ("end_date", "End Date", "entry"), ("hours", "Hours", "entry"), ("description", "Description", "text")],
    },
    "organizations": {
        "label": "Organizations",
        "display": ["organization", "role", "start_year", "end_year"],
        "fields": [("organization", "Organization", "entry"), ("role", "Role", "entry"), ("start_year", "Start Year", "entry"), ("end_year", "End Year", "entry"), ("notes", "Notes", "text")],
    },
    "skills": {
        "label": "Skills & Tools",
        "display": ["skill", "category", "proficiency"],
        "fields": [("skill", "Skill / Tool", "entry"), ("category", "Category", "entry"), ("proficiency", "Proficiency", "entry"), ("notes", "Notes", "text")],
    },
    "achievements": {
        "label": "Achievements",
        "display": ["achievement_date", "achievement", "organization", "category"],
        "fields": [("achievement", "Achievement", "entry"), ("achievement_date", "Date", "entry"), ("organization", "Organization", "entry"), ("category", "Category", "entry"), ("description", "Description", "text")],
    },
}


def application_dir() -> Path:
    """Return the folder containing the executable or source files."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def portable_data_dir() -> Path:
    """Store writable application data beside the app for flash-drive use."""
    path = application_dir() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def ui_settings_path() -> Path:
    return portable_data_dir() / "ui_settings.json"


def load_theme_preference() -> str:
    try:
        value = json.loads(ui_settings_path().read_text(encoding="utf-8")).get("theme", "light")
        return value if value in {"light", "dark"} else "light"
    except Exception:
        return "light"


def save_theme_preference(theme: str) -> None:
    try:
        ui_settings_path().write_text(json.dumps({"theme": theme}, indent=2), encoding="utf-8")
    except OSError:
        pass


def portable_resume_dir() -> Path:
    """Store generated CVs beside the application for flash-drive portability."""
    path = application_dir() / "Resume"
    path.mkdir(parents=True, exist_ok=True)
    return path


def legacy_database_path() -> Path:
    """Location used by v1 before portable storage was enabled."""
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    else:
        base = Path.home() / ".local" / "share"
    return base / "ForensicCVManager" / "forensic_cv.sqlite3"


def prepare_portable_database() -> Path:
    """Create a writable portable database from the release template on first run."""
    db_path = portable_data_dir() / "forensic_cv.sqlite3"
    template_path = portable_data_dir() / "template.sqlite3"
    legacy_path = legacy_database_path()
    if not db_path.exists():
        source = template_path if template_path.exists() else (legacy_path if legacy_path.exists() else None)
        if source:
            try:
                shutil.copy2(source, db_path)
            except OSError:
                pass
    return db_path


class ProfileNameDialog(tk.Toplevel):
    def __init__(self, parent, title: str, initial: str = ""):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.result = None
        self.var = tk.StringVar(value=initial)
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Profile Name:").grid(row=0, column=0, sticky="w", pady=5)
        entry = ttk.Entry(frame, textvariable=self.var, width=42)
        entry.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, sticky="e")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right", padx=4)
        ttk.Button(buttons, text="Save", command=self.save).pack(side="right", padx=4)
        entry.focus_set()
        self.bind("<Return>", lambda e: self.save())
        self.bind("<Escape>", lambda e: self.destroy())

    def save(self):
        value = self.var.get().strip()
        if not value:
            messagebox.showerror("Profile Name", "Enter a profile name.", parent=self)
            return
        self.result = value
        self.destroy()


class RecordDialog(tk.Toplevel):
    def __init__(self, parent, table: str, config: dict[str, Any], initial: dict[str, Any] | None = None):
        super().__init__(parent)
        self.title(("Edit " if initial else "Add ") + config["label"])
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        self.result = None
        self.vars: dict[str, Any] = {}
        self.widgets: dict[str, Any] = {}
        self.columnconfigure(1, weight=1)
        row = 0
        for field in config["fields"]:
            name, label, kind, *extra = field
            ttk.Label(self, text=label + ":").grid(row=row, column=0, sticky="nw", padx=8, pady=5)
            value = "" if initial is None or initial.get(name) is None else initial.get(name)
            if kind == "text":
                widget = tk.Text(self, width=65, height=5, wrap="word")
                try:
                    root = parent.winfo_toplevel()
                    if getattr(root, "theme_name", "light") == "dark":
                        widget.configure(bg="#313338", fg="#f2f3f5", insertbackground="#f2f3f5")
                except Exception:
                    pass
                widget.insert("1.0", str(value))
                widget.grid(row=row, column=1, sticky="nsew", padx=8, pady=5)
                self.rowconfigure(row, weight=1)
            elif kind == "check":
                var = tk.IntVar(value=int(value or 0))
                widget = ttk.Checkbutton(self, variable=var)
                widget.grid(row=row, column=1, sticky="w", padx=8, pady=5)
                self.vars[name] = var
            elif kind == "combo":
                var = tk.StringVar(value=str(value))
                widget = ttk.Combobox(self, textvariable=var, values=extra[0], state="readonly")
                if not value and extra[0]:
                    var.set(extra[0][0])
                widget.grid(row=row, column=1, sticky="ew", padx=8, pady=5)
                self.vars[name] = var
            else:
                var = tk.StringVar(value=str(value))
                widget = ttk.Entry(self, textvariable=var, width=65)
                widget.grid(row=row, column=1, sticky="ew", padx=8, pady=5)
                self.vars[name] = var
            self.widgets[name] = widget
            row += 1
        buttons = ttk.Frame(self)
        buttons.grid(row=row, column=0, columnspan=2, sticky="e", padx=8, pady=10)
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right", padx=4)
        ttk.Button(buttons, text="Save", command=self.save).pack(side="right", padx=4)
        self.bind("<Escape>", lambda e: self.destroy())

    def save(self):
        data = {}
        for field in self.widgets:
            widget = self.widgets[field]
            if isinstance(widget, tk.Text):
                value = widget.get("1.0", "end").strip()
            elif field in self.vars:
                value = self.vars[field].get()
            else:
                value = ""
            if field in DATE_FIELDS or field in YEAR_FIELDS:
                allow_present = field in {"end_date", "end_year"}
                try:
                    value = normalize_date(str(value), allow_present=allow_present)
                except ValueError as exc:
                    messagebox.showerror("Invalid Date", f"{exc}", parent=self)
                    widget.focus_set()
                    return
            data[field] = value
        if "hours" in data and data["hours"] not in ("", None):
            try:
                data["hours"] = float(data["hours"])
            except ValueError:
                messagebox.showerror("Invalid Hours", "Hours must be a number.", parent=self)
                return
        self.result = data
        self.destroy()


class RecordTab(ttk.Frame):
    def __init__(self, parent, app, table: str, config: dict[str, Any]):
        super().__init__(parent)
        self.app = app
        self.db = app.db
        self.table = table
        self.config = config
        self.search_var = tk.StringVar()
        self.sort_column: str | None = None
        self.sort_descending = False
        self.base_headings: dict[str, str] = {}
        self._build()
        self.refresh()

    def _build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Button(top, text="Add", command=self.add).pack(side="left")
        ttk.Button(top, text="Edit", command=self.edit).pack(side="left", padx=5)
        ttk.Button(top, text="Delete", command=self.delete).pack(side="left")
        ttk.Label(top, text="Search:").pack(side="left", padx=(20, 5))
        search = ttk.Entry(top, textvariable=self.search_var, width=30)
        search.pack(side="left")
        search.bind("<KeyRelease>", lambda e: self.refresh())
        columns = self.config["display"]
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            heading = col.replace("_", " ").title()
            self.base_headings[col] = heading
            self.tree.heading(col, text=heading, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=150, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.tree.bind("<Double-1>", lambda e: self.edit())

    def _sort_value(self, record: dict[str, Any], column: str):
        value = record.get(column)
        if value is None or str(value).strip() == "":
            return None
        if column in DATE_FIELDS or column in YEAR_FIELDS or column.endswith("_date") or column.endswith("_year"):
            return date_sort_key(str(value))
        if column == "hours":
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
        if column == "core_training":
            return int(bool(value))
        text = str(value).strip().casefold()
        import re
        return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text))

    def _sorted_records(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.sort_column:
            return records
        column = self.sort_column
        nonblank = []
        blank = []
        for record in records:
            key = self._sort_value(record, column)
            if key is None:
                blank.append(record)
            else:
                nonblank.append((key, record))
        nonblank.sort(key=lambda item: item[0], reverse=self.sort_descending)
        return [record for _, record in nonblank] + blank

    def _update_sort_headings(self):
        for column, base in self.base_headings.items():
            if column == self.sort_column:
                indicator = " ▼" if self.sort_descending else " ▲"
            else:
                indicator = ""
            self.tree.heading(column, text=base + indicator, command=lambda c=column: self.sort_by_column(c))

    def sort_by_column(self, column: str):
        if self.sort_column == column:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = column
            self.sort_descending = False
        self._update_sort_headings()
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        rows = self._sorted_records(self.db.list(self.table, self.search_var.get()))
        for row in rows:
            vals = []
            for col in self.config["display"]:
                val = row.get(col, "")
                if col == "core_training":
                    val = "Yes" if val else "No"
                vals.append(val)
            self.tree.insert("", "end", iid=str(row["id"]), values=vals)
        if self.app.notebook.select() and self.app.notebook.tab(self.app.notebook.select(), "text") == self.config["label"]:
            sort_note = ""
            if self.sort_column:
                direction = "descending" if self.sort_descending else "ascending"
                sort_note = f" | Sorted by {self.base_headings[self.sort_column]} ({direction})"
            self.app.set_status(f"{self.config['label']}: {len(rows)} records{sort_note}")

    def selected_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def add(self):
        dlg = RecordDialog(self, self.table, self.config)
        self.wait_window(dlg)
        if dlg.result is not None:
            self.db.insert(self.table, dlg.result)
            self.refresh()
            self.app.refresh_dashboard()
            self.app.set_status(f"Added {self.config['label']} record")

    def edit(self):
        rid = self.selected_id()
        if not rid:
            messagebox.showinfo("Edit", "Select a record first.", parent=self)
            return
        record = self.db.get(self.table, rid)
        dlg = RecordDialog(self, self.table, self.config, record)
        self.wait_window(dlg)
        if dlg.result is not None:
            self.db.update(self.table, rid, dlg.result)
            self.refresh()
            self.app.refresh_dashboard()
            self.app.set_status(f"Updated {self.config['label']} record")

    def delete(self):
        rid = self.selected_id()
        if not rid:
            messagebox.showinfo("Delete", "Select a record first.", parent=self)
            return
        if not messagebox.askyesno("Delete Record", "Permanently delete the selected record?", parent=self):
            return
        self.db.delete(self.table, rid)
        self.refresh()
        self.app.refresh_dashboard()
        self.app.set_status(f"Deleted {self.config['label']} record")


class HelpWindow(tk.Toplevel):
    def __init__(self, parent, section: str | None = None):
        super().__init__(parent)
        self.title(f"{APP_NAME} {APP_VERSION} - User Manual")
        self.geometry("820x650")
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)
        text = tk.Text(frame, wrap="word", padx=12, pady=12)
        text.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, command=text.yview)
        scroll.pack(side="right", fill="y")
        text.configure(yscrollcommand=scroll.set)
        try:
            if getattr(parent, "theme_name", "light") == "dark":
                text.configure(bg="#313338", fg="#f2f3f5", insertbackground="#f2f3f5")
        except Exception:
            pass
        manual = self.manual_text()
        text.insert("1.0", manual)
        text.configure(state="disabled")
        if section:
            pos = text.search(section, "1.0", stopindex="end")
            if pos:
                text.see(pos)

    @staticmethod
    def manual_text() -> str:
        return f"""{APP_NAME} {APP_VERSION}
USER MANUAL

OVERVIEW
{APP_NAME} stores professional CV information in a portable SQLite database and generates Word and PDF curriculum vitae documents on demand. Multiple examiner profiles may be maintained in one database.

1. PROFILES
Use the profile selector near the top of the application to switch users. File > New Profile creates an empty profile. File > Rename Profile changes the selected profile's display name. File > Delete Profile permanently deletes that profile and all records belonging to it.

2. HOW TO ADD RECORDS
Select the appropriate tab, such as Employment, Education, Training, Certifications, Courtroom Testimony, Teaching, Organizations, Skills & Tools, or Achievements.

Click Add. Complete the fields in the Add Record window and choose Save. The new record immediately becomes part of the selected profile's database.

Dates accept common formats such as 3/5/2026, 03-05-2026, 2026-03-05, March 5 2026, March 2026, 03/2026, and 2026. End-date fields may also use Present, Current, Ongoing, or Now. Dates are normalized internally to keep chronological sorting reliable.

Training Hours should contain a number, such as 8, 16, or 40. Select Include in Core Training when the course should appear in the shorter Core Training section of a generated CV.

Long Notes, Duties, and Description fields are stored and generated in full; they are not limited to the amount visible in the entry window.

3. EDITING RECORDS
Select a record and click Edit, or double-click the record. Make the required changes and click Save.

4. DELETING RECORDS
Select a record and click Delete. Confirm the warning. Deletion is permanent, so create regular database backups.

5. SEARCHING
Use the Search box on a record tab to filter that tab's records. Clearing the Search box restores the complete list.

6. DASHBOARD
The Dashboard summarizes employment, education, training, certifications, testimony, and other professional records. Certification alerts identify expired credentials and credentials expiring within 90 days.

7. GENERATING A CV
Open Generate CV. Select the sections to include. Generate Word CV creates an editable DOCX file. Preview & Save PDF creates a native PDF preview inside the application and allows saving after review. Generate Word + PDF produces both independently from the same current SQLite records. PDF output always uses the Professional report style. Microsoft Word is not required to generate PDF documents.

Generated reports default to the Resume folder beside the application, which keeps the workflow portable when the program is run from a flash drive.

8. IMPORT / EXPORT
File > Export Profile saves the selected examiner profile and its records as a JSON package. File > Import Profile loads a previously exported package as another profile.

9. BACKUPS
File > Backup Database creates a complete SQLite backup. File > Restore Database replaces the current database from a backup. The database contains every profile, so a database backup is the recommended full backup method.

10. PORTABLE USE
Keep the executable and its data folder together. The writable database is stored in data/forensic_cv.sqlite3. The Resume folder is also created beside the application. Moving the complete application folder to a flash drive keeps the database and generated CV files together.

11. SAMPLE DATA
File > Load Sample Data can replace the selected profile's records with fictitious demonstration information. Use this only when you intentionally want demonstration data in that profile.

12. APPEARANCE
Tools > Appearance switches between Light and Dark mode. The selection is saved in data/ui_settings.json and follows the portable application.

13. PDF PREVIEW
Generate CV > Preview & Save PDF opens the native integrated viewer. Use Previous/Next to change pages, Zoom +/- for magnification, Fit Width to resize the current page, and Save PDF to place the reviewed document in the Resume folder or another chosen location.

14. UPDATES
Tools > Check for Updates compares this version ({APP_VERSION}) with the latest published GitHub Release when an update repository has been configured. The update check does not modify the application automatically.
"""


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.theme_name = load_theme_preference()
        splash = SplashScreen(self, theme_name=self.theme_name)
        splash.set_status("Preparing portable database...", 25)
        self.withdraw()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1200x780")
        self.minsize(980, 650)
        try:
            icon_path = resource_path("assets/app.ico")
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass
        self.db_path = prepare_portable_database()
        splash.set_status("Opening SQLite database...", 48)
        self.db = Database(self.db_path)
        if not self.db.list_profiles():
            seed(self.db)
        self.style = ttk.Style(self)
        splash.set_status("Loading interface...", 66)
        self._configure_styles()
        self.status = tk.StringVar(value="Ready")
        self.profile_display_to_id: dict[str, int] = {}
        self.record_tabs: dict[str, RecordTab] = {}
        self._menu()
        self._topbar()
        self._build_tabs()
        self._statusbar()
        self.refresh_profiles(select_current=True)
        self._apply_theme()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.after_idle(self._on_tab_changed)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        splash.set_status("Ready", 100)
        self.update_idletasks()
        splash.close()
        self.deiconify()
        self.after(50, self.lift)
        self.after(750, self._startup_update_check)

    def _configure_styles(self):
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        self.style.configure("Stat.TLabel", font=("Segoe UI", 18, "bold"))

    def _apply_theme(self):
        dark = self.theme_name == "dark"
        bg = "#202225" if dark else "SystemButtonFace"
        panel = "#2b2d31" if dark else "#ffffff"
        field = "#313338" if dark else "#ffffff"
        fg = "#f2f3f5" if dark else "#212529"
        muted = "#b5bac1" if dark else "#495057"
        select = "#3f526f" if dark else "#d9e8f6"
        self.configure(bg=bg)
        self.option_add("*TCombobox*Listbox.background", field)
        self.option_add("*TCombobox*Listbox.foreground", fg)
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("Title.TLabel", background=bg, foreground=fg, font=("Segoe UI", 16, "bold"))
        self.style.configure("Stat.TLabel", background=bg, foreground=fg, font=("Segoe UI", 18, "bold"))
        self.style.configure("TButton", padding=(8, 4))
        self.style.configure("TCheckbutton", background=bg, foreground=fg)
        self.style.configure("TLabelframe", background=bg)
        self.style.configure("TLabelframe.Label", background=bg, foreground=fg)
        self.style.configure("TNotebook", background=bg)
        self.style.configure("TNotebook.Tab", padding=(10, 5))
        self.style.configure("TEntry", fieldbackground=field, foreground=fg)
        self.style.configure("TCombobox", fieldbackground=field, foreground=fg)
        self.style.configure("Treeview", background=field, fieldbackground=field, foreground=fg, rowheight=24)
        self.style.map("Treeview", background=[("selected", select)], foreground=[("selected", fg)])
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        for widget in self.winfo_children():
            self._theme_tk_children(widget, dark, field, fg)
        if hasattr(self, "dashboard_chart"):
            self.dashboard_chart.configure(bg=field, highlightthickness=1, highlightbackground=("#4a4d52" if dark else "#cccccc"))
            self.refresh_dashboard()

    def _theme_tk_children(self, widget, dark, field, fg):
        if isinstance(widget, tk.Text):
            try:
                widget.configure(bg=field, fg=fg, insertbackground=fg, selectbackground="#3f526f" if dark else "#cce1f5")
            except tk.TclError:
                pass
        if isinstance(widget, tk.Canvas):
            try:
                widget.configure(bg=field)
            except tk.TclError:
                pass
        for child in widget.winfo_children():
            self._theme_tk_children(child, dark, field, fg)

    def set_theme(self, theme: str):
        if theme not in {"light", "dark"} or theme == self.theme_name:
            return
        self.theme_name = theme
        save_theme_preference(theme)
        self._apply_theme()
        self.set_status(f"Appearance changed to {theme.title()} Mode")

    def _menu(self):
        menu = tk.Menu(self)
        filem = tk.Menu(menu, tearoff=0)
        filem.add_command(label="New Profile...", command=self.new_profile)
        filem.add_command(label="Rename Profile...", command=self.rename_profile)
        filem.add_command(label="Delete Profile...", command=self.delete_profile)
        filem.add_separator()
        filem.add_command(label="Export Profile...", command=self.export_current_profile)
        filem.add_command(label="Import Profile...", command=self.import_profile_package)
        filem.add_separator()
        filem.add_command(label="Backup Database...", command=self.backup_db)
        filem.add_command(label="Restore Database...", command=self.restore_db)
        filem.add_command(label="Open Data Folder", command=self.open_data_folder)
        filem.add_command(label="Open Resume Folder", command=self.open_resume_folder)
        filem.add_separator()
        filem.add_command(label="Load Sample Data...", command=self.load_sample_data)
        filem.add_command(label="Clear Current Profile Data...", command=self.clear_current_profile_data)
        filem.add_separator()
        filem.add_command(label="Exit", command=self.on_close)
        menu.add_cascade(label="File", menu=filem)

        toolsm = tk.Menu(menu, tearoff=0)
        appearancem = tk.Menu(toolsm, tearoff=0)
        appearancem.add_radiobutton(label="Light Mode", value="light", variable=tk.StringVar(value=self.theme_name), command=lambda: self.set_theme("light"))
        appearancem.add_radiobutton(label="Dark Mode", value="dark", variable=tk.StringVar(value=self.theme_name), command=lambda: self.set_theme("dark"))
        # Retain a persistent StringVar so radio indicators track the current setting.
        self.appearance_menu_var = tk.StringVar(value=self.theme_name)
        appearancem.delete(0, "end")
        appearancem.add_radiobutton(label="Light Mode", value="light", variable=self.appearance_menu_var, command=lambda: self.set_theme("light"))
        appearancem.add_radiobutton(label="Dark Mode", value="dark", variable=self.appearance_menu_var, command=lambda: self.set_theme("dark"))
        toolsm.add_cascade(label="Appearance", menu=appearancem)
        toolsm.add_separator()
        toolsm.add_command(label="Check for Updates", command=lambda: self.check_for_updates(manual=True))
        menu.add_cascade(label="Tools", menu=toolsm)

        helpm = tk.Menu(menu, tearoff=0)
        helpm.add_command(label="User Manual", command=lambda: HelpWindow(self))
        helpm.add_command(label="How to Add Records", command=lambda: HelpWindow(self, "2. HOW TO ADD RECORDS"))
        helpm.add_separator()
        helpm.add_command(label="About", command=self.show_about)
        menu.add_cascade(label="Help", menu=helpm)
        self.config(menu=menu)

    def show_about(self):
        messagebox.showinfo("About", f"{APP_NAME}\nVersion {APP_VERSION}\n\nPortable professional portfolio and CV management for digital forensic examiners and expert witnesses.\n\nNative PDF generation uses ReportLab; PDF preview uses PyMuPDF.")

    def _startup_update_check(self):
        try:
            self.check_for_updates(manual=False)
        except Exception:
            pass

    def check_for_updates(self, manual: bool = True):
        if not GITHUB_REPOSITORY:
            if manual:
                messagebox.showinfo("Updates", "No GitHub update repository is configured.")
            return
        result = check_github_release(APP_VERSION, GITHUB_REPOSITORY)
        if not result.get("ok"):
            if manual:
                messagebox.showerror("Update Check", result.get("message", "Unable to check for updates."))
            return
        if result.get("update_available"):
            answer = messagebox.askyesno("Update Available", f"Version {result['latest_version']} is available.\n\nOpen the GitHub release page?")
            if answer:
                webbrowser.open(result.get("html_url", f"https://github.com/{GITHUB_REPOSITORY}/releases/latest"))
        elif manual:
            messagebox.showinfo("Updates", f"You are running the latest published version ({APP_VERSION}).")

    def _topbar(self):
        top = ttk.Frame(self, padding=(10, 8))
        top.pack(fill="x")
        ttk.Label(top, text="Profile:").pack(side="left")
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(top, textvariable=self.profile_var, state="readonly", width=44)
        self.profile_combo.pack(side="left", padx=8)
        self.profile_combo.bind("<<ComboboxSelected>>", self.switch_profile)
        ttk.Button(top, text="New Profile", command=self.new_profile).pack(side="left")
        ttk.Button(top, text="Export", command=self.export_current_profile).pack(side="right", padx=4)
        ttk.Button(top, text="Backup", command=self.backup_db).pack(side="right", padx=4)

    def _statusbar(self):
        ttk.Label(self, textvariable=self.status, anchor="w", relief="sunken").pack(side="bottom", fill="x")

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=6)
        self._dashboard_tab()
        self._profile_tab()
        for table, config in TABLE_CONFIG.items():
            tab = RecordTab(self.notebook, self, table, config)
            self.record_tabs[table] = tab
            self.notebook.add(tab, text=config["label"])
        self._generate_tab()

    def _profile_display_names(self, profiles: list[dict[str, Any]]) -> dict[str, int]:
        """Build clean labels without exposing internal SQLite profile IDs."""
        used: dict[str, int] = {}
        result: dict[str, int] = {}
        for p in profiles:
            base = (p.get("profile_name") or p.get("preferred_name") or p.get("full_name") or "Unnamed Profile").strip()
            count = used.get(base.casefold(), 0) + 1
            used[base.casefold()] = count
            label = base if count == 1 else f"{base} ({count})"
            result[label] = int(p["id"])
        return result

    def refresh_profiles(self, select_current=False):
        profiles = self.db.list_profiles()
        self.profile_display_to_id = self._profile_display_names(profiles)
        values = list(self.profile_display_to_id)
        self.profile_combo["values"] = values
        current_id = self.db.get_current_profile_id()
        target_label = next((label for label, pid in self.profile_display_to_id.items() if pid == current_id), None)
        if target_label:
            self.profile_var.set(target_label)
        elif values:
            self.profile_var.set(values[0])
            self.db.set_current_profile(self.profile_display_to_id[values[0]])
        if hasattr(self, "record_tabs"):
            self.refresh_all_tabs()
        if hasattr(self, "profile_vars"):
            self.load_profile_form()
        if hasattr(self, "dashboard_stats"):
            self.refresh_dashboard()

    def switch_profile(self, _event=None):
        label = self.profile_var.get()
        pid = self.profile_display_to_id.get(label)
        if pid:
            self.db.set_current_profile(pid)
            self.refresh_profiles()
            self.set_status(f"Active profile: {label}")

    def new_profile(self):
        dlg = ProfileNameDialog(self, "New Profile")
        self.wait_window(dlg)
        if dlg.result:
            pid = self.db.create_profile(dlg.result)
            self.db.set_current_profile(pid)
            self.refresh_profiles()
            self.notebook.select(1)
            self.set_status(f"Created profile: {dlg.result}")

    def rename_profile(self):
        current = self.db.get_profile()
        dlg = ProfileNameDialog(self, "Rename Profile", current.get("profile_name", ""))
        self.wait_window(dlg)
        if dlg.result:
            self.db.rename_profile(current["id"], dlg.result)
            self.refresh_profiles()

    def delete_profile(self):
        profiles = self.db.list_profiles()
        if len(profiles) <= 1:
            messagebox.showwarning("Delete Profile", "At least one profile must remain.")
            return
        current = self.db.get_profile()
        name = current.get("profile_name") or current.get("full_name") or "this profile"
        if not messagebox.askyesno("Delete Profile", f"Permanently delete {name} and all of its records?\n\nThis cannot be undone."):
            return
        self.db.delete_profile(current["id"])
        self.refresh_profiles()

    def clear_current_profile_data(self):
        profile = self.db.get_profile()
        name = profile.get("profile_name") or "current profile"
        if not messagebox.askyesno("Clear Profile Data", f"Delete all professional records for {name}?\n\nThe profile itself will remain. This cannot be undone."):
            return
        self.db.clear_profile_records(profile["id"])
        self.refresh_all_tabs()
        self.refresh_dashboard()

    def load_sample_data(self):
        profile = self.db.get_profile()
        if not messagebox.askyesno("Load Sample Data", "Replace this profile's current records with fictitious demonstration data?"):
            return
        load_sample_profile(self.db, profile["id"])
        self.refresh_profiles()
        self.set_status("Sample data loaded")

    def export_current_profile(self):
        profile = self.db.get_profile()
        safe_name = (profile.get("profile_name") or "profile").replace(" ", "_")
        out = filedialog.asksaveasfilename(title="Export Profile", defaultextension=".json", initialfile=f"{safe_name}_portfolio.json", filetypes=[("Profile Package", "*.json"), ("All Files", "*.*")])
        if not out:
            return
        export_profile(self.db, profile["id"], Path(out))
        self.set_status(f"Profile exported: {out}")

    def import_profile_package(self):
        src = filedialog.askopenfilename(title="Import Profile", filetypes=[("Profile Package", "*.json"), ("All Files", "*.*")])
        if not src:
            return
        try:
            pid = import_profile(self.db, Path(src))
            self.db.set_current_profile(pid)
            self.refresh_profiles()
            self.set_status(f"Profile imported: {src}")
        except Exception as exc:
            messagebox.showerror("Import Error", str(exc))

    def refresh_all_tabs(self):
        for tab in self.record_tabs.values():
            tab.db = self.db
            tab.refresh()
        self.load_profile_form()
        self.refresh_dashboard()

    def load_profile_form(self):
        if not hasattr(self, "profile_vars"):
            return
        p = self.db.get_profile()
        for key, var in self.profile_vars.items():
            var.set(p.get(key, "") or "")
        self.profile_summary.delete("1.0", "end")
        self.profile_summary.insert("1.0", p.get("summary", "") or "")

    def _dashboard_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dashboard")
        outer = ttk.Frame(tab, padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Professional Portfolio Dashboard", style="Title.TLabel").pack(anchor="w", pady=(0, 12))
        stats = ttk.Frame(outer)
        stats.pack(fill="x")
        self.dashboard_stats = {}
        labels = [("Training Hours", "training_hours"), ("Training Records", "training"), ("Certifications", "certifications"), ("Testimony", "testimony"), ("Employment", "employment"), ("Education", "education")]
        for i, (label, key) in enumerate(labels):
            box = ttk.LabelFrame(stats, text=label, padding=12)
            box.grid(row=0, column=i, padx=4, sticky="nsew")
            stats.columnconfigure(i, weight=1)
            var = tk.StringVar(value="0")
            ttk.Label(box, textvariable=var, style="Stat.TLabel").pack()
            self.dashboard_stats[key] = var
        lower = ttk.Frame(outer)
        lower.pack(fill="both", expand=True, pady=(15, 0))
        alerts = ttk.LabelFrame(lower, text="Certification Alerts", padding=10)
        alerts.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.alerts_list = tk.Listbox(alerts, height=15)
        self.alerts_list.pack(fill="both", expand=True)
        chart = ttk.LabelFrame(lower, text="Record Counts", padding=10)
        chart.pack(side="left", fill="both", expand=True)
        self.dashboard_chart = tk.Canvas(chart, height=290, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.dashboard_chart.pack(fill="both", expand=True)
        self.dashboard_chart.bind("<Configure>", lambda e: self.draw_dashboard_chart())
        self.refresh_dashboard()

    def refresh_dashboard(self):
        if not hasattr(self, "dashboard_stats"):
            return
        counts = {table: self.db.count(table) for table in TABLE_CONFIG}
        hours = self.db.total_training_hours()
        self.dashboard_stats["training_hours"].set(f"{hours:g}")
        for key in ["training", "certifications", "testimony", "employment", "education"]:
            self.dashboard_stats[key].set(str(counts.get(key, 0)))
        self.alerts_list.delete(0, "end")
        today = date.today()
        for cert in self.db.list("certifications"):
            exp = (cert.get("expiration_date") or "").strip()
            if not exp or exp.lower() in {"present", "current", "ongoing", "now"}:
                continue
            try:
                d = datetime.strptime(exp, "%Y-%m-%d").date() if len(exp) == 10 else (datetime.strptime(exp, "%Y-%m").date() if len(exp) == 7 else None)
            except ValueError:
                d = None
            if not d:
                continue
            days = (d - today).days
            name = cert.get("certification") or "Certification"
            if days < 0:
                self.alerts_list.insert("end", f"EXPIRED: {name} ({exp})")
            elif days <= 90:
                self.alerts_list.insert("end", f"Expires in {days} days: {name} ({exp})")
        if self.alerts_list.size() == 0:
            self.alerts_list.insert("end", "No certification expirations within 90 days.")
        self.draw_dashboard_chart()

    def draw_dashboard_chart(self):
        if not hasattr(self, "dashboard_chart"):
            return
        c = self.dashboard_chart
        c.delete("all")
        counts = [("Training", self.db.count("training")), ("Certs", self.db.count("certifications")), ("Testimony", self.db.count("testimony")), ("Employment", self.db.count("employment")), ("Education", self.db.count("education")), ("Skills", self.db.count("skills"))]
        c.update_idletasks()
        width = max(self.dashboard_chart.winfo_width(), 360); height = max(self.dashboard_chart.winfo_height(), 260)
        max_value = max([v for _, v in counts] + [1])
        left, top, bottom = 75, 20, height - 35
        usable = max(120, width - left - 20)
        bar_h = max(22, min(38, (bottom - top) // len(counts) - 8))
        chart_fg = "#f2f3f5" if self.theme_name == "dark" else "#212529"
        for i, (label, value) in enumerate(counts):
            y = top + i * ((bottom-top) / len(counts))
            x2 = left + usable * (value / max_value)
            self.dashboard_chart.create_text(left-8, y+bar_h/2, text=label, anchor="e", fill=chart_fg)
            self.dashboard_chart.create_rectangle(left, y, x2, y+bar_h, fill="#1f4e79", outline="")
            self.dashboard_chart.create_text(x2+6, y+bar_h/2, text=str(value), anchor="w", fill=chart_fg)

    def _profile_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Profile")
        profile = self.db.get_profile()
        self.profile_vars = {}
        fields = [("full_name", "Full Name"), ("preferred_name", "Preferred Name"), ("title", "Professional Title"), ("agency", "Agency / Employer"), ("email", "Email"), ("phone", "Phone")]
        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)
        for i, (name, label) in enumerate(fields):
            ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="w", pady=5)
            var = tk.StringVar(value=profile.get(name, ""))
            ttk.Entry(frame, textvariable=var, width=70).grid(row=i, column=1, sticky="ew", padx=8, pady=5)
            self.profile_vars[name] = var
        ttk.Label(frame, text="Professional Summary:").grid(row=len(fields), column=0, sticky="nw", pady=5)
        self.profile_summary = tk.Text(frame, height=12, wrap="word")
        self.profile_summary.insert("1.0", profile.get("summary", ""))
        self.profile_summary.grid(row=len(fields), column=1, sticky="nsew", padx=8, pady=5)
        frame.rowconfigure(len(fields), weight=1)
        ttk.Button(frame, text="Save Profile", command=self.save_profile).grid(row=len(fields)+1, column=1, sticky="e", pady=10)

    def save_profile(self):
        data = {k: v.get().strip() for k, v in self.profile_vars.items()}
        data["summary"] = self.profile_summary.get("1.0", "end").strip()
        self.db.save_profile(data)
        self.set_status("Profile saved")
        self.refresh_dashboard()

    def _generate_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Generate CV")
        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Create CV", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(frame, text="Select the sections to include. Word and PDF outputs are generated independently from the same current SQLite records.").pack(anchor="w", pady=(0, 12))
        self.cv_options = {}
        options = [("summary", "Professional Summary", 1), ("core_training", "Core Training", 1), ("employment", "Work Experience", 1), ("teaching", "Teaching Experience", 1), ("organizations", "Professional Organizations", 1), ("certifications", "Certifications", 1), ("skills", "Skills and Tools", 1), ("education", "Education", 1), ("testimony", "Courtroom Testimony", 1), ("achievements", "Professional Achievements", 1), ("full_training", "Detailed Training Appendix", 0)]
        checks = ttk.LabelFrame(frame, text="CV Sections", padding=12)
        checks.pack(fill="x", pady=8)
        for i, (key, label, default) in enumerate(options):
            var = tk.IntVar(value=default)
            ttk.Checkbutton(checks, text=label, variable=var).grid(row=i // 2, column=i % 2, sticky="w", padx=12, pady=5)
            self.cv_options[key] = var

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=16)
        ttk.Button(actions, text="Generate Word CV...", command=lambda: self.generate("docx")).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Preview & Save PDF...", command=self.preview_pdf).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Generate Word + PDF", command=lambda: self.generate("both")).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Open Resume Folder", command=self.open_resume_folder).pack(side="left")

    def preview_pdf(self):
        profile = self.db.get_profile()
        base = (profile.get("preferred_name") or profile.get("full_name") or "Forensic").replace(" ", "_") + "_CV.pdf"
        temp_path = make_preview_temp_path()
        try:
            options = {k: bool(v.get()) for k, v in self.cv_options.items()}
            self.set_status("Rendering PDF preview...")
            self.update_idletasks()
            generate_pdf(self.db, temp_path, options, theme_name="Professional")
            default_save = portable_resume_dir() / base
            PdfPreviewWindow(self, temp_path, default_save, on_saved=lambda p: self.set_status(f"PDF saved: {p}"))
            self.set_status("PDF preview ready")
        except Exception as exc:
            messagebox.showerror("PDF Preview", str(exc), parent=self)
            self.set_status("Ready")

    def generate(self, output_type: str = "docx"):
        profile = self.db.get_profile()
        base = (profile.get("preferred_name") or profile.get("full_name") or "Forensic").replace(" ", "_") + "_CV"
        extension = ".pdf" if output_type == "pdf" else ".docx"
        out = filedialog.asksaveasfilename(title="Save CV", defaultextension=extension, initialdir=str(portable_resume_dir()), initialfile=base + extension, filetypes=[("PDF Document", "*.pdf")] if extension == ".pdf" else [("Word Document", "*.docx")])
        if not out:
            return
        try:
            options = {k: bool(v.get()) for k, v in self.cv_options.items()}
            if output_type == "pdf":
                pdf_path = Path(out)
                generate_pdf(self.db, pdf_path, options, theme_name="Professional")
                generated = pdf_path
            else:
                docx_path = Path(out)
                generate_cv(self.db, docx_path, options)
                generated = docx_path
                if output_type == "both":
                    generate_pdf(self.db, docx_path.with_suffix(".pdf"), options, theme_name="Professional")
            self.set_status(f"CV generated: {generated}")
            if messagebox.askyesno("CV Generated", "The CV was created successfully. Open the output folder now?"):
                self.open_resume_folder()
        except Exception as exc:
            messagebox.showerror("Generation Error", str(exc))

    def backup_db(self):
        out = filedialog.asksaveasfilename(title="Backup Database", defaultextension=".sqlite3", initialfile="forensic_cv_backup.sqlite3", filetypes=[("SQLite Database", "*.sqlite3"), ("All Files", "*.*")])
        if out:
            self.db.conn.commit()
            shutil.copy2(self.db_path, out)
            self.set_status(f"Database backed up: {out}")

    def restore_db(self):
        src = filedialog.askopenfilename(title="Restore Database", filetypes=[("SQLite Database", "*.sqlite3"), ("All Files", "*.*")])
        if not src:
            return
        if not messagebox.askyesno("Restore Database", "This will replace the current database. Continue?"):
            return
        try:
            check = sqlite3.connect(src)
            check.execute("SELECT name FROM sqlite_master LIMIT 1").fetchone()
            check.close()
            self.db.close()
            shutil.copy2(src, self.db_path)
            self.db = Database(self.db_path)
            messagebox.showinfo("Restore Complete", "Database restored. The application will now restart.")
            self.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as exc:
            messagebox.showerror("Restore Error", str(exc))

    def open_resume_folder(self):
        path = str(portable_resume_dir())
        if sys.platform.startswith("win"):
            os.startfile(path)
        else:
            os.system(f'xdg-open "{path}" >/dev/null 2>&1 &')

    def open_data_folder(self):
        path = str(portable_data_dir())
        if sys.platform.startswith("win"):
            os.startfile(path)
        else:
            os.system(f'xdg-open "{path}" >/dev/null 2>&1 &')

    def _on_tab_changed(self, _event=None):
        """Keep the status bar relevant to the currently selected tab."""
        if not hasattr(self, "notebook") or not self.notebook.tabs():
            return
        try:
            selected = self.notebook.select()
            tab_text = self.notebook.tab(selected, "text")
        except tk.TclError:
            return

        if tab_text == "Dashboard":
            profile = self.db.get_profile()
            name = profile.get("profile_name") or profile.get("preferred_name") or profile.get("full_name") or "Current profile"
            self.set_status(f"Dashboard: {name}")
            return
        if tab_text == "Profile":
            profile = self.db.get_profile()
            name = profile.get("profile_name") or profile.get("preferred_name") or profile.get("full_name") or "Current profile"
            self.set_status(f"Profile: {name}")
            return
        if tab_text == "Generate CV":
            self.set_status("Generate CV: select sections, then create Word or preview PDF")
            return

        for table, record_tab in getattr(self, "record_tabs", {}).items():
            if TABLE_CONFIG[table]["label"] == tab_text:
                record_tab.refresh()
                return
        self.set_status(tab_text)

    def set_status(self, text):
        self.status.set(text)

    def on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
