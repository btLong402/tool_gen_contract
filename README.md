# Contract Automation Desktop App (Python)

A desktop application for turning DOCX contract templates into smart templates with `{{variable}}` tags, rendering dynamic forms, and exporting completed contracts.

## Tech Stack
- Python 3.10+
- PyQt6
- docxtpl
- SQLite

## Features in this MVP
- Import `.docx` template files
- Auto-scan tags like `{{full_name}}`
- Save templates in a local library (SQLite)
- Generate dynamic form from tags
- Save drafts
- Re-open and continue editing a saved draft, then export
- Export filled contract as `.docx`
- Optional export to `.pdf` (best effort via `docx2pdf`)
- View export/draft history per template
- Basic partner profile reuse (auto-fill based on key fields)

## Quick Start
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run:
   ```bash
   python src/main.py
   ```

## Run Tests
1. Install test dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
2. Execute tests:
   ```bash
   pytest
   ```

## Windows Packaging (PyInstaller)
1. Put icon file at `assets/app.ico`.
2. Install packaging dependency:
   ```bash
   pip install -r requirements.txt
   ```
3. Build on Windows:
   - Onedir build:
     ```bat
     packaging\windows\build_onedir.bat
     ```
   - Onefile build:
     ```bat
     packaging\windows\build_onefile.bat
     ```

You can also customize `contract_automation.spec` for advanced build options.

## macOS Packaging (.app and .dmg)
1. Optional but recommended: put icon file at `assets/app.icns`.
2. Build `.app` bundle:
   ```bash
   ./packaging/macos/build_app.sh
   ```
3. Build `.dmg` installer:
   ```bash
   ./packaging/macos/build_dmg.sh
   ```

Output files:
- `dist/ContractAutomation.app`
- `dist/ContractAutomation.dmg`

If you distribute outside your machine, consider Apple code signing and notarization.

## Release Automation (Versioned Artifacts)

Use the release scripts to build and package artifacts into `releases/` with version + timestamp naming.

### macOS
- Auto version from git tag/commit:
   ```bash
   ./packaging/macos/release.sh
   ```
- Explicit version:
   ```bash
   RELEASE_VERSION=v1.2.0 ./packaging/macos/release.sh
   ```

Artifacts are generated under `releases/macos/`:
- `ContractAutomation_<version>_<timestamp>_macos_app.zip`
- `ContractAutomation_<version>_<timestamp>_macos.dmg`

### Windows
- Onedir release:
   ```bat
   packaging\windows\release_onedir.bat v1.2.0
   ```
- Onefile release:
   ```bat
   packaging\windows\release_onefile.bat v1.2.0
   ```

Artifacts are generated under `releases\windows\`.

## GitHub Workflow (Auto Release)

This project includes CI/CD workflow at `.github/workflows/release.yml`.

Trigger condition:
- Push tag matching `v*` (example: `v1.2.0`)

What it does:
- Build macOS artifacts (`.dmg` + app `.zip`)
- Build Windows artifacts (onedir `.zip` + onefile `.exe`)
- Create GitHub Release and attach all artifacts

Release command sequence:
```bash
git tag v1.2.0
git push origin v1.2.0
```

## Notes
- PDF export depends on local Microsoft Word integration (`docx2pdf`).
- Keep template placeholders in jinja-compatible syntax: `{{variable_name}}`.
- Template files are copied to `templates_storage/` to avoid accidental source changes.
