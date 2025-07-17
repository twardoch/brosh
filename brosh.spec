# this_file: brosh.spec
# PyInstaller spec file for brosh binary builds

# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

# Get the source directory
src_dir = Path(__file__).parent / "src"

# Collect all data and hidden imports for dependencies
datas = []
hiddenimports = []
binaries = []

# Collect playwright data
playwright_datas, playwright_binaries, playwright_hiddenimports = collect_all('playwright')
datas.extend(playwright_datas)
binaries.extend(playwright_binaries)
hiddenimports.extend(playwright_hiddenimports)

# Collect brosh data
brosh_datas, brosh_binaries, brosh_hiddenimports = collect_all('brosh')
datas.extend(brosh_datas)
binaries.extend(brosh_binaries)
hiddenimports.extend(brosh_hiddenimports)

# Additional hidden imports
hiddenimports.extend([
    'brosh.cli',
    'brosh.mcp',
    'brosh.api',
    'brosh.browser',
    'brosh.capture',
    'brosh.image',
    'brosh.models',
    'brosh.tool',
    'brosh.texthtml',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'loguru',
    'fire',
    'fastmcp',
    'platformdirs',
    'html2text',
    'pyoxipng',
    'pydantic',
    'asyncio',
    'json',
    'pathlib',
    'typing',
    'collections',
    'functools',
    'itertools',
    'urllib.parse',
    'urllib.request',
    'urllib.error',
    'concurrent.futures',
    'tempfile',
    'shutil',
    'os',
    'sys',
    'subprocess',
    'platform',
    'time',
    'datetime',
    'base64',
    'gzip',
    'zlib',
    'hashlib',
    'uuid',
    'secrets',
    'weakref',
    'copy',
    'socket',
    'ssl',
    'http.client',
    'email.utils',
    'mimetypes',
    'locale',
    'encodings',
    'encodings.utf_8',
    'encodings.latin_1',
    'encodings.ascii',
])

# Add brosh package data
datas.append((str(src_dir / "brosh"), "brosh"))

# Analysis
a = Analysis(
    [str(src_dir / "brosh" / "__main__.py")],
    pathex=[str(src_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'jupyter',
        'IPython',
        'notebook',
        'pytest',
        'coverage',
        'mypy',
        'ruff',
        'black',
        'isort',
        'flake8',
        'pylint',
        'pre_commit',
        'setuptools',
        'wheel',
        'pip',
        'distutils',
        'pkg_resources',
        'packaging',
        'importlib_metadata',
        'xmlrpc',
        'xml.etree',
        'xml.parsers',
        'xml.sax',
        'xml.dom',
        'curses',
        'readline',
        'rlcompleter',
        'pdb',
        'doctest',
        'unittest',
        'test',
        'tests',
        'lib2to3',
        'email.mime',
        'email.message',
        'email.header',
        'email.charset',
        'email.encoders',
        'email.errors',
        'email.generator',
        'email.iterators',
        'email.parser',
        'email.policy',
        'multiprocessing',
        'queue',
        'threading',
        'concurrent',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='brosh',
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
    icon=None,
)