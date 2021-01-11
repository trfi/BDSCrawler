# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
         ( 'dist/config.json', '.' ),
         ( 'dist/changelog.txt', '.' ),
         ( 'dist/readme.txt', '.' ),
         ( 'dist/counter.json', '.' ),
         ( 'data.json', '.' ),
         ( 'keywords.txt', '.' ),
         ( 'keywords-th.txt', '.' ),
         ( 'icon-bds.ico', '.' ),
         ( 'text_unidecode', 'text_unidecode' )
         ]
a = Analysis(['main.py'],
             pathex=['D:\\Work\\BDS\\BDSCrawler'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='BDSCrawler',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='icon-bds.ico'
          )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='BDSCrawler')
