# Forensic CV Manager Professional

**Current Version: 2.5.1**

Forensic CV Manager Professional is a digital-forensics-focused professional experience, casework, training, certification, expert-witness, and career tracking application.

This project is an expanded fork of the original Forensic CV Manager and adds professional tracking, casework statistics, reporting, dashboard metrics, tool normalization, expert-witness documentation, and other DFIR-focused features.


## What's New in v2.5.1

Version 2.5.1 expands Training and Case Work tracking and adds additional current-year forensic workload metrics.

### Training Improvements

- Added an editable **Provider** dropdown.
- Added an editable **Category** dropdown.
- Both dropdowns include common predefined values while still allowing custom text entries.
- Default Provider and Category options can be customized in `professional_v251.py`.

### Case Work Improvements

Added the following fields:

- **Evidence Size (GB)**
- **Image Date**
- **Image Time (Minutes)**
- **Process Date**
- **Process Time (Minutes)**
- **Artifacts Identified**

Also added:

- **PST** as a Device Type option.

### Dashboard Improvements

Added current-year forensic workload statistics:

- **Imaging Time**
- **Processing Time**
- **Data Analyzed**

Imaging time is calculated using the **Image Date**.

Processing time and Data Analyzed are calculated using the **Process Date**.

Time totals are displayed automatically in days, hours, and minutes:

```text
2d 6h 31m```

## Features Introduced in v2.5

### 1. Global Search
A **Global Search** button appears beside **Manage Profiles**.

It searches all professional record tables for the active profile and can jump directly to the selected record.

### 2. Filters on record tabs
Record tabs now support:
- Normal text search
- Table-appropriate dropdown filters
- Year filtering when the table has a primary date
- Clear Filters
- `Showing X of Y records`

### 3. Dashboard drill-down
Dashboard metric cards are buttons.

Examples:
- Cases -> Case Index
- Examinations -> Case Work
- Reports -> Forensic Reports
- Peer Reviews -> Peer / Technical Reviews
- Testimony -> Courtroom Testimony
- Training Hrs -> Training

The dashboard also shows current-year activity.

### 4. Annual statistics
Current-year activity is summarized on the dashboard.

Generate CV also gains an **Annual Activity Report...** button that creates both:
- `.docx`
- `.pdf`

The annual report includes examination counts/hours, reports, reviews, testimony, training/CPE, teaching, presentations, publications, validation, SOP/policy, mentoring, projects, device types, acquisition methods, and tool usage.

### 5. Tool normalization
A new **Tool Library** stores canonical tool names and aliases.

The Case Work `Tools Used` field becomes a multi-select selector.

Examples:
- `AXIOM`
- `Magnet Axiom`
- `Magnet AXIOM`

can all normalize to:

`Magnet AXIOM`

Tool Library has a **Normalize Existing Case Work** command.

### 6. Case-to-record relationships
A new **Case Index** provides one case/reference record per case number.

The database adds an internal `case_id` link to:
- Case Work
- Forensic Reports
- Peer / Technical Reviews
- Testimony
- Court Qualifications

Existing records are linked automatically by matching case number.

Select a Case Index record and choose **View Linked Records** to see its related professional-history records.

### 7. Export presets
Generate CV gains these built-in presets:
- Standard CV
- Expert Witness CV
- Voir Dire Package
- Full Professional Record
- Annual Review
- Training / CPE Report

You can also save/delete custom presets.

Privacy fields stay off unless you explicitly enable them.

### 8. Expert Qualification / Voir Dire report
Generate CV gains **Expert Qualification Report...**

It creates both Word and PDF and summarizes:
- Cases/examinations
- Examination hours
- Reports
- Peer reviews
- Expert testimony
- Court qualification records
- Training
- Certifications
- Tool usage
- Quality/validation experience

It intentionally omits case numbers and evidence identifiers.

### 9. Annual Professional Activity report
Choose a calendar year and generate an annual activity report in Word and PDF.

### 10. Certification/CPE alerts
Dashboard alerts include:
- Expired credentials
- Credentials within 90 / 180 / 365 days
- CPE/CE progress and remaining credits when those fields are populated

### 11. Data validation
The new record dialog checks:
- Numeric fields
- Negative numeric values
- Date formats
- End date before start date
- Data-size entries such as `938 GB` or `1.5 TB`
- Duplicate certification warnings
- Duplicate Case Work warnings
- Duplicate Case Index numbers
- Duplicate Tool Library names

### 12. Automatic backups
On application startup, if a working SQLite database already exists, a daily copy is stored in:

`Backups\Auto\`

File format:

`forensic_cv_auto_YYYY-MM-DD.sqlite3`

The newest **30** automatic backups are retained.

This does not replace a separate encrypted/off-device backup strategy.

### 13. Schema versioning
The database now contains:

`schema_meta`

with:

`schema_version = 5`

and:

`professional_version = 2.5.1`

### 14. About screen
The About screen identifies the Professional Edition, application version, database schema, and backup policy.

### 15. Changelog
Help gains:

**Professional Edition Changelog**

## Install

1. Close Forensic CV Manager.
2. Extract this ZIP.
3. Copy/run the package from your project folder, or copy these files there:
   - `professional_v25.py`
   - `apply_v25_upgrade.py`
4. Open Command Prompt:

```bat
cd /d "D:\Forensic-CV-Manager-2.5.0"
python apply_v25_upgrade.py
```

The installer creates:

`upgrade_backups\v25_YYYYMMDD_HHMMSS\`

before modifying source/version files.

It also preserves/copies `professional_tracking.py` if needed.

## First test

Run:

```bat
python app.py
```

Before entering real data, use TEST records.

Verify:

1. **Global Search** button exists.
2. Under **Forensics**, confirm:
   - Case Work
   - Forensic Reports
   - Peer / Technical Reviews
   - Tool Experience
   - Case Index
   - Tool Library
3. Open Case Work:
   - Tool selector should be multi-select.
4. Open Case Index:
   - Select a test case and click **View Linked Records**.
5. Open several tabs:
   - Test filters and year filtering.
6. Open Generate CV:
   - Apply **Standard CV**
   - Apply **Voir Dire Package**
   - Save a custom preset
7. Create an Expert Qualification report.
8. Create an Annual Activity report.
9. Restart the app and confirm:
   `Backups\Auto\forensic_cv_auto_YYYY-MM-DD.sqlite3`

## Rebuild only after testing

When `python app.py` is working correctly:

```bat
build_windows.bat
```

Test:

`dist\ForensicCVManager.exe`

Then:

```bat
build_installer.bat
```

## Documentation

- [Portable Build and Update Guide](docs/README_Portable_Build_and_Update_Guide.md)
- [Customizing Training Provider and Category Dropdowns](docs/README_Training_Dropdown_Customization.md)

## Privacy reminder

This application remains a portable SQLite-backed professional-history application. Do not store restricted investigative information merely because a field exists.

Keep victim/suspect names, passwords, contraband descriptions, sensitive investigative narrative, CUI/classified data, and other restricted information out of this database unless the storage environment and applicable policy specifically authorize it.
