@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  Forensic CV Manager - Portable Builder
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found on PATH.
    echo Install Python and select "Add Python to PATH", then try again.
    pause
    exit /b 1
)

echo [1/4] Installing required packages...
python -m pip install --upgrade pip
if errorlevel 1 goto :build_failed

python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :build_failed

echo.
echo [2/4] Creating Windows executable...
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "ForensicCVManager" app.py
if errorlevel 1 goto :build_failed

echo.
echo [3/4] Preparing portable folder...
if not exist "dist\data" mkdir "dist\data"
copy /Y "README.md" "dist\README.txt" >nul

echo.
echo [4/4] Build complete.
echo Portable folder: "%~dp0dist"
echo Executable:      "%~dp0dist\ForensicCVManager.exe"
echo Database:        "%~dp0dist\data\forensic_cv.sqlite3"
echo.
echo Copy the entire dist folder to the flash drive.
echo The database file will be created automatically on first launch.
echo.
pause
exit /b 0

:build_failed
echo.
echo Build failed. Review the error messages above.
pause
exit /b 1
