# -*- mode: python -*-

block_cipher = None


a = Analysis(['palette-editor\\bin\\palette_editor.py'],
             pathex=['Z:\\home\\portnov\\src\\progs\\python\\color\\palette-editor'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='palette_editor',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               Tree("palette-editor\\share", prefix="share"),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='palette_editor')
