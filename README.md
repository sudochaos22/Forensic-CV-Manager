# Forensic CV Manager Professional

**Current Version: 2.5.1**

Forensic CV Manager Professional is a digital-forensics-focused professional experience, casework, training, certification, expert-witness, and career tracking application.

This project is an expanded fork of the original **Forensic CV Manager** and adds professional tracking, casework statistics, reporting, dashboard metrics, tool normalization, expert-witness documentation, and other DFIR-focused features.

---

## What's New in v2.5.1

Version 2.5.1 expands Training and Case Work tracking and adds additional current-year forensic workload metrics.

### Training Improvements

- Added an editable **Provider** dropdown.
- Added an editable **Category** dropdown.
- Both dropdowns include predefined values while still allowing custom text entries.
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
2d 6h 31m
```

Data totals automatically scale to an appropriate unit:

```text
850 GB
1.50 TB
3.72 TB
```

For **Data Analyzed**, Evidence Size is counted toward the calendar year in which the evidence was processed.

---

## Features Introduced in v2.5

### Global Search

A **Global Search** button appears beside **Manage Profiles**.

It searches professional record tables for the active profile and can jump directly to a selected record.

### Filters on Record Tabs

Record tabs support:

- Normal text search
- Table-appropriate dropdown filters
- Year filtering when the table has a primary date
- Clear Filters
- `Showing X of Y records`

### Dashboard Drill-Down

Dashboard metric cards are clickable.

Examples:

- Cases -> Case Index
- Examinations -> Case Work
- Reports -> Forensic Reports
- Peer Reviews -> Peer / Technical Reviews
- Testimony -> Courtroom Testimony
- Training Hrs -> Training

The dashboard also shows current-year activity.

### Annual Statistics

Current-year activity is summarized on the dashboard.

Generate CV also includes an **Annual Activity Report** option that creates:

- `.docx`
- `.pdf`

The annual report can summarize examination counts/hours, reports, reviews, testimony, training/CPE, teaching, presentations, publications, validation, SOP/policy work, mentoring, projects, device types, acquisition methods, and tool usage.

### Tool Normalization

A **Tool Library** stores canonical tool names and aliases.

The Case Work **Tools Used** field supports multi-select tool selection.

For example:

```text
AXIOM
Magnet Axiom
Magnet AXIOM
```

can normalize to:

```text
Magnet AXIOM
```

Tool Library also includes a **Normalize Existing Case Work** function.

### Case-to-Record Relationships

A **Case Index** provides one case/reference record per case number.

The database can internally link Case Index records to:

- Case Work
- Forensic Reports
- Peer / Technical Reviews
- Testimony
- Court Qualifications

Existing records can be linked by matching case number.

### Export Presets

Generate CV includes built-in presets such as:

- Standard CV
- Expert Witness CV
- Voir Dire Package
- Full Professional Record
- Annual Review
- Training / CPE Report

Custom presets can also be saved.

Privacy-sensitive fields remain excluded unless explicitly enabled.

### Expert Qualification / Voir Dire Report

Generate CV includes an **Expert Qualification Report** option.

The report can summarize:

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

The report intentionally omits case numbers and evidence identifiers.

### Annual Professional Activity Report

A calendar year can be selected to generate an annual professional activity report in Word and PDF formats.

### Certification / CPE Alerts

Dashboard alerts can include:

- Expired credentials
- Credentials within 90 / 180 / 365 days
- CPE/CE progress and remaining credits when those fields are populated

### Data Validation

Record entry includes validation for items such as:

- Numeric fields
- Negative numeric values
- Date formats
- End date before start date
- Data-size entries
- Duplicate certifications
- Duplicate Case Work entries
- Duplicate Case Index numbers
- Duplicate Tool Library names

### Automatic Backups

On application startup, if a working SQLite database already exists, a daily backup is stored in:

```text
Backups\Auto\
```

Backup file format:

```text
forensic_cv_auto_YYYY-MM-DD.sqlite3
```

The newest **30** automatic backups are retained.

Automatic backups do not replace a separate encrypted or off-device backup strategy.

### Schema Versioning

The database includes schema metadata such as:

```text
schema_version = 5
professional_version = 2.5.1
```

### About Screen

The About screen identifies the Professional Edition, application version, database schema, and backup policy.

### Changelog

Help includes a **Professional Edition Changelog**.

---

# Installation

Forensic CV Manager Professional can be run directly from source or built as a portable Windows executable.

No upgrade script is required when cloning or downloading the current repository. The current repository already contains the Professional v2.5.1 source files.

## Option 1 — Run From Source

### Requirements

You will need:

- Windows
- Python 3
- `pip`
- Git, if cloning the repository

Clone the repository:

```bat
git clone https://github.com/sudochaos22/Forensic-CV-Manager.git
cd Forensic-CV-Manager
```

Alternatively, download the repository as a ZIP from GitHub and extract it.

Install the required Python dependencies:

```bat
python -m pip install -r requirements.txt
```

Run the application:

```bat
python app.py
```

The application uses a working SQLite database under:

```text
data\forensic_cv.sqlite3
```

The working database contains user-entered data and should not be committed to a public repository.

---

## Option 2 — Build the Portable Windows Application

The included Windows build script creates a portable application.

From the project directory, run:

```bat
build_windows.bat
```

The build process prepares the required Python dependencies, installs or uses PyInstaller, creates the Windows executable, and prepares the portable release folder.

The completed portable application is created under:

```text
dist\
```

The main executable is:

```text
dist\ForensicCVManager.exe
```

Once built, the portable application does **not** normally require Python, pip, PyInstaller, or the development dependencies on the computer where it is being used.

Run the completed application with:

```text
ForensicCVManager.exe
```

---

## Portable Use

The entire `dist` folder can be copied or renamed and used as a portable application folder.

For example:

```text
Forensic-CV-Manager-Professional\
│
├── ForensicCVManager.exe
├── data\
│   ├── forensic_cv.sqlite3
│   └── template.sqlite3
├── Backups\
├── Resume\
└── supporting files
```

You can move the portable folder to another writable location, external drive, USB drive, or compatible Windows computer.

The application data is stored outside the EXE, primarily in:

```text
data\forensic_cv.sqlite3
```

That file should be protected and backed up because it contains the working professional-history database.

For additional details, see:

[Portable Build and Update Guide](docs/README_Portable_Build_and_Update_Guide.md)

---

## Updating a Portable Working Copy

When updating the application:

1. Update the source files.
2. Install or refresh dependencies if needed:

   ```bat
   python -m pip install -r requirements.txt
   ```

3. Test the source version:

   ```bat
   python app.py
   ```

4. Build a fresh executable:

   ```bat
   build_windows.bat
   ```

5. Test:

   ```text
   dist\ForensicCVManager.exe
   ```

6. Back up the existing working database:

   ```text
   data\forensic_cv.sqlite3
   ```

7. Copy the newly built `ForensicCVManager.exe` into the existing portable working folder and replace the old EXE.

8. Keep the existing `data\forensic_cv.sqlite3` so the user's records remain intact.

A clean build may recreate the development `dist` folder, so the permanent working database should not rely on the build folder being its only copy.

---

## Building the Windows Installer

If **Inno Setup 6** is installed, a Windows installer can also be created after the portable application has been built and tested.

Run:

```bat
build_installer.bat
```

Build and test the portable executable before creating the installer.

---

# First Run / Testing

When running either:

```bat
python app.py
```

or:

```text
ForensicCVManager.exe
```

it is recommended to create TEST records first and verify the major functions before entering production data.

Verify:

1. **Global Search** is available.
2. Under **Forensics**, confirm:
   - Case Work
   - Forensic Reports
   - Peer / Technical Reviews
   - Tool Experience
   - Case Index
   - Tool Library
3. Open **Case Work** and verify:
   - Tool selection
   - Evidence Size
   - Image Date
   - Image Time
   - Process Date
   - Process Time
   - Artifacts Identified
   - PST Device Type
4. Open **Training** and verify:
   - Editable Provider dropdown
   - Editable Category dropdown
5. Verify the dashboard shows:
   - Current-year Imaging Time
   - Current-year Processing Time
   - Current-year Data Analyzed
6. Test CV and professional report generation.
7. Restart the application and verify automatic backups are being created under:

```text
Backups\Auto\
```

---

# Documentation

Additional documentation is available in the `docs` folder:

- [Portable Build and Update Guide](docs/README_Portable_Build_and_Update_Guide.md)
- [Customizing Training Provider and Category Dropdowns](docs/README_Training_Dropdown_Customization.md)

---

# Customizing Training Dropdowns

Training Provider and Category dropdown values are configured in:

```text
professional_v251.py
```

Both dropdowns are editable, so users can select a predefined value or manually enter a value that is not listed.

See:

[Customizing Training Provider and Category Dropdowns](docs/README_Training_Dropdown_Customization.md)

---

# Privacy and Data Handling

Forensic CV Manager Professional is a portable SQLite-backed professional-history application.

Do not store restricted investigative information merely because a field exists.

Avoid storing items such as:

- Victim or suspect names
- Passwords
- Contraband descriptions
- Sensitive investigative narrative
- CUI or classified information
- Other restricted information

unless the storage environment and applicable policy specifically authorize it.

The working database:

```text
data\forensic_cv.sqlite3
```

should not be published or distributed if it contains real user data.

When creating a clean distribution for another user, use the clean template database and do not include a personal working database.

---

# Project Structure

Important project files include:

```text
app.py
database.py
professional_tracking.py
professional_v25.py
professional_v251.py
requirements.txt
build_windows.bat
build_installer.bat
version.py
```

`professional_v251.py` is part of the current runtime source and should remain in the project.

---

# Upstream Project and Attribution

Forensic CV Manager Professional is a fork and expanded version of:

```text
JSPadilla/Forensic-CV-Manager
```

Original work remains credited to its respective author(s).

This fork contains additional Professional Edition modifications focused on digital forensics, DFIR professional-history tracking, casework metrics, training, expert-witness documentation, reporting, and portable workflow improvements.

---

# License

This project remains licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

See the included license file for the complete license text.
