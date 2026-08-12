from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable

DATA_TABLES = [
    "employment", "education", "training", "certifications", "testimony",
    "teaching", "organizations", "skills", "achievements",
]

TABLE_FIELDS = {
    "employment": ["employer", "title", "start_date", "end_date", "location", "description", "sort_order"],
    "education": ["degree", "institution", "graduation_date", "honors", "notes", "sort_order"],
    "training": ["attended_date", "course_name", "provider", "hours", "category", "certificate_number", "expiration_date", "notes", "core_training", "sort_order"],
    "certifications": ["certification", "issuing_organization", "earned_date", "expiration_date", "credential_number", "status", "notes", "sort_order"],
    "testimony": ["testimony_date", "case_number", "court", "jurisdiction", "witness_type", "party", "subject", "outcome", "notes", "sort_order"],
    "teaching": ["organization", "role", "course_name", "start_date", "end_date", "description", "hours", "sort_order"],
    "organizations": ["organization", "role", "start_year", "end_year", "notes", "sort_order"],
    "skills": ["skill", "category", "proficiency", "notes", "sort_order"],
    "achievements": ["achievement", "achievement_date", "organization", "description", "category", "sort_order"],
}

CREATE_DATA_TABLES = {
"employment": """CREATE TABLE IF NOT EXISTS employment (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER NOT NULL, employer TEXT NOT NULL, title TEXT NOT NULL, start_date TEXT, end_date TEXT, location TEXT, description TEXT, sort_order INTEGER DEFAULT 0, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)""",
"education": """CREATE TABLE IF NOT EXISTS education (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER NOT NULL, degree TEXT NOT NULL, institution TEXT NOT NULL, graduation_date TEXT, honors TEXT, notes TEXT, sort_order INTEGER DEFAULT 0, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)""",
"training": """CREATE TABLE IF NOT EXISTS training (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER NOT NULL, attended_date TEXT, course_name TEXT NOT NULL, provider TEXT, hours REAL, category TEXT DEFAULT 'Digital Forensics', certificate_number TEXT, expiration_date TEXT, notes TEXT, core_training INTEGER DEFAULT 0, sort_order INTEGER DEFAULT 0, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)""",
"certifications": """CREATE TABLE IF NOT EXISTS certifications (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER NOT NULL, certification TEXT NOT NULL, issuing_organization TEXT, earned_date TEXT, expiration_date TEXT, credential_number TEXT, status TEXT DEFAULT 'Active', notes TEXT, sort_order INTEGER DEFAULT 0, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)""",
"testimony": """CREATE TABLE IF NOT EXISTS testimony (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER NOT NULL, testimony_date TEXT, case_number TEXT, court TEXT, jurisdiction TEXT, witness_type TEXT DEFAULT 'Fact Witness', party TEXT DEFAULT 'Prosecution', subject TEXT, outcome TEXT, notes TEXT, sort_order INTEGER DEFAULT 0, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)""",
"teaching": """CREATE TABLE IF NOT EXISTS teaching (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER NOT NULL, organization TEXT NOT NULL, role TEXT NOT NULL, course_name TEXT, start_date TEXT, end_date TEXT, description TEXT, hours REAL, sort_order INTEGER DEFAULT 0, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)""",
"organizations": """CREATE TABLE IF NOT EXISTS organizations (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER NOT NULL, organization TEXT NOT NULL, role TEXT, start_year TEXT, end_year TEXT, notes TEXT, sort_order INTEGER DEFAULT 0, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)""",
"skills": """CREATE TABLE IF NOT EXISTS skills (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER NOT NULL, skill TEXT NOT NULL, category TEXT DEFAULT 'Tools', proficiency TEXT, notes TEXT, sort_order INTEGER DEFAULT 0, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)""",
"achievements": """CREATE TABLE IF NOT EXISTS achievements (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER NOT NULL, achievement TEXT NOT NULL, achievement_date TEXT, organization TEXT, description TEXT, category TEXT DEFAULT 'Professional', sort_order INTEGER DEFAULT 0, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)""",
}

PROFILE_FIELDS = ["full_name", "preferred_name", "title", "email", "phone", "summary", "agency"]

class Database:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._migrate_schema()
        self.current_profile_id = self._load_current_profile_id()

    def _table_exists(self, name: str) -> bool:
        return self.conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None

    def _columns(self, table: str) -> list[str]:
        return [r[1] for r in self.conn.execute(f"PRAGMA table_info({table})")]

    def _migrate_schema(self) -> None:
        legacy_profile = None
        if self._table_exists("profile"):
            row = self.conn.execute("SELECT * FROM profile LIMIT 1").fetchone()
            legacy_profile = dict(row) if row else None

        self.conn.execute("""CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_name TEXT NOT NULL,
            full_name TEXT NOT NULL DEFAULT '', preferred_name TEXT DEFAULT '', title TEXT DEFAULT '',
            email TEXT DEFAULT '', phone TEXT DEFAULT '', summary TEXT DEFAULT '', agency TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        self.conn.execute("CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS cv_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER,
            name TEXT NOT NULL, description TEXT, settings_json TEXT NOT NULL,
            FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
        )""")

        existing_profile = self.conn.execute("SELECT id FROM profiles ORDER BY id LIMIT 1").fetchone()
        if not existing_profile:
            p = legacy_profile or {}
            display = p.get("preferred_name") or p.get("full_name") or "Default Profile"
            values = [display] + [p.get(f, "") for f in PROFILE_FIELDS]
            cur = self.conn.execute(
                f"INSERT INTO profiles (profile_name,{','.join(PROFILE_FIELDS)}) VALUES ({','.join('?' for _ in values)})", values)
            default_id = int(cur.lastrowid)
        else:
            default_id = int(existing_profile[0])

        for table in DATA_TABLES:
            if not self._table_exists(table):
                self.conn.execute(CREATE_DATA_TABLES[table])
            elif "profile_id" not in self._columns(table):
                self.conn.execute(f"ALTER TABLE {table} ADD COLUMN profile_id INTEGER")
                self.conn.execute(f"UPDATE {table} SET profile_id=? WHERE profile_id IS NULL", (default_id,))
            self.conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_profile ON {table}(profile_id)")

        for table in DATA_TABLES:
            self.conn.execute(f"UPDATE {table} SET profile_id=? WHERE profile_id IS NULL", (default_id,))
        self.conn.commit()

    def _load_current_profile_id(self) -> int:
        row = self.conn.execute("SELECT value FROM app_settings WHERE key='current_profile_id'").fetchone()
        pid = int(row[0]) if row and str(row[0]).isdigit() else 0
        if not self.conn.execute("SELECT 1 FROM profiles WHERE id=?", (pid,)).fetchone():
            pid = int(self.conn.execute("SELECT id FROM profiles ORDER BY id LIMIT 1").fetchone()[0])
        self.set_current_profile(pid)
        return pid

    def close(self) -> None:
        self.conn.close()

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
        return str(row[0]) if row else default

    def set_setting(self, key: str, value: str) -> None:
        self.conn.execute("INSERT OR REPLACE INTO app_settings(key,value) VALUES(?,?)", (key, str(value)))
        self.conn.commit()

    def create_blank_profile(self, profile_name: str = "New Profile") -> int:
        return self.create_profile(profile_name, "")

    def list_profiles(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM profiles ORDER BY profile_name COLLATE NOCASE")]

    def create_profile(self, profile_name: str, full_name: str = "") -> int:
        cur = self.conn.execute("INSERT INTO profiles (profile_name, full_name) VALUES (?,?)", (profile_name.strip(), full_name.strip()))
        self.conn.commit()
        return int(cur.lastrowid)

    def rename_profile(self, profile_id: int, profile_name: str) -> None:
        self.conn.execute("UPDATE profiles SET profile_name=? WHERE id=?", (profile_name.strip(), profile_id))
        self.conn.commit()

    def set_current_profile(self, profile_id: int) -> None:
        if not self.conn.execute("SELECT 1 FROM profiles WHERE id=?", (profile_id,)).fetchone():
            raise ValueError("Profile not found")
        self.current_profile_id = profile_id
        self.conn.execute("INSERT OR REPLACE INTO app_settings(key,value) VALUES('current_profile_id',?)", (str(profile_id),))
        self.conn.commit()

    def delete_profile(self, profile_id: int) -> None:
        if len(self.list_profiles()) <= 1:
            raise ValueError("At least one profile must remain.")
        self.conn.execute("DELETE FROM profiles WHERE id=?", (profile_id,))
        self.conn.commit()
        if profile_id == self.current_profile_id:
            self.set_current_profile(int(self.conn.execute("SELECT id FROM profiles ORDER BY id LIMIT 1").fetchone()[0]))

    def clear_current_profile_data(self) -> None:
        for table in DATA_TABLES:
            self.conn.execute(f"DELETE FROM {table} WHERE profile_id=?", (self.current_profile_id,))
        self.conn.commit()

    def get_profile(self) -> dict[str, Any]:
        row = self.conn.execute("SELECT * FROM profiles WHERE id=?", (self.current_profile_id,)).fetchone()
        return dict(row) if row else {}

    def save_profile(self, data: dict[str, Any]) -> None:
        values = [data.get(f, "") for f in PROFILE_FIELDS] + [self.current_profile_id]
        self.conn.execute(f"UPDATE profiles SET {', '.join(f'{f}=?' for f in PROFILE_FIELDS)} WHERE id=?", values)
        current = self.get_profile()
        if current.get("profile_name") in ("Default Profile", "") and (data.get("preferred_name") or data.get("full_name")):
            self.conn.execute("UPDATE profiles SET profile_name=? WHERE id=?", (data.get("preferred_name") or data.get("full_name"), self.current_profile_id))
        self.conn.commit()

    def list_rows(self, table: str, order_by: str | None = None) -> list[dict[str, Any]]:
        self._validate_table(table)
        if order_by is None:
            date_fields = {"employment":"COALESCE(end_date, 'Present') DESC, start_date DESC", "education":"graduation_date DESC", "training":"attended_date DESC", "certifications":"earned_date DESC", "testimony":"testimony_date DESC", "teaching":"start_date DESC", "organizations":"start_year DESC", "skills":"category, skill", "achievements":"achievement_date DESC"}
            order_by = f"{date_fields[table]}, sort_order, id DESC"
        rows = self.conn.execute(f"SELECT * FROM {table} WHERE profile_id=? ORDER BY {order_by}", (self.current_profile_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_row(self, table: str, row_id: int) -> dict[str, Any] | None:
        self._validate_table(table)
        row = self.conn.execute(f"SELECT * FROM {table} WHERE id=? AND profile_id=?", (row_id, self.current_profile_id)).fetchone()
        return dict(row) if row else None

    def insert_row(self, table: str, data: dict[str, Any]) -> int:
        self._validate_table(table)
        fields = [f for f in TABLE_FIELDS[table] if f in data]
        values = [self.current_profile_id] + [data[f] for f in fields]
        cur = self.conn.execute(f"INSERT INTO {table} (profile_id,{','.join(fields)}) VALUES ({','.join('?' for _ in values)})", values)
        self.conn.commit()
        return int(cur.lastrowid)

    def update_row(self, table: str, row_id: int, data: dict[str, Any]) -> None:
        self._validate_table(table)
        fields = [f for f in TABLE_FIELDS[table] if f in data]
        values = [data[f] for f in fields] + [row_id, self.current_profile_id]
        self.conn.execute(f"UPDATE {table} SET {', '.join(f'{f}=?' for f in fields)} WHERE id=? AND profile_id=?", values)
        self.conn.commit()

    def delete_row(self, table: str, row_id: int) -> None:
        self._validate_table(table)
        self.conn.execute(f"DELETE FROM {table} WHERE id=? AND profile_id=?", (row_id, self.current_profile_id))
        self.conn.commit()

    def count(self, table: str) -> int:
        self._validate_table(table)
        return int(self.conn.execute(f"SELECT COUNT(*) FROM {table} WHERE profile_id=?", (self.current_profile_id,)).fetchone()[0])

    def scalar(self, query: str, params: Iterable[Any] = ()) -> Any:
        lowered = query.lower()
        for table in DATA_TABLES:
            marker = f" from {table}"
            if marker in lowered and "profile_id" not in lowered:
                if " where " in lowered:
                    query += " AND profile_id=?"
                else:
                    query += " WHERE profile_id=?"
                params = tuple(params) + (self.current_profile_id,)
                break
        row = self.conn.execute(query, tuple(params)).fetchone()
        return row[0] if row else None

    def _validate_table(self, table: str) -> None:
        if table not in TABLE_FIELDS:
            raise ValueError(f"Unsupported table: {table}")
