## Customizing Training Provider and Category Dropdowns

Forensic CV Manager Professional includes editable dropdowns for the **Provider** and **Category** fields under the **Training** tab.

These dropdowns provide commonly used values while still allowing users to manually enter a value that is not included in the predefined list.

The predefined options are configured in:

```text
professional_v251.py
```

### Training Providers

Near the top of `professional_v251.py`, locate:

```python
TRAINING_PROVIDERS = [
    "",
    "Carnegie Mellon",
    "CISA",
    "DC3",
    "DCSA",
    "EC-Council",
    "Magnet Forensics",
    "SANS",
    "Skillsoft",
    "Mandiant",
    "ISC2",
    "CompTIA",
]
```

To add a provider, add another quoted value to the list:

```python
TRAINING_PROVIDERS = [
    "",
    "Carnegie Mellon",
    "CISA",
    "DC3",
    "DCSA",
    "EC-Council",
    "Magnet Forensics",
    "SANS",
    "Skillsoft",
    "Mandiant",
    "ISC2",
    "CompTIA",
    "Example Training Provider",
]
```

To remove a provider, simply delete its corresponding line.

### Training Categories

The Training category options are controlled by:

```python
TRAINING_CATEGORIES = [
    "",
    "Windows Forensics",
    "Mac Forensics",
    "Phone Forensics",
    "Linux Forensics",
    "Cyber",
    "Cyber Threat Intelligence",
    "Insider Threat",
    "AI",
]
```

Additional categories can be added in the same manner:

```python
TRAINING_CATEGORIES = [
    "",
    "Windows Forensics",
    "Mac Forensics",
    "Phone Forensics",
    "Linux Forensics",
    "Cyber",
    "Cyber Threat Intelligence",
    "Insider Threat",
    "AI",
    "Malware Analysis",
    "Reverse Engineering",
]
```

### Custom Values

Both fields are **editable dropdowns**. A value does not have to appear in the predefined list to be used.

For example, a user can type:

```text
Local Training Academy
```

directly into the Provider field even if it is not listed in `TRAINING_PROVIDERS`.

This makes it possible to keep the default public distribution organization-neutral while allowing individual users to customize the available choices for their own workplace, agency, training providers, or specialty areas.

### Applying Changes

After modifying `professional_v251.py`, test the source version:

```bat
python app.py
```

If the updated dropdowns appear correctly, rebuild the Windows executable:

```bat
build_windows.bat
```

The updated executable will be created under:

```text
dist\ForensicCVManager.exe
```

Removing an option from a dropdown does **not** delete or modify existing Training records that already contain that value. The dropdown list only controls the predefined choices presented when adding or editing records.
