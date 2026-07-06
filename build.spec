# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

project_root = Path(SPECPATH)

icon_candidates = [
    project_root / "assets" / "icon.ico",
    project_root / "app" / "assets" / "icon.ico",
]
icon = next((str(p) for p in icon_candidates if p.is_file()), None)

_tool_ui_modules = [
    "app.ui.tools",
    "app.ui.tools.resize",
    "app.ui.tools.compress",
    "app.ui.tools.convert",
    "app.ui.tools.crop",
    "app.ui.tools.rotate",
    "app.ui.tools.merge",
    "app.ui.tools.bulk_rename",
]

hiddenimports = list(
    dict.fromkeys(_tool_ui_modules + collect_submodules("app"))
)

datas = [
    ("assets", "assets"),
    ("app/assets", "app/assets"),
]
third_party = project_root / "third_party"
if third_party.is_dir():
    datas.append(("third_party", "third_party"))

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="HyoImage",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="HyoImage",
)
