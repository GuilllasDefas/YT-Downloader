# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/styles/*.qss', 'resources/styles'),
        ('resources/logo.ico', '.'), 
        ('config.json', '.'), 
        ('logs', 'logs'),
    ],
    hiddenimports=[
        'yt_dlp', 
        'mutagen', 
        'pillow', 
        'requests', 
        'PyQt5', 
        'PyQt5-Qt5', 
        'PyQt5_sip',
        'ffmpeg',
        'PyQt5.sip',
        'src',
        'src.ui',
        'src.core',
        'src.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pyinstaller'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    exclude_binaries=True,
    name='YouTube Downloader',
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
    icon=['resources/logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YouTube Downloader',
)
