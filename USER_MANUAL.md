# Forensic CV Manager User Manual

## Adding records

1. Select the intended examiner from **Active Profile**.
2. Open the appropriate record tab, such as Training, Certifications, Employment, or Courtroom Testimony.
3. Select **Add** in the upper-right corner.
4. Complete the available fields.
5. Select **Save**. The record is immediately available to the dashboard and CV generator.

Common date formats are accepted, including `3/5/2026`, `03-05-2026`, `2026-03-05`, `March 5, 2026`, `March 2026`, `03/2026`, and `2026`. Employment end dates may use `Present`, `Current`, `Ongoing`, or `Now`.

Description and Notes fields support multiline text and are printed in full. Enter only documented numeric course hours in the Hours field. Select **Include in Core Training** when a training record should appear in the concise Core Training section.

## Editing and deleting

Select a record and choose **Edit** to revise it. Select **Delete** to permanently remove it. Back up the database before bulk deletion.

## Profiles

Use **Active Profile** to switch examiners. Select **Manage Profiles** to add, rename, switch, or delete profiles. Profile import and export are available from the File menu.

## Generating a CV

Open **Generate CV**, select the desired sections, then choose Word, PDF, or both. PDF reports use the consistent Professional style. Generated files default to the portable `Resume` folder. Date-based sections are sorted newest to oldest.

## Backup and portability

Keep the executable and its `data`, `Resume`, and `Backups` folders together. Use **File > Backup Database** regularly and store a separate copy in an approved secure location.

## Appearance

Use **Tools > Appearance > Light Mode** or **Dark Mode**. The choice is stored in the portable `data` folder and restored on the next launch. Light mode intentionally retains the v2.2.0 Windows-style interface.

## PDF Preview

On **Generate CV**, select **Preview & Save PDF**. A temporary native PDF opens in the integrated viewer. Use Previous/Next, Zoom, or Fit Width to review it. Select **Save PDF** to write the approved copy to the portable `Resume` folder or another chosen location. Closing the preview without saving does not create a resume file.

## Sorting Records

Record lists can be sorted by clicking a column heading. Click once for ascending order and click the same heading again for descending order. The active heading displays an arrow showing the current direction. Dates are sorted chronologically, hours numerically, and text alphabetically using natural ordering. Sorting changes only the on-screen list; it does not alter the database or the chronological ordering used by generated CV reports.
