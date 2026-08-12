# Changelog

All notable changes to Forensic CV Manager are documented here. The project follows [Semantic Versioning](https://semver.org/).

> Historical note: versions through 2.4.0 were developed before this GitHub release history was backfilled. The release PRs were reconstructed afterward from preserved release packages and the development record. They intentionally document the progression without pretending the PR creation dates were the original release dates.

## [2.4.1]
### Fixed
- Restored compatibility between `app.py` and the splash-screen API after the 2.4.0 source synchronization.
- Added support for the `theme_name`, `set_status()`, and `close()` calls used by the current application startup sequence.
- Replaced the deprecated `fitz` import with `pymupdf` while preserving the existing PDF preview implementation.

## [2.4.0]
### Added
- Click-to-sort column headers on record tabs with ascending/descending toggling.
- Type-aware date/year, numeric, Yes/No, and natural-text sorting; blanks remain at the bottom.
### Notes
- UI sorting does not change SQLite data or generated CV ordering.

## [2.3.4]
### Fixed
- Status bar now reflects the active tab and relevant record count/context.
- Removed obsolete date-format guidance.
### Changed
- Removed PDF style selection; all PDFs use Professional styling.

## [2.3.3]
### Changed
- Restored the 2.2.0 visual/layout baseline while retaining light/dark mode, branding, splash screen, PDF preview, and installer branding.
- Removed ttkbootstrap and returned Light Mode to the original Windows ttk styling.

## [2.3.2]
### Changed
- Removed the grouped ribbon and restored the traditional File / Tools / Help menu bar.

## [2.3.1]
### Fixed
- Fixed the ttkbootstrap startup crash caused by a `Style` naming collision.

## [2.3.0]
### Added
- Professional branding and icons.
- Startup splash screen with version/loading status.
- Light/dark appearance support.
- Integrated PDF preview with page navigation and zoom.
- Branded Inno Setup installer assets/workflow.

## [2.2.0]
### Added
- Native ReportLab PDF generation with no Word/LibreOffice dependency.
- Shared CV data model for independent Word and PDF renderers.
- Page numbers, clickable contact links, PDF metadata, and professional formatting.

## [2.1.0]
### Added
- Semantic Versioning with a single `version.py` source of truth.
- Version synchronization across UI, executable metadata, and installer.
- Built-in user manual and How to Add Records help.

## [2.0.1]
### Fixed
- Removed internal numeric IDs from profile display names.
- Improved duplicate-name handling and GitHub update-checker 404 guidance.

## [2.0.0]
### Added
- Sanitized fictitious release seed/template database.
- Blank profile and sample-data workflows.
- Profile JSON import/export.
- Dashboard chart and certification expiration alerts.
- Word/PDF/combined output commands.
- Optional GitHub update checker, Inno Setup project, and Authenticode signing support.

## [1.2.2]
### Fixed
- Accepted common full-date, month/year, and year-only formats and normalized them for sorting.
- Accepted Present/Current/Ongoing/Now where applicable.
- Defaulted generated CV output to a portable `Resume` folder.

## [1.2.1]
### Fixed
- Removed report-output truncation and preserved long/multiline text.
- Standardized date-based report sections to newest-to-oldest ordering.

## [1.2.0]
### Added
- Multiple profiles with isolated professional records.
- Profile create/switch/rename/delete and clear-profile-data workflows.
- Automatic migration of existing single-user data into the first profile.

## [1.1.0]
### Added
- Portable flash-drive database/storage architecture.
- Automatic migration/copy of an existing local database into portable storage.

## [1.0.1]
### Fixed
- Corrected the Windows build script to use `python -m PyInstaller` when PyInstaller is not on PATH.

## [1.0.0]
### Added
- Initial stable Forensic CV Manager desktop application.
- SQLite-backed tracking for professional CV records.
- GUI record management and on-demand CV generation.
