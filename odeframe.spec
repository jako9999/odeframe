# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import os

from PyInstaller.utils.hooks import collect_dynamic_libs


PROJECT_DIR = Path.cwd()
TESSERACT_DIR = Path(os.environ.get("TESSERACT_DIR", r"C:\Program Files\Tesseract-OCR"))
TESSDATA_LANGS = [
    lang.strip() for lang in os.environ.get("TESSDATA_LANGS", "eng").split(",")
    if lang.strip()
]
BUNDLE_TESSERACT = os.environ.get("BUNDLE_TESSERACT", "1").strip().lower() not in {"0", "false", "no"}


def collect_tesseract_assets(base_dir: Path):
    datas = []
    binaries = []
    if not base_dir.exists():
        return datas, binaries

    for item in base_dir.iterdir():
        if item.is_dir() and item.name.lower() == "tessdata":
            for root, _, files in os.walk(item):
                for name in files:
                    src = Path(root) / name
                    rel = src.parent.relative_to(base_dir)
                    if src.suffix.lower() == ".traineddata":
                        if src.stem not in TESSDATA_LANGS:
                            continue
                    datas.append((str(src), str(Path("Tesseract-OCR") / rel)))
        elif item.is_file():
            ext = item.suffix.lower()
            if ext in {".exe", ".dll", ".pyd"}:
                binaries.append((str(item), "Tesseract-OCR"))
            else:
                datas.append((str(item), "Tesseract-OCR"))
    return datas, binaries


datas = [
    (str(PROJECT_DIR / "odeframe_icon.png"), "."),
]
binaries = []
hiddenimports = [
    "keyboard",
    "mss",
    "pytesseract",
    "PIL",
    "cv2",
    "numpy",
]
excludes = [
    "PyQt6.Qt3DAnimation",
    "PyQt6.Qt3DCore",
    "PyQt6.Qt3DExtras",
    "PyQt6.Qt3DInput",
    "PyQt6.Qt3DLogic",
    "PyQt6.Qt3DRender",
    "PyQt6.QtBluetooth",
    "PyQt6.QtCharts",
    "PyQt6.QtDBus",
    "PyQt6.QtDesigner",
    "PyQt6.QtHelp",
    "PyQt6.QtMultimedia",
    "PyQt6.QtMultimediaWidgets",
    "PyQt6.QtNetwork",
    "PyQt6.QtNfc",
    "PyQt6.QtOpenGL",
    "PyQt6.QtOpenGLWidgets",
    "PyQt6.QtPdf",
    "PyQt6.QtPdfWidgets",
    "PyQt6.QtPositioning",
    "PyQt6.QtPrintSupport",
    "PyQt6.QtQml",
    "PyQt6.QtQuick",
    "PyQt6.QtQuick3D",
    "PyQt6.QtQuickWidgets",
    "PyQt6.QtRemoteObjects",
    "PyQt6.QtSensors",
    "PyQt6.QtSerialPort",
    "PyQt6.QtSql",
    "PyQt6.QtStateMachine",
    "PyQt6.QtSvg",
    "PyQt6.QtSvgWidgets",
    "PyQt6.QtTest",
    "PyQt6.QtTextToSpeech",
    "PyQt6.QtWebChannel",
    "PyQt6.QtWebSockets",
    "PyQt6.QtXml",
    "PyQt6.uic",
]

binaries += collect_dynamic_libs("cv2")

if BUNDLE_TESSERACT:
    tess_datas, tess_binaries = collect_tesseract_assets(TESSERACT_DIR)
    datas += tess_datas
    binaries += tess_binaries


a = Analysis(
    ["main.py"],
    pathex=[str(PROJECT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
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
    name="OdeFrame",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_DIR / "odeframe_icon.ico"),
    uac_admin=True,
)
