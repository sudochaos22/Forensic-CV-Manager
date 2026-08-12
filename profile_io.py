from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from database import DATA_TABLES, PROFILE_FIELDS, Database

FORMAT_NAME = "ForensicCVManagerProfile"
FORMAT_VERSION = 1

def export_profile(db: Database, output_path: str | Path) -> Path:
    profile = db.get_profile()
    payload: dict[str, Any] = {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "profile": {k: profile.get(k, "") for k in ["profile_name", *PROFILE_FIELDS]},
        "records": {table: db.list_rows(table) for table in DATA_TABLES},
    }
    for rows in payload["records"].values():
        for row in rows:
            row.pop("id", None); row.pop("profile_id", None)
    path = Path(output_path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

def import_profile(db: Database, input_path: str | Path, profile_name: str | None = None) -> int:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    if payload.get("format") != FORMAT_NAME or payload.get("version") != FORMAT_VERSION:
        raise ValueError("This is not a supported Forensic CV Manager profile export.")
    p = payload.get("profile") or {}
    name = (profile_name or p.get("profile_name") or p.get("preferred_name") or p.get("full_name") or "Imported Profile").strip()
    pid = db.create_profile(name, p.get("full_name", ""))
    prior = db.current_profile_id
    try:
        db.set_current_profile(pid)
        db.save_profile({field: p.get(field, "") for field in PROFILE_FIELDS})
        records = payload.get("records") or {}
        for table in DATA_TABLES:
            for row in records.get(table, []):
                clean = {k: v for k, v in row.items() if k not in {"id", "profile_id"}}
                db.insert_row(table, clean)
    except Exception:
        db.set_current_profile(prior)
        db.delete_profile(pid)
        raise
    return pid
