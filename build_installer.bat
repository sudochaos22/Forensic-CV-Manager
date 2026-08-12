@echo off
setlocal
cd /d "%~dp0"
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
  echo Inno Setup 6 was not found. Install it, then run this script again.
  pause
  exit /b 1
)
python build_metadata.py
if errorlevel 1 goto :failed

if not exist "dist\ForensicCVManager.exe" (
  echo Build the portable application first with build_windows.bat.
  pause
  exit /b 1
)
"%ISCC%" ForensicCVManager.iss
if errorlevel 1 goto :failed

echo Installer created in the installer folder.
pause
exit /b 0
:failed
echo Installer build failed.
pause
exit /b 1
