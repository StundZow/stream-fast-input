# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('SoundVolumeView.exe', '.')],
    datas=[('spotifyswitcher/assets', 'spotifyswitcher/assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'numpy', 'PIL',
        'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuick3D',
        'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
        'PySide6.QtNetwork', 'PySide6.QtMultimedia', 'PySide6.QtCharts',
        'PySide6.QtSql', 'PySide6.QtTest', 'PySide6.QtPdf', 'PySide6.QtPdfWidgets',
        'PySide6.Qt3DCore', 'PySide6.Qt3DRender', 'PySide6.QtBluetooth',
        'PySide6.QtSensors', 'PySide6.QtWebChannel', 'PySide6.QtWebSockets',
        'PySide6.QtDesigner', 'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# Measured onedir (a folder of ~100 loose DLLs) against onefile on this
# machine: onedir was ~3x SLOWER to reach input-idle (~1.9s vs ~0.65s),
# consistently, even after several warm-cache runs. Windows Defender's
# real-time protection is on here, and it scans a freshly-built folder of
# many small, unsigned DLLs individually on access — that cost dominated
# over onefile's single-archive extraction. Staying on onefile; upx stays
# off since decompressing it adds pure overhead with no upside for speed.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='StreamFastInput',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
