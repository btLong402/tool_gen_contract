@echo off
setlocal

REM Build Windows onefile package using CLI flags
set ICON_ARG=
if exist assets\app.ico (
	set ICON_ARG=--icon assets\app.ico
) else (
	echo [info] Icon not found at assets\app.ico. Building without custom icon.
)

pyinstaller --noconfirm --clean --onefile --windowed --name ContractAutomation %ICON_ARG% --add-data "templates_storage;templates_storage" --add-data "exports;exports" src\main.py

echo.
echo Build complete. Output is in dist\ContractAutomation.exe
endlocal
