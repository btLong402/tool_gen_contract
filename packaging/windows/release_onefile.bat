@echo off
setlocal

set APP_NAME=ContractAutomation
set VERSION=%~1
if "%VERSION%"=="" set VERSION=dev

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set RELEASE_DIR=releases\windows
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"

echo [release] VERSION=%VERSION%
echo [release] Building onefile package
call packaging\windows\build_onefile.bat
if errorlevel 1 exit /b 1

set SRC_EXE=dist\%APP_NAME%.exe
if not exist "%SRC_EXE%" (
  echo [error] Missing executable: %SRC_EXE%
  exit /b 1
)

set TARGET_EXE=%RELEASE_DIR%\%APP_NAME%_%VERSION%_%TS%_windows_onefile.exe
copy /Y "%SRC_EXE%" "%TARGET_EXE%" >nul
if errorlevel 1 exit /b 1

echo [done] Release artifact created:
echo - %TARGET_EXE%

endlocal
