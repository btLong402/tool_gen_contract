@echo off
setlocal

REM Build Windows onedir package using CLI flags
pyinstaller --noconfirm --clean --windowed --name ContractAutomation --icon assets\app.ico --add-data "templates_storage;templates_storage" --add-data "exports;exports" src\main.py

echo.
echo Build complete. Output is in dist\ContractAutomation\
endlocal
