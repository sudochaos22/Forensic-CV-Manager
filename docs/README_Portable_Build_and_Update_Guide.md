# Forensic CV Manager Professional — Build, Portable Use, and Update Guide

This guide explains the difference between the **development/build environment** and the **portable application**, and provides a safe workflow for updating the program without losing your working data.

---

## 1. Development / Build Environment

When building Forensic CV Manager from source, the development computer needs the required build tools and Python dependencies installed.

Typical requirements include:

- Python
- `pip`
- The Python packages listed in `requirements.txt`
- PyInstaller
- Any additional Python packages used by the Professional extensions
- Inno Setup 6, if building the Windows installer
- The project source files, including files such as:
  - `app.py`
  - `database.py`
  - `professional_tracking.py`
  - `professional_v25.py`
  - `professional_v251.py`
  - other project `.py` files

Install or refresh the Python dependencies with:

```bat
python -m pip install -r requirements.txt
```

The dependencies are needed on the **computer used to build the application**.

They are not normally required on a computer that is only running the finished PyInstaller executable.

---

## 2. Building the Windows Executable

After making source-code changes, test the application from Python first:

```bat
python app.py
```

If everything works correctly, build a fresh Windows executable:

```bat
build_windows.bat
```

The finished executable will normally be created at:

```text
dist\ForensicCVManager.exe
```

PyInstaller bundles Python and the required Python modules into the executable, so a normal Windows computer does not need Python or the development dependencies installed just to run the finished application.

---

## 3. Using the EXE for Normal Daily Use

Once the program has been built successfully, normal use should be through:

```text
ForensicCVManager.exe
```

The computer running the portable application does not normally need:

- Python
- pip
- PyInstaller
- Inno Setup
- the source `.py` files
- the development environment

The executable contains the Python runtime and application code needed to run the program.

The application's data remains outside the EXE, typically in:

```text
data\forensic_cv.sqlite3
```

That SQLite database contains the user's working information.

---

## 4. Making the Application Portable

The `dist` folder can be copied to another location and renamed.

For example, after a successful build:

```text
dist\
```

can be copied and renamed to:

```text
Forensic-CV-Manager-Professional\
```

or:

```text
Forensic-CV-Manager-Professional-Portable\
```

A portable folder might look like:

```text
Forensic-CV-Manager-Professional\
│
├── ForensicCVManager.exe
│
├── data\
│   ├── forensic_cv.sqlite3
│   └── template.sqlite3
│
├── Backups\
├── Resume\
└── other release files
```

That entire folder can be moved to another writable location, such as:

- another folder on the computer
- an external SSD
- a USB drive
- another Windows computer

Run the application by opening:

```text
ForensicCVManager.exe
```

### Important

The application writes data beside the executable, so the portable folder should be stored in a location where the user has permission to write files.

---

## 5. Recommended Portable Working Folder

It is safer to keep the permanent working copy separate from the development project's automatically generated `dist` folder.

For example:

```text
D:\Portable Apps\Forensic-CV-Manager-Professional\
```

The development project can continue producing new builds under:

```text
D:\Forensic-CV-Manager\dist\
```

while the portable working folder keeps the real user database and backups.

This separation helps prevent a clean build from accidentally deleting working data.

---

## 6. Updating the Application

When the program is updated, rebuild the application from the updated source rather than modifying the old EXE.

Recommended workflow:

### Step 1 — Update the Source Code

Make the desired changes to the source files.

If dependencies have changed, install or refresh them:

```bat
python -m pip install -r requirements.txt
```

### Step 2 — Test the Source Version

Run:

```bat
python app.py
```

Confirm that the application starts and that the updated features work correctly.

### Step 3 — Build a Fresh EXE

Run:

```bat
build_windows.bat
```

This creates a new executable:

```text
dist\ForensicCVManager.exe
```

### Step 4 — Test the Newly Built EXE

Before replacing the daily-use copy, run:

```bat
dist\ForensicCVManager.exe
```

Confirm that the executable starts and behaves correctly.

### Step 5 — Back Up the Working Database

Before replacing the old executable, make a backup of:

```text
data\forensic_cv.sqlite3
```

For example:

```bat
copy "D:\Portable Apps\Forensic-CV-Manager-Professional\data\forensic_cv.sqlite3" "D:\Portable Apps\Forensic-CV-Manager-Professional\Backups\forensic_cv_BEFORE_UPDATE.sqlite3"
```

### Step 6 — Replace Only the EXE

Copy the newly built executable:

```text
dist\ForensicCVManager.exe
```

into the existing portable working folder and replace the older EXE.

Example:

```bat
copy /Y "dist\ForensicCVManager.exe" "D:\Portable Apps\Forensic-CV-Manager-Professional\ForensicCVManager.exe"
```

The existing working database remains in place:

```text
data\forensic_cv.sqlite3
```

This means the application code is updated while the user's existing data is preserved.

---

## 7. What Gets Replaced During an Update

Normally, replace:

```text
ForensicCVManager.exe
```

Do **not** replace the user's working database unless intentionally restoring or migrating it:

```text
data\forensic_cv.sqlite3
```

The database is the important file containing the user's records.

The general update model is:

```text
UPDATED SOURCE CODE
        ↓
python app.py
        ↓
build_windows.bat
        ↓
NEW ForensicCVManager.exe
        ↓
copy into portable folder
        ↓
replace OLD ForensicCVManager.exe
        ↓
KEEP existing forensic_cv.sqlite3
```

---

## 8. Database Schema Updates

Some application updates may add new database fields or tables.

When properly implemented, the application performs database migrations when the new version starts.

This allows an existing:

```text
data\forensic_cv.sqlite3
```

database to be opened by the newer executable while preserving existing records.

A database backup should still be made before every significant application upgrade.

---

## 9. Do Not Treat the Build `dist` Folder as the Only Copy of Your Data

A development build process may delete and recreate:

```text
dist\
```

For example, a clean build may use commands such as:

```bat
rmdir /s /q build
rmdir /s /q dist
build_windows.bat
```

If the only copy of the working database is inside that `dist` folder, deleting `dist` could also delete the user's data.

For that reason, the recommended setup is:

```text
Development Project
│
├── source files
├── build\
└── dist\
    └── newly built release
```

and separately:

```text
Portable Working Copy
│
├── ForensicCVManager.exe
├── data\
│   └── forensic_cv.sqlite3
├── Backups\
└── Resume\
```

---

## 10. Moving the Portable Application to Another Computer

To move an existing working copy to another Windows computer, copy the **entire portable folder**.

Example:

```text
Forensic-CV-Manager-Professional\
```

Copying the entire folder preserves:

- the executable
- the working SQLite database
- application backups
- generated documents or resumes stored in the application folders
- supporting portable files

On the new computer, open:

```text
ForensicCVManager.exe
```

Python and the development dependencies do not normally need to be installed.

---

## 11. Creating a Clean Copy for Another User

When distributing the application to someone else, do not include your personal working database.

Remove:

```text
data\forensic_cv.sqlite3
```

from the copy being distributed.

Keep the clean template database:

```text
data\template.sqlite3
```

The application can then create a new working database for the new user.

Never publish or distribute a working database that contains real case information, professional records, personal information, or other sensitive data.

---

## Quick Reference

### Development computer

Needs the development environment and dependencies:

```text
Python
pip
requirements.txt packages
PyInstaller
source code
Inno Setup 6 (installer builds)
```

### Normal portable computer

Runs:

```text
ForensicCVManager.exe
```

No Python installation is normally required.

### Updating

```text
Update source
    ↓
python app.py
    ↓
build_windows.bat
    ↓
test dist\ForensicCVManager.exe
    ↓
back up forensic_cv.sqlite3
    ↓
copy new EXE into portable folder
    ↓
replace old EXE
    ↓
keep existing database
```

### Portable use

Copy or rename the entire release folder:

```text
dist
```

to something more descriptive, such as:

```text
Forensic-CV-Manager-Professional
```

Then keep that folder together when moving the application between computers.
