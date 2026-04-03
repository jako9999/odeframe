"""
AION2 컨텐츠 트래커 오버레이
- 게임 최상단 오버레이
- 설정창 (단축키 · 투명도 · 최상단 고정)
- 전체화면 관리창 (캐릭터 · 서버 · 컨텐츠 숨김)
- 자동 초기화 (일간 05:00 / 주간 수요 05:00 / 회랑 화목토 21:00)
"""





import sys, json, os, re
from datetime import datetime, timedelta
import threading
import base64

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QInputDialog,
    QMessageBox, QSlider, QCheckBox, QLineEdit, QDialog,
    QTabWidget, QGroupBox, QComboBox, QSizePolicy, QStackedWidget,
    QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt, QPoint, QTimer, QSize, pyqtSignal, pyqtSlot, QPointF
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QFontDatabase,
    QLinearGradient, QCursor, QKeySequence, QPolygonF, QIcon,
)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# OCR — 오드 자동 동기화
# ─────────────────────────────────────────────
# 아이콘 이미지 (base64 내장 — 파일 불필요)

_ODE_ICON_B64  = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAAuABwDASIAAhEBAxEB/8QAHAAAAQQDAQAAAAAAAAAAAAAACAIFBgcAAQME/8QALRAAAgEDAwEHAwUBAAAAAAAAAQIDBAURBhIhAAcTFDFBUWEIIjIjJFJxgfD/xAAWAQEBAQAAAAAAAAAAAAAAAAADBQT/xAAjEQACAgIBAwUBAAAAAAAAAAABAgADBBEhBTFBEiKBkaHR/9oADAMBAAIRAxEAPwAQNuF9uuwU7R88dajRpJAijk8Y9+rf7Iuy+tuFVHqO9U80Nko+7m3NAdlUd4HdgkEc8A8HzGRjJAXWipSzdpoRGc6EjFn7K9YXTTkV9pqAeFkSRwrEiQIq7lYL5nvCGVQMklecAqTB3UoxVhtI8x7Ho99YiSx2KCCYFqipVXq0kCmJiucKGZmJ2gKoCnnAJ5yQEWt44oNY3iBIVhWKtmQRqoUIA5GABwAPb06x4OY97MGEW+kVjiSf6f8AStt1Tr+moruWNOrRv3KgjxBM0abGYcqpD5JGDweQcHohtD2rXesu0ulqWprbS0lJRK1KhMkVPboc7I0iEa43r+YTKhtrcrjiq/pUt1PUVt9qh38ddT0TvTTRvgRkQzSZI9TvijP9KRjnIJXR9yo9HWOqrl2Grlwqoyr977ARllCl0UZ2k4OCf8r4qVPTkWWgEAADf2fyQ+o9RONlY+Ovdtn+Ty6j0/eZKLVdonqEqWt8sMoqXp1jEqeGhcgA7iAGVsKD7/dxggdqalmpdR3KmqapqqeKrlSWdiSZWDkFiTycnnnou9X6weGnr71dbzPBTxk+NrMDgumBTxou0SSuqkBc8AMSVVWaMRtSXCK6aguFygp3p4qqpkmSKSQSMgZiQrMFUMRnk7Rk+g6idOId3sRdKda+Jdv4VVY+7zLN+nO+1FqvN2pKeFZHqaFguc+Z/T9PiVjkEfiP8luodd2i0LU1Nw1C9Zcni2JTUYEjKcOVy2e7QBwFIB3LvyFbnA+SHAAAwMc/P/Y6SQxVnDH1Oc+o+OnfDFjlmJ0eSPyGHCgH0jY435jtqrU101FJEa+b9vT7hBTISI492NxA/kcLk+Z2geSrhl9v69sdKIXbgDj06wLkZ61qAqhR2hkknZn/2Q=="
_PLUS_ICON_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAAqACADASIAAhEBAxEB/8QAGgAAAgMBAQAAAAAAAAAAAAAABAUBBgcDCP/EACkQAAEDAwMDBAIDAAAAAAAAAAECAwQABREGIVESMWEHEyJBMnFSgZH/xAAYAQADAQEAAAAAAAAAAAAAAAABAgMABP/EABoRAQEBAQEBAQAAAAAAAAAAAAEAESECAxL/2gAMAwEAAhEDEQA/APIjSvd2V9d8UXEhPTJSGGkdZP8AgHJoO3RpMqWhmKgqcUf6A5Pin8uYiCwqFCKVKIw88B+R4HipPl3lU9mdgZseRGfMdxvpUj6+scjxQrh79Z34Ham0aU3PjpgzVBCgMMv/AMfB8UmmxJkWSph9PQoH67Ec54ofnJz6CTeQtu2Mrt8MkuHZ97GCo8DxWiej/pPrW8X3S+pUadblafcuLDzrrklgpWyl4BzLal9RGEq2xvwazuM8i9NhpwpRcEj4qOweA+j5onRNxYsOurHdp6HQxbrnHkvpQnK+lt1KlAA9zgGqlzte/WD0m1rZ77qjUq9OtxdPt3GQ8063JY6UsqeIbw2lfUBhSdsbcCs/gSGZ8dFum59wfFh3GSnwfFd9a3Bm/a5vl2gIdLFxuciSwlacL6XHVKTkc4IoKW8ixoLbZSu4KHyUNwyOP3QceMTTpIUqKVBQJBByCPqn0d9F6bDTpSi4pGEqOweHB81X6gKKVBSSQQcgg7isWe1lW+3ZWy0ghyeR8yN/ZHjzSOQ42olRIWSc5Pc1xaUpT3Uokk7kk96hf5j90uazjhf/2Q=="

_OCR_DEBUG_ENABLED = False

def _app_base_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def _user_data_dir():
    base = os.path.join(os.path.expanduser("~"), ".aion2tracker")
    os.makedirs(base, exist_ok=True)
    return base

def _resource_path(*parts):
    return os.path.join(_app_base_dir(), *parts)

def _resolve_tesseract_cmd():
    candidates = [
        _resource_path("Tesseract-OCR", "tesseract.exe"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]

def _app_icon():
    icon_path = _resource_path("odeframe_icon.ico")
    if not os.path.exists(icon_path):
        icon_path = _resource_path("odeframe_icon.png")
    return QIcon(icon_path) if os.path.exists(icon_path) else QIcon()


_OCR_DEBUG_DIR = _user_data_dir()

def _ocr_log(message):
    if _OCR_DEBUG_ENABLED:
        print(f"[OCR] {message}")

def _ocr_log_exception(prefix, exc):
    _ocr_log(f"{prefix}: {exc}")
    if _OCR_DEBUG_ENABLED:
        import traceback
        traceback.print_exc()

def _ocr_debug_save(image, filename):
    if not _OCR_DEBUG_ENABLED or image is None:
        return
    path = os.path.join(_OCR_DEBUG_DIR, filename)
    image.save(path)
    _ocr_log(f"저장: {path}")

def _find_aion2_window_info():
    """Aion2.exe의 PID/창/캐릭터명을 탐색해 dict로 반환."""
    import ctypes, ctypes.wintypes

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize",              ctypes.wintypes.DWORD),
            ("cntUsage",            ctypes.wintypes.DWORD),
            ("th32ProcessID",       ctypes.wintypes.DWORD),
            ("th32DefaultHeapID",   ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID",        ctypes.wintypes.DWORD),
            ("cntThreads",          ctypes.wintypes.DWORD),
            ("th32ParentProcessID", ctypes.wintypes.DWORD),
            ("pcPriClassBase",      ctypes.c_long),
            ("dwFlags",             ctypes.wintypes.DWORD),
            ("szExeFile",           ctypes.c_char * 260),
        ]

    target_pid = None
    TH32CS_SNAPPROCESS = 0x00000002
    snap = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap:
        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
        if ctypes.windll.kernel32.Process32First(snap, ctypes.byref(entry)):
            while True:
                name = entry.szExeFile.decode("utf-8", errors="ignore")
                if name.lower() == "aion2.exe":
                    target_pid = entry.th32ProcessID
                    break
                if not ctypes.windll.kernel32.Process32Next(snap, ctypes.byref(entry)):
                    break
        ctypes.windll.kernel32.CloseHandle(snap)

    if not target_pid:
        return {"pid": None, "hwnd": None, "titles": [], "char_name": None}

    found_titles, found_hwnds = [], []

    def enum_cb(hwnd, _):
        pid = ctypes.wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value != target_pid:
            return True
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
        if buf.value:
            found_titles.append(buf.value)
            found_hwnds.append(hwnd)
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    ctypes.windll.user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

    char_name = None
    for title in found_titles:
        m = re.search(r'AION2\s+l\s+(.+)', title)
        if not m:
            continue
        candidate = m.group(1).strip()
        if not candidate or len(candidate) > 12:
            continue
        char_name = candidate
        break

    return {
        "pid": target_pid,
        "hwnd": found_hwnds[0] if found_hwnds else None,
        "titles": found_titles,
        "char_name": char_name,
    }

def _ocr_load_template(b64_str):
    """base64 문자열 → OpenCV grayscale 이미지"""
    try:
        import cv2, numpy as np
        data = base64.b64decode(b64_str)
        arr  = np.frombuffer(data, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    except Exception:
        return None

def _ocr_set_dpi_aware():
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def _ocr_capture_topbar(hwnd):
    """게임 클라이언트 상단 바를 mss로 캡처. PIL Image 반환."""
    import ctypes, ctypes.wintypes, mss
    from PIL import Image as _Image

    # GetWindowRect: DPI 무관하게 실제 화면 픽셀 좌표 반환
    win_rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(win_rect))

    win_w = win_rect.right  - win_rect.left
    win_h = win_rect.bottom - win_rect.top

    # 상단 바 고정 높이: 전체 창 높이의 8% (최소 60px, 최대 120px)
    h_crop = max(60, min(120, int(win_h * 0.08)))

    _ocr_log(f"GetWindowRect: ({win_rect.left},{win_rect.top}) ~ ({win_rect.right},{win_rect.bottom})  창크기={win_w}x{win_h}  h_crop={h_crop}")

    # HWND 좌표 비정상 시 → 첫 번째 모니터 기준으로 폴백
    with mss.mss() as sct:
        if win_rect.top < 0 or win_w <= 0 or win_h <= 10:
            _ocr_log("HWND 좌표 비정상 → 모니터 폴백")
            mon = sct.monitors[1]
            left   = mon["left"]
            top    = mon["top"]
            full_w = mon["width"]
            full_h = mon["height"]
        else:
            left   = win_rect.left
            top    = win_rect.top
            full_w = win_w
            full_h = win_h

        # 세로: 전체 높이의 8% (최소 80px, 최대 160px)
        h_crop = max(80, min(160, int(full_h * 0.08)))
        # 가로: 중앙 기준 우측 절반만
        x_start = full_w // 2
        w_crop  = full_w - x_start

        _ocr_log(f"캡처 영역: left={left+x_start}, top={top}, width={w_crop}, height={h_crop}")

        shot = sct.grab({
            "left":   left + x_start,
            "top":    top,
            "width":  w_crop,
            "height": h_crop,
        })
        return _Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

def _ocr_find_icon(topbar_img, tpl_gray):
    """멀티스케일 템플릿 매칭. (x, y, w, h, score) 또는 None."""
    try:
        import cv2, numpy as np
        src  = cv2.cvtColor(np.array(topbar_img), cv2.COLOR_RGB2GRAY)
        th, tw = tpl_gray.shape
        sh, sw = src.shape
        best_score, best_pos, best_size = -1, None, None
        for scale in np.arange(0.5, 2.1, 0.1):
            nw, nh = max(1, int(tw * scale)), max(1, int(th * scale))
            if nw > sw or nh > sh:
                continue
            resized = cv2.resize(tpl_gray, (nw, nh), interpolation=cv2.INTER_LINEAR)
            res     = cv2.matchTemplate(src, resized, cv2.TM_CCOEFF_NORMED)
            _, val, _, loc = cv2.minMaxLoc(res)
            if val > best_score:
                best_score, best_pos, best_size = val, loc, (nw, nh)
        if best_score < 0.5 or best_pos is None:
            return None
        return (best_pos[0], best_pos[1], best_size[0], best_size[1], best_score)
    except Exception:
        return None

def _ocr_preprocess(img):
    """흰색 + 파란색 글씨 추출 → 이진화 이미지."""
    try:
        import numpy as np
        from PIL import Image as _Image
        w, h = img.size
        img  = img.resize((w * 2, h * 2), _Image.LANCZOS)
        arr  = np.array(img).astype(np.int32)
        R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        white = (R > 200) & (G > 200) & (B > 200)
        blue  = (B > 140) & (R < 120) & (B > R + 50)
        out   = np.zeros(arr.shape[:2], dtype=np.uint8)
        out[white | blue] = 255
        return _Image.fromarray(out, mode="L")
    except Exception:
        return None

def _ocr_parse(text):
    """OCR 결과 문자열 → (base, extra, max) 또는 None."""
    m = re.search(r'(\d+)\(\+?([\d,]+)\)/(\d+)', text)
    if m:
        return int(m.group(1)), int(m.group(2).replace(",", "")), int(m.group(3))
    return None

def _normalize_ode_result(result):
    """OCR 결과를 (base, extra, max|None) 형식으로 정규화."""
    if isinstance(result, dict):
        base = int(result.get("base", 0))
        extra = int(result.get("extra", 0))
        max_val = result.get("max")
        max_val = int(max_val) if max_val is not None else None
        return base, extra, max_val
    if isinstance(result, (tuple, list)) and len(result) >= 2:
        base = int(result[0])
        extra = int(result[1])
        max_val = int(result[2]) if len(result) >= 3 and result[2] is not None else None
        return base, extra, max_val
    return None

def capture_ode_from_game(hwnd):
    """
    hwnd 기준으로 오드 에너지를 OCR로 읽어 (base, extra, max) 반환.
    실패 시 None 반환.
    """
    try:
        import pytesseract
        _ocr_log(f"시작 — hwnd={hwnd}")
        _ocr_set_dpi_aware()

        # Tesseract 경로 설정
        tess_path = _resolve_tesseract_cmd()
        pytesseract.pytesseract.tesseract_cmd = tess_path
        _ocr_log(f"Tesseract 경로: {tess_path}")

        tpl_ode  = _ocr_load_template(_ODE_ICON_B64)
        tpl_plus = _ocr_load_template(_PLUS_ICON_B64)
        if tpl_ode is None or tpl_plus is None:
            _ocr_log("템플릿 로드 실패")
            return None
        _ocr_log("템플릿 로드 성공")

        topbar = _ocr_capture_topbar(hwnd)
        _ocr_log(f"탑바 캡처: {topbar.size}")
        # _ocr_debug_save(topbar, "ocr_debug_topbar.png")

        ode_hit  = _ocr_find_icon(topbar, tpl_ode)
        plus_hit = _ocr_find_icon(topbar, tpl_plus)
        _ocr_log(f"오드 아이콘: {ode_hit}")
        _ocr_log(f"+ 아이콘: {plus_hit}")

        if ode_hit is None or plus_hit is None:
            _ocr_log("아이콘 매칭 실패 → 종료")
            return None

        ox, oy, ow, oh, _ = ode_hit
        px, py, pw, ph, _ = plus_hit

        x1 = ox + ow + 4
        x2 = px - 4
        y1 = max(0, min(oy, py) - 2)
        y2 = min(topbar.height, max(oy + oh, py + ph) + 2)
        _ocr_log(f"텍스트 ROI: ({x1},{y1}) ~ ({x2},{y2})")
        if x2 <= x1:
            _ocr_log("ROI 폭 0 이하 → 종료")
            return None

        roi = topbar.crop((x1, y1, x2, y2))
        # _ocr_debug_save(roi, "ocr_debug_roi.png")

        processed = _ocr_preprocess(roi)
        if processed is None:
            _ocr_log("전처리 실패 → 종료")
            return None
        # _ocr_debug_save(processed, "ocr_debug_processed.png")

        config = r"--psm 6 -c tessedit_char_whitelist=0123456789()+/,"
        text   = pytesseract.image_to_string(processed, config=config, lang="eng").strip()
        _ocr_log(f"결과 텍스트: '{text}'")

        result = _ocr_parse(text)
        _ocr_log(f"파싱 결과: {result}")
        return result

    except Exception as e:
        _ocr_log_exception("예외 발생", e)
        return None

LEGACY_SAVE_PATH = os.path.join(os.path.expanduser("~"), ".aion2tracker.json")
SAVE_PATH = LEGACY_SAVE_PATH



# ALL_TASKS는 이제 state["tasks"]에서 동적으로 관리됨 (하위 호환용 빈 리스트)

C = {
    "bg":          "#0d0f14",
    "surface":     "#13161e",
    "surface2":    "#1a1e28",
    "border":      "#363d52",   # #252a38 → 밝게
    "border2":     "#4a5270",   # #2e3548 → 밝게
    "accent":      "#4f9cf9",
    "accent_dim":  "#4f9cf918",
    "gold":        "#c9a84c",
    "gold_dim":    "#c9a84c22",
    "done":        "#3dd68c",
    "done_dim":    "#3dd68c18",
    "text":        "#e8ecf4",
    "text_dim":    "#9aa3bd",   # #7a8299 → 밝게
    "text_muted":  "#6b7490",   # #4a5168 → 밝게
    "red":         "#f95f5f",
    "red_dim":     "#f95f5f18",
    "corridor":    "#b06fff",
}

RESET_COLOR = {"daily": "#4f9cf9", "weekly": "#c9a84c", "corridor": "#b06fff", "sanctuary": "#c9a84c", "directive": "#c9a84c"}
RESET_LABEL = {"daily": "일간",    "weekly": "주간",    "corridor": "회랑",    "sanctuary": "성역",   "directive": "지령서"}

# 카테고리 표시 고정 순서. sanctuary/directive는 weekly의 시각적 하위그룹이므로
# 표시 상 weekly로 묶임. 실제 reset_type은 유지.
RT_ORDER      = ["daily", "corridor", "weekly", "sanctuary", "directive"]
RT_WEEKLY_GRP = {"weekly", "sanctuary", "directive"}  # 주간 초기화 그룹

# ─────────────────────────────────────────────
# ROUNDED CARD  (안티앨리어싱 라운드 테두리 위젯)
# CSS border-radius 대신 QPainter로 직접 그려서 계단현상 제거
# ─────────────────────────────────────────────
class _RoundedCard(QWidget):
    """
    QPainterPath + Antialiasing 기반 라운드 컨테이너.
    bottom_corners=False 이면 상단 두 모서리만 라운딩 (탑바용).
    자식 위젯이 모서리를 넘치지 않도록 paintEvent에서 클리핑 경로를 설정.
    """
    def __init__(self, parent=None, *, bg="#0d0f14", border="#363d52",
                 radius=10, bottom_corners=True):
        super().__init__(parent)
        self._bg     = QColor(bg)
        self._border = QColor(border) if border else None
        self._radius = radius
        self._bottom = bottom_corners
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    def _make_path(self):
        from PyQt6.QtGui import QPainterPath
        w, h, r = self.width(), self.height(), self._radius
        path = QPainterPath()
        if self._bottom:
            path.addRoundedRect(0.5, 0.5, w - 1, h - 1, r, r)
        else:
            # 상단 두 모서리만 라운딩, 하단은 직각
            path.moveTo(r, 0.5)
            path.lineTo(w - r, 0.5)
            path.arcTo(w - 2*r, 0.5, 2*r - 1, 2*r - 1, 90, -90)
            path.lineTo(w - 0.5, h)
            path.lineTo(0.5, h)
            path.lineTo(0.5, r)
            path.arcTo(0.5, 0.5, 2*r - 1, 2*r - 1, 180, -90)
            path.closeSubpath()
        return path

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.update()  # paintEvent 재호출로 안티앨리어싱 경로 갱신

    def paintEvent(self, event):
        path = self._make_path()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        # 자식 위젯이 모서리 밖으로 넘치지 않도록 클리핑
        p.setClipPath(path)
        # 배경 채우기
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(self._bg))
        p.drawPath(path)
        p.end()
        # 테두리는 클리핑 없이 별도로 그려야 선이 잘리지 않음
        if self._border:
            p2 = QPainter(self)
            p2.setRenderHint(QPainter.RenderHint.Antialiasing)
            p2.setBrush(Qt.BrushStyle.NoBrush)
            p2.setPen(QPen(self._border, 1.0))
            p2.drawPath(path)
            p2.end()

# ─────────────────────────────────────────────
# ODE / KINA CONSTANTS
# ─────────────────────────────────────────────
ODE_SCHEDULE  = [2, 5, 8, 11, 14, 17, 20, 23]   # 매일 이 시각 정각 +15
ODE_AMT       = 15
ODE_MAX       = 840
ODE_EXTRA_MAX = 2000
ODE_COST      = 80


KINA_STEPS = {
    "jeongbok": [
        {"label":"100%","max":84,       "color":"#64dca0"},
        {"label":"80%", "max":105,      "color":"#60c8ff"},
        {"label":"60%", "max":126,      "color":"#ffe566"},
        {"label":"40%", "max":147,      "color":"#ffaa44"},
        {"label":"20%", "max":float("inf"),"color":"#ff6060"},
    ],
    "choweol": [
        {"label":"100%","max":56,       "color":"#64dca0"},
        {"label":"80%", "max":70,       "color":"#60c8ff"},
        {"label":"60%", "max":84,       "color":"#ffe566"},
        {"label":"40%", "max":98,       "color":"#ffaa44"},
        {"label":"20%", "max":float("inf"),"color":"#ff6060"},
    ],
}

def get_kina_tier(kina_id, value):
    steps = KINA_STEPS.get(kina_id, [])
    if not steps or value == 0: return None
    for s in steps:
        if value <= s["max"]: return s
    return steps[-1]

def count_ode_charges(from_ms, to_ms):
    """from_ms ~ to_ms 사이에 지나간 ODE 충전 정각 횟수."""
    if not from_ms or to_ms <= from_ms: return 0
    count = 0
    from_dt = datetime.fromtimestamp(from_ms / 1000)
    to_dt   = datetime.fromtimestamp(to_ms   / 1000)
    cur = from_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end = to_dt.replace(  hour=0, minute=0, second=0, microsecond=0)
    while cur <= end:
        for h in ODE_SCHEDULE:
            t = cur.replace(hour=h)
            if from_dt < t <= to_dt:
                count += 1
        cur += timedelta(days=1)
    return count

def apply_charges(state):
    """앱 시작/틱 시 밀린 오드 자동충전을 state에 반영. 변경 시 True 반환."""
    to_ms = int(datetime.now().timestamp() * 1000)
    changed = False
    ode_data = state.setdefault("ode", {})
    for c in state["chars"]:
        od = ode_data.setdefault(c, {
            "base":0,"extra":0,"recorded_at":None,"memo":""})
        from_ode = od.get("recorded_at")
        n_ode    = count_ode_charges(from_ode, to_ms)
        if n_ode == 0 and from_ode is not None:
            continue
        if n_ode > 0:
            od["base"] = min(ODE_MAX, od.get("base", 0) + n_ode * ODE_AMT)
        od["recorded_at"] = to_ms
        changed = True
    return changed

# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────
def default_state():
    chars = ["캐릭터1","캐릭터2","캐릭터3","캐릭터4"]
    tasks = [
        {"id": "daily_samyeong",     "name": "사명",              "reset": "daily",    "max": 1, "short_name": "사명"},
        {"id": "corridor_abyss",     "name": "어비스 회랑",       "reset": "corridor", "max": 1, "short_name": "회랑"},
        {"id": "weekly_awakening",   "name": "각성전",            "reset": "weekly",   "max": 3, "short_name": "각성"},
        {"id": "weekly_raid",        "name": "토벌전",            "reset": "weekly",   "max": 3, "short_name": "토벌"},
        {"id": "weekly_dungeon",     "name": "일일 던전",         "reset": "weekly",   "max": 7, "sub_input": True, "short_name": "일던"},
        {"id": "weekly_akmong",      "name": "악몽",              "reset": "weekly",   "max": 14},
        {"id": "weekly_abyss_rec",   "name": "심연의 재련",       "reset": "sanctuary","max": 4, "short_name": "심연"},
        {"id": "weekly_erosion",     "name": "침식의 정화소",     "reset": "sanctuary","max": 4, "short_name": "침식"},
        {"id": "weekly_altcard",     "name": "알트카르드 지령서", "reset": "directive","max": 1, "short_name": "알트"},
        {"id": "weekly_abyss_order", "name": "어비스 지령서",     "reset": "directive","max": 1, "short_name": "어비스"},
        {"id": "weekly_ode_shop", "name": "물질변환/산들바람", "reset": "weekly", "max": 1, "short_name": "오드"},
    ]
    checks = {c: {} for c in chars}
    # 오드 에너지 (캐릭터별)
    ode = {c: {
        "base": 0, "extra": 0,
        "recorded_at": None,   # ms timestamp
        "akmong_stock": 0,
        "akmong_recorded_at": None,
        "memo": "",
    } for c in chars}
    # 키나 획득률 (서버별)  {"서버명": {"jeongbok": 0, "choweol": 0}}
    kina = {}
    return {
        "chars":  chars,
        "checks": checks,
        "tasks":  tasks,
        "servers":        {c: "" for c in chars},
        "ode":            ode,
        "kina":           kina,
        "hidden_tasks":   [],
        "daily_reset":    "", "weekly_reset": "", "corridor_reset": "",
        "opacity":        100,
        "hotkey":         "Ctrl+H",
        "sync_hotkey":    "Ctrl+R",
        "overlay_pos":    [None, None],
    }

def load_state():
    try:
        if os.path.exists(SAVE_PATH):
            with open(SAVE_PATH,"r",encoding="utf-8") as f:
                data = json.load(f)
            dflt = default_state()
            for k,v in dflt.items():
                if k not in data: data[k] = v
            data.setdefault("servers", {})
            data.setdefault("hidden_tasks", [])
            data.setdefault("tasks", [])
            data.setdefault("kina", {})
            data.setdefault("ode", {})
            data.setdefault("sync_hotkey", "Ctrl+R")

            # ── 기본 컨텐츠 주입 (없는 것만 추가, 순서 보존) ──
            DEFAULT_TASKS = [
                {"id": "daily_samyeong",     "name": "사명",              "reset": "daily",    "max": 1, "short_name": "사명"},
                {"id": "corridor_abyss",     "name": "어비스 회랑",       "reset": "corridor", "max": 1, "short_name": "회랑"},
                {"id": "weekly_awakening",   "name": "각성전",            "reset": "weekly",   "max": 3, "short_name": "각성"},
                {"id": "weekly_raid",        "name": "토벌전",            "reset": "weekly",   "max": 3, "short_name": "토벌"},
                {"id": "weekly_dungeon",     "name": "일일 던전",         "reset": "weekly",   "max": 7, "sub_input": True, "short_name": "일던"},
                {"id": "weekly_akmong",      "name": "악몽",              "reset": "weekly",   "max": 14},
                {"id": "weekly_abyss_rec",   "name": "심연의 재련",       "reset": "sanctuary","max": 4, "short_name": "심연"},
                {"id": "weekly_erosion",     "name": "침식의 정화소",     "reset": "sanctuary","max": 4, "short_name": "침식"},
                {"id": "weekly_altcard",     "name": "알트카르드 지령서", "reset": "directive","max": 1, "short_name": "알트"},
                {"id": "weekly_abyss_order", "name": "어비스 지령서",     "reset": "directive","max": 1, "short_name": "어비스"},
                {"id": "weekly_ode_shop", "name": "물질변환/산들바람", "reset": "weekly", "max": 1, "short_name": "오드"},
            ]
            existing_ids = {t["id"] for t in data["tasks"]}
            for dt in DEFAULT_TASKS:
                if dt["id"] not in existing_ids:
                    data["tasks"].append(dt)
            # max 필드 없는 기존 task 보정
            id_to_default = {dt["id"]: dt for dt in DEFAULT_TASKS}
            for t in data["tasks"]:
                if "max" not in t:
                    t["max"] = id_to_default.get(t["id"], {}).get("max", 1)
                if "sub_input" not in t and t.get("id") in id_to_default:
                    si = id_to_default[t["id"]].get("sub_input", False)
                    if si: t["sub_input"] = si
                # 오탈자 수정
                if t.get("name") == "심연의 재권":
                    t["name"] = "심연의 재련"
                # 성역 타입 마이그레이션
                if t.get("id") in ("weekly_abyss_rec", "weekly_erosion"):
                    t["reset"] = "sanctuary"
                    # 패치: 입장횟수 2→4
                    if t.get("max", 2) < 4:
                        t["max"] = 4
                # 지령서 타입 마이그레이션
                if t.get("id") in ("weekly_altcard", "weekly_abyss_order"):
                    t["reset"] = "directive"
                    if t.get("id") == "weekly_altcard":
                        t["short_name"] = "알트"
                    else:
                        t["short_name"] = "어비스"
                # short_name 없으면 기본값 주입
                if "short_name" not in t:
                    sn_map = {
                        "daily_samyeong": "사명", "corridor_abyss": "회랑",
                        "weekly_altcard": "알트", "weekly_abyss_order": "어비스",
                        "weekly_awakening": "각성", "weekly_raid": "토벌",
                        "weekly_dungeon": "일던", "weekly_abyss_rec": "심연",
                        "weekly_erosion": "침식", "weekly_ode_shop": "오드",
                    }
                    if t.get("id") in sn_map:
                        t["short_name"] = sn_map[t["id"]]
            tasks = data["tasks"]
            _ode_default = {"base":0,"extra":0,"recorded_at":None,
                            "memo":""}
            for c in data["chars"]:
                data["checks"].setdefault(c, {})
                data["servers"].setdefault(c, "")
                data["ode"].setdefault(c, dict(_ode_default))
                for k, v in _ode_default.items():
                    data["ode"][c].setdefault(k, v)
                for t in tasks:
                    data["checks"][c].setdefault(t["id"], False)
            return data
    except Exception:
        pass
    return default_state()

def save_state(state):
    try:
        with open(SAVE_PATH,"w",encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ─────────────────────────────────────────────
# RESET LOGIC
# ─────────────────────────────────────────────
def _key_daily():
    now = datetime.now()
    t = now.replace(hour=5,minute=0,second=0,microsecond=0)
    return now.strftime("%Y-%m-%d") if now >= t else (now-timedelta(days=1)).strftime("%Y-%m-%d")

def _key_weekly():
    now = datetime.now()
    days_since = (now.weekday()-2) % 7
    last_wed = (now-timedelta(days=days_since)).replace(hour=5,minute=0,second=0,microsecond=0)
    if now < last_wed: last_wed -= timedelta(weeks=1)
    return last_wed.strftime("%Y-%m-%d")

def _key_corridor():
    now = datetime.now()
    for offset in range(8):
        d = now - timedelta(days=offset)
        if d.weekday() in [1,3,5]:
            t = d.replace(hour=21,minute=0,second=0,microsecond=0)
            if now >= t: return t.strftime("%Y-%m-%d-%H")
    return "never"

def check_auto_reset(state):
    changed = False
    tasks = state.get("tasks", [])
    for key_fn, reset_types, state_key in [
        (_key_daily,    {"daily"},                             "daily_reset"),
        (_key_weekly,   {"weekly", "sanctuary", "directive"},  "weekly_reset"),
        (_key_corridor, {"corridor"},                          "corridor_reset"),
    ]:
        k = key_fn()
        if state.get(state_key) != k:
            for c in state["chars"]:
                for t in tasks:
                    if t["reset"] in reset_types:
                        state["checks"][c][t["id"]] = False

            # 주간 초기화 시 키나 획득률도 리셋
            if state_key == "weekly_reset":
                for srv_data in state.get("kina", {}).values():
                    srv_data["jeongbok"] = 0
                    srv_data["choweol"]  = 0

            state[state_key] = k
            changed = True
    return changed

def _next_time(hour, weekday=None):
    now = datetime.now()
    if weekday is None:
        t = now.replace(hour=hour,minute=0,second=0,microsecond=0)
        if now >= t: t += timedelta(days=1)
        return t
    else:
        if isinstance(weekday, list):
            candidates = []
            for wd in weekday:
                for offset in range(8):
                    d = now + timedelta(days=offset)
                    if d.weekday() == wd:
                        t = d.replace(hour=hour,minute=0,second=0,microsecond=0)
                        if t > now: candidates.append(t); break
            return min(candidates) if candidates else now+timedelta(days=7)
        days = (weekday - now.weekday()) % 7 or 7
        t = (now+timedelta(days=days)).replace(hour=hour,minute=0,second=0,microsecond=0)
        if t <= now: t += timedelta(weeks=1)
        return t

def fmt_cd(target):
    diff = target - datetime.now()
    if diff.total_seconds() <= 0: return "곧 초기화"
    total_m = int(diff.total_seconds() // 60)
    d = total_m // 1440
    h = (total_m % 1440) // 60
    m = total_m % 60
    if d > 0: return f"{d}d {h}h {m}m"
    return f"{h}h {m}m"

# ─────────────────────────────────────────────
# STYLE HELPERS
# ─────────────────────────────────────────────
def _sbtn(hover=None, danger=False):
    hc = C["red"] if danger else (hover or C["text"])
    bg_hover = C["red_dim"] if danger else C["accent_dim"]
    return f"""
        QPushButton {{
            color:{C['text_dim']}; background:none;
            border:1px solid {C['border2']}; border-radius:4px;
            padding:2px 8px; font-size:10px; font-family:'Noto Sans KR';
        }}
        QPushButton:hover {{ color:{hc}; border-color:{hc}; background:{bg_hover}; }}
    """

def _sbtn_disabled():
    return f"""
        QPushButton {{
            color:{C['text_muted']}44;
            background:none;
            border:1px solid {C['border']}44;
            border-radius:4px;
            padding:2px 8px;
            font-size:10px;
            font-family:'Noto Sans KR';
        }}
        QPushButton:hover {{
            color:{C['text_muted']}44;
            border-color:{C['border']}44;
            background:none;
        }}
    """

# ─────────────────────────────────────────────
# CHECK ROW
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# ARROW BUTTON  (좌우 방향, 상하로 긴 삼각형)
# ─────────────────────────────────────────────
class _ArrowButton(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._right   = True
        self._hover   = False
        self._enabled = True
        self.setFixedSize(12, 28)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def set_right(self, v):   self._right = v;   self.update()
    def set_enabled(self, v):
        self._enabled = v
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor if v else Qt.CursorShape.ForbiddenCursor))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self._enabled:
            color = QColor(C["text_muted"]); color.setAlpha(60)
        else:
            color = QColor(C["text"] if self._hover else C["text_muted"])
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(color)
        w, h = self.width(), self.height()
        tip = 10
        poly = QPolygonF()
        if self._right:
            poly.append(QPointF(w//2 - tip//2, 2))
            poly.append(QPointF(w//2 + tip//2, h//2))
            poly.append(QPointF(w//2 - tip//2, h-2))
        else:
            poly.append(QPointF(w//2 + tip//2, 2))
            poly.append(QPointF(w//2 - tip//2, h//2))
            poly.append(QPointF(w//2 + tip//2, h-2))
        p.drawPolygon(poly); p.end()

    def enterEvent(self, e): self._hover = True;  self.update()
    def leaveEvent(self, e): self._hover = False; self.update()
    def mousePressEvent(self, e):
        if self._enabled and e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class CheckRow(QWidget):
    toggled = pyqtSignal(str)

    DOT_SIZE    = 12
    DOT_GAP     = 4
    MAX_PER_ROW = 7
    ROW_H       = 30

    def __init__(self, task, value, show_badge=True):
        super().__init__()
        self.task_id    = task["id"]
        self.reset_type = task["reset"]
        self._max       = task.get("max", 1)
        self._sub_input = task.get("sub_input", False)
        self.count      = (1 if value else 0) if self._max == 1 else (int(value) if isinstance(value, int) else 0)
        self._hov       = False
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # 높이: 도트 줄 수 × ROW_H (+ sub_input 행)
        dot_rows = (self._max + self.MAX_PER_ROW - 1) // self.MAX_PER_ROW
        self._sub_h = 26 if self._sub_input else 0
        self.setFixedHeight(self.ROW_H * dot_rows + self._sub_h)

        # 텍스트 라벨만 레이아웃에 배치 (도트는 paintEvent)
        h = QHBoxLayout(self); h.setContentsMargins(14, 0, 14, self._sub_h); h.setSpacing(9)
        self.lbl = QLabel(task["name"]); self.lbl.setFont(QFont("Noto Sans KR", 10))
        h.addWidget(self.lbl, 1)
        if show_badge:
            ltext = RESET_LABEL.get(task["reset"], "")
            if ltext:
                bc = RESET_COLOR.get(task["reset"], C["text_dim"])
                badge = QLabel(ltext); badge.setFont(QFont("Rajdhani", 8, QFont.Weight.Bold))
                badge.setStyleSheet(f"color:{bc};background:{bc}22;border:1px solid {bc}55;border-radius:3px;padding:1px 5px;")
                h.addWidget(badge)

        # sub_input 위젯
        if self._sub_input:
            self._sub_val = 0
            sub_row = QWidget(self); sub_row.setStyleSheet("background:transparent;")
            sub_row.setGeometry(0, self.ROW_H * dot_rows, self.width(), self._sub_h)
            sub_row.setFixedHeight(self._sub_h)
            sh = QHBoxLayout(sub_row); sh.setContentsMargins(14, 0, 14, 4); sh.setSpacing(4)
            sub_lbl = QLabel("추가 충전 수"); sub_lbl.setFont(QFont("Noto Sans KR", 8))
            sub_lbl.setStyleSheet(f"color:{C['text_muted']};background:transparent;")
            sh.addWidget(sub_lbl); sh.addStretch()
            btn_m = QPushButton("−"); btn_m.setFixedSize(18, 16)
            btn_m.setStyleSheet(_sbtn() + "QPushButton{padding:0;font-size:11px;}")
            self._sub_lbl = QLabel("0"); self._sub_lbl.setFixedWidth(30)
            self._sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sub_lbl.setFont(QFont("Rajdhani", 9, QFont.Weight.Bold))
            self._sub_lbl.setStyleSheet(f"color:{C['text']};background:transparent;")
            btn_p = QPushButton("+"); btn_p.setFixedSize(18, 16)
            btn_p.setStyleSheet(_sbtn() + "QPushButton{padding:0;font-size:11px;}")
            btn_m.clicked.connect(lambda: self._adj_sub(-1))
            btn_p.clicked.connect(lambda: self._adj_sub(+1))
            sh.addWidget(btn_m); sh.addWidget(self._sub_lbl); sh.addWidget(btn_p)
            self._sub_row = sub_row

        self._refresh()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._sub_input and hasattr(self, '_sub_row'):
            dot_rows = (self._max + self.MAX_PER_ROW - 1) // self.MAX_PER_ROW
            self._sub_row.setGeometry(0, self.ROW_H * dot_rows, self.width(), self._sub_h)

    def _adj_sub(self, d):
        self._sub_val = max(0, self._sub_val + d)
        self._sub_lbl.setText(str(self._sub_val))

    @property
    def is_done(self): return self.count >= self._max

    def _refresh(self):
        col = C["text_muted"] if self.is_done else C["text"]
        dec = "line-through" if self.is_done else "none"
        self.lbl.setStyleSheet(f"color:{col};text-decoration:{dec};")

    def paintEvent(self, ev):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._hov: p.fillRect(0, 0, self.width(), self.ROW_H, QColor(C["surface2"]))
        col = RESET_COLOR.get(self.reset_type, C["border2"])
        ds = self.DOT_SIZE; dg = self.DOT_GAP
        # 도트는 우측 정렬
        dots_w = min(self._max, self.MAX_PER_ROW) * (ds + dg)
        cb_right = self.width() - 14

        for i in range(self._max):
            row_i = i // self.MAX_PER_ROW
            col_i = i % self.MAX_PER_ROW
            ddx = cb_right - dots_w + col_i * (ds + dg)
            ddy = row_i * self.ROW_H + (self.ROW_H - ds) // 2
            filled = i < self.count
            p.setPen(QPen(QColor(col if filled else C["border2"]), 1.2))
            p.setBrush(QColor(col) if filled else Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(ddx, ddy, ds, ds, 2, 2)
        p.end()

    def enterEvent(self, e): self._hov = True;  self.update()
    def leaveEvent(self, e): self._hov = False; self.update()
    def mousePressEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton: return
        if self._max == 1:
            self.count = 0 if self.count else 1
        else:
            ds = self.DOT_SIZE; dg = self.DOT_GAP
            dots_w = min(self._max, self.MAX_PER_ROW) * (ds + dg)
            x = int(e.position().x())
            col_i = (x - (self.width() - 14 - dots_w)) // (ds + dg)
            col_i = max(0, min(self._max - 1, col_i))
            self.count = (self.count - 1) if col_i == self.count - 1 else col_i + 1
        self._refresh(); self.update(); self.toggled.emit(self.task_id)

# ─────────────────────────────────────────────
# SUMMARY VIEW  (요약뷰)
# JSX SpreadsheetView 구조 기반
# ─────────────────────────────────────────────
class _SummaryView(QWidget):
    char_selected = pyqtSignal(str)
    check_toggled = pyqtSignal(str, str)

    # ── 치수 ──
    HDR1_H  = 28
    HDR2_H  = 30
    ROW_H   = 44
    SRV_W   = 0
    CHAR_W  = 96
    TASK1_W = 38
    TASKN_W = 48
    PAD     = 6
    DOT     = 11

    # 그룹 메타 (색상/레이블 참조용 — 순서는 state["tasks"]를 따름)
    _GROUP_META = {
        "daily":     ("일간",  "#4f9cf9"),
        "corridor":  ("회랑",  "#b06fff"),
        "directive": ("지령서","#c9a84c"),
        "weekly":    ("주간",  "#c9a84c"),
        "sanctuary": ("성역",  "#c9a84c"),
    }
    GROUPS = [  # 하위호환용 (참조 코드 없으면 제거 가능)
        ("daily",     "일간",  "#4f9cf9"),
        ("corridor",  "회랑",  "#b06fff"),
        ("directive", "지령서","#c9a84c"),
        ("weekly",    "주간",  "#c9a84c"),
        ("sanctuary", "성역",  "#c9a84c"),
    ]
    BD  = (255, 255, 255, 18)   # 일반 테두리 RGBA
    BDS = (255, 255, 255, 8)    # 흐린 테두리

    def __init__(self, state, active_char, parent=None):
        super().__init__(parent)
        self._state      = state
        self._active_char= active_char
        self._hov_row    = None
        self._hov_col    = None
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.setMouseTracking(True)
        self._recalc()

    def _tasks(self):
        excl = {"weekly_akmong"}
        return [t for t in self._state.get("tasks", []) if t["id"] not in excl]

    def _servers(self):
        chars = self._state.get("chars", [])
        srvs  = self._state.get("servers", {})
        grp, order = {}, []
        for c in chars:
            s = srvs.get(c, "") or "공통"
            if s not in grp: grp[s] = []; order.append(s)
            grp[s].append(c)
        return [(s, grp[s]) for s in order]

    def _task_w(self, t):
        return self.TASK1_W if t.get("max", 1) == 1 else self.TASKN_W

    def _tasks_x(self):
        x = self.SRV_W + self.CHAR_W
        xs = []
        for t in self._tasks():
            xs.append(x); x += self._task_w(t)
        return xs

    def _total_w(self):
        return self.SRV_W + self.CHAR_W + sum(self._task_w(t) for t in self._tasks())

    def _total_h(self):
        return sum(len(cs) for _, cs in self._servers()) * self.ROW_H

    def _recalc(self):
        self.setFixedSize(self._total_w(), self._total_h())

    def refresh(self, state, active_char):
        self._state = state; self._active_char = active_char
        self._recalc(); self.update()
        
        
        
    def _paint_header(self, p):
        W = self._total_w()
        tasks = self._tasks()
        txs = self._tasks_x()
        bd_pen = QPen(QColor(*self.BD), 1)   # pen() 헬퍼 대신 직접 생성

        # ── HDR1: 좌측 타이머 3행 + 우측 그룹 헤더 ──
        p.fillRect(0, 0, W, self.HDR1_H, QColor(C["surface"]))

        TOTAL_HDR_H = self.HDR1_H + self.HDR2_H   # 58px
        SLOT_H      = TOTAL_HDR_H // 3             # ~19px per row
        TIMER_W     = self.CHAR_W

        TIMERS = [
            ("일간", RESET_COLOR["daily"],    fmt_cd(_next_time(5))),
            ("회랑", RESET_COLOR["corridor"], fmt_cd(_next_time(21, [1, 3, 5]))),
            ("주간", RESET_COLOR["weekly"],   fmt_cd(_next_time(5, 2))),
        ]
        for si, (label, col, cd) in enumerate(TIMERS):
            sy = si * SLOT_H
            # 레이블
            p.setFont(QFont("Noto Sans KR", 7, QFont.Weight.Bold))
            p.setPen(QColor(col))
            p.drawText(self.PAD, sy, 24, SLOT_H, Qt.AlignmentFlag.AlignVCenter, label)
            # 카운트다운
            p.setFont(QFont("Rajdhani", 8))
            p.setPen(QColor(255, 255, 255, 160))
            p.drawText(self.PAD + 26, sy, TIMER_W - self.PAD - 26, SLOT_H,
                       Qt.AlignmentFlag.AlignVCenter, cd)
            # 행 하단선 (마지막 제외)
            if si < 2:
                p.setPen(bd_pen)
                p.drawLine(0, sy + SLOT_H, TIMER_W, sy + SLOT_H)

        # 타이머 영역 우측 선 (HDR1+HDR2 전체 높이)
        p.setPen(bd_pen)
        p.drawLine(TIMER_W, 0, TIMER_W, TOTAL_HDR_H)

        # 컨텐츠 그룹 헤더 (우측 영역, HDR1 높이 기준)
        HDR1_GROUPS = [
            ({"daily"},      "일간",  RESET_COLOR["daily"]),
            ({"corridor"},   "회랑",  RESET_COLOR["corridor"]),
            (RT_WEEKLY_GRP,  "주간",  RESET_COLOR["weekly"]),
        ]
        for rt_set, glabel, gcol in HDR1_GROUPS:
            g_tasks = [(i, t) for i, t in enumerate(tasks) if t["reset"] in rt_set]
            if not g_tasks: continue
            gx0 = txs[g_tasks[0][0]]
            gx1 = txs[g_tasks[-1][0]] + self._task_w(g_tasks[-1][1])
            p.setPen(QColor(gcol))
            p.setFont(QFont("Noto Sans KR", 8, QFont.Weight.Bold))
            p.drawText(gx0, 0, gx1 - gx0, self.HDR1_H, Qt.AlignmentFlag.AlignCenter, glabel.upper())
            p.setPen(QPen(QColor(gcol), 1))
            p.drawLine(gx0, self.HDR1_H - 1, gx1, self.HDR1_H - 1)

        # HDR1 하단선 (우측 컨텐츠 영역만)
        p.setPen(bd_pen)
        p.drawLine(TIMER_W, self.HDR1_H, W, self.HDR1_H)

        # ── HDR2: 컬럼 헤더 (좌측 CHAR_W는 타이머 영역이므로 제외) ──
        hdr2_y = self.HDR1_H
        p.fillRect(self.CHAR_W, hdr2_y, W - self.CHAR_W, self.HDR2_H, QColor(C["surface"]))

        for i, t in enumerate(tasks):
            cw = self._task_w(t)
            col = RESET_COLOR.get(t["reset"], C["text_dim"])
            is_hov = self._hov_col == i

            if is_hov:
                p.fillRect(
                    txs[i], hdr2_y, cw, self.HDR2_H,
                    QColor(130, 90, 255, 30)
                )

            p.setPen(QColor(255, 255, 255, 200) if is_hov else QColor(col))
            p.setFont(
                QFont(
                    "Noto Sans KR",
                    8,
                    QFont.Weight.Bold if is_hov else QFont.Weight.Normal
                )
            )

            p.drawText(
                txs[i], hdr2_y, cw, self.HDR2_H,
                Qt.AlignmentFlag.AlignCenter,
                t.get("short_name", t["name"])
            )

            # 컬럼 좌측 선
            p.setPen(bd_pen)
            p.drawLine(txs[i], hdr2_y, txs[i], hdr2_y + self.HDR2_H)

        # HDR2 하단선
        p.setPen(bd_pen)
        p.drawLine(0, hdr2_y + self.HDR2_H, W, hdr2_y + self.HDR2_H)



    def paintEvent(self, ev):
        from PyQt6.QtGui import QPainterPath
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 창 가득 채울 때 모서리를 라운드 클리핑
        clip = QPainterPath()
        clip.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        p.setClipPath(clip)

        W = self.width()
        tasks = self._tasks(); txs = self._tasks_x()
        checks = self._state.get("checks", {})
        ode_d  = self._state.get("ode", {})

        def pen(rgba): return QPen(QColor(*rgba), 1)
        BD = self.BD; BDS = self.BDS

        # ── 전체 배경 ──
        # 창 배경이 이미 _SummaryWindow에서 라운드 처리되므로
        # 내부 표는 투명 바탕 위에 필요한 영역만 그린다.
        p.fillRect(self.rect(), QColor(0, 0, 0, 0))

        # ── 컬럼 그룹 배경 ──
        GROUP_BG = {
            "daily":    QColor(79,156,249,10),
            "corridor": QColor(176,111,255,10),
            "weekly":   QColor(201,168,76,10),
            "sanctuary":QColor(201,168,76,7),
        }
        for i, t in enumerate(tasks):
            if self._hov_col == i:
                p.fillRect(txs[i], 0, self._task_w(t), self._total_h(), QColor(130,90,255,22))
            else:
                p.fillRect(txs[i], 0, self._task_w(t), self._total_h(), GROUP_BG.get(t["reset"], QColor(0,0,0,0)))

        # ── 데이터 행 (헤더는 _SummaryWindow.paintEvent에서 고정 렌더링) ──
        y = 0
        for srv, chars in self._servers():
            srv_y     = y
            srv_total = len(chars) * self.ROW_H



            for ri, char in enumerate(chars):
                is_last = ri == len(chars) - 1
                is_hov  = self._hov_row == char
                row_bd  = BD if is_last else BDS

                # hover
                if is_hov:
                    p.fillRect(self.SRV_W, y, W - self.SRV_W, self.ROW_H, QColor(130,90,255,16))

                # 캐릭터명 + 오드 바 레이아웃
                is_act   = char == self._active_char
                ode_base = self._state.get("ode", {}).get(char, {}).get("base", 0)

                # 캐릭터명: 상단 (ROW_H 의 약 60%)
                NAME_H  = 26
                BAR_H   = 5
                BAR_Y   = y + NAME_H + 4   # 캐릭터명 아래 4px 여백
                BAR_X   = self.SRV_W + self.PAD
                BAR_W   = self.CHAR_W - self.PAD * 2

                p.setFont(QFont("Noto Sans KR", 10, QFont.Weight.Bold))
                p.setPen(QColor(C["accent"] if is_act else "#ede6ff"))
                p.drawText(self.SRV_W + self.PAD, y,
                           self.CHAR_W - self.PAD*2, NAME_H,
                           Qt.AlignmentFlag.AlignVCenter, char)
                # 밑줄
                fm = p.fontMetrics()
                tw = min(fm.horizontalAdvance(char), self.CHAR_W - self.PAD*2 - 16)
                uly = y + NAME_H//2 + fm.ascent()//2 + 1
                p.setPen(QPen(QColor(160,128,255,80), 1))
                p.drawLine(self.SRV_W + self.PAD, uly, self.SRV_W + self.PAD + tw, uly)
                p.setFont(QFont("Noto Sans KR", 8)); p.setPen(QColor(160,128,255,100))
                p.drawText(self.SRV_W + self.PAD + tw + 2, y, 14, NAME_H,
                           Qt.AlignmentFlag.AlignVCenter, "↗")

                # 오드 바
                ratio     = min(ode_base / 840, 1.0)
                fill_w    = int(BAR_W * ratio)
                bar_color = (
                    QColor("#f95f5f") if ratio >= 0.8 else
                    QColor("#f9c74f") if ratio >= 0.4 else
                    QColor("#4dbd74")
                )
                # 배경 트랙
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QColor(255, 255, 255, 18))
                p.drawRoundedRect(BAR_X, BAR_Y, BAR_W, BAR_H, 2, 2)
                # 채움
                if fill_w > 0:
                    p.setBrush(bar_color)
                    p.drawRoundedRect(BAR_X, BAR_Y, fill_w, BAR_H, 2, 2)

                # 캐릭터 셀 우측 선
                p.setPen(pen(BD))
                p.drawLine(self.SRV_W + self.CHAR_W, y, self.SRV_W + self.CHAR_W, y + self.ROW_H)


                # 컨텐츠 셀
                cc2 = checks.get(char, {})
                for i, t in enumerate(tasks):
                    _max = t.get("max", 1)
                    raw  = cc2.get(t["id"], 0)
                    cnt  = 1 if (raw and _max==1) else (int(raw) if isinstance(raw,int) else 0)
                    done = cnt >= _max
                    tc   = RESET_COLOR.get(t["reset"], C["border2"])
                    cw   = self._task_w(t)

                    if _max == 1:
                        ds = self.DOT
                        cx = txs[i] + (cw - ds)//2
                        cy = y + (self.ROW_H - ds)//2
                        p.setPen(QPen(QColor(tc if done else C["border2"]), 1.2))
                        p.setBrush(QColor(tc) if done else Qt.BrushStyle.NoBrush)
                        p.drawRoundedRect(cx, cy, ds, ds, 2, 2)
                    else:
                        p.setFont(QFont("Rajdhani", 10))
                        p.setPen(QColor(tc if done else C["text_muted"]))
                        p.drawText(txs[i], y, cw, self.ROW_H, Qt.AlignmentFlag.AlignCenter,
                                   f"{cnt}/{_max}")
                    # 컬럼 좌측 선
                    p.setPen(pen(BD))
                    p.drawLine(txs[i], y, txs[i], y + self.ROW_H)

                # 행 하단선
                p.setPen(pen(row_bd))
                p.drawLine(self.SRV_W, y+self.ROW_H-1, W, y+self.ROW_H-1)
                y += self.ROW_H

            # 서버 그룹 하단 외곽선
            p.setPen(pen(BD)); p.drawLine(0, y, W, y)

        # 외곽 테두리
        p.setPen(pen(BD)); p.drawRect(0, 0, W-1, self._total_h()-1)
        p.end()

    def _hit(self, mx, my):
        tasks = self._tasks(); txs = self._tasks_x()
        y = 0
        for _, chars in self._servers():
            for char in chars:
                if y <= my < y + self.ROW_H:
                    if self.SRV_W <= mx < self.SRV_W + self.CHAR_W:
                        return ("char", char)
                    for i, t in enumerate(tasks):
                        if txs[i] <= mx < txs[i] + self._task_w(t):
                            return ("task", char, i)
                y += self.ROW_H
        return None

    def _col_at(self, mx):
        txs = self._tasks_x()
        for i, t in enumerate(self._tasks()):
            if txs[i] <= mx < txs[i] + self._task_w(t):
                return i
        return None

    def mouseMoveEvent(self, e):
        mx, my = int(e.position().x()), int(e.position().y())
        hit = self._hit(mx, my)
        new_row = hit[1] if hit and hit[0] in ("char","task") else None
        new_col = self._col_at(mx) if my >= self.HDR1_H else None
        if new_row != self._hov_row or new_col != self._hov_col:
            self._hov_row = new_row; self._hov_col = new_col
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor if hit
                                   else Qt.CursorShape.ArrowCursor))
            self.update()

    def leaveEvent(self, e):
        self._hov_row = None; self._hov_col = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor)); self.update()

    def mousePressEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton: return
        hit = self._hit(int(e.position().x()), int(e.position().y()))
        if not hit: return
        if hit[0] == "char":
            self.char_selected.emit(hit[1])
        elif hit[0] == "task":
            _, char, ci = hit
            t    = self._tasks()[ci]
            _max = t.get("max", 1)
            cc2  = self._state["checks"].setdefault(char, {})
            raw  = cc2.get(t["id"], 0)
            cnt  = 1 if (raw and _max==1) else (int(raw) if isinstance(raw,int) else 0)
            if _max == 1:
                cc2[t["id"]] = not bool(cnt)
            else:
                cc2[t["id"]] = 0 if cnt >= _max else cnt + 1
            self.check_toggled.emit(char, t["id"])
            self.update()



# ─────────────────────────────────────────────
# PROGRESS BAR
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# SETTINGS DIALOG
# ─────────────────────────────────────────────
def _paint_rounded_window(widget, radius=10):
    """FramelessHint QDialog/QWidget의 paintEvent에서 호출.
    배경+클리핑+테두리를 안티앨리어싱으로 그린다."""
    from PyQt6.QtGui import QPainterPath
    w, h = widget.width(), widget.height()
    path = QPainterPath()
    path.addRoundedRect(0.5, 0.5, w - 1, h - 1, radius, radius)

    p = QPainter(widget)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.fillRect(widget.rect(), QColor(0, 0, 0, 0))   # 투명 배경 초기화
    p.setClipPath(path)                              # 자식 위젯 클리핑
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(C["bg"])))
    p.drawPath(path)
    p.end()

    # 테두리는 클리핑 밖에서 그려야 선이 잘리지 않음
    p2 = QPainter(widget)
    p2.setRenderHint(QPainter.RenderHint.Antialiasing)
    p2.setBrush(Qt.BrushStyle.NoBrush)
    p2.setPen(QPen(QColor(C["border"]), 1.0))
    p2.drawPath(path)
    p2.end()

def _apply_rounded_mask(widget, radius=10):
    """더 이상 폴리곤 마스크를 사용하지 않음. paintEvent + WA_TranslucentBackground로 처리."""
    widget.clearMask()


class SettingsDialog(QDialog):
    applied  = pyqtSignal(dict)
    live_opacity = pyqtSignal(int)   # emitted while dragging slider

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self._rec  = False
        self._rec_target = None
        self._orig_opacity = state.get("opacity", 100)   # restore on cancel

        # ── Frameless, same dark style as overlay ──
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self._drag_pos = None
        self._build()

    # ── Custom paint: rounded dark card (안티앨리어싱) ──
    def paintEvent(self, e):
        _paint_rounded_window(self)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        _apply_rounded_mask(self)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)
    def mouseReleaseEvent(self, e): self._drag_pos = None

    def _lbl(self, text, size=11, color=None):
        l = QLabel(text); l.setFont(QFont("Noto Sans KR", size))
        l.setStyleSheet(f"color:{color or C['text']};background:transparent;")
        return l

    def _divider(self):
        d = QFrame(); d.setFrameShape(QFrame.Shape.HLine)
        d.setStyleSheet(f"color:{C['border']};"); return d

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(0); root.setContentsMargins(0, 0, 0, 0)

        # ── 타이틀바 (드래그용) ──
        bar = _RoundedCard(self, bg=C["surface"], border=None, radius=10, bottom_corners=False)
        bar.setFixedHeight(36)
        bh = QHBoxLayout(bar); bh.setContentsMargins(14, 0, 10, 0); bh.setSpacing(6)
        tl = QLabel("설정"); tl.setFont(QFont("Rajdhani", 11, QFont.Weight.Bold))
        tl.setStyleSheet(f"color:{C['text']};letter-spacing:1.5px;background:transparent;"); bh.addWidget(tl, 1)
        xb = QPushButton("✕"); xb.setFixedSize(20, 18)
        xb.setStyleSheet(f"QPushButton{{color:{C['text_muted']};background:none;border:none;font-size:11px;}}"
                         f"QPushButton:hover{{color:{C['red']};}}")
        xb.clicked.connect(self._cancel); bh.addWidget(xb)
        root.addWidget(bar)

        # ── 본문 ──
        body = QWidget(); body.setStyleSheet("background:transparent;")
        bv = QVBoxLayout(body); bv.setContentsMargins(16, 12, 16, 14); bv.setSpacing(10)

        # 오버레이 동작 섹션
        bv.addWidget(self._sec_label("오버레이 동작"))

        # opacity row
        op_hdr = QHBoxLayout()
        op_hdr.addWidget(self._lbl("투명도"), 1)
        self._op_val = QLabel(f"{self.state.get('opacity',100)}%")
        self._op_val.setFont(QFont("Rajdhani", 12, QFont.Weight.Bold))
        self._op_val.setStyleSheet(f"color:{C['accent']};background:transparent;")
        op_hdr.addWidget(self._op_val); bv.addLayout(op_hdr)

        self._op_sl = QSlider(Qt.Orientation.Horizontal)
        self._op_sl.setRange(20, 100); self._op_sl.setValue(self.state.get("opacity", 100))
        self._op_sl.setStyleSheet(self._sl_css()); self._op_sl.setFixedHeight(20)
        self._op_sl.valueChanged.connect(self._on_opacity_change)
        bv.addWidget(self._op_sl)

        bv.addWidget(self._divider())

        # hotkey 섹션
        bv.addWidget(self._sec_label("최소화 단축키"))
        hk_row = QHBoxLayout(); hk_row.setSpacing(6)
        self._hk = QLineEdit(self.state.get("hotkey", "Ctrl+Shift+H")); self._hk.setReadOnly(True)
        self._hk.setStyleSheet(
            f"background:{C['surface2']};color:{C['accent']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:5px 9px;font-family:'Rajdhani';font-size:12px;")
        self._hk.setFixedHeight(30)
        rec = QPushButton("키 입력"); rec.setFixedSize(76, 30)
        rec.setStyleSheet(_sbtn(C["accent"])); rec.clicked.connect(lambda: self._start_rec("toggle"))
        hk_row.addWidget(self._hk, 1); hk_row.addWidget(rec); bv.addLayout(hk_row)

        bv.addWidget(self._divider())

        bv.addWidget(self._sec_label("오드 동기화 단축키"))
        sync_row = QHBoxLayout(); sync_row.setSpacing(6)
        self._sync_hk = QLineEdit(self.state.get("sync_hotkey", "Ctrl+R")); self._sync_hk.setReadOnly(True)
        self._sync_hk.setStyleSheet(
            f"background:{C['surface2']};color:#4dbd74;border:1px solid {C['border']};"
            f"border-radius:4px;padding:5px 9px;font-family:'Rajdhani';font-size:12px;")
        self._sync_hk.setFixedHeight(30)
        sync_rec = QPushButton("키 입력"); sync_rec.setFixedSize(76, 30)
        sync_rec.setStyleSheet(_sbtn("#4dbd74")); sync_rec.clicked.connect(lambda: self._start_rec("sync"))
        sync_row.addWidget(self._sync_hk, 1); sync_row.addWidget(sync_rec); bv.addLayout(sync_row)

        bv.addWidget(self._divider())

        # ── 버튼행 ──
        br = QHBoxLayout(); br.setSpacing(8)
        br.addStretch()
        cancel_btn = QPushButton("취소"); cancel_btn.setFixedSize(80, 32)
        cancel_btn.setStyleSheet(self._action_btn(False)); cancel_btn.clicked.connect(self._cancel)
        ok_btn = QPushButton("적용"); ok_btn.setFixedSize(80, 32)
        ok_btn.setStyleSheet(self._action_btn(True)); ok_btn.clicked.connect(self._apply)
        br.addWidget(cancel_btn); br.addWidget(ok_btn); bv.addLayout(br)

        root.addWidget(body)
        self.adjustSize()

        # center on parent
        if self.parent():
            pp = self.parent().geometry()
            self.move(pp.center() - self.rect().center())

    def _sec_label(self, text):
        l = QLabel(text); l.setFont(QFont("Noto Sans KR", 9, QFont.Weight.Medium))
        l.setStyleSheet(f"color:{C['text_muted']};letter-spacing:0.5px;background:transparent;")
        return l

    def _action_btn(self, primary):
        if primary:
            return f"""
                QPushButton{{background:{C['accent']};color:#fff;border:none;border-radius:5px;
                    font-family:'Noto Sans KR';font-size:11px;font-weight:500;}}
                QPushButton:hover{{background:#6aaaff;}}
            """
        return f"""
            QPushButton{{background:{C['surface2']};color:{C['text_dim']};border:1px solid {C['border']};
                border-radius:5px;font-family:'Noto Sans KR';font-size:11px;}}
            QPushButton:hover{{border-color:{C['border2']};color:{C['text']};}}
        """

    def _sl_css(self):
        return f"""
            QSlider::groove:horizontal{{height:4px;background:{C['surface2']};border-radius:2px;}}
            QSlider::handle:horizontal{{background:{C['accent']};width:14px;height:14px;border-radius:7px;margin:-5px 0;}}
            QSlider::sub-page:horizontal{{background:{C['accent']};border-radius:2px;}}
        """

    def _on_opacity_change(self, v):
        self._op_val.setText(f"{v}%")
        self.live_opacity.emit(v)   # live preview

    def _start_rec(self, target):
        self._rec = True
        self._rec_target = target
        if target == "sync":
            self._sync_hk.setText("...")
        else:
            self._hk.setText("...")
        self.setFocus()
        # 녹화 중 전역 훅 일시 해제
        overlay = self.parent()
        if overlay:
            for attr in ("_hk_hook", "_sync_hk_hook"):
                hook = getattr(overlay, attr, None)
                if hook:
                    try:
                        import keyboard as _kb; _kb.remove_hotkey(hook)
                    except Exception:
                        pass
                    setattr(overlay, attr, None)

    def _stop_rec(self):
        """녹화 종료 후 전역 훅 복원."""
        self._rec = False
        self._rec_target = None
        overlay = self.parent()
        if overlay and hasattr(overlay, "_setup_global_hotkey"):
            overlay._setup_global_hotkey()

    def keyPressEvent(self,e):
        if not self._rec: return super().keyPressEvent(e)
        key=e.key()
        if key==Qt.Key.Key_Escape:
            self._hk.setText(self.state.get("hotkey","Ctrl+Shift+H"))
            self._sync_hk.setText(self.state.get("sync_hotkey","Ctrl+R"))
            self._stop_rec(); return
        # modifier 단독 키는 무시 — 조합키 완성 대기
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift, Qt.Key.Key_Meta):
            return
        mods=e.modifiers(); parts=[]
        if mods & Qt.KeyboardModifier.ControlModifier: parts.append("Ctrl")
        if mods & Qt.KeyboardModifier.AltModifier:     parts.append("Alt")
        if mods & Qt.KeyboardModifier.ShiftModifier:   parts.append("Shift")
        if mods & Qt.KeyboardModifier.MetaModifier:    parts.append("Meta")
        kname=QKeySequence(key).toString()
        if kname and kname not in ("Ctrl","Alt","Shift","Meta",""):
            parts.append(kname)
        combo="+".join(parts)
        if combo:
            if self._rec_target == "sync":
                self._sync_hk.setText(combo)
            else:
                self._hk.setText(combo)
            self._stop_rec()

    def _cancel(self):
        # restore original opacity on cancel
        self.live_opacity.emit(self._orig_opacity)
        self.reject()

    def _apply(self):
        self.applied.emit({
            "opacity": self._op_sl.value(),
            "hotkey": self._hk.text(),
            "sync_hotkey": self._sync_hk.text(),
        })
        self.accept()

# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# CHAR DRAG CONTAINER  (직접 드래그 구현 - Qt 내장 D&D 완전 대체)
# ─────────────────────────────────────────────
class _CharDragContainer(QWidget):
    """
    캐릭터 행을 QWidget으로 직접 그리고, mousePressEvent/mouseMoveEvent/mouseReleaseEvent로
    드래그를 구현한다. Qt 내장 QListWidget D&D의 맨앞/끝 삭제 버그를 완전히 우회.
    """
    order_changed = pyqtSignal(list)

    ROW_H = 42      # 행 높이
    HANDLE_W = 32   # 드래그 핸들 영역 너비

    def __init__(self, state, manager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._state   = state
        self._rows    = []          # list of char_key in display order
        self._drag_idx   = None     # 현재 드래그 중인 행 인덱스
        self._drag_y     = 0        # 드래그 시작 시 마우스 y (위젯 기준)
        self._drag_offset= 0        # 드래그 시작 시 행 top ~ 마우스 y 오프셋
        self._hover_idx  = None
        self.setMouseTracking(True)
        self.rebuild(state)

    def rebuild(self, state):
        self._state = state
        self._rows  = list(state["chars"])
        self._drag_idx = None
        total_h = max(len(self._rows) * self.ROW_H + 8, 60)
        self.setMinimumHeight(total_h)
        self.setFixedHeight(total_h)
        self.update()

    def _row_top(self, idx):
        return 4 + idx * self.ROW_H

    def _idx_at(self, y):
        idx = (y - 4) // self.ROW_H
        return max(0, min(len(self._rows)-1, idx))

    # ── 페인트 ──
    def paintEvent(self, e):
        from PyQt6.QtGui import QPainterPath
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(C["surface"]))

        for i, key in enumerate(self._rows):
            top = self._row_top(i)
            rect_y = top
            h = self.ROW_H

            # 드래그 중인 행은 나중에 맨 위에 그림
            if i == self._drag_idx:
                continue

            # 호버 배경
            if i == self._hover_idx:
                p.fillRect(4, rect_y+1, self.width()-8, h-2, QColor(C["surface2"]))

            self._draw_row(p, key, 4, rect_y, self.width()-8, h, False)

        # 드래그 중인 행: 마우스 위치에 floating으로 그림
        if self._drag_idx is not None:
            key = self._rows[self._drag_idx]
            float_y = self._drag_y - self._drag_offset
            float_y = max(4, min(self.height() - self.ROW_H - 4, float_y))
            # 그림자 효과
            p.setOpacity(0.18)
            p.fillRect(6, float_y+3, self.width()-8, self.ROW_H-2, QColor(0,0,0))
            p.setOpacity(0.92)
            path = QPainterPath()
            path.addRoundedRect(4, float_y, self.width()-8, self.ROW_H-2, 5, 5)
            p.fillPath(path, QColor(C["surface2"]))
            p.setOpacity(1.0)
            self._draw_row(p, key, 4, float_y, self.width()-8, self.ROW_H, True)

            # 삽입 위치 표시선
            insert_idx = self._insert_index()
            line_y = 4 + insert_idx * self.ROW_H
            line_y = max(4, min(self.height()-4, line_y))
            p.setPen(QPen(QColor(C["accent"]), 2))
            p.drawLine(12, line_y, self.width()-12, line_y)

        p.end()

    def _draw_row(self, p, key, x, y, w, h, is_dragging):
        srv     = self._state.get("servers", {}).get(key, "")
        display = f"{key}[{srv}]" if srv else key

        # 핸들
        p.setPen(QColor(C["accent"] if is_dragging else C["text_muted"]))
        p.setFont(QFont("Noto Sans KR", 13))
        p.drawText(x+6, y, 20, h, Qt.AlignmentFlag.AlignVCenter, "⠿")

        # 이름
        p.setPen(QColor(C["text"]))
        p.setFont(QFont("Noto Sans KR", 10))
        p.drawText(x+28, y, w-28-68, h, Qt.AlignmentFlag.AlignVCenter, display)

        # 편집(✎) 버튼
        edit_x = x + w - 64
        p.setPen(QColor(C["border"]))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(edit_x, y+8, 26, 22, 3, 3)
        p.setPen(QColor(C["text_muted"]))
        p.setFont(QFont("Noto Sans KR", 10))
        p.drawText(edit_x, y+8, 26, 22, Qt.AlignmentFlag.AlignCenter, "✎")

        # 삭제(✕) 버튼
        del_x = x + w - 32
        p.setPen(QColor(C["border"]))
        p.drawRoundedRect(del_x, y+8, 26, 22, 3, 3)
        p.setPen(QColor(C["text_muted"]))
        p.drawText(del_x, y+8, 26, 22, Qt.AlignmentFlag.AlignCenter, "✕")

    def _insert_index(self):
        """드래그 현재 위치에서 삽입될 인덱스 계산."""
        float_y = self._drag_y - self._drag_offset + self.ROW_H // 2
        idx = (float_y - 4) // self.ROW_H
        idx = max(0, min(len(self._rows), idx))
        return idx

    # ── 마우스 이벤트 ──
    def mousePressEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton: return
        y = int(e.position().y()); x = int(e.position().x())
        idx = self._idx_at(y)
        if 0 <= idx < len(self._rows):
            # 핸들 영역(왼쪽 HANDLE_W px)에서만 드래그 시작
            if x <= self.HANDLE_W:
                self._drag_idx    = idx
                self._drag_y      = y
                self._drag_offset = y - self._row_top(idx)
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                self.update()
            else:
                # 편집/삭제 버튼 영역 클릭 처리
                self._handle_btn_click(idx, x, y)

    def mouseMoveEvent(self, e):
        y = int(e.position().y()); x = int(e.position().x())
        if self._drag_idx is not None:
            self._drag_y = y
            self.update()
        else:
            idx = self._idx_at(y)
            if self._hover_idx != idx:
                self._hover_idx = idx
                self.update()
            # 핸들 위면 커서 변경
            if x <= self.HANDLE_W:
                self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mouseReleaseEvent(self, e):
        if self._drag_idx is None: return
        src  = self._drag_idx
        dest = self._insert_index()
        # dest 보정: src보다 아래로 이동 시 dest-1
        if dest > src:
            dest -= 1
        self._drag_idx = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        if src != dest:
            new_order = list(self._rows)
            item = new_order.pop(src)
            new_order.insert(dest, item)
            self._rows = new_order
            self.order_changed.emit(new_order)
        self.update()

    def leaveEvent(self, e):
        self._hover_idx = None
        self.update()

    def _handle_btn_click(self, idx, x, w):
        """편집(✎)·삭제(✕) 버튼 영역 클릭 처리."""
        row_w = self.width()
        # 삭제 버튼: 오른쪽 30px
        if x >= row_w - 36:
            self._manager._del_char(self._rows[idx])
        # 편집 버튼: 삭제 버튼 왼쪽 30px
        elif x >= row_w - 68:
            self._manager._inline_edit(self._rows[idx])

    def sizeHint(self):
        return QSize(self.width(), max(len(self._rows) * self.ROW_H + 8, 60))




# ─────────────────────────────────────────────
# TASK DRAG CONTAINER  (컨텐츠 순서 드래그)
# ─────────────────────────────────────────────
class _TaskDragContainer(QWidget):
    """
    드래그 유닛 구성:
    - 기본 타입(예: weekly)의 태스크는 각각 1유닛
    - 그룹 타입(예: sanctuary, directive)은 타입 전체가 1유닛 (내부 항목은 표시만)
    - 모든 유닛은 같은 레벨에서 자유롭게 순서 변경 가능
    """
    order_changed = pyqtSignal(list)

    ROW_H    = 36   # 단일 유닛 높이
    GRP_H    = 22   # 그룹 유닛 헤더 높이
    SUB_H    = 28   # 그룹 유닛 서브항목 높이
    HANDLE_W = 30

    def __init__(self, state, reset_type, manager,
                 group_types=None, parent=None):
        """
        reset_type  : 개별 드래그되는 기본 타입 (str 또는 list)
        group_types : 그룹 단위로 드래그되는 타입 리스트 (예: ["sanctuary","directive"])
        """
        super().__init__(parent)
        base = reset_type if isinstance(reset_type, list) else [reset_type]
        self._base_types  = base
        self._group_types = group_types or []
        self._all_types   = base + self._group_types
        self._state   = state
        self._manager = manager
        self._units   = []   # {"kind":"single"|"group", "rt":str, "tasks":[...]}
        self._drag_idx   = None
        self._drag_y     = 0
        self._drag_offset= 0
        self._hover_idx  = None
        self.setMouseTracking(True)
        self.rebuild(state)

    # ── 유닛 높이 ───────────────────────────────
    def _unit_h(self, u):
        return self.ROW_H

    def _unit_top(self, idx):
        y = 4
        for i, u in enumerate(self._units):
            if i == idx: return y
            y += self._unit_h(u)
        return y

    def _total_content_h(self):
        return 8 + sum(self._unit_h(u) for u in self._units)

    def _unit_at(self, y):
        cy = 4
        for i, u in enumerate(self._units):
            h = self._unit_h(u)
            if cy <= y < cy + h: return i
            cy += h
        return max(0, len(self._units) - 1)

    # ── rebuild ─────────────────────────────────
    def rebuild(self, state):
        self._state = state
        tasks = state.get("tasks", [])

        # 전체 순서대로 유닛 생성
        # 먼저 담당 타입 태스크만 추출 (순서 유지)
        my_tasks = [t for t in tasks if t["reset"] in self._all_types]

        self._units = []
        consumed = set()
        for t in my_tasks:
            if t["id"] in consumed: continue
            if t["reset"] in self._group_types:
                # 같은 타입 전체를 그룹 유닛으로
                grp = [x for x in my_tasks if x["reset"] == t["reset"]]
                for x in grp: consumed.add(x["id"])
                self._units.append({"kind": "group", "rt": t["reset"], "tasks": grp})
            else:
                consumed.add(t["id"])
                self._units.append({"kind": "single", "rt": t["reset"], "tasks": [t]})

        self._drag_idx = None
        self.setFixedHeight(max(self._total_content_h(), 40))
        self.update()

    # ── paint ────────────────────────────────────
    def paintEvent(self, e):
        from PyQt6.QtGui import QPainterPath
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(C["surface"]))

        for i, u in enumerate(self._units):
            if i == self._drag_idx: continue
            self._draw_unit(p, u, self._unit_top(i), i == self._hover_idx, False)

        if self._drag_idx is not None:
            u = self._units[self._drag_idx]
            uh = self._unit_h(u)
            fy = max(4, min(self.height()-uh-4, self._drag_y - self._drag_offset))

            # 삽입선
            dest = self._insert_index()
            ly = (self._unit_top(dest) if dest < len(self._units)
                  else self._unit_top(len(self._units)-1) + self._unit_h(self._units[-1]))
            p.setPen(QPen(QColor(C["accent"]), 2))
            p.drawLine(12, max(4, min(self.height()-4, ly)), self.width()-12, max(4, min(self.height()-4, ly)))

            # floating 유닛
            p.setOpacity(0.15); p.fillRect(6, fy+3, self.width()-8, uh-2, QColor(0,0,0))
            p.setOpacity(0.92)
            path = QPainterPath(); path.addRoundedRect(4, fy, self.width()-8, uh-2, 5, 5)
            p.fillPath(path, QColor(C["surface2"])); p.setOpacity(1.0)
            self._draw_unit(p, u, fy, False, True)
        p.end()

    def _draw_unit(self, p, u, top, is_hov, is_drag):
        w = self.width()
        color = RESET_COLOR.get(u["rt"], C["border2"])

        if u["kind"] == "group":
            if is_hov and not is_drag:
                p.fillRect(4, top+1, w-8, self.ROW_H-2, QColor(C["surface2"]))
            p.setPen(QColor(C["accent"] if is_drag else C["text_muted"]))
            p.setFont(QFont("Noto Sans KR", 13))
            p.drawText(6, top, 22, self.ROW_H, Qt.AlignmentFlag.AlignVCenter, "⠿")
            p.setPen(QColor(color))
            p.setFont(QFont("Noto Sans KR", 9, QFont.Weight.Bold))
            p.drawText(26, top, w-34, self.ROW_H, Qt.AlignmentFlag.AlignVCenter,
                       RESET_LABEL.get(u["rt"], u["rt"]))
        else:
            # 단일 항목
            if is_hov and not is_drag:
                p.fillRect(4, top+1, w-8, self.ROW_H-2, QColor(C["surface2"]))
            p.setPen(QColor(C["accent"] if is_drag else C["text_muted"]))
            p.setFont(QFont("Noto Sans KR", 13))
            p.drawText(6, top, 22, self.ROW_H, Qt.AlignmentFlag.AlignVCenter, "⠿")
            p.setPen(QColor(C["text"]))
            p.setFont(QFont("Noto Sans KR", 10))
            p.drawText(26, top, w-34, self.ROW_H,
                       Qt.AlignmentFlag.AlignVCenter, u["tasks"][0]["name"])

    # ── insert index ─────────────────────────────
    def _insert_index(self):
        if self._drag_idx is None: return 0
        uh = self._unit_h(self._units[self._drag_idx])
        mid = self._drag_y - self._drag_offset + uh // 2
        for i in range(len(self._units)):
            if self._unit_top(i) >= mid: return i
        return len(self._units)

    # ── mouse ────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton: return
        y = int(e.position().y()); x = int(e.position().x())
        idx = self._unit_at(y)
        if 0 <= idx < len(self._units) and x <= self.HANDLE_W:
            self._drag_idx    = idx
            self._drag_y      = y
            self._drag_offset = y - self._unit_top(idx)
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            self.update()

    def mouseMoveEvent(self, e):
        y = int(e.position().y()); x = int(e.position().x())
        if self._drag_idx is not None:
            self._drag_y = y; self.update()
        else:
            idx = self._unit_at(y)
            if self._hover_idx != idx: self._hover_idx = idx; self.update()
            self.setCursor(QCursor(
                Qt.CursorShape.SizeVerCursor if x <= self.HANDLE_W
                else Qt.CursorShape.ArrowCursor))

    def leaveEvent(self, e):
        self._hover_idx = None; self.update()

    def mouseReleaseEvent(self, e):
        if self._drag_idx is None: return
        src  = self._drag_idx
        dest = self._insert_index()
        if dest > src: dest -= 1
        self._drag_idx = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        if src != dest:
            new_units = list(self._units)
            item = new_units.pop(src)
            new_units.insert(dest, item)
            self._units = new_units

            # state["tasks"] 재구성
            new_order = []
            for u in self._units:
                new_order.extend(u["tasks"])
            my_types = set(self._all_types)
            new_tasks = []
            inserted = False
            for t in self._state["tasks"]:
                if t["reset"] in my_types and not inserted:
                    new_tasks.extend(new_order); inserted = True
                elif t["reset"] not in my_types:
                    new_tasks.append(t)
            self._state["tasks"] = new_tasks
            self.rebuild(self._state)
            self.order_changed.emit(new_order)
        self.update()

    def sizeHint(self):
        return QSize(self.width(), max(self._total_content_h(), 40))

class KinaPanel(QWidget):
    changed = pyqtSignal()

    KINA_ITEMS = [
        ("jeongbok", "정복"),
        ("choweol",  "초월"),
    ]

    def __init__(self, state, server_name, overlay=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background:transparent;")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.state       = state
        self.server_name = server_name
        self._overlay    = overlay   # Overlay 참조 (오드 차감용)
        self._build()
        self.refresh()

    def _kina_data(self):
        return self.state.setdefault("kina", {}).setdefault(
            self.server_name, {"jeongbok": 0, "choweol": 0})

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(8,6,8,6); root.setSpacing(6)

        # 헤더
        hdr = QHBoxLayout()
        title = QLabel("키나 획득률"); title.setFont(QFont("Noto Sans KR",9,QFont.Weight.Bold))
        title.setStyleSheet(f"color:{C['gold']};background:transparent;")
        hdr.addWidget(title)
        badge = QLabel("서버 공유"); badge.setFont(QFont("Noto Sans KR",8))
        badge.setStyleSheet(f"color:{C['text_muted']};background:transparent;")
        hdr.addWidget(badge); hdr.addStretch()
        root.addLayout(hdr)

        # 각 키나 항목
        self._bars = {}
        for kid, klabel in self.KINA_ITEMS:
            root.addWidget(self._make_kina_row(kid, klabel))

    def _make_kina_row(self, kid, klabel):
        # 고정 블록은 [− val +] 만 — 오드 패널의 버튼 너비와 통일
        CTRL_W = 20; VAL_W = 38
        FIXED_W = CTRL_W + 4 + VAL_W + 4 + CTRL_W  # 20+4+38+4+20 = 86

        w = QWidget(); w.setStyleSheet("background:transparent;")
        v = QVBoxLayout(w); v.setContentsMargins(0,0,0,0); v.setSpacing(4)

        top = QHBoxLayout(); top.setSpacing(4)

        # 컨텐츠 라벨
        lbl = QLabel(klabel); lbl.setFont(QFont("Noto Sans KR",9,QFont.Weight.Medium))
        lbl.setStyleSheet(f"color:{C['text']};background:transparent;")
        top.addWidget(lbl)

        # tier badge (고정 블록 밖)
        tier_lbl = QLabel("100%"); tier_lbl.setFont(QFont("Rajdhani",9,QFont.Weight.Bold))
        tier_lbl.setFixedWidth(38); tier_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        tier_lbl.setStyleSheet("color:#64dca0;background:transparent;")
        top.addWidget(tier_lbl)

        top.addStretch()

        # 보상 버튼 (고정 블록 밖)
        enter_btn = QPushButton("−80"); enter_btn.setFixedSize(36, 22)
        enter_btn.setFont(QFont("Rajdhani", 9, QFont.Weight.Bold))
        enter_btn.setStyleSheet(f"""
            QPushButton{{color:{C['text_muted']};background:{C['surface2']};
                border:1px solid {C['border']};border-radius:4px;padding:0;}}
            QPushButton:hover{{color:#5ed49a;border-color:rgba(94,212,154,0.4);
                background:rgba(94,212,154,0.08);}}
        """)
        enter_btn.clicked.connect(lambda _, k=kid: self._enter_reward(k))
        top.addWidget(enter_btn)

        # ── 고정 블록: [− val +] ──
        right = QWidget(); right.setFixedWidth(FIXED_W)
        right.setStyleSheet("background:transparent;")
        rh = QHBoxLayout(right); rh.setContentsMargins(0,0,0,0); rh.setSpacing(4)

        btn_m = QPushButton("−"); btn_m.setFixedSize(CTRL_W, 22)
        btn_m.setStyleSheet(self._btn_style())
        btn_m.clicked.connect(lambda _, k=kid: self._adjust(k, -1))
        rh.addWidget(btn_m)

        # 숫자 라벨 + 편집용 QLineEdit (오드와 동일 구조)
        num_stack = QWidget(); num_stack.setFixedSize(VAL_W, 22)
        num_stack.setStyleSheet("background:transparent;")

        val_lbl = QLabel("0"); val_lbl.setFont(QFont("Rajdhani",11,QFont.Weight.Bold))
        val_lbl.setGeometry(0,0,VAL_W,22); val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_lbl.setStyleSheet(f"color:{C['text']};background:transparent;"
                              f"border-bottom:1px solid {C['border2']};")
        val_lbl.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        val_lbl.setParent(num_stack)

        val_edit = QLineEdit("0"); val_edit.setFixedSize(VAL_W, 22)
        val_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_edit.setFont(QFont("Rajdhani",11,QFont.Weight.Bold))
        val_edit.setStyleSheet(f"""
            QLineEdit{{color:{C['text']};background:{C['surface2']};
                border:1px solid {C['border2']};border-radius:3px;
                font-family:'Rajdhani';font-size:11px;padding:0;}}
            QLineEdit:focus{{border:1px solid {C['border2']};outline:0;}}
        """)
        val_edit.setParent(num_stack); val_edit.hide()

        def _start(e, k=kid, lbl=val_lbl, edit=val_edit):
            edit.setText(str(self._kina_data().get(k, 0)))
            lbl.hide(); edit.show(); edit.setFocus(); edit.selectAll()
        def _commit(k=kid, lbl=val_lbl, edit=val_edit):
            try: v2 = max(0, int(edit.text()))
            except ValueError: v2 = self._kina_data().get(k, 0)
            self._kina_data()[k] = v2
            edit.hide(); lbl.show()
            self.refresh(); self.changed.emit()

        val_lbl.mousePressEvent = _start
        val_edit.returnPressed.connect(_commit)
        val_edit.editingFinished.connect(_commit)
        rh.addWidget(num_stack)

        btn_p = QPushButton("+"); btn_p.setFixedSize(CTRL_W, 22)
        btn_p.setStyleSheet(self._btn_style())
        btn_p.clicked.connect(lambda _, k=kid: self._adjust(k, +1))
        rh.addWidget(btn_p)

        top.addWidget(right)
        v.addLayout(top)

        # 진행 바
        bar = _KinaBar(kid); v.addWidget(bar)

        self._bars.setdefault(kid, {}).update({
            "tier": tier_lbl, "val": val_lbl, "bar": bar, "enter_btn": enter_btn
        })
        return w

    def _btn_style(self):
        return f"""QPushButton{{color:{C['text_muted']};background:{C['surface2']};
            border:1px solid {C['border']};border-radius:4px;font-size:13px;padding:0;}}
            QPushButton:hover{{color:{C['text']};border-color:{C['border2']};}}"""

    def _enter_reward(self, kid):
        """보상획득: 오드 -80 (해당 캐릭터), 키나 횟수 +1"""
        char_key = self._overlay.active_char if self._overlay and hasattr(self._overlay, "active_char") else None
        if char_key:
            od = self.state.setdefault("ode", {}).setdefault(char_key, {
                "base":0,"extra":0,"recorded_at":None,
                "memo":""})
            base  = od.get("base",  0)
            extra = od.get("extra", 0)
            # 오드 차감 (있는 만큼만, 0 이하로 내려가지 않음)
            deduct = ODE_COST
            b_d = min(base, deduct);  deduct -= b_d
            e_d = min(extra, deduct)
            od["base"]  = base  - b_d
            od["extra"] = extra - e_d
            # OdePanel 즉시 갱신
            if self._overlay and hasattr(self._overlay, "_ode_panel") and self._overlay._ode_panel:
                self._overlay._ode_panel.refresh()
        # 키나 +1 (오드 유무 관계없이 항상)
        self._adjust(kid, 1)   # refresh + changed.emit + save 포함

    def _adjust(self, kid, delta):
        d = self._kina_data()
        d[kid] = max(0, d.get(kid, 0) + delta)
        self.refresh(); self.changed.emit()

    def refresh(self):
        d = self._kina_data()
        # 오드 총량 (보상버튼 색상 결정용)
        char_key = self._overlay.active_char if self._overlay and hasattr(self._overlay, "active_char") else None
        od = self.state.get("ode", {}).get(char_key, {}) if char_key else {}
        ode_total = od.get("base", 0) + od.get("extra", 0)
        ode_ok = ode_total >= ODE_COST

        for kid, _ in self.KINA_ITEMS:
            v    = d.get(kid, 0)
            tier = get_kina_tier(kid, v)
            refs = self._bars[kid]
            # val_lbl이 숨겨져 있으면 편집 중 → 업데이트 스킵
            if not refs["val"].isHidden():
                refs["val"].setText(str(v))
            refs["bar"].set_value(v)
            if tier:
                refs["tier"].setText(tier["label"])
                refs["tier"].setStyleSheet(f"color:{tier['color']};background:transparent;")
            else:
                refs["tier"].setText("100%")
                refs["tier"].setStyleSheet("color:#64dca0;background:transparent;")
            # 보상버튼 색상
            btn = refs.get("enter_btn")
            if btn:
                if ode_ok:
                    btn.setStyleSheet(f"""
                        QPushButton{{color:#5ed49a;background:rgba(94,212,154,0.1);
                            border:1px solid rgba(94,212,154,0.4);border-radius:4px;
                            padding:0 7px;font-family:'Noto Sans KR';font-size:8px;}}
                        QPushButton:hover{{background:rgba(94,212,154,0.18);}}
                    """)
                else:
                    btn.setStyleSheet(f"""
                        QPushButton{{color:{C['text_muted']};background:{C['surface2']};
                            border:1px solid {C['border']};border-radius:4px;
                            padding:0 7px;font-family:'Noto Sans KR';font-size:8px;}}
                        QPushButton:hover{{color:#5ed49a;border-color:rgba(94,212,154,0.4);
                            background:rgba(94,212,154,0.08);}}
                    """)



class _KinaBar(QWidget):
    """키나 획득률 시각적 진행 바."""
    def __init__(self, kina_id):
        super().__init__(); self.kina_id = kina_id; self._value = 0
        self.setFixedHeight(10)

    def set_value(self, v): self._value = v; self.update()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width(); h = self.height()
        steps = KINA_STEPS.get(self.kina_id, [])
        if not steps: p.end(); return
        slider_max = steps[-2]["max"]   # 20% 시작점

        # 배경
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(C["surface2"]))
        p.drawRoundedRect(0, 2, w, h-4, 3, 3)

        # 채움
        pct = min(self._value / slider_max, 1.0) if slider_max > 0 else 0
        fw  = int(w * pct)
        tier = get_kina_tier(self.kina_id, self._value)
        color = tier["color"] if tier else "#64dca0"
        if fw > 0:
            p.setBrush(QColor(color))
            p.drawRoundedRect(0, 2, fw, h-4, 3, 3)

        # 구간 경계선
        p.setPen(QPen(QColor(C["bg"]), 1))
        for s in steps[:-1]:
            if s["max"] < slider_max:
                x = int((s["max"] / slider_max) * w)
                p.drawLine(x, 2, x, h-2)
        p.end()


# ─────────────────────────────────────────────
# ODE PANEL  (캐릭터 단위 오드 에너지 + 악몽)
# ─────────────────────────────────────────────
class OdePanel(QWidget):
    changed = pyqtSignal()

    def __init__(self, state, char_key, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background:transparent;")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.state    = state
        self.char_key = char_key
        self._build()
        self.refresh()

        # 1분 틱 타이머
        self._tick_tmr = QTimer(); self._tick_tmr.timeout.connect(self._tick)
        self._tick_tmr.start(60000)
        # 1초 카운트다운 타이머
        self._sec_tmr = QTimer(); self._sec_tmr.timeout.connect(self._upd_timer_labels)
        self._sec_tmr.start(1000)

    def _od(self):
        return self.state.setdefault("ode", {}).setdefault(self.char_key, {
            "base":0,"extra":0,"recorded_at":None,
            "memo":""})

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(8,6,8,6); root.setSpacing(6)

        # ── 오드 에너지 헤더 ──
        hdr = QHBoxLayout()
        title = QLabel("오드 에너지"); title.setFont(QFont("Noto Sans KR",9,QFont.Weight.Bold))
        title.setStyleSheet(f"color:#4dbd74;background:transparent;"); hdr.addWidget(title,1)
        self._ode_timer_lbl = QLabel("")
        self._ode_timer_lbl.setFont(QFont("Rajdhani",10,QFont.Weight.Bold))
        self._ode_timer_lbl.setStyleSheet(f"color:#4dbd74;background:transparent;")
        hdr.addWidget(self._ode_timer_lbl)
        charge_hint = QLabel(f"+{ODE_AMT}"); charge_hint.setFont(QFont("Noto Sans KR",8))
        charge_hint.setStyleSheet(f"color:{C['text_muted']};background:transparent;")
        hdr.addWidget(charge_hint)
        root.addLayout(hdr)

        # 오드 스케줄 바
        self._ode_sched = _OdeScheduleBar(); root.addWidget(self._ode_sched)

        # 기본 / 추가 슬라이더
        root.addWidget(self._make_ode_row("base",  "기본",      ODE_MAX,       "#4dbd74"))
        root.addWidget(self._make_ode_row("extra", "추가(수동)", ODE_EXTRA_MAX, "#ff9040"))

    def _make_ode_row(self, field, label, max_val, color):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        v = QVBoxLayout(w); v.setContentsMargins(0,0,0,0); v.setSpacing(3)

        # 상단: [라벨 stretch] [고정 우측 블록: − 숫자/max +]
        top = QHBoxLayout(); top.setSpacing(0)

        lbl = QLabel(label); lbl.setFont(QFont("Noto Sans KR",9,QFont.Weight.Medium))
        lbl.setStyleSheet(f"color:{C['text']};background:transparent;")
        top.addWidget(lbl, 1)

        # ── 고정 너비 우측 블록 — 키나와 동일한 96px ──
        RIGHT_W = 86
        right = QWidget(); right.setFixedWidth(RIGHT_W)
        right.setStyleSheet("background:transparent;")
        rh = QHBoxLayout(right); rh.setContentsMargins(0,0,0,0); rh.setSpacing(4)

        # − 버튼
        btn_minus = QPushButton("−"); btn_minus.setFixedSize(22,22)
        btn_minus.setStyleSheet(self._btn_style())
        btn_minus.clicked.connect(lambda _, f=field, mv=max_val: self._adjust_ode(f, mv, -5))
        rh.addWidget(btn_minus)

        # 숫자 라벨 + 편집용 QLineEdit (겹침 컨테이너)
        NUM_W = 38
        num_stack = QWidget(); num_stack.setFixedSize(NUM_W, 22)
        num_stack.setStyleSheet("background:transparent;")

        val_lbl = QLabel("0"); val_lbl.setFont(QFont("Rajdhani",11,QFont.Weight.Bold))
        val_lbl.setGeometry(0,0,NUM_W,22); val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_lbl.setStyleSheet(f"color:{color};background:transparent;"
                              f"border-bottom:1px solid {color}33;")
        val_lbl.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        val_lbl.setParent(num_stack)

        val_edit = QLineEdit("0"); val_edit.setFixedSize(NUM_W,22)
        val_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_edit.setFont(QFont("Rajdhani",11,QFont.Weight.Bold))
        val_edit.setStyleSheet(f"""
            QLineEdit{{color:{color};background:{C['surface2']};
                border:1px solid {C['border2']};border-radius:3px;
                font-family:'Rajdhani';font-size:11px;padding:0;}}
            QLineEdit:focus{{border:1px solid {C['border2']};outline:0;}}
        """)
        val_edit.setParent(num_stack); val_edit.hide()

        def start_edit(e, f=field, mv=max_val, lbl=val_lbl, edit=val_edit):
            edit.setText(str(self._od().get(f, 0)))
            lbl.hide(); edit.show(); edit.setFocus(); edit.selectAll()
        def commit_edit(f=field, mv=max_val, lbl=val_lbl, edit=val_edit):
            try: v2 = max(0, min(mv, int(edit.text())))
            except ValueError: v2 = self._od().get(f, 0)
            self._od()[f] = v2; edit.hide(); lbl.show()
            self.refresh(); self.changed.emit()

        val_lbl.mousePressEvent = start_edit
        val_edit.returnPressed.connect(commit_edit)
        val_edit.editingFinished.connect(commit_edit)
        rh.addWidget(num_stack)

        # + 버튼
        btn_plus = QPushButton("+"); btn_plus.setFixedSize(22,22)
        btn_plus.setStyleSheet(self._btn_style())
        btn_plus.clicked.connect(lambda _, f=field, mv=max_val: self._adjust_ode(f, mv, +5))
        rh.addWidget(btn_plus)

        top.addWidget(right)
        v.addLayout(top)

        # 슬라이더
        slider = QSlider(Qt.Orientation.Horizontal); slider.setRange(0, max_val)
        slider.setSingleStep(5); slider.setPageStep(5)
        slider.setFixedHeight(16)
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal{{height:4px;background:{C['surface2']};border-radius:2px;}}
            QSlider::handle:horizontal{{background:{color};width:12px;height:12px;
                border-radius:6px;margin:-4px 0;}}
            QSlider::sub-page:horizontal{{background:{color};border-radius:2px;}}
        """)
        slider.valueChanged.connect(lambda val, f=field, mv=max_val: self._set_ode(f, mv, round(val/5)*5))
        v.addWidget(slider)

        setattr(self, f"_val_{field}",    val_lbl)
        setattr(self, f"_edit_{field}",   val_edit)
        setattr(self, f"_slider_{field}", slider)
        setattr(self, f"_max_{field}",    max_val)
        return w

    def _btn_style(self):
        return f"""QPushButton{{color:{C['text_muted']};background:{C['surface2']};
            border:1px solid {C['border']};border-radius:4px;font-size:14px;padding:0;}}
            QPushButton:hover{{color:{C['text']};border-color:{C['border2']};}}"""

    def _set_ode(self, field, max_val, val):
        """슬라이더 드래그로 직접 세팅"""
        od = self._od(); od[field] = max(0, min(max_val, val))
        # 라벨만 업데이트 (슬라이더 시그널 루프 방지)
        getattr(self, f"_val_{field}").setText(str(od[field]))
        self.changed.emit()

    def _adjust_ode(self, field, max_val, delta):
        od = self._od(); cur = od.get(field, 0)
        od[field] = max(0, min(max_val, cur + delta))
        self.refresh(); self.changed.emit()

    def _tick(self):
        if apply_charges(self.state):
            self.refresh(); self.changed.emit()

    def _upd_timer_labels(self):
        now = datetime.now()
        self._ode_timer_lbl.setText(_next_charge_str(now, ODE_SCHEDULE))
        self._ode_sched.update_now(now)

    def refresh(self):
        od = self._od()
        for field, max_val in [("base", ODE_MAX), ("extra", ODE_EXTRA_MAX)]:
            v = od.get(field, 0)
            # 라벨 (편집 중이 아닐 때만)
            edit = getattr(self, f"_edit_{field}")
            if not edit.isVisible():
                getattr(self, f"_val_{field}").setText(str(v))
            # 슬라이더 (시그널 차단 후 세팅)
            sl = getattr(self, f"_slider_{field}")
            sl.blockSignals(True); sl.setValue(v); sl.blockSignals(False)
        self._upd_timer_labels()



def _next_charge_str(now, schedule):
    cur_min = now.hour * 60 + now.minute
    nxt = next((h for h in schedule if h * 60 > cur_min), schedule[0] + 24)
    diff_sec = (nxt * 60 - cur_min) * 60 - now.second
    h = diff_sec // 3600; m = (diff_sec % 3600) // 60; s = diff_sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


class _OdeScheduleBar(QWidget):
    def __init__(self): super().__init__(); self._now = datetime.now(); self.setFixedHeight(10)
    def update_now(self, now): self._now = now; self.update()
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width(); h = self.height()
        n = len(ODE_SCHEDULE)
        slot_w = w / n
        cur_min = self._now.hour * 60 + self._now.minute
        for i, hour in enumerate(ODE_SCHEDULE):
            done   = hour * 60 <= cur_min
            is_next= (ODE_SCHEDULE[i] == next((x for x in ODE_SCHEDULE if x*60 > cur_min), None))
            x  = int(i * slot_w) + 1
            bw = int(slot_w) - 2
            bh = h - 4 if is_next else h - 6
            by = (h - bh) // 2
            color = "#4dbd74" if done else ("rgba(77,189,116,0.5)" if is_next else C["border2"])
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(color))
            p.drawRoundedRect(x, by, bw, bh, 2, 2)
        p.end()


# INPUT DIALOG  (프레임리스 텍스트 입력)
# ─────────────────────────────────────────────
class _InputDialog(QDialog):
    def __init__(self, title_text, placeholder="", prefill="", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self._build(title_text, placeholder, prefill)

    def paintEvent(self, e):
        _paint_rounded_window(self)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        _apply_rounded_mask(self)

    def _build(self, title_text, placeholder, prefill):
        v = QVBoxLayout(self); v.setContentsMargins(20, 18, 20, 16); v.setSpacing(10)

        tl = QLabel(title_text); tl.setFont(QFont("Noto Sans KR", 11, QFont.Weight.Medium))
        tl.setStyleSheet(f"color:{C['text']};background:transparent;"); v.addWidget(tl)

        self._edit = QLineEdit(prefill)
        self._edit.setPlaceholderText(placeholder)
        self._edit.setFixedHeight(32)
        self._edit.setStyleSheet(f"""
            QLineEdit{{background:{C['surface2']};color:{C['text']};border:1px solid {C['border2']};
                border-radius:5px;padding:4px 10px;font-family:'Noto Sans KR';font-size:11px;}}
            QLineEdit:focus{{border-color:{C['accent']};}}
        """)
        self._edit.returnPressed.connect(self._ok)
        v.addWidget(self._edit)

        br = QHBoxLayout(); br.setSpacing(8); br.addStretch()
        cancel = QPushButton("취소"); cancel.setFixedSize(72, 30)
        cancel.setStyleSheet(f"""QPushButton{{background:{C['surface2']};color:{C['text_dim']};
            border:1px solid {C['border']};border-radius:5px;font-family:'Noto Sans KR';font-size:10px;}}
            QPushButton:hover{{border-color:{C['border2']};color:{C['text']};}}""")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("확인"); ok.setFixedSize(72, 30)
        ok.setStyleSheet(f"""QPushButton{{background:{C['accent']};color:#fff;border:none;
            border-radius:5px;font-family:'Noto Sans KR';font-size:10px;}}
            QPushButton:hover{{background:#6aaaff;}}""")
        ok.clicked.connect(self._ok)
        br.addWidget(cancel); br.addWidget(ok); v.addLayout(br)

        self.adjustSize()
        if self.parent():
            pp = self.parent().geometry()
            self.move(pp.center() - self.rect().center())
        self._edit.setFocus()

    def _ok(self): self.accept()

    def value(self): return self._edit.text().strip()

    @staticmethod
    def get_text(parent, title, placeholder="", prefill=""):
        dlg = _InputDialog(title, placeholder, prefill, parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.value(), True
        return "", False

# ─────────────────────────────────────────────
# CONFIRM DIALOG  (삭제 확인용 커스텀 다이얼로그)
# ─────────────────────────────────────────────
class _ConfirmDialog(QDialog):
    def __init__(self, title_text, body_text="", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self._build(title_text, body_text)

    def paintEvent(self, e):
        _paint_rounded_window(self)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        _apply_rounded_mask(self)

    def _build(self, title_text, body_text):
        v = QVBoxLayout(self); v.setContentsMargins(22, 20, 22, 18); v.setSpacing(10)

        tl = QLabel(title_text); tl.setFont(QFont("Noto Sans KR", 12, QFont.Weight.Medium))
        tl.setStyleSheet(f"color:{C['text']};background:transparent;"); tl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(tl)

        if body_text:
            bl = QLabel(body_text); bl.setFont(QFont("Noto Sans KR", 9))
            bl.setStyleSheet(f"color:{C['text_muted']};background:transparent;")
            bl.setAlignment(Qt.AlignmentFlag.AlignCenter); bl.setWordWrap(True); v.addWidget(bl)

        v.addSpacing(4)
        br = QHBoxLayout(); br.setSpacing(8); br.addStretch()
        cancel = QPushButton("취소"); cancel.setFixedSize(80, 32)
        cancel.setStyleSheet(f"""
            QPushButton{{background:{C['surface2']};color:{C['text_dim']};border:1px solid {C['border']};
                border-radius:5px;font-family:'Noto Sans KR';font-size:11px;}}
            QPushButton:hover{{border-color:{C['border2']};color:{C['text']};}}
        """)
        cancel.clicked.connect(self.reject)
        confirm = QPushButton("삭제"); confirm.setFixedSize(80, 32)
        confirm.setStyleSheet(f"""
            QPushButton{{background:{C['red_dim']};color:{C['red']};border:1px solid {C['red']}55;
                border-radius:5px;font-family:'Noto Sans KR';font-size:11px;}}
            QPushButton:hover{{background:{C['red']}33;border-color:{C['red']};}}
        """)
        confirm.clicked.connect(self.accept)
        br.addWidget(cancel); br.addWidget(confirm); br.addStretch()
        v.addLayout(br)
        self.adjustSize()
        if self.parent():
            pp = self.parent().geometry()
            self.move(pp.center() - self.rect().center())

# ─────────────────────────────────────────────
# MANAGER WINDOW
# ─────────────────────────────────────────────
def _parse_char_input(raw):
    """'닉네임[서버명]' → (nickname, server) or (raw, '')"""
    raw = raw.strip()
    if raw.endswith("]") and "[" in raw:
        idx = raw.rfind("[")
        nick = raw[:idx].strip()
        srv  = raw[idx+1:-1].strip()
        return nick, srv
    return raw, ""

# ─────────────────────────────────────────────
# SUMMARY WINDOW  (요약뷰 별도 창 — 메인 우측 snap)
# ─────────────────────────────────────────────
class _SummaryWindow(QWidget):
    closed = pyqtSignal()
    char_selected = pyqtSignal(str)

    RADIUS = 10

    def __init__(self, state, active_char, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._state = state

        rl = QVBoxLayout(self)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        # 요약뷰
        self._sv = _SummaryView(state, active_char)
        self._sv.char_selected.connect(self.char_selected)

        # 헤더 높이
        self._header_h = self._sv.HDR1_H + self._sv.HDR2_H

        # 스크롤 영역 — _sv 전체(헤더+바디)를 담되,
        # 레이아웃 상단 마진을 헤더 높이만큼 줘서 헤더 영역은 스크롤 밖에 위치하게 함
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(False)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{ border:none; background:transparent; }}
            QScrollBar:vertical {{ width:4px; background:transparent; }}
            QScrollBar::handle:vertical {{ background:{C['border2']}; border-radius:2px; }}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {{ height:0; }}
        """)
        self._scroll.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._scroll.viewport().setStyleSheet("border:none; background:transparent;")
        self._scroll.setWidget(self._sv)

        # 레이아웃 상단 마진 = 헤더 높이
        # → 헤더는 paintEvent에서 창 상단 고정으로 그리고,
        #   스크롤 영역은 그 아래부터 배치
        rl.setContentsMargins(0, self._header_h, 0, 0)
        rl.addWidget(self._scroll)

        # 창 너비 = 내용 너비에 맞춤
        self.setFixedWidth(self._sv._total_w())




    def paintEvent(self, e):
        from PyQt6.QtGui import QPainterPath
        _paint_rounded_window(self, radius=self.RADIUS)

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(0.5, 0.5, self.width() - 1, self.height() - 1, self.RADIUS, self.RADIUS)
        p.setClipPath(clip)

        W        = self.width()
        hdr_h    = self._header_h   # HDR1_H + HDR2_H

        # ── 고정 헤더 배경 (창 상단에 항상 고정) ──
        p.fillRect(0, 0, W, hdr_h, QColor(C["surface"]))

        # ── 헤더 내용 그리기 (_sv 좌표계와 동일하므로 translate 불필요) ──
        self._sv._paint_header(p)

        p.end()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        _apply_rounded_mask(self, self.RADIUS)

    def snap_height(self, h):
        """메인 창 높이에 맞춰 스크롤 영역 높이를 동기화."""
        # 전체 창 높이 = 헤더 고정 영역 + 스크롤 영역
        self._scroll.setFixedHeight(h - self._header_h)
        self.setFixedHeight(h)
        _apply_rounded_mask(self, self.RADIUS)

    def refresh(self, state, active_char):
        self._state = state
        self._sv.refresh(state, active_char)
        # 캐릭터/컨텐츠 변경 시 너비 재계산
        self.setFixedWidth(self._sv._total_w())

    def closeEvent(self, e): self.closed.emit(); super().closeEvent(e)

class ManagerWindow(QWidget):
    state_changed = pyqtSignal()

    def __init__(self, state):
        super().__init__()
        self.state = state
        self._drag_pos = None
        # Frameless + stays on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(453, 416)
        self.resize(453, 416)
        self.setStyleSheet(f"""
            QWidget{{background:transparent;color:{C['text']};font-family:'Noto Sans KR';}}
            QTabWidget::pane{{border:1px solid {C['border']};border-radius:0 6px 6px 6px;background:{C['bg']};}}
            QTabBar::tab{{background:{C['surface']};color:{C['text_muted']};border:1px solid {C['border']};
                border-bottom:none;padding:6px 18px;font-family:'Noto Sans KR';font-size:11px;
                border-radius:4px 4px 0 0;margin-right:2px;}}
            QTabBar::tab:selected{{background:{C['surface2']};color:{C['text']};border-bottom:2px solid {C['accent']};}}
            QScrollBar:vertical{{background:transparent;width:5px;}}
            QScrollBar::handle:vertical{{background:{C['border']};border-radius:2px;min-height:20px;}}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
        """)
        self._build()

    def paintEvent(self, e):
        _paint_rounded_window(self)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        _apply_rounded_mask(self)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and e.position().y() < 36:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)
    def mouseReleaseEvent(self, e): self._drag_pos = None

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        # ── 타이틀바 ──
        bar = _RoundedCard(self, bg=C["surface"], border=None, radius=10, bottom_corners=False)
        bar.setFixedHeight(36)
        bh = QHBoxLayout(bar); bh.setContentsMargins(12, 0, 10, 0); bh.setSpacing(6)
        tl = QLabel("OdeFrame  —  관리"); tl.setFont(QFont("Rajdhani", 11, QFont.Weight.Bold))
        tl.setStyleSheet(f"color:{C['text']};letter-spacing:1.5px;background:transparent;"); bh.addWidget(tl, 1)
        xb = QPushButton("✕"); xb.setFixedSize(20, 18)
        xb.setStyleSheet(f"QPushButton{{color:{C['text_muted']};background:none;border:none;font-size:11px;}}"
                         f"QPushButton:hover{{color:{C['red']};}}")
        xb.clicked.connect(self.close); bh.addWidget(xb)
        root.addWidget(bar)

        # ── 구분선 + 탭 ──
        body = QWidget(); body.setStyleSheet(f"background:{C['bg']};")
        bv = QVBoxLayout(body); bv.setContentsMargins(10, 10, 10, 10); bv.setSpacing(0)
        tabs = QTabWidget()
        tabs.addTab(self._char_tab(),    "캐릭터 관리")
        tabs.addTab(self._content_tab(), "컨텐츠 설정")
        bv.addWidget(tabs, 1)
        root.addWidget(body, 1)

    # ── 캐릭터 탭 ──
    def _char_tab(self):
        w = QWidget(); w.setStyleSheet(f"background:{C['bg']};")
        v = QVBoxLayout(w); v.setContentsMargins(10,10,10,10); v.setSpacing(8)

        hint = QLabel("⠿ 핸들 드래그로 순서 변경  ·  ex) 닉네임[서버명]")
        hint.setStyleSheet(f"color:{C['text_muted']};font-size:10px;background:transparent;")
        v.addWidget(hint)

        # ── 커스텀 드래그 리스트 컨테이너 ──
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea{{background:{C['surface']};border:1px solid {C['border']};border-radius:6px;}}
            QScrollBar:vertical{{background:transparent;width:4px;}}
            QScrollBar::handle:vertical{{background:{C['border2']};border-radius:2px;min-height:16px;}}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
        """)
        self._char_container = _CharDragContainer(self.state, self)
        self._char_container.order_changed.connect(self._on_order_changed)
        scroll.setWidget(self._char_container)
        v.addWidget(scroll, 1)

        # ── 하단 + 버튼 ──
        add_row = QHBoxLayout(); add_row.addStretch()
        add_btn = QPushButton("＋  캐릭터 추가"); add_btn.setFixedSize(140, 30)
        add_btn.setStyleSheet(f"""
            QPushButton{{background:{C['accent_dim']};color:{C['accent']};border:1px solid {C['accent']}44;
                border-radius:5px;font-family:'Noto Sans KR';font-size:10px;}}
            QPushButton:hover{{background:{C['accent']}33;border-color:{C['accent']};}}
        """)
        add_btn.clicked.connect(self._add_char)
        add_row.addWidget(add_btn); add_row.addStretch()
        v.addLayout(add_row)

        self._refresh_clist()
        return w

    def _refresh_clist(self):
        self._char_container.rebuild(self.state)

    def _on_order_changed(self, new_order):
        self.state["chars"] = new_order
        save_state(self.state)
        self._char_container.rebuild(self.state)
        self.state_changed.emit()

    # ── 인라인 편집 ──
    def _inline_edit(self, old_key):
        old_srv = self.state.get("servers", {}).get(old_key, "")
        prefill = f"{old_key}[{old_srv}]" if old_srv else old_key
        raw, ok = _InputDialog.get_text(
            self, "캐릭터 편집", placeholder="ex) 닉네임[서버명]", prefill=prefill)
        if not ok: return
        if not raw:
            self._del_char(old_key, silent=True); return
        nick, srv = _parse_char_input(raw)
        if not nick: return
        if nick != old_key and nick in self.state["chars"]:
            QMessageBox.warning(self, "오류", "이미 있는 닉네임입니다."); return
        if nick != old_key:
            idx = self.state["chars"].index(old_key)
            self.state["chars"][idx] = nick
            self.state["checks"][nick] = self.state["checks"].pop(old_key)
            self.state.get("servers", {}).pop(old_key, None)
        self.state.setdefault("servers", {})[nick] = srv
        save_state(self.state); self._refresh_clist(); self.state_changed.emit()

    # ── 추가 ──
    def _add_char(self):
        raw, ok = _InputDialog.get_text(self, "캐릭터 추가", placeholder="ex) 닉네임[서버명]")
        if not ok or not raw: return
        nick, srv = _parse_char_input(raw)
        if not nick: return
        if nick in self.state["chars"]:
            QMessageBox.warning(self, "오류", "이미 있는 닉네임입니다."); return
        self.state["chars"].append(nick)
        self.state["checks"][nick] = {}
        self.state.setdefault("servers", {})[nick] = srv
        save_state(self.state); self._refresh_clist(); self.state_changed.emit()

    # ── 삭제 ──
    def _del_char(self, char_key, silent=False):
        if len(self.state["chars"]) <= 1:
            QMessageBox.warning(self, "오류", "마지막 캐릭터는 삭제할 수 없습니다."); return
        if not silent:
            srv     = self.state.get("servers", {}).get(char_key, "")
            display = f"{char_key}[{srv}]" if srv else char_key
            dlg = _ConfirmDialog(f"[{display}] 삭제",
                                 "삭제하면 해당 캐릭터의\n모든 체크 기록도 사라집니다.",
                                 parent=self)
            if not dlg.exec(): return
        self.state["chars"].remove(char_key)
        self.state["checks"].pop(char_key, None)
        self.state.get("servers", {}).pop(char_key, None)
        save_state(self.state); self._refresh_clist(); self.state_changed.emit()


    # ── 컨텐츠 탭 ──
    def _content_tab(self):
        w = QWidget(); w.setStyleSheet(f"background:{C['bg']};")
        v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(6)

        hint = QLabel("⠿ 핸들 드래그로 같은 초기화 타입 내 순서 변경")
        hint.setStyleSheet(f"color:{C['text_muted']};font-size:9px;background:transparent;")
        v.addWidget(hint)

        # ── 2열 레이아웃: 좌(일간+회랑) | 우(주간) ──
        cols = QHBoxLayout(); cols.setSpacing(8)

        def _make_section(reset_type):
            """섹션 헤더 + 드래그 컨테이너."""
            col = QWidget(); col.setStyleSheet("background:transparent;")
            cv = QVBoxLayout(col); cv.setContentsMargins(0,0,0,0); cv.setSpacing(4)
            color = RESET_COLOR[reset_type]
            label = RESET_LABEL[reset_type]
            # 헤더
            hdr = QHBoxLayout(); hdr.setSpacing(5)
            dot = QLabel("●"); dot.setFixedWidth(12)
            dot.setStyleSheet(f"color:{color};font-size:8px;background:transparent;")
            hdr.addWidget(dot)
            tl = QLabel(label); tl.setFont(QFont("Noto Sans KR", 9, QFont.Weight.Medium))
            tl.setStyleSheet(f"color:{color};background:transparent;")
            hdr.addWidget(tl)
            ln = QFrame(); ln.setFrameShape(QFrame.Shape.HLine)
            ln.setStyleSheet(f"color:{color};"); hdr.addWidget(ln, 1)
            cv.addLayout(hdr)
            # 드래그 컨테이너
            scroll = QScrollArea(); scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setStyleSheet(f"""
                QScrollArea{{background:{C['surface']};border:1px solid {C['border']};border-radius:5px;}}
                QScrollBar:vertical{{width:3px;background:transparent;}}
                QScrollBar::handle:vertical{{background:{C['border2']};border-radius:2px;}}
                QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
            """)
            container = _TaskDragContainer(self.state, reset_type, self)
            container.order_changed.connect(self._on_task_reorder)
            scroll.setWidget(container)
            cv.addWidget(scroll, 1)
            return col, container

        left_col = QWidget(); left_col.setStyleSheet("background:transparent;")
        lv = QVBoxLayout(left_col); lv.setContentsMargins(0,0,0,0); lv.setSpacing(8)
        daily_col,    self._task_cont_daily    = _make_section("daily")
        corridor_col, self._task_cont_corridor = _make_section("corridor")
        lv.addWidget(daily_col, 1)
        lv.addWidget(corridor_col, 1)

        # 우측: 주간 + 성역 + 지령서 통합 컨테이너
        right_col = QWidget(); right_col.setStyleSheet("background:transparent;")
        rv = QVBoxLayout(right_col); rv.setContentsMargins(0,0,0,0); rv.setSpacing(4)
        # 헤더
        hdr = QHBoxLayout(); hdr.setSpacing(5)
        dot_r = QLabel("●"); dot_r.setFixedWidth(12)
        dot_r.setStyleSheet(f"color:{C['gold']};font-size:8px;background:transparent;")
        hdr.addWidget(dot_r)
        tl_r = QLabel("주간 / 성역 / 지령서"); tl_r.setFont(QFont("Noto Sans KR", 9, QFont.Weight.Medium))
        tl_r.setStyleSheet(f"color:{C['gold']};background:transparent;")
        hdr.addWidget(tl_r)
        ln_r = QFrame(); ln_r.setFrameShape(QFrame.Shape.HLine)
        ln_r.setStyleSheet(f"color:{C['gold']};"); hdr.addWidget(ln_r, 1)
        rv.addLayout(hdr)
        scroll_r = QScrollArea(); scroll_r.setWidgetResizable(True)
        scroll_r.setFrameShape(QFrame.Shape.NoFrame)
        scroll_r.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_r.setStyleSheet(f"""
            QScrollArea{{background:{C['surface']};border:1px solid {C['border']};border-radius:5px;}}
            QScrollBar:vertical{{width:3px;background:transparent;}}
            QScrollBar::handle:vertical{{background:{C['border2']};border-radius:2px;}}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
        """)
        self._task_cont_weekly = _TaskDragContainer(
            self.state, "weekly",
            self, group_types=["sanctuary", "directive"])
        self._task_cont_weekly.order_changed.connect(self._on_task_reorder)
        scroll_r.setWidget(self._task_cont_weekly)
        rv.addWidget(scroll_r, 1)

        cols.addWidget(left_col, 1); cols.addWidget(right_col, 1)
        v.addLayout(cols, 1)
        return w

    def _refresh_content_tab(self):
        for attr in ("_task_cont_daily", "_task_cont_corridor", "_task_cont_weekly"):
            if hasattr(self, attr):
                getattr(self, attr).rebuild(self.state)

    def _on_task_reorder(self):
        save_state(self.state)
        self.state_changed.emit()

    def _add_task(self, reset_type): pass
    def _edit_task(self, task): pass
    def _del_task(self, tid): pass
    def _make_task_row(self, task, color): pass


class UpdateManager:
    @staticmethod
    def get_now():
        return datetime.now()

    @staticmethod
    def should_reset_daily(last_reset_str):
        try:
            last_reset = datetime.fromisoformat(last_reset_str)
            now = UpdateManager.get_now()
            today_5am = now.replace(hour=5, minute=0, second=0, microsecond=0)
            if now < today_5am:
                today_5am -= timedelta(days=1)
            return last_reset < today_5am
        except: return True

    @staticmethod
    def should_reset_weekly(last_reset_str):
        try:
            last_reset = datetime.fromisoformat(last_reset_str)
            now = UpdateManager.get_now()
            days_since_wed = (now.weekday() - 2) % 7
            last_wed_5am = (now - timedelta(days=days_since_wed)).replace(hour=5, minute=0, second=0, microsecond=0)
            if now < last_wed_5am:
                last_wed_5am -= timedelta(weeks=1)
            return last_reset < last_wed_5am
        except: return True


# ─────────────────────────────────────────────
# MAIN OVERLAY
# ─────────────────────────────────────────────
class Overlay(QWidget):
    _hotkey_signal = pyqtSignal()   # 전역 단축키 → 메인 스레드로 안전하게 전달
    _ode_sync_result_signal = pyqtSignal(str, object)
    _sync_hotkey_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowIcon(_app_icon())
        self.state = load_state()
        self.active_char = self.state["chars"][0]
        self.active_server = None
        self._drag_pos = None
        self._manager = None
        self._hotkey_seq = None
        self._sync_hotkey_seq = None
        self._hk_hook = None
        self._sync_hk_hook = None
        self._global_hotkeys_active = False
        self._hotkey_str = ""
        self._sync_hotkey_str = ""
        self._last_hk_time = 0
        self._last_sync_hk_time = 0
        self._hotkey_signal.connect(self._toggle_visibility)
        self._ode_sync_result_signal.connect(self._apply_ode_result)
        self._sync_hotkey_signal.connect(self._sync_ode_from_hotkey)

        # UI 구성 (타이머 로직 실행 전 필수)
        self._setup_window()
        self._build_ui()

        # 통합 로직 초기 실행 및 타이머 설정
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_all_logic)
        self.refresh_timer.start(60000) 
        self.update_all_logic()
        
        # OCR 로직
        # self._ode_ocr = OdeOCRService()
        
        # 렌더링 및 기타 타이머 시작
        self._render_chars()
        self._render_tasks()
        self._start_timers()
        self._apply_cfg()
        QTimer.singleShot(200, self._poll_game_window)

    # ── Window ──
    def _setup_window(self):
        flags = (Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(285)
        self.adjustSize()
        px,py=self.state.get("overlay_pos",[None,None])
        if px is not None: self.move(int(px),int(py))
        else:
            scr=QApplication.primaryScreen().geometry()
            self.move(scr.width()-324,20)

    def _apply_cfg(self):
        opacity = self.state.get("opacity", 100) / 100
        self.setWindowOpacity(opacity)
        if self._summary_win:
            self._summary_win.setWindowOpacity(opacity)
        self._hotkey_str = self.state.get("hotkey", "Ctrl+Shift+H")
        self._hotkey_seq = QKeySequence(self._hotkey_str)
        self._sync_hotkey_str = self.state.get("sync_hotkey", "Ctrl+R")
        self._sync_hotkey_seq = QKeySequence(self._sync_hotkey_str)
        self._set_global_hotkeys_active(getattr(self, "_global_hotkeys_active", False))

    def _set_global_hotkeys_active(self, active):
        active = bool(active)
        if active == getattr(self, "_global_hotkeys_active", False):
            return
        self._global_hotkeys_active = active
        if active:
            self._setup_global_hotkey()
        else:
            for attr in ("_hk_hook", "_sync_hk_hook"):
                hook = getattr(self, attr, None)
                if hook:
                    try:
                        import keyboard as _kb
                        _kb.remove_hotkey(hook)
                    except Exception:
                        pass
                    setattr(self, attr, None)

    def _setup_global_hotkey(self):
        """게임 감지 중일 때만 keyboard 훅 기반 전역 단축키 등록."""
        if not getattr(self, "_global_hotkeys_active", False):
            return

        # 기존 훅 해제
        for attr in ("_hk_hook", "_sync_hk_hook"):
            hook = getattr(self, attr, None)
            if hook:
                try:
                    import keyboard as _kb
                    _kb.remove_hotkey(hook)
                except Exception:
                    pass
                setattr(self, attr, None)
        try:
            import keyboard as _kb
            # QKeySequence 문자열 → keyboard 모듈 포맷 변환
            hk = self._hotkey_str.lower().replace("ctrl","ctrl").replace("shift","shift").replace("alt","alt")
            self._hk_hook = _kb.add_hotkey(hk, self._on_global_hotkey)
            sync_hk = self._sync_hotkey_str.lower().replace("ctrl","ctrl").replace("shift","shift").replace("alt","alt")
            self._sync_hk_hook = _kb.add_hotkey(sync_hk, self._on_sync_hotkey)
        except Exception:
            self._hk_hook = None
            self._sync_hk_hook = None   # keyboard 미설치 시 기존 keyPressEvent만 사용

    def _on_global_hotkey(self):
        """keyboard 스레드 → Qt 메인 스레드로 시그널 전달. 반복 방지."""
        import time
        now = time.monotonic()
        if now - getattr(self, "_last_hk_time", 0) < 0.15:
            return   # 400ms 내 재호출 무시
        self._last_hk_time = now
        self._hotkey_signal.emit()

    def _on_sync_hotkey(self):
        """keyboard 스레드 → OCR 동기화 시그널 전달."""
        import time
        now = time.monotonic()
        if now - getattr(self, "_last_sync_hk_time", 0) < 0.15:
            return
        self._last_sync_hk_time = now
        self._sync_hotkey_signal.emit()

    @pyqtSlot()
    def _sync_ode_from_hotkey(self):
        if getattr(self, "_btn_sync_ode", None) and not self._btn_sync_ode.isEnabled():
            return
        self._sync_ode_from_game()
   
    @pyqtSlot()
    @pyqtSlot()
    def _toggle_visibility(self):
        """단축키 → 최소화 토글."""
        self._toggle_minimize()

    # ── UI ──
    def _build_ui(self):
        self.card = _RoundedCard(self, bg=C["bg"], border=C["border"], radius=10)
        self.card.setObjectName("card")
        rl=QVBoxLayout(self); rl.setContentsMargins(0,0,0,0); rl.addWidget(self.card)

        # 카드 가로 분리: 좌측(메인)만 — 체크리스트는 별도 창
        card_h = QHBoxLayout(self.card); card_h.setContentsMargins(0,0,0,0); card_h.setSpacing(0)

        # 좌측 메인
        self._left_widget = QWidget(); self._left_widget.setStyleSheet("background:transparent;")
        self._left_widget.setFixedWidth(285)
        self._vb = QVBoxLayout(self._left_widget); self._vb.setContentsMargins(0,0,0,0); self._vb.setSpacing(0)
        card_h.addWidget(self._left_widget)

        # 탑바
        self._build_topbar()

        # 콘텐츠 위젯
        self._content_widget = QWidget(); self._content_widget.setStyleSheet("background:transparent;")
        self._cvb = QVBoxLayout(self._content_widget)
        self._cvb.setContentsMargins(0,0,0,0); self._cvb.setSpacing(0)
        self._vb.addWidget(self._content_widget)

        # 상태 초기화
        self._summary_win = None   # 요약 창
        self._ui_mode = "A"

        self._build_char_row()
        self._build_content_area()

    def _build_topbar(self):
        self._bar = _RoundedCard(self._left_widget, bg=C["surface"], border=None, radius=10, bottom_corners=False)
        self._bar.setFixedSize(285, 38)
        bar = self._bar
        h=QHBoxLayout(bar); h.setContentsMargins(8,0,10,0); h.setSpacing(8)

        # 앱 아이콘
        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(22, 22)
        _icon_path = _resource_path("odeframe_icon.png")
        if os.path.exists(_icon_path):
            from PyQt6.QtGui import QPixmap
            self._icon_lbl.setPixmap(
                QPixmap(_icon_path).scaled(
                    22, 22,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
            self._icon_lbl.setStyleSheet("background:transparent; border:none;")
        else:
            self._icon_lbl.setStyleSheet(f"""
                background:{C['surface2']};border:1px solid {C['border2']};
                border-radius:4px;
            """)
        h.addWidget(self._icon_lbl)

        self._tl=QLabel("OdeFrame"); self._tl.setFont(QFont("Rajdhani",11,QFont.Weight.Bold))
        self._tl.setStyleSheet(f"color:{C['text']};letter-spacing:2px;"); h.addWidget(self._tl)

        # ── 미니모드 라벨: 레이아웃 밖, bar 기준 절대 위치 ──
        # 미니모드 아이콘 (기본창과 동일)
        self._mini_icon_lbl = QLabel("", bar)
        self._mini_icon_lbl.setFixedSize(22, 22)
        self._mini_icon_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._mini_icon_lbl.setGeometry(8, 8, 22, 22)
        _icon_path2 = _resource_path("odeframe_icon.png")
        if os.path.exists(_icon_path2):
            from PyQt6.QtGui import QPixmap
            self._mini_icon_lbl.setPixmap(
                QPixmap(_icon_path2).scaled(
                    22, 22,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
            self._mini_icon_lbl.setStyleSheet("background:transparent; border:none;")
        else:
            self._mini_icon_lbl.setStyleSheet(f"background:{C['surface2']};border:1px solid {C['border2']};border-radius:4px;")
        self._mini_icon_lbl.hide()

        self._mini_char_lbl = QLabel("", bar)
        self._mini_char_lbl.setFont(QFont("Noto Sans KR", 9, QFont.Weight.Bold))
        self._mini_char_lbl.setStyleSheet(f"color:{C['text']};background:transparent;")
        self._mini_char_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._mini_char_lbl.setGeometry(36, 0, 107, 38)  # 아이콘(22) + 간격(6) = x:36
        self._mini_char_lbl.hide()

        self._mini_ode_lbl = QLabel("", bar)
        self._mini_ode_lbl.setFont(QFont("Rajdhani", 10, QFont.Weight.Bold))
        self._mini_ode_lbl.setStyleSheet(f"color:#4dbd74;background:transparent;")
        self._mini_ode_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._mini_ode_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._mini_ode_lbl.setGeometry(143, 0, 44, 38)
        self._mini_ode_lbl.hide()

        # ── 버튼 3개: bar 기준 절대 위치 고정 ──
        def _mk_btn(text, x):
            b = QPushButton(text, bar)
            b.setFixedSize(26, 20)
            b.move(x, 9)
            b.setStyleSheet(_sbtn(C["accent"]) + "QPushButton{padding:0;}")
            return b

        # 최소화 버튼
        self._btn_minimize = _mk_btn("−", 249)
        self._btn_minimize.clicked.connect(self._toggle_minimize)

        # 오드 동기화 버튼
        self._btn_sync_ode = _mk_btn("↻", 219)
        self._btn_sync_ode.setToolTip("게임 오드값 OCR 동기화")
        self._btn_sync_ode.clicked.connect(self._sync_ode_from_game)

        # 확장 버튼
        self._btn_expand = _mk_btn("▷", 189)
        self._btn_expand.setStyleSheet(
            _sbtn(C["accent"]) + "QPushButton{padding:0;font-size:11px;}"
        )
        self._btn_expand.clicked.connect(self._toggle_summary)

        # ── 설정·관리 버튼 (우클릭 메뉴용) ──
        self._btn_settings = QPushButton(); self._btn_settings.setVisible(False)
        self._btn_settings.clicked.connect(self._open_settings)
        self._btn_manager = QPushButton(); self._btn_manager.setVisible(False)
        self._btn_manager.clicked.connect(self._open_manager)
        bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        bar.customContextMenuRequested.connect(self._show_topbar_menu)

        self._topbar_h = 38   # 드래그 판별용 탑바 높이
        self._vb.addWidget(bar)

    # ── 모드 전환 ──
    MODE_LEFT_W = 285

    def _toggle_summary(self):
        if self._summary_win and self._summary_win.isVisible():
            self._summary_win.close()
        else:
            self._open_summary_win()
        self._upd_mode_btns()

    def _open_summary_win(self):
        if self._summary_win:
            try: self._summary_win.close()
            except: pass
        self._summary_win = _SummaryWindow(self.state, self.active_char)
        self._summary_win.char_selected.connect(self._on_summary_char_select)
        self._summary_win.closed.connect(self._on_summary_win_closed)
        self._summary_win._sv.check_toggled.connect(self._on_summary_toggle)
        # show() 전에 위치/높이를 미리 지정 — OS가 show() 시점에 덮어쓰는 것을 방지
        p = self.pos()
        self._summary_win.snap_height(self.height())
        self._summary_win.move(p.x() + self.width() + 4, p.y())
        self._summary_win.show()
        self._summary_win.setWindowOpacity(self.state.get("opacity", 100) / 100)
        # show() 후 OS 재배치에 대비해 한 프레임 뒤에 한 번 더 snap
        QTimer.singleShot(0, self._snap_summary_win)

    def _on_summary_win_closed(self):
        self._summary_win = None
        self._upd_mode_btns()

    def _snap_summary_win(self):
        """요약창을 메인 창 우측에 snap, 높이를 메인 창에 맞춤."""
        if not self._summary_win:
            return
        p = self.pos()
        target_x = p.x() + self.width() + 4
        target_y = p.y()
        # 높이 먼저 고정
        self._summary_win.snap_height(self.height())
        # 높이 변경 후 OS가 위치를 재조정할 수 있으므로 move를 두 번 호출
        self._summary_win.move(target_x, target_y)
        QTimer.singleShot(0, lambda: self._summary_win.move(target_x, target_y) if self._summary_win else None)

    def _apply_layout(self): pass

    def _adj_height(self):
        self.setMinimumHeight(0); self.setMaximumHeight(16777215)
        self._left_widget.setMinimumHeight(0); self._left_widget.setMaximumHeight(16777215)
        self._content_widget.updateGeometry()
        self._left_widget.updateGeometry()
        self.updateGeometry(); self.adjustSize()
        QTimer.singleShot(10, self._snap_summary_win)

    def _upd_mode_btns(self):
        smr_on = bool(self._summary_win and self._summary_win.isVisible())
        self._btn_expand.setText("◁" if smr_on else "▷")
        if smr_on:
            self._btn_expand.setStyleSheet(_sbtn(C["gold"]) + "QPushButton{padding:0;font-size:11px;}")
        else:
            self._btn_expand.setStyleSheet(_sbtn(C["accent"]) + "QPushButton{padding:0;font-size:11px;}")

    def _build_char_row(self):
        self._crow = QWidget(); self._crow.setFixedHeight(36)
        self._crow.setStyleSheet(f"border-bottom:1px solid {C['border']};")
        self._ch = QHBoxLayout(self._crow)
        self._ch.setContentsMargins(6, 0, 6, 0); self._ch.setSpacing(6)

        # 서버 드롭다운
        self._srv_combo = QComboBox()
        self._srv_combo.setFixedSize(75, 24)
        self._srv_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._srv_combo.setFont(QFont("Noto Sans KR", 10))
        self._srv_combo.setStyleSheet(self._combo_style(C["gold"]))
        self._srv_combo.currentIndexChanged.connect(self._on_srv_combo_changed)
        self._ch.addWidget(self._srv_combo)

        # 구분선
        self._sep = QFrame(); self._sep.setFrameShape(QFrame.Shape.VLine)
        self._sep.setStyleSheet(f"color:{C['border2']};"); self._sep.setFixedWidth(1)
        self._ch.addWidget(self._sep)

        # 캐릭터 드롭다운
        self._char_combo = QComboBox()
        self._char_combo.setFixedHeight(24)
        self._char_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._char_combo.setFont(QFont("Noto Sans KR", 10))
        self._char_combo.setStyleSheet(self._combo_style(C["accent"]))
        self._char_combo.currentIndexChanged.connect(self._on_char_combo_changed)
        self._ch.addWidget(self._char_combo, 1)

        self._cvb.addWidget(self._crow)

    def _combo_style(self, color):
        return f"""
            QComboBox {{
                color:{color}; background:{C['surface2']};
                border:1px solid {C['border2']}; border-radius:5px;
                padding:0 20px 0 8px;
                font-family:'Noto Sans KR'; font-size:10px;
            }}
            QComboBox:hover {{ border-color:{color}88; }}
            QComboBox::drop-down {{
                subcontrol-origin:padding; subcontrol-position:right center;
                width:18px; border:none; background:transparent;
            }}
            QComboBox::down-arrow {{
                image:none;
                width:0; height:0;
            }}
            QComboBox QAbstractItemView {{
                background:{C['surface2']}; color:{C['text']};
                border:1px solid {C['border2']};
                selection-background-color:{color}22;
                font-family:'Noto Sans KR'; font-size:10px; padding:2px;
                outline:0;
            }}
        """

    def _render_chars(self):
        # ── 서버 목록 추출 ──
        seen = []; servers = []
        for c in self.state["chars"]:
            srv = self.state.get("servers", {}).get(c, "")
            if srv and srv not in seen:
                seen.append(srv); servers.append(srv)

        # ── 서버 드롭다운 갱신 ──
        self._srv_combo.blockSignals(True)
        self._srv_combo.clear()
        if servers:
            for s in servers:
                self._srv_combo.addItem(s, s)
            # active_server가 None(전체)이면 첫 서버로 초기화
            if self.active_server is None:
                self.active_server = servers[0]
            idx = 0
            for i in range(self._srv_combo.count()):
                if self._srv_combo.itemData(i) == self.active_server:
                    idx = i; break
            self._srv_combo.setCurrentIndex(idx)
            self._srv_combo.setVisible(True)
            self._sep.setVisible(True)
        else:
            self._srv_combo.setVisible(False)
            self._sep.setVisible(False)
        self._srv_combo.blockSignals(False)

        # ── 캐릭터 드롭다운 갱신 ──
        visible_chars = [
            c for c in self.state["chars"]
            if self.active_server is None or
               self.state.get("servers", {}).get(c, "") == self.active_server
        ]
        if visible_chars and self.active_char not in visible_chars:
            self.active_char = visible_chars[0]

        self._char_combo.blockSignals(True)
        self._char_combo.clear()
        for c in visible_chars:
            self._char_combo.addItem(c, c)
        # active_char 반영
        for i in range(self._char_combo.count()):
            if self._char_combo.itemData(i) == self.active_char:
                self._char_combo.setCurrentIndex(i); break
        self._char_combo.blockSignals(False)

    def _on_srv_combo_changed(self, idx):
        self.active_server = self._srv_combo.itemData(idx)
        self._render_chars()
        self._render_tasks()

    def _on_char_combo_changed(self, idx):
        key = self._char_combo.itemData(idx)
        if key and key != self.active_char:
            self.active_char = key
            self._render_tasks()

    def _build_content_area(self):
        # 현재 페이지 크기만 반환하는 커스텀 스택
        class _SizedStack(QStackedWidget):
            def sizeHint(self):
                w = self.currentWidget()
                return w.sizeHint() if w else super().sizeHint()
            def minimumSizeHint(self):
                w = self.currentWidget()
                return w.minimumSizeHint() if w else super().minimumSizeHint()

        self._stack = _SizedStack()
        self._stack.setStyleSheet("background:transparent;")
        self._stack.currentChanged.connect(lambda _: self._stack.updateGeometry())

        # 페이지 0: 키나 획득률 + 오드 에너지
        self._page0 = QWidget(); self._page0.setStyleSheet("background:transparent;")
        p0v = QVBoxLayout(self._page0)
        p0v.setContentsMargins(0,2,0,2); p0v.setSpacing(0)
        self._p0v = p0v
        self._stack.addWidget(self._page0)

        # 페이지 1: 컨텐츠 체크리스트
        self._page1 = QWidget(); self._page1.setStyleSheet("background:transparent;")
        self._cvb1 = QVBoxLayout(self._page1)
        self._cvb1.setContentsMargins(0,2,0,2); self._cvb1.setSpacing(0)
        self._stack.addWidget(self._page1)

        self._cvb.addWidget(self._stack, 0)
        self._page_idx = 0




    def _render_tasks(self):
        # ── 페이지 0: 키나 획득률 + 오드 에너지 ──
        while self._p0v.count():
            it = self._p0v.takeAt(0)
            if it.widget(): it.widget().deleteLater()

        srv = self.state.get("servers", {}).get(self.active_char, "") or "공통"
        self._kina_panel = KinaPanel(self.state, srv, self)
        self._kina_panel.changed.connect(lambda: save_state(self.state))
        self._p0v.addWidget(self._kina_panel)

        div = QFrame(); div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color:{C['border']};margin:0 8px;")
        self._p0v.addWidget(div)

        self._ode_panel = OdePanel(self.state, self.active_char)
        self._ode_panel.changed.connect(lambda: save_state(self.state))
        self._p0v.addWidget(self._ode_panel)

        # ── 페이지 1: 컨텐츠 체크리스트 ──
        while self._cvb1.count():
            it = self._cvb1.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        checks = self.state["checks"].get(self.active_char, {})
        tasks  = self.state.get("tasks", [])
        grp_info = {
            "daily":     ("일간",  RESET_COLOR["daily"]),
            "corridor":  ("회랑",  RESET_COLOR["corridor"]),
            "directive": ("지령서",RESET_COLOR["directive"]),
            "weekly":    ("주간",  RESET_COLOR["weekly"]),
            "sanctuary": ("성역",  RESET_COLOR["sanctuary"]),
        }
        has_tasks = False
        for rt in RT_ORDER:
            rt_tasks = [t for t in tasks if t["reset"] == rt]
            if not rt_tasks: continue
            has_tasks = True
            label, color = grp_info.get(rt, (rt, C["text_dim"]))
            sl = QLabel(label.upper()); sl.setFont(QFont("Noto Sans KR",8,QFont.Weight.Medium))
            sl.setStyleSheet(f"color:{color};letter-spacing:1.5px;padding:7px 14px 3px;")
            self._cvb1.addWidget(sl)
            for t in rt_tasks:
                row = CheckRow(t, checks.get(t["id"], False))
                row.toggled.connect(self._on_toggle); self._cvb1.addWidget(row)
        if not has_tasks:
            empty = QLabel("등록된 컨텐츠 없음")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"color:{C['text_muted']};font-size:9px;padding:20px 0;")
            self._cvb1.addWidget(empty)

        def _adj_and_log():
            if self._ui_mode in ("A", "B", "S"):
                self.setMinimumHeight(0)
                self.setMaximumHeight(16777215)
                self._left_widget.setMinimumHeight(0)
                self._left_widget.setMaximumHeight(16777215)
                self._content_widget.updateGeometry()
                self._left_widget.updateGeometry()
                self.updateGeometry()
                self.adjustSize()
        QTimer.singleShot(0, _adj_and_log)

    def _on_summary_char_select(self, char):
        """요약뷰 캐릭터 클릭 → 해당 캐릭터+서버 선택."""
        self.active_char = char
        self.active_server = self.state.get("servers", {}).get(char, "") or None
        self._render_chars()
        self._render_tasks()
        # 요약창도 갱신
        if self._summary_win:
            self._summary_win.refresh(self.state, self.active_char)

    def _on_summary_toggle(self, char, tid):
        save_state(self.state)
        if char == self.active_char:
            self._render_tasks()

    # ── Actions ──
    def _on_toggle(self, tid):
        sender = self.sender()
        d = self.state["checks"].setdefault(self.active_char, {})
        if hasattr(sender, 'count'):
            d[tid] = sender.count
        else:
            d[tid] = not d.get(tid, False)
        save_state(self.state)


    def _find_game_hwnd(self):
        """Aion2.exe HWND 탐색. 캐시 우선, 없으면 직접 탐색."""
        cached = getattr(self, "_game_hwnd", None)
        if cached:
            return cached
        try:
            info = _find_aion2_window_info()
            if info["hwnd"]:
                self._game_hwnd = info["hwnd"]
                return info["hwnd"]
        except Exception:
            pass
        return None

    def _sync_ode_from_game(self):
        """탑바 ↻ 버튼 → OCR로 오드값 읽어 현재 캐릭터에 반영."""
        btn = self._btn_sync_ode
        btn.setEnabled(False)
        btn.setText("…")

        # 클릭 시점 캐릭터 + HWND 고정
        char = self.active_char
        hwnd = self._find_game_hwnd()

        if not hwnd:
            btn.setText("✕")
            QTimer.singleShot(1500, lambda: btn.setText("↻"))
            btn.setEnabled(True)
            return

        def _run():
            result = capture_ode_from_game(hwnd)
            self._ode_sync_result_signal.emit(char, result)

        threading.Thread(target=_run, daemon=True).start()

    @pyqtSlot(str, object)
    def _apply_ode_result(self, char, result):
        """OCR 결과를 state에 반영하고 UI 갱신. 메인 스레드에서 실행."""
        btn = self._btn_sync_ode
        parsed = _normalize_ode_result(result)
        _ocr_log(f"UI 반영 수신 — char={char}, raw={result}, parsed={parsed}")
        if parsed:
            base, extra, _ = parsed
            od = self.state.setdefault("ode", {}).setdefault(char, {
                "base": 0, "extra": 0, "recorded_at": None, "memo": ""
            })
            od["base"]  = max(0, min(ODE_MAX,       base))
            od["extra"] = max(0, min(ODE_EXTRA_MAX, extra))
            od["recorded_at"] = int(datetime.now().timestamp() * 1000)
            _ocr_log(f"상태 반영 완료 — char={char}, base={od['base']}, extra={od['extra']}")
            save_state(self.state)
            # OdePanel 갱신
            if hasattr(self, "_ode_panel") and self._ode_panel:
                self._ode_panel.char_key = self.active_char
                self._ode_panel.refresh()
            # 미니모드 라벨 갱신
            if getattr(self, "_is_mini", False):
                self._upd_mini_labels()
            # 요약창 갱신
            if self._summary_win and self._summary_win.isVisible():
                self._summary_win.refresh(self.state, self.active_char)
            btn.setText("↻")
        else:
            # 실패: ✕ 잠깐 표시 후 복구
            _ocr_log(f"UI 반영 실패 — unexpected result: {result}")
            btn.setText("✕")
            QTimer.singleShot(1500, lambda: btn.setText("↻"))

        btn.setEnabled(True)

    def _toggle_minimize(self):
        self._is_mini = not getattr(self, "_is_mini", False)
        vis = not self._is_mini
        for w in [self._crow]:
            w.setVisible(vis)
        if not vis:
            self._srv_combo.setVisible(False)
        else:
            self._render_chars()

        # 아이콘 + 타이틀: 미니모드 시 숨김
        self._icon_lbl.setVisible(vis)
        self._tl.setVisible(vis)

        # 탑바 버튼: 최소화 시 숨김
        for btn in [self._btn_expand]:
            btn.setVisible(vis)

        # 콘텐츠 숨김/표시
        self._content_widget.setVisible(vis)
        if not vis:
            # 최소화 시 부속 창들도 숨김
            if self._summary_win and self._summary_win.isVisible():
                self._summary_win.hide()
        else:
            # 복원 시 부속 창들도 다시 표시
            if self._summary_win:
                self._summary_win.show()
                self._snap_summary_win()

        # 미니모드 라벨
        self._mini_icon_lbl.setVisible(not vis)
        self._mini_char_lbl.setVisible(not vis)
        self._mini_ode_lbl.setVisible(not vis)
        if not vis:
            self._upd_mini_labels()

        self._btn_minimize.setText("+" if not vis else "−")
        # 최소화 시 탑바 단독 표시 → 하단도 라운딩
        self._bar._bottom = not vis
        self._bar.update()

        if vis:
            self.setMaximumSize(16777215, 16777215)
            self._left_widget.setFixedWidth(self.MODE_LEFT_W)
            QTimer.singleShot(0, self._adj_height)
            self._upd_mode_btns()
        else:
            self.setMaximumSize(16777215, 16777215)
            self._left_widget.setFixedWidth(self.MODE_LEFT_W)
            self.setFixedWidth(self.MODE_LEFT_W)
            self.setFixedHeight(38)
        if not vis:  # 최소화 전환 시점에 1회 즉시 감지
            self._poll_game_window()

    def _upd_mini_labels(self):
        """미니모드 캐릭터명 + 기본 오드 에너지 갱신."""
        char = self.active_char
        self._mini_char_lbl.setText(char)
        od   = self.state.get("ode", {}).get(char, {})
        base = od.get("base", 0)
        self._mini_ode_lbl.setText(f"⚡{base}")

    def _show_topbar_menu(self, pos):
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background:{C['surface2']}; color:{C['text']};
                border:1px solid {C['border2']}; border-radius:6px;
                padding:3px; font-family:'Noto Sans KR'; font-size:10px;
            }}
            QMenu::item {{
                padding:5px 14px 5px 10px;
                border-radius:4px; min-width:90px;
            }}
            QMenu::item:selected {{
                background:{C['accent_dim']}; color:{C['accent']};
            }}
            QMenu::separator {{
                height: 1px; background: {C['border']}; margin: 3px 8px;
            }}
        """)
        act_settings = menu.addAction("설정")
        act_manager  = menu.addAction("관리창")
        menu.addSeparator()
        act_quit     = menu.addAction("종료")
        act = menu.exec(self.mapToGlobal(pos))
        if act == act_settings: self._open_settings()
        elif act == act_manager: self._open_manager()
        elif act == act_quit:    QApplication.quit()

    def _open_settings(self):
        dlg=SettingsDialog(self.state,self)
        dlg.applied.connect(self._on_cfg)
        def _live_opacity(v):
            f = v / 100
            self.setWindowOpacity(f)
            if self._summary_win: self._summary_win.setWindowOpacity(f)
        dlg.live_opacity.connect(_live_opacity)
        dlg.exec()

    def _on_cfg(self, cfg):
        self.state.update(cfg); save_state(self.state)
        flags = (Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.Tool |
                 Qt.WindowType.WindowStaysOnTopHint)
        pos=self.pos(); self.setWindowFlags(flags); self.move(pos); self.show()
        opacity = cfg["opacity"] / 100
        self.setWindowOpacity(opacity)
        if self._summary_win:
            self._summary_win.setWindowOpacity(opacity)
        self._hotkey_str = cfg["hotkey"]
        self._hotkey_seq = QKeySequence(cfg["hotkey"])
        self._sync_hotkey_str = cfg.get("sync_hotkey", "Ctrl+R")
        self._sync_hotkey_seq = QKeySequence(self._sync_hotkey_str)
        self._set_global_hotkeys_active(getattr(self, "_global_hotkeys_active", False))

    def _open_manager(self):
        if self._manager and not self._manager.isHidden(): self._manager.raise_(); return
        self._manager=ManagerWindow(self.state); self._manager.state_changed.connect(self._on_state_ch); self._manager.show()

    def _on_state_ch(self):
        if self.active_char not in self.state["chars"]: self.active_char=self.state["chars"][0]
        self._render_chars(); self._render_tasks()

    # ── Drag ──
    def _drag_start(self,e):
        if e.button()==Qt.MouseButton.LeftButton:
            self._drag_pos=e.globalPosition().toPoint()-self.frameGeometry().topLeft()
    def _drag_move(self,e):
        if self._drag_pos and e.buttons()==Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint()-self._drag_pos)
    def _drag_end(self,e):
        if self._drag_pos:
            p=self.pos(); self.state["overlay_pos"]=[p.x(),p.y()]; save_state(self.state)
        self._drag_pos=None

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._apply_card_mask()
        self._snap_summary_win()

    def moveEvent(self, e):
        super().moveEvent(e)
        self._snap_summary_win()

    def _snap_summary_win(self):
        """요약창을 메인 창 바로 아래, 좌측 정렬."""
        if self._summary_win and self._summary_win.isVisible():
            p = self.pos()
            self._summary_win.move(p.x() + self.width() + 4, p.y())

    def _apply_card_mask(self):
        pass  # _RoundedCard handles painting directly; no mask needed

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            y = e.position().y(); x = e.position().x()
            in_topbar_y = y <= self._topbar_h
            in_topbar_x = x <= 285   # 탑바는 항상 285px 너비
            if in_topbar_y and in_topbar_x:
                self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)
    def mouseReleaseEvent(self, e):
        if self._drag_pos:
            p = self.pos(); self.state["overlay_pos"] = [p.x(), p.y()]; save_state(self.state)
        self._drag_pos = None

    # ── Timers ──
    def _start_timers(self):
        # 게임 창 타이틀 폴링 (3초마다)
        self._poll_tmr = QTimer(); self._poll_tmr.timeout.connect(self._poll_game_window)
        self._poll_tmr.start(3000)

    def _poll_game_window(self):
        """Aion2.exe 창에서 캐릭터명을 감지해 현재 캐릭터를 자동 선택."""
        try:
            info = _find_aion2_window_info()
        except Exception:
            self._set_global_hotkeys_active(False)
            return   # 예외 → 조용히 무시

        self._set_global_hotkeys_active(bool(info["hwnd"]))

        if info["hwnd"]:
            self._game_hwnd = info["hwnd"]

        char_name = info["char_name"]
        if not char_name:
            return   # 파싱 실패 → 조용히 무시

        # ── 캐릭터 목록 대조 ──
        chars = self.state.get("chars", [])
        if char_name not in chars:
            return   # 등록된 캐릭터 아님 → 무시

        if char_name == self.active_char:
            return   # 이미 선택됨

        # ── 자동 선택 ──
        self.active_char = char_name
        srv = self.state.get("servers", {}).get(char_name, "")
        if srv and srv != self.active_server:
            self.active_server = srv
        self._render_chars()
        self._render_tasks()
        # if self._is_mini:
        self._upd_mini_labels()
        # 요약창이 열려있으면 해당 캐릭터로 갱신
        if self._summary_win:
            self._summary_win.refresh(self.state, self.active_char)
    def update_all_logic(self):
        """1분마다 실행되는 통합 로직: 자동 초기화, 오드 충전, 라벨 갱신 등"""
        changed = check_auto_reset(self.state)
        if apply_charges(self.state): 
            changed = True
        
        if changed: 
            save_state(self.state)
            self._render_tasks()
            if self._summary_win and self._summary_win.isVisible():
                self._summary_win.refresh(self.state, self.active_char)

        # 미니모드일 경우 라벨 갱신
        if getattr(self, "_is_mini", False):
            self._upd_mini_labels()
        
        # 오드/키나 패널 갱신 (열려있을 때만)
        if hasattr(self, "_ode_panel") and self._ode_panel:
            self._ode_panel.refresh()
        if hasattr(self, "_kina_panel") and self._kina_panel:
            self._kina_panel.refresh()

    # ── Hotkey ──
    def _toggle_visibility(self):
        self._toggle_minimize()

    def keyPressEvent(self,e):
        if e.isAutoRepeat(): return
        # 전역 훅이 살아있으면 keyPressEvent로는 처리하지 않음 (이중 발화 방지)
        if self._hk_hook or self._sync_hk_hook: return super().keyPressEvent(e)
        ks=QKeySequence(e.key() | e.modifiers().value)
        if self._hotkey_seq and ks==self._hotkey_seq:
            self._toggle_visibility(); return
        if self._sync_hotkey_seq and ks==self._sync_hotkey_seq:
            self._sync_ode_from_hotkey(); return
        super().keyPressEvent(e)

    def paintEvent(self,e):
        p=QPainter(self); p.fillRect(self.rect(),QColor(0,0,0,0)); p.end()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        _apply_rounded_mask(self)

    def _update_mask(self):
        _apply_rounded_mask(self)

    def closeEvent(self, e):
        self._set_global_hotkeys_active(False)
        super().closeEvent(e)

# ─────────────────────────────────────────────
# ENTRY
# ─────────────────────────────────────────────
if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setApplicationName("OdeFrame")
    app.setWindowIcon(_app_icon())
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(f"""
        QToolTip {{
            background:{C['surface2']}; color:{C['text']};
            border:1px solid {C['border2']}; border-radius:4px;
            padding:3px 7px; font-family:'Noto Sans KR'; font-size:9px;
        }}
    """)
    for _fp in [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "C:/Windows/Fonts/malgun.ttf",
    ]:
        if os.path.exists(_fp):
            QFontDatabase.addApplicationFont(_fp)
            break
    overlay=Overlay()
    overlay.show()
    sys.exit(app.exec())
