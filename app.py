from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from database import Database
from seed_data import seed
from cv_generator import generate_cv
from date_utils import normalize_date

APP_NAME = "Forensic CV Manager"

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
    """Use the portable DB and carry forward an existing v1 DB once."""
    db_path = portable_data_dir() / "forensic_cv.sqlite3"
    legacy_path = legacy_database_path()
    if not db_path.exists() and legacy_path.exists():
        try:
            shutil.copy2(legacy_path, db_path)
        except OSError:
            # If migration is unavailable, Database will create a new portable DB.
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
        self.geometry("760x620")

    def save(self):
        result = {}
        for field in self.widgets:
            widget = self.widgets[field]
            if isinstance(widget, tk.Text):
                value = widget.get("1.0", "end").strip()
            else:
                value = self.vars[field].get()
            if field == "hours":
                try:
                    value = float(value) if str(value).strip() else None
                except ValueError:
                    messagebox.showerror("Invalid Hours", "Hours must be a number.", parent=self)
                    return
            elif field in DATE_FIELDS:
                try:
                    value = normalize_date(value, allow_present=field == "end_date")
                except ValueError as exc:
                    messagebox.showerror("Invalid Date", str(exc), parent=self)
                    self.widgets[field].focus_set()
                    return
            elif field in YEAR_FIELDS:
                try:
                    value = normalize_date(value, allow_present=field == "end_year", allow_year_only=True)
                    if value not in ("", "Present") and len(value) != 4:
                        raise ValueError(f'"{value}" must be a four-digit year or Present.')
                except ValueError as exc:
                    messagebox.showerror("Invalid Year", str(exc), parent=self)
                    self.widgets[field].focus_set()
                    return
            result[field] = value
        self.result = result
        self.destroy()


class RecordsTab(ttk.Frame):
    def __init__(self, parent, db: Database, table: str, status_callback):
        super().__init__(parent)
        self.db = db
        self.table = table
        self.config_data = TABLE_CONFIG[table]
        self.status_callback = status_callback
        self.search_var = tk.StringVar()
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Label(top, text="Search:").pack(side="left")
        entry = ttk.Entry(top, textvariable=self.search_var, width=35)
        entry.pack(side="left", padx=5)
        self.search_var.trace_add("write", lambda *_: self.refresh())
        ttk.Button(top, text="Add", command=self.add).pack(side="right", padx=3)
        ttk.Button(top, text="Edit", command=self.edit).pack(side="right", padx=3)
        ttk.Button(top, text="Delete", command=self.delete).pack(side="right", padx=3)

        cols = self.config_data["display"]
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col.replace("_", " ").title())
            width = 110
            if col in {"course_name", "certification", "employer", "degree", "skill", "achievement"}:
                width = 260
            self.tree.column(col, width=width, minwidth=70, stretch=True)
        y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y.set, xscrollcommand=x.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 8))
        y.pack(side="right", fill="y", padx=(0, 8), pady=(0, 8))
        x.pack(side="bottom", fill="x", padx=8)
        self.tree.bind("<Double-1>", lambda e: self.edit())
        self.refresh()

    def refresh(self):
        term = self.search_var.get().lower().strip()
        self.tree.delete(*self.tree.get_children())
        for row in self.db.list_rows(self.table):
            hay = " ".join(str(v or "") for v in row.values()).lower()
            if term and term not in hay:
                continue
            values = []
            for col in self.config_data["display"]:
                value = row.get(col, "")
                if col == "core_training":
                    value = "Yes" if value else "No"
                values.append("" if value is None else value)
            self.tree.insert("", "end", iid=str(row["id"]), values=values)
        self.status_callback(f"{self.config_data['label']}: {len(self.tree.get_children())} record(s)")

    def selected_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def add(self):
        dlg = RecordDialog(self, self.table, self.config_data)
        self.wait_window(dlg)
        if dlg.result is not None:
            self.db.insert_row(self.table, dlg.result)
            self.refresh()

    def edit(self):
        row_id = self.selected_id()
        if not row_id:
            messagebox.showinfo("Select Record", "Select a record to edit.", parent=self)
            return
        dlg = RecordDialog(self, self.table, self.config_data, self.db.get_row(self.table, row_id))
        self.wait_window(dlg)
        if dlg.result is not None:
            self.db.update_row(self.table, row_id, dlg.result)
            self.refresh()

    def delete(self):
        row_id = self.selected_id()
        if not row_id:
            messagebox.showinfo("Select Record", "Select a record to delete.", parent=self)
            return
        if messagebox.askyesno("Delete Record", "Delete the selected record?", parent=self):
            self.db.delete_row(self.table, row_id)
            self.refresh()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1250x760")
        self.minsize(950, 600)
        self.db_path = prepare_portable_database()
        self.db = Database(self.db_path)
        seed(self.db)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._style()
        self._menu()
        self.status = tk.StringVar(value="Ready")
        self.profile_bar = ttk.Frame(self, padding=(8, 6))
        self.profile_bar.pack(fill="x")
        ttk.Label(self.profile_bar, text="Active Profile:").pack(side="left")
        self.profile_choice = tk.StringVar()
        self.profile_combo = ttk.Combobox(self.profile_bar, textvariable=self.profile_choice, state="readonly", width=34)
        self.profile_combo.pack(side="left", padx=6)
        self.profile_combo.bind("<<ComboboxSelected>>", self.switch_profile)
        ttk.Button(self.profile_bar, text="Manage Profiles", command=self.manage_profiles).pack(side="left", padx=3)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        self._dashboard_tab()
        self._profile_tab()
        self.record_tabs = {}
        for table in TABLE_CONFIG:
            tab = RecordsTab(self.notebook, self.db, table, self.set_status)
            self.record_tabs[table] = tab
            self.notebook.add(tab, text=TABLE_CONFIG[table]["label"])
        self._generate_tab()
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", side="bottom")
        self.refresh_profile_selector()

    def _style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("vista" if sys.platform.startswith("win") else "clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=26)
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Metric.TLabel", font=("Segoe UI", 20, "bold"), foreground="#1f4e79")

    def _menu(self):
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Backup Database...", command=self.backup_db)
        file_menu.add_command(label="Restore Database...", command=self.restore_db)
        file_menu.add_separator()
        file_menu.add_command(label="Clear Current Profile Data...", command=self.clear_profile_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menu.add_cascade(label="File", menu=file_menu)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Forensic CV Manager\nSQLite-backed professional credential and CV tracking."))
        menu.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu)

    def refresh_profile_selector(self):
        self._profiles = self.db.list_profiles()
        self._profile_by_label = {f"{p['profile_name']}  [#{p['id']}]": p['id'] for p in self._profiles}
        labels = list(self._profile_by_label)
        self.profile_combo["values"] = labels
        for label, pid in self._profile_by_label.items():
            if pid == self.db.current_profile_id:
                self.profile_choice.set(label)
                break

    def switch_profile(self, event=None):
        pid = self._profile_by_label.get(self.profile_choice.get())
        if not pid or pid == self.db.current_profile_id:
            return
        self.db.set_current_profile(pid)
        self.reload_current_profile()
        self.set_status(f"Active profile changed to {self.db.get_profile().get('profile_name', '')}")

    def reload_current_profile(self):
        profile = self.db.get_profile()
        for name, var in getattr(self, "profile_vars", {}).items():
            var.set(profile.get(name, ""))
        if hasattr(self, "profile_summary"):
            self.profile_summary.delete("1.0", "end")
            self.profile_summary.insert("1.0", profile.get("summary", ""))
        for tab in getattr(self, "record_tabs", {}).values():
            tab.refresh()
        self.refresh_dashboard()
        self.refresh_profile_selector()

    def manage_profiles(self):
        win = tk.Toplevel(self)
        win.title("Manage Profiles")
        win.transient(self)
        win.grab_set()
        win.geometry("560x360")
        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=("name", "full_name"), show="headings", selectmode="browse")
        tree.heading("name", text="Profile Name")
        tree.heading("full_name", text="Full Name")
        tree.column("name", width=200)
        tree.column("full_name", width=280)
        tree.pack(fill="both", expand=True)
        def refresh():
            tree.delete(*tree.get_children())
            for p in self.db.list_profiles():
                tree.insert("", "end", iid=str(p["id"]), values=(p["profile_name"], p["full_name"]))
        def selected():
            sel = tree.selection()
            return int(sel[0]) if sel else None
        def add():
            dlg = ProfileNameDialog(win, "Add Profile")
            win.wait_window(dlg)
            if dlg.result:
                pid = self.db.create_profile(dlg.result)
                self.db.set_current_profile(pid)
                refresh(); self.reload_current_profile()
        def rename():
            pid = selected()
            if not pid:
                messagebox.showinfo("Select Profile", "Select a profile to rename.", parent=win); return
            current = next(p for p in self.db.list_profiles() if p["id"] == pid)
            dlg = ProfileNameDialog(win, "Rename Profile", current["profile_name"])
            win.wait_window(dlg)
            if dlg.result:
                self.db.rename_profile(pid, dlg.result); refresh(); self.refresh_profile_selector()
        def activate():
            pid = selected()
            if pid:
                self.db.set_current_profile(pid); self.reload_current_profile(); win.destroy()
        def delete():
            pid = selected()
            if not pid:
                messagebox.showinfo("Select Profile", "Select a profile to delete.", parent=win); return
            current = next(p for p in self.db.list_profiles() if p["id"] == pid)
            prompt = f"Permanently delete profile '{current['profile_name']}' and every record linked to it?\n\nThis cannot be undone."
            if not messagebox.askyesno("Delete Profile", prompt, parent=win):
                return
            try:
                self.db.delete_profile(pid); refresh(); self.reload_current_profile()
            except ValueError as exc:
                messagebox.showerror("Delete Profile", str(exc), parent=win)
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(10,0))
        ttk.Button(buttons, text="Add", command=add).pack(side="left", padx=3)
        ttk.Button(buttons, text="Rename", command=rename).pack(side="left", padx=3)
        ttk.Button(buttons, text="Set Active", command=activate).pack(side="left", padx=3)
        ttk.Button(buttons, text="Delete", command=delete).pack(side="left", padx=3)
        ttk.Button(buttons, text="Close", command=win.destroy).pack(side="right", padx=3)
        tree.bind("<Double-1>", lambda e: activate())
        refresh()

    def clear_profile_data(self):
        profile = self.db.get_profile()
        name = profile.get("profile_name") or profile.get("full_name") or "current profile"
        prompt = f"Delete ALL employment, education, training, certification, testimony, teaching, organization, skill, and achievement records for '{name}'?\n\nThe profile itself will remain. This cannot be undone."
        if messagebox.askyesno("Clear Profile Data", prompt, parent=self):
            self.db.clear_current_profile_data()
            self.reload_current_profile()
            self.set_status(f"All records cleared for {name}")

    def _dashboard_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dashboard")
        ttk.Label(tab, text="Professional Qualifications Dashboard", style="Title.TLabel").pack(anchor="w", padx=20, pady=(20, 10))
        self.metrics_frame = ttk.Frame(tab)
        self.metrics_frame.pack(fill="x", padx=20)
        ttk.Button(tab, text="Refresh Dashboard", command=self.refresh_dashboard).pack(anchor="w", padx=20, pady=15)
        self.summary_text = tk.Text(tab, height=18, wrap="word", state="disabled")
        self.summary_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.refresh_dashboard()

    def refresh_dashboard(self):
        for w in self.metrics_frame.winfo_children():
            w.destroy()
        total_hours = self.db.scalar("SELECT COALESCE(SUM(hours),0) FROM training") or 0
        expert = self.db.scalar("SELECT COUNT(*) FROM testimony WHERE witness_type='Expert Witness'") or 0
        fact = self.db.scalar("SELECT COUNT(*) FROM testimony WHERE witness_type='Fact Witness'") or 0
        metrics = [("Training Hours", f"{total_hours:,.2f}"), ("Training Records", str(self.db.count('training'))), ("Certifications", str(self.db.count('certifications'))), ("Expert Testimony", str(expert)), ("Fact Testimony", str(fact))]
        for i, (label, value) in enumerate(metrics):
            box = ttk.LabelFrame(self.metrics_frame, text=label, padding=12)
            box.grid(row=0, column=i, padx=5, sticky="nsew")
            ttk.Label(box, text=value, style="Metric.TLabel").pack()
            self.metrics_frame.columnconfigure(i, weight=1)
        expiring = self.db.conn.execute("SELECT certification, expiration_date FROM certifications WHERE profile_id=? AND expiration_date <> '' ORDER BY expiration_date", (self.db.current_profile_id,)).fetchall()
        text = "Credential expiration tracking\n\n"
        text += "\n".join(f"• {r['certification']}: {r['expiration_date']}" for r in expiring) or "No expiration dates entered."
        text += "\n\nDatabase location\n\n" + str(self.db_path)
        self.summary_text.config(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", text)
        self.summary_text.config(state="disabled")

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
        ttk.Label(frame, text="Select the sections to include. The generated Word document is built directly from the current SQLite records.").pack(anchor="w", pady=(0, 12))
        self.cv_options = {}
        options = [("summary", "Professional Summary", 1), ("core_training", "Core Training", 1), ("employment", "Work Experience", 1), ("teaching", "Teaching Experience", 1), ("organizations", "Professional Organizations", 1), ("certifications", "Certifications", 1), ("skills", "Skills and Tools", 1), ("education", "Education", 1), ("testimony", "Courtroom Testimony", 1), ("full_training", "Detailed Training Appendix", 0)]
        checks = ttk.LabelFrame(frame, text="CV Sections", padding=12)
        checks.pack(fill="x", pady=8)
        for i, (key, label, default) in enumerate(options):
            var = tk.IntVar(value=default)
            ttk.Checkbutton(checks, text=label, variable=var).grid(row=i // 2, column=i % 2, sticky="w", padx=12, pady=5)
            self.cv_options[key] = var
        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=16)
        ttk.Button(actions, text="Generate Word CV...", command=self.generate).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Open Data Folder", command=self.open_data_folder).pack(side="left")
        note = "Date format: YYYY-MM-DD is recommended. Use 'Present' for an ongoing position. Training-hour totals are calculated automatically from records that contain an hours value."
        ttk.Label(frame, text=note, wraplength=850, justify="left").pack(anchor="w", pady=8)

    def generate(self):
        profile = self.db.get_profile()
        default = (profile.get("preferred_name") or "Forensic") + "_CV.docx"
        out = filedialog.asksaveasfilename(title="Save CV", defaultextension=".docx", initialdir=str(portable_resume_dir()), initialfile=default, filetypes=[("Word Document", "*.docx")])
        if not out:
            return
        try:
            options = {k: bool(v.get()) for k, v in self.cv_options.items()}
            generate_cv(self.db, out, options)
            self.set_status(f"CV generated: {out}")
            if messagebox.askyesno("CV Generated", "The CV was created successfully. Open it now?"):
                os.startfile(out) if sys.platform.startswith("win") else os.system(f'xdg-open "{out}" >/dev/null 2>&1 &')
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

    def open_data_folder(self):
        path = str(portable_data_dir())
        if sys.platform.startswith("win"):
            os.startfile(path)
        else:
            os.system(f'xdg-open "{path}" >/dev/null 2>&1 &')

    def set_status(self, text):
        self.status.set(text)

    def on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
