@echo off
setlocal

REM Build Windows onedir package using CLI flags
set ICON_ARG=
if exist assets\app.ico (
	set ICON_ARG=--icon assets\app.ico
) else (
	echo [info] Icon not found at assets\app.ico. Building without custom icon.
)

if not exist templates_storage mkdir templates_storage
if not exist exports mkdir exports

pyinstaller --noconfirm --clean --windowed --name ContractAutomation %ICON_ARG% --add-data "templates_storage;templates_storage" --add-data "exports;exports" src\main.py
if errorlevel 1 exit /b 1

echo.
echo Build complete. Output is in dist\ContractAutomation\
endlocal
