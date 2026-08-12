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
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def portable_data_dir() -> Path:
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
    path = application_dir() / "Resume"
    path.mkdir(parents=True, exist_ok=True)
    return path


def legacy_database_path() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    else:
        base = Path.home() / ".local" / "share"
    return base / "ForensicCVManager" / "forensic_cv.sqlite3"


def prepare_portable_database() -> Path:
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
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right", padx=5)
        ttk.Button(buttons, text="Save", command=self.save).pack(side="right", padx=5)
        self.bind("<Escape>", lambda e: self.destroy())

    def save(self):
        result = {}
        for field in TABLE_CONFIG[self.table]["fields"] if hasattr(self, "table") else []:
            pass
        for name, widget in self.widgets.items():
            if isinstance(widget, tk.Text):
                result[name] = widget.get("1.0", "end").strip()
            elif name in self.vars:
                result[name] = self.vars[name].get()
        for name in DATE_FIELDS | YEAR_FIELDS:
            if name in result and str(result[name]).strip():
                result[name] = normalize_date(result[name], allow_present=name in {"end_date", "end_year"})
        if "hours" in result and str(result["hours"]).strip():
            try:
                result["hours"] = float(result["hours"])
            except ValueError:
                messagebox.showerror("Hours", "Hours must be numeric.", parent=self)
                return
        self.result = result
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        splash = SplashScreen(self, APP_VERSION)
        splash.step("Preparing portable folders…", 20)
        self.db_path = prepare_portable_database()
        splash.step("Opening database…", 42)
        self.db = Database(self.db_path)
        splash.step("Loading interface…", 65)
        self.theme_name = load_theme_preference()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1180x720")
        self.minsize(900, 580)
        try:
            self.iconbitmap(str(resource_path("assets/app.ico")))
        except Exception:
            pass
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._configure_styles()
        self._build_menu()
        self._build_profile_bar()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        self.record_tabs = {}
        self._dashboard_tab()
        self._profile_tab()
        for table, config in TABLE_CONFIG.items():
            self.record_tabs[table] = RecordTab(self.notebook, self, table, config)
        self._generate_tab()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", side="bottom")
        splash.step("Refreshing records…", 88)
        self.refresh_all()
        splash.step("Ready", 100)
        self.after(180, splash.destroy)
        self.after(200, self.deiconify)

    def _configure_styles(self):
        style = ttk.Style(self)
        if sys.platform.startswith("win"):
            try:
                style.theme_use("vista")
            except tk.TclError:
                pass
        if self.theme_name == "dark":
            bg, panel, fg, muted = "#202124", "#2b2d31", "#f2f3f5", "#b5bac1"
            self.configure(bg=bg)
            style.configure("TFrame", background=bg)
            style.configure("TLabelframe", background=bg, foreground=fg)
            style.configure("TLabelframe.Label", background=bg, foreground=fg)
            style.configure("TLabel", background=bg, foreground=fg)
            style.configure("TButton", padding=(8, 4))
            style.configure("TEntry", fieldbackground=panel, foreground=fg)
            style.configure("TCombobox", fieldbackground=panel, foreground=fg)
            style.configure("Treeview", background=panel, fieldbackground=panel, foreground=fg)
            style.configure("Treeview.Heading", background="#35373c", foreground=fg)
            style.map("Treeview", background=[("selected", "#1f4e79")], foreground=[("selected", "#ffffff")])
            style.configure("TNotebook", background=bg)
            style.configure("TNotebook.Tab", background="#35373c", foreground=fg, padding=(10, 5))
            style.map("TNotebook.Tab", background=[("selected", panel)], foreground=[("selected", "#ffffff")])
            style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#8ab4f8", background=bg)
            style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground=muted, background=bg)
        else:
            self.configure(bg="SystemButtonFace" if sys.platform.startswith("win") else "#f0f0f0")
            try:
                style.configure("TFrame", background="SystemButtonFace")
                style.configure("TLabel", background="SystemButtonFace", foreground="SystemWindowText")
                style.configure("TLabelframe", background="SystemButtonFace")
                style.configure("TLabelframe.Label", background="SystemButtonFace", foreground="SystemWindowText")
            except tk.TclError:
                pass
            style.configure("TButton", padding=(6, 3))
            style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1f4e79")
            style.configure("Subtitle.TLabel", font=("Segoe UI", 10))

    def _build_menu(self):
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="New Blank Profile", command=self.new_blank_profile)
        file_menu.add_command(label="Export Current Profile…", command=self.export_current_profile)
        file_menu.add_command(label="Import Profile…", command=self.import_profile_file)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Database…", command=self.backup_db)
        file_menu.add_command(label="Restore Database…", command=self.restore_db)
        file_menu.add_command(label="Open Resume Folder", command=self.open_resume_folder)
        file_menu.add_command(label="Open Data Folder", command=self.open_data_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menu.add_cascade(label="File", menu=file_menu)

        tools = tk.Menu(menu, tearoff=False)
        tools.add_command(label="Manage Profiles…", command=self.manage_profiles)
        tools.add_command(label="Load Sample Data", command=self.load_sample_data)
        tools.add_command(label="Clear Current Profile Data…", command=self.clear_current_profile_data)
        tools.add_separator()
        appearance = tk.Menu(tools, tearoff=False)
        appearance.add_command(label="Light Mode", command=lambda: self.set_theme("light"))
        appearance.add_command(label="Dark Mode", command=lambda: self.set_theme("dark"))
        tools.add_cascade(label="Appearance", menu=appearance)
        tools.add_separator()
        tools.add_command(label="Check for Updates", command=self.check_updates)
        menu.add_cascade(label="Tools", menu=tools)

        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="User Manual", command=self.show_manual)
        help_menu.add_command(label="How to Add Records", command=lambda: self.show_manual("Adding records"))
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        menu.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu)

    def set_theme(self, theme: str):
        if theme == self.theme_name:
            return
        self.theme_name = theme
        save_theme_preference(theme)
        messagebox.showinfo("Appearance", "Appearance changed. Restart the application to apply it completely.", parent=self)

    def show_manual(self, section: str | None = None):
        text = (
            "Forensic CV Manager User Manual\n\n"
            "Adding records\n"
            "1. Select the intended examiner from Active Profile.\n"
            "2. Open the appropriate record tab.\n"
            "3. Select Add, complete the fields, and select Save.\n\n"
            "Dates\n"
            "Common date formats are accepted, including full dates, month/year values, and year-only values. Employment end dates may use Present, Current, Ongoing, or Now.\n\n"
            "Editing and deleting\n"
            "Select a record and use Edit or Delete. Deletion is permanent.\n\n"
            "Profiles\n"
            "Use Active Profile to switch examiners. Manage Profiles can add, rename, switch, or delete profiles.\n\n"
            "Generating a CV\n"
            "Use Generate CV to select sections. PDF output uses Professional styling and is generated directly by the application.\n\n"
            "Backup and portability\n"
            "Keep the executable and data, Resume, and Backups folders together. Back up the database regularly."
        )
        win = tk.Toplevel(self)
        win.title("User Manual")
        win.geometry("720x560")
        box = tk.Text(win, wrap="word", padx=14, pady=14)
        box.insert("1.0", text)
        box.config(state="disabled")
        box.pack(fill="both", expand=True)
        if section:
            pos = box.search(section, "1.0", nocase=True)
            if pos:
                box.see(pos)

    def show_about(self):
        messagebox.showinfo("About", f"{APP_NAME}\nVersion {APP_VERSION}\n\nPortable professional portfolio and CV manager.", parent=self)

    def check_updates(self):
        try:
            result = check_github_release(GITHUB_REPOSITORY, APP_VERSION)
            if result.message:
                messagebox.showinfo("Updates", result.message, parent=self)
            elif result.update_available:
                if messagebox.askyesno("Update Available", f"Version {result.latest_version} is available. Open the release page?", parent=self):
                    webbrowser.open(result.release_url)
            else:
                messagebox.showinfo("Updates", f"You are using the current version ({APP_VERSION}).", parent=self)
        except Exception as exc:
            messagebox.showerror("Update Check", str(exc), parent=self)

    def _build_profile_bar(self):
        bar = ttk.Frame(self, padding=(8, 6))
        bar.pack(fill="x")
        ttk.Label(bar, text="Active Profile:").pack(side="left")
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(bar, textvariable=self.profile_var, state="readonly", width=34)
        self.profile_combo.pack(side="left", padx=(6, 8))
        self.profile_combo.bind("<<ComboboxSelected>>", self.switch_profile)
        ttk.Button(bar, text="Manage Profiles", command=self.manage_profiles).pack(side="left")
        self.refresh_profile_selector()

    def refresh_profile_selector(self):
        profiles = self.db.list_profiles()
        display_names = []
        used = {}
        self.profile_lookup = {}
        for p in profiles:
            base = (p.get("profile_name") or p.get("preferred_name") or p.get("full_name") or "Profile").strip()
            used[base] = used.get(base, 0) + 1
            display = base if used[base] == 1 else f"{base} ({used[base]})"
            display_names.append(display)
            self.profile_lookup[display] = p["id"]
            if p["id"] == self.db.current_profile_id:
                self.profile_var.set(display)
        self.profile_combo["values"] = display_names

    def switch_profile(self, _event=None):
        pid = self.profile_lookup.get(self.profile_var.get())
        if pid:
            self.db.set_current_profile(pid)
            self.refresh_all()

    def new_blank_profile(self):
        dialog = ProfileNameDialog(self, "New Blank Profile")
        self.wait_window(dialog)
        if dialog.result:
            pid = self.db.create_blank_profile(dialog.result)
            self.db.set_current_profile(pid)
            self.refresh_profile_selector()
            self.refresh_all()

    def manage_profiles(self):
        win = tk.Toplevel(self)
        win.title("Manage Profiles")
        win.geometry("520x360")
        tree = ttk.Treeview(win, columns=("name", "full"), show="headings")
        tree.heading("name", text="Profile Name"); tree.heading("full", text="Full Name")
        tree.column("name", width=210); tree.column("full", width=250)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def refresh():
            tree.delete(*tree.get_children())
            for p in self.db.list_profiles():
                tree.insert("", "end", iid=str(p["id"]), values=(p.get("profile_name", ""), p.get("full_name", "")))

        def add():
            dialog = ProfileNameDialog(win, "Add Profile")
            win.wait_window(dialog)
            if dialog.result:
                self.db.create_profile(dialog.result)
                refresh(); self.refresh_profile_selector()

        def rename():
            sel = tree.selection()
            if not sel: return
            pid = int(sel[0]); current = tree.item(sel[0], "values")[0]
            dialog = ProfileNameDialog(win, "Rename Profile", current)
            win.wait_window(dialog)
            if dialog.result:
                self.db.rename_profile(pid, dialog.result); refresh(); self.refresh_profile_selector()

        def activate():
            sel = tree.selection()
            if not sel: return
            self.db.set_current_profile(int(sel[0])); self.refresh_profile_selector(); self.refresh_all(); win.destroy()

        def delete():
            sel = tree.selection()
            if not sel: return
            if messagebox.askyesno("Delete Profile", "Delete this profile and all of its records permanently?", parent=win):
                try:
                    self.db.delete_profile(int(sel[0])); refresh(); self.refresh_profile_selector(); self.refresh_all()
                except Exception as exc:
                    messagebox.showerror("Delete Profile", str(exc), parent=win)

        buttons = ttk.Frame(win); buttons.pack(fill="x", padx=10, pady=(0, 10))
        for text, cmd in [("Add", add), ("Rename", rename), ("Activate", activate), ("Delete", delete)]:
            ttk.Button(buttons, text=text, command=cmd).pack(side="left", padx=4)
        refresh()

    def export_current_profile(self):
        out = filedialog.asksaveasfilename(title="Export Profile", defaultextension=".fcvprofile.json", filetypes=[("Forensic CV Profile", "*.fcvprofile.json"), ("JSON", "*.json")])
        if out:
            export_profile(self.db, out); self.set_status(f"Profile exported: {out}")

    def import_profile_file(self):
        src = filedialog.askopenfilename(title="Import Profile", filetypes=[("Forensic CV Profile", "*.fcvprofile.json"), ("JSON", "*.json")])
        if not src: return
        try:
            pid = import_profile(self.db, src)
            self.db.set_current_profile(pid)
            self.refresh_profile_selector(); self.refresh_all()
            messagebox.showinfo("Import Profile", "Profile imported successfully.", parent=self)
        except Exception as exc:
            messagebox.showerror("Import Profile", str(exc), parent=self)

    def load_sample_data(self):
        if messagebox.askyesno("Load Sample Data", "Replace records in the current profile with the fictitious demonstration data?", parent=self):
            load_sample_profile(self.db, clear=True)
            self.refresh_all()

    def clear_current_profile_data(self):
        if messagebox.askyesno("Clear Profile Data", "Permanently delete all CV records for the active profile?", parent=self):
            self.db.clear_current_profile_data(); self.refresh_all()

    def _dashboard_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dashboard")
        self.dashboard_tab = tab
        outer = ttk.Frame(tab, padding=18)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Professional Portfolio Dashboard", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Current-profile metrics and credential status", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.dashboard_metrics = ttk.Frame(outer); self.dashboard_metrics.pack(fill="x")
        body = ttk.Frame(outer); body.pack(fill="both", expand=True, pady=12)
        self.dashboard_chart = tk.Canvas(body, height=300, highlightthickness=0)
        self.dashboard_chart.pack(side="left", fill="both", expand=True)
        self.cert_alerts = tk.Text(body, width=48, wrap="word", height=18)
        self.cert_alerts.pack(side="right", fill="y", padx=(12, 0))

    def refresh_dashboard(self):
        for w in self.dashboard_metrics.winfo_children(): w.destroy()
        metrics = [
            ("Training Hours", f"{float(self.db.scalar('SELECT COALESCE(SUM(hours),0) FROM training') or 0):,.1f}"),
            ("Training Records", str(self.db.count('training'))),
            ("Certifications", str(self.db.count('certifications'))),
            ("Testimony", str(self.db.count('testimony'))),
        ]
        for i, (label, value) in enumerate(metrics):
            box = ttk.LabelFrame(self.dashboard_metrics, text=label, padding=10)
            box.grid(row=0, column=i, padx=6, sticky="nsew"); self.dashboard_metrics.columnconfigure(i, weight=1)
            ttk.Label(box, text=value, font=("Segoe UI", 18, "bold")).pack()

        counts = [(TABLE_CONFIG[t]["label"], self.db.count(t)) for t in TABLE_CONFIG]
        self._draw_dashboard_chart(counts)
        self.cert_alerts.config(state="normal"); self.cert_alerts.delete("1.0", "end")
        self.cert_alerts.insert("end", "Certification Status\n\n")
        today = date.today()
        for row in self.db.list_rows("certifications"):
            exp = row.get("expiration_date")
            if exp:
                try:
                    y, m, d, *_ = date_sort_key(exp)
                    if y > 0:
                        dt = date(y, max(m, 1), max(d, 1))
                        days = (dt - today).days
                        status = "EXPIRED" if days < 0 else (f"Expires in {days} days" if days <= 180 else "Active")
                        self.cert_alerts.insert("end", f"• {row.get('certification')}: {status}\n")
                except Exception:
                    pass
        self.cert_alerts.config(state="disabled")

    def _draw_dashboard_chart(self, counts):
        self.dashboard_chart.delete("all")
        self.dashboard_chart.configure(bg="#2b2d31" if self.theme_name == "dark" else "white")
        self.dashboard_chart.update_idletasks()
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
