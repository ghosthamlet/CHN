# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['ui.py'],
             pathex=['/home/han/work/CHN'],
             binaries=[],
             datas=[('README.txt', '.'), ('config.py', '.'), ('data/*.pkl', 'data/')],
             hiddenimports=['en_core_web_sm','en_core_web_md','numpy.random.common','numpy.random.bounded_integers','numpy.random.entropy','srsly.msgpack.util','cymem','preshed.maps','cymem.cymem','thinc.linalg','murmurhash.mrmr','cytoolz.utils','cytoolz._signatures','spacy.strings','spacy.morphology','spacy.lexeme','spacy.tokens','spacy.gold','spacy.tokens.underscore','spacy.parts_of_speech','dill','blis','blis.cy','blis.py','spacy.tokens.printers','spacy.tokens._retokenize','spacy.syntax','spacy.syntax.stateclass','spacy.syntax.transition_system','spacy.syntax.nonproj','spacy.syntax.nn_parser','spacy.syntax.arc_eager','thinc.extra.search','spacy.syntax._beam_utils','spacy.syntax.ner','spacy._align','thinc.neural._classes.difference','thinc.neural._aligned_alloc','spacy.lang.en', 'spacy.syntax._parser_model', 'spacy.kb', 'spacy.matcher._schemas', 'sklearn.utils._cython_blas', 'sklearn.utils._logistic_sigmoid'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['config.py', 'torch', 'IPython', 'notebook', 'jupyter', 'pandas'],
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
          name='CHN',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='CHN')
