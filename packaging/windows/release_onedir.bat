@echo off
setlocal

set APP_NAME=ContractAutomation
set VERSION=%~1
if "%VERSION%"=="" set VERSION=dev

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set RELEASE_DIR=releases\windows
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"

echo [release] VERSION=%VERSION%
echo [release] Building onedir package
call packaging\windows\build_onedir.bat
if errorlevel 1 exit /b 1

set SRC_DIR=dist\%APP_NAME%
if not exist "%SRC_DIR%" (
  echo [error] Missing build directory: %SRC_DIR%
  exit /b 1
)

set ZIP_PATH=%RELEASE_DIR%\%APP_NAME%_%VERSION%_%TS%_windows_onedir.zip
powershell -NoProfile -Command "Compress-Archive -Path '%SRC_DIR%\*' -DestinationPath '%ZIP_PATH%' -Force"
if errorlevel 1 exit /b 1

echo [done] Release artifact created:
echo - %ZIP_PATH%

endlocal
