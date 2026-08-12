# Forensic CV Manager 2.4.0

Forensic CV Manager is a portable SQLite-backed desktop application for tracking professional qualifications and generating court-ready curricula vitae.

## Release privacy

The release template contains only fictitious demonstration data for **Alex Morgan** at the fictional **Metro Regional Public Safety Laboratory**. No developer, agency, personal email, phone number, case number, or employment history is included.

On first launch, `data/template.sqlite3` is copied to `data/forensic_cv.sqlite3`. The template remains unchanged and the working database stores all user edits.

## Features

- Semantic Versioning with one centralized version source
- Built-in user manual under Help
- Persistent light and dark appearance modes while retaining the v2.2.0 base layout
- Branded application icon and startup splash screen with version/loading status
- Integrated PDF preview with page navigation, zoom, fit-width, and save-after-review
- Branded optional Inno Setup installer artwork and license screen
- Restored v2.2.0-style Tkinter layout and visual scheme
- Portable SQLite database beside the executable
- Multiple independent examiner profiles
- Create, edit, and delete individual records
- Clear all records for the selected profile
- Fictitious sample database and reusable sample-data command
- Import/export a single profile as `.fcvprofile.json`
- Flexible date entry with chronological report sorting
- Dashboard metrics, record-count chart, and certification expiration alerts
- Word CV generation
- Native PDF generation through ReportLab with no Office dependency
- Consistent Professional-style native PDF output
- PDF page numbers, clickable links, and document metadata
- Shared renderer-neutral CV data model for consistent Word and PDF content
- Portable `Resume`, `data`, and `Backups` folders
- Optional GitHub release update checker
- Portable ZIP build and optional Inno Setup installer
- Optional Authenticode signing hook
- Click-to-sort record columns with type-aware date, numeric, Yes/No, and natural-text ordering

## Run from Python

```bat
python -m pip install -r requirements.txt
python app.py
```

## Build the portable Windows release

```bat
build_windows.bat
```

Copy the entire `dist` folder to the flash drive. Do not copy only the executable.

## Build an installer

Install Inno Setup 6, run `build_windows.bat`, and then run:

```bat
build_installer.bat
```

The installer is created in the `installer` folder. The portable build remains the preferred option for flash-drive use.

## Code signing

A trusted signing certificate is not included. To sign during the build, install the Windows SDK so `signtool.exe` is available and set these environment variables before running `build_windows.bat`:

```bat
set SIGN_PFX=C:\Certificates\YourCodeSigningCertificate.pfx
set SIGN_PASSWORD=your-password
build_windows.bat
```

Without a trusted certificate, Windows may display **Unknown Publisher**. The build cannot legitimately remove that warning by itself.

## Update checker

`app_config.py` is configured for:

```python
GITHUB_REPOSITORY = "JSPadilla/Forensic-CV-Manager"
```

The checker reads the latest public GitHub release and compares its tag with `APP_VERSION`. It does not download or install updates automatically.

## PDF generation

Use **Preview & Save PDF** on the Generate CV tab to review a temporary native PDF inside the application before saving it. PDF files are generated directly with ReportLab. Microsoft Word and LibreOffice are not required. Word documents are generated independently with python-docx for users who need an editable copy. Both renderers use the same normalized CV data model.

## Profile exchange

Use **File > Export Current Profile** to create a JSON profile package. Use **File > Import Profile** to add it as a separate profile. Imports never overwrite an existing profile.

## Backups

The working database is:

```text
data\forensic_cv.sqlite3
```

Back up that file regularly to a location separate from the flash drive.

## Version management

The release version is defined once in `version.py` using Semantic Versioning (`MAJOR.MINOR.PATCH`). The build scripts generate Windows executable metadata and Inno Setup version information from that value.

## User manual

Open **Help > User Manual** for instructions covering profiles, adding records, flexible dates, editing, deletion, CV generation, backups, and portable use. **Help > How to Add Records** opens directly to the record-entry instructions.

## Sorting records

Record lists can be sorted by clicking a column heading. Click once for ascending order and click the same heading again for descending order. The active heading displays an arrow showing the current direction. Dates are sorted chronologically, hours numerically, and text alphabetically using natural ordering. Sorting changes only the on-screen list; it does not alter the database or the chronological ordering used by generated CV reports.
