# -*- mode: python ; coding: utf-8 -*-

import os

project_root = os.path.abspath(os.path.join(SPECPATH, '..'))
main_script = os.path.join(project_root, 'desktop', 'main.py')

a = Analysis(
    [main_script],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'data'), 'data'),
        (os.path.join(project_root, 'web', 'templates'), 'web/templates'),
        (os.path.join(project_root, 'web', 'static'), 'web/static'),
    ],
    hiddenimports=[
        'web',
        'web.app',
        'src',
        'src.repository',
        'src.service',
        'src.visualize',
        'src.lineage',
    ],
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
    a.binaries,
    a.datas,
    [],
    name='family-tree',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
