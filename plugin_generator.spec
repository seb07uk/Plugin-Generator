# ──────────────────────────────────────────────────────────
#  polsoft.ITS™ Plugin Generator — PyInstaller SPEC
#  Wersja:      4.2.0
#  Programista: Sebastian Januchowski
#  Firma:       polsoft.ITS™ Group
#  Email:       polsoft.its@fastservice.com
#  GitHub:      https://github.com/seb07uk
#  2026© Sebastian Januchowski & polsoft.ITS™. All rights reserved.
#
#  Wymagane pliki w tym samym katalogu:
#    plugin_generator.py   — kod źródłowy
#    ico.ico               — ikona aplikacji
#    version.txt           — Windows VERSIONINFO resource
# ──────────────────────────────────────────────────────────

import os

block_cipher = None

# Ścieżka do ikony (graceful fallback gdy brak pliku)
_ico = "ico.ico" if os.path.exists("ico.ico") else None

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    ["plugin_generator.py"],
    pathex=[],
    binaries=[],
    datas=(
        [("ico.ico", ".")] if _ico else []
    ),
    hiddenimports=[
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.filedialog",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib", "numpy", "pandas", "scipy",
        "PIL", "cv2", "pytest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ── PYZ archive ───────────────────────────────────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── EXE (single-file portable) ────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="PluginGenerator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_ico,
    version="version.txt",
    uac_admin=False,
    uac_uiaccess=False,
)
