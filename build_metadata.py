"""Generate Windows and installer metadata from version.py."""
from pathlib import Path
from version import __version__

ROOT = Path(__file__).resolve().parent
parts = [int(p) for p in __version__.split('.')]
if len(parts) != 3:
    raise SystemExit('Version must use MAJOR.MINOR.PATCH format.')
major, minor, patch = parts
quad = f"{major}, {minor}, {patch}, 0"

version_info = f'''# UTF-8\nVSVersionInfo(\n  ffi=FixedFileInfo(\n    filevers=({quad}),\n    prodvers=({quad}),\n    mask=0x3f,\n    flags=0x0,\n    OS=0x40004,\n    fileType=0x1,\n    subtype=0x0,\n    date=(0, 0)\n  ),\n  kids=[\n    StringFileInfo([\n      StringTable(\n        u'040904B0',\n        [StringStruct(u'CompanyName', u'Forensic CV Manager'),\n         StringStruct(u'FileDescription', u'Forensic CV Manager'),\n         StringStruct(u'FileVersion', u'{__version__}'),\n         StringStruct(u'InternalName', u'ForensicCVManager'),\n         StringStruct(u'OriginalFilename', u'ForensicCVManager.exe'),\n         StringStruct(u'ProductName', u'Forensic CV Manager'),\n         StringStruct(u'ProductVersion', u'{__version__}')])\n    ]),\n    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])\n  ]\n)\n'''
(ROOT / 'version_info.txt').write_text(version_info, encoding='utf-8')
(ROOT / 'installer_version.iss').write_text(f'#define MyAppVersion "{__version__}"\n', encoding='utf-8')
print(f'Generated build metadata for {__version__}')
