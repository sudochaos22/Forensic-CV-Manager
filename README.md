# Forensic CV Manager v1.2 Portable Multi-Profile

A Windows-friendly, database-driven Python application for tracking the professional qualifications of a sworn law-enforcement digital forensic examiner and generating a Microsoft Word CV on demand.

## Included in this version

- Tkinter desktop GUI with a resizable interface
- SQLite database stored in the user's local application-data folder
- Dashboard with training hours, record counts, and testimony totals
- Profile and professional-summary management
- Employment, education, training, certifications, testimony, teaching, organizations, skills, and achievements
- Search, add, edit, and delete functions for every record category
- Core-training flag for selecting prominent courses
- Credential expiration-date tracking
- Configurable Word CV generation
- Optional full training appendix with automatically calculated hours
- Database backup and restore
- Starter data derived from the supplied 2026 CV

## Installation from source

1. Install Python 3.11 or newer.
2. Open Command Prompt in this folder.
3. Run:

   `python -m pip install -r requirements.txt`

4. Start the application:

   `python app.py`

On Windows, `run_windows.bat` performs step 4.

## Build a standalone Windows executable

Run `build_windows.bat`. The finished executable will be placed in:

`dist\ForensicCVManager.exe`

The SQLite database is not embedded in the executable. It is created in:

`%LOCALAPPDATA%\ForensicCVManager\forensic_cv.sqlite3`

This design allows the executable to be replaced or upgraded without overwriting the user's records.

## Recommended data conventions

- Dates: `YYYY-MM-DD`
- Month-only employment dates: `YYYY-MM`
- Ongoing position: `Present`
- Training hours: numeric values only
- Credential expiration dates: `YYYY-MM-DD`

## Important note about imported training

The supplied CV reports 3,319.25 total training hours, but some lines mix course hours, expiration dates, degree credits, or missing hour values. This starter database includes the clearly structured training entries available from the CV, but the dashboard total should be reconciled against source certificates and the complete training spreadsheet before being treated as an official total.


## Windows executable build note

Run `build_windows.bat`. The script invokes PyInstaller through `python -m PyInstaller`, avoiding PATH issues with user-level installations.

## Multiple profiles and deletion controls

This version supports multiple independent users/examiners in one portable database.

- Use the **Active Profile** selector at the top of the application to switch users.
- Select **Manage Profiles** to add, rename, activate, or permanently delete a profile.
- Each profile has separate employment, education, training, certifications, testimony, teaching, organizations, skills, achievements, dashboard totals, and generated CV output.
- The Delete button on each data tab permanently deletes the selected record.
- Select **File > Clear Current Profile Data...** to delete all CV records for the active profile while retaining the profile itself.
- Deleting a profile permanently deletes all records linked to that profile. At least one profile must remain.

Existing single-user v1 databases are migrated automatically into the first profile. Back up the portable database before deleting a profile or clearing profile data.

## Version 1.3 report corrections

- CV generation now writes complete stored text without shortening dates or rebuilding descriptions sentence-by-sentence.
- User-entered line breaks are preserved in summaries and narrative descriptions.
- Date-bearing records are ordered newest to oldest in generated CV sections and record lists; manual sort order is used only to break ties.
- Date formatting is compatible with Windows Python.

## Version 1.4 updates

- Date fields accept common formats such as `3/5/2026`, `03-05-2026`, `2026-03-05`, `March 5, 2026`, `March 2026`, and `2026`.
- Accepted dates are normalized internally for reliable chronological sorting.
- Employment end dates also accept `Present`, `Current`, `Ongoing`, or `Now`.
- Generated CVs now default to a portable `Resume` folder beside the application executable. The folder is created automatically.

## Version 1.4 updates

- Date fields accept common formats such as `3/5/2026`, `03-05-2026`, `2026-03-05`, `March 5, 2026`, `March 2026`, and `2026`.
- Accepted dates are normalized internally for reliable chronological sorting.
- Employment end dates also accept `Present`, `Current`, `Ongoing`, or `Now`.
- Generated CVs now default to a portable `Resume` folder beside the application executable. The folder is created automatically.
