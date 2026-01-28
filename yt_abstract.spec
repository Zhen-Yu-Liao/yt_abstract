# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\User\\桌面\\Nathan\\side_project\\yt_abstract\\backend\\main.py'],
    pathex=[],
    binaries=[('D:\\User\\桌面\\Nathan\\side_project\\yt_abstract\\backend\\bin\\ffmpeg.exe', '.'), ('D:\\User\\桌面\\Nathan\\side_project\\yt_abstract\\backend\\bin\\ffprobe.exe', '.')],
    datas=[('D:\\User\\桌面\\Nathan\\side_project\\yt_abstract\\backend\\static', 'static')],
    hiddenimports=['uvicorn', 'fastapi', 'engineio.async_drivers.asgi'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'matplotlib', 'PIL', 'tkinter', 'pynvml', 'faster_whisper'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='yt_abstract',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\User\\桌面\\Nathan\\side_project\\yt_abstract\\app_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='yt_abstract',
)
