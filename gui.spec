# -*- mode: python -*-
a = Analysis(['gui.py'],
             pathex=['C:\\Python\\installer\\colors'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='gui.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               Tree("templates", prefix="templates"),
               Tree("icons", prefix="icons"),
               Tree("icons", prefix="po"),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='gui')
