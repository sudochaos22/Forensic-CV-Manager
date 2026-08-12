from pathlib import Path
from database import Database
from sample_data import load_sample_profile

root = Path(__file__).resolve().parent
data_dir = root / "data"
data_dir.mkdir(exist_ok=True)
path = data_dir / "template.sqlite3"
path.unlink(missing_ok=True)
db = Database(path)
load_sample_profile(db, clear=True)
db.rename_profile(db.current_profile_id, "Sample Examiner")
db.set_setting("release_template", "1")
db.close()
print(path)
