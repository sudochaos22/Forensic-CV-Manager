from pathlib import Path
from database import Database
from cv_generator import generate_cv
from pdf_export import generate_pdf

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "template.sqlite3"
if not DB_PATH.exists():
    raise SystemExit("Run create_release_template.py first")

db = Database(DB_PATH)
try:
    generate_cv(db, ROOT / "Sample_Generated_CV.docx", {"full_training": True})
    generate_pdf(db, ROOT / "Sample_Generated_CV.pdf", {"full_training": True}, theme_name="Professional")
finally:
    db.close()
print("Sample CV outputs generated.")
