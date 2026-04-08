# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path(__file__).resolve().parent
icon_path = str(project_root / "assets" / "app.ico")
onefile_mode = False


a = Analysis(
    ['src/main.py'],
    pathex=[str(project_root / 'src')],
    binaries=[],
    datas=[
        (str(project_root / 'templates_storage'), 'templates_storage'),
        (str(project_root / 'exports'), 'exports'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=not onefile_mode,
    name='ContractAutomation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_path,
)

if onefile_mode:
    app = exe
else:
    app = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='ContractAutomation',
    )
