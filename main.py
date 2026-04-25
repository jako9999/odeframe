"""
AION2 컨텐츠 트래커 오버레이
- 게임 최상단 오버레이
- 설정창 (단축키 · 투명도 · 최상단 고정)
- 전체화면 관리창 (캐릭터 · 서버 · 컨텐츠 숨김)
- 자동 초기화 (일간 05:00 / 주간 수요 05:00 / 회랑 수토 22:00)
"""





import sys, json, os, re
from datetime import datetime, timedelta
import threading
import base64

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QInputDialog,
    QMessageBox, QSlider, QCheckBox, QLineEdit, QDialog,
    QTabWidget, QSizePolicy,
    QListWidget, QListWidgetItem, QMenu,
)
from PyQt6.QtCore import Qt, QPoint, QTimer, QSize, pyqtSignal, pyqtSlot, QPointF, QEvent
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QFontDatabase,
    QLinearGradient, QCursor, QKeySequence, QPolygonF, QIcon, QFontMetrics,
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
UI_SCALE_PRESETS = [
    ("작게", 100),
    ("보통", 125),
    ("크게", 150),
]
UI_SCALE_FONT_FACTORS = {
    100: 1.00,
    125: 1.15,
    150: 1.30,
}

def _clamp_ui_scale(value):
    try:
        value = int(value)
    except Exception:
        value = 100
    preset_values = [v for _, v in UI_SCALE_PRESETS]
    return min(preset_values, key=lambda preset: abs(preset - value))

def _ui_scale_factor(state_or_value):
    if isinstance(state_or_value, dict):
        value = state_or_value.get("ui_scale", 100)
    else:
        value = state_or_value
    return _clamp_ui_scale(value) / 100.0

def _scaled(value, scale):
    return max(1, int(round(value * scale)))

def _scaled_font_size(base_size, scale):
    if not base_size or base_size <= 0:
        return base_size
    preset = _clamp_ui_scale(int(round(scale * 100)))
    target = float(base_size) * UI_SCALE_FONT_FACTORS.get(preset, 1.0)
    return max(1.0, round(target * 2) / 2.0)

def _ui_scale_label(value):
    value = _clamp_ui_scale(value)
    for label, preset in UI_SCALE_PRESETS:
        if preset == value:
            return label
    return "작게"

def _apply_layout_scale(layout, scale):
    if layout is None:
        return
    base_spacing = layout.property("_base_spacing")
    if base_spacing is None:
        base_spacing = layout.spacing()
        layout.setProperty("_base_spacing", base_spacing)
    if isinstance(base_spacing, int) and base_spacing >= 0:
        layout.setSpacing(_scaled(base_spacing, scale))

    base_margins = layout.property("_base_margins")
    if base_margins is None:
        base_margins = list(layout.getContentsMargins())
        layout.setProperty("_base_margins", base_margins)
    if base_margins:
        layout.setContentsMargins(*[_scaled(v, scale) for v in base_margins])

def _scale_stylesheet_text(text, scale):
    if not text:
        return text

    prop_pattern = re.compile(
        r'(?P<prefix>(?:^|[;{])\s*)(?P<prop>font-size|padding(?:-[a-z]+)?|margin(?:-[a-z]+)?|border-radius|letter-spacing|(?:min-|max-)?width|(?:min-|max-)?height)\s*:\s*(?P<value>[^;]+);',
        re.IGNORECASE | re.MULTILINE
    )
    num_pattern = re.compile(r'(-?\d+(?:\.\d+)?)\s*(px|pt)?', re.IGNORECASE)

    def _scale_value(match):
        value_text = match.group("value")

        def _scale_num(num_match):
            raw = float(num_match.group(1))
            unit = num_match.group(2) or ""
            if raw == 0:
                scaled = 0
            elif raw < 0:
                scaled = raw
            else:
                scaled = _scaled(raw, scale) if raw >= 1 else raw
            if isinstance(scaled, float) and scaled.is_integer():
                scaled = int(scaled)
            return f"{scaled}{unit}"

        scaled_value = num_pattern.sub(_scale_num, value_text)
        return f"{match.group('prefix')}{match.group('prop')}: {scaled_value};"

    return prop_pattern.sub(_scale_value, text)

def _apply_stylesheet_scale(widget, scale):
    current = widget.styleSheet()
    if not current:
        return
    base = widget.property("_base_stylesheet")
    last_scaled = widget.property("_last_scaled_stylesheet")
    if base is None or (current != last_scaled and current != base):
        base = current
        widget.setProperty("_base_stylesheet", base)
    scaled = _scale_stylesheet_text(base, scale)
    if scaled != current:
        widget.setStyleSheet(scaled)
    widget.setProperty("_last_scaled_stylesheet", scaled)

def _apply_widget_scale(root, scale, *, scale_width=True, width_scale=None):
    eff_width_scale = width_scale if width_scale is not None else scale
    widgets = [root] + root.findChildren(QWidget)
    for widget in widgets:
        _apply_stylesheet_scale(widget, scale)
        font = widget.font()
        if font is not None:
            base_font = widget.property("_base_font_size")
            if base_font is None:
                base_font = font.pointSizeF()
                if base_font > 0:
                    widget.setProperty("_base_font_size", base_font)
            try:
                base_font_value = float(base_font)
            except (TypeError, ValueError):
                base_font_value = -1.0
            if base_font_value > 0:
                font.setPointSizeF(_scaled_font_size(base_font_value, scale))
                widget.setFont(font)

        max_w = widget.maximumWidth()
        min_w = widget.minimumWidth()
        if scale_width and 0 < max_w < 16777215 and max_w == min_w:
            base_w = widget.property("_base_fixed_w")
            if base_w is None:
                base_w = max_w
                widget.setProperty("_base_fixed_w", base_w)
            widget.setFixedWidth(_scaled(int(base_w), eff_width_scale))

        max_h = widget.maximumHeight()
        min_h = widget.minimumHeight()
        if 0 < max_h < 16777215 and max_h == min_h:
            base_h = widget.property("_base_fixed_h")
            if base_h is None:
                base_h = max_h
                widget.setProperty("_base_fixed_h", base_h)
            widget.setFixedHeight(_scaled(int(base_h), scale))

        _apply_layout_scale(widget.layout(), scale)

def _bind_lineedit_commit_on_focus_out(line_edit, commit_fn):
    def _focus_out(event):
        commit_fn()
        QLineEdit.focusOutEvent(line_edit, event)
    line_edit.focusOutEvent = _focus_out

def _bind_lineedit_escape(line_edit, escape_fn):
    def _key_press(event):
        if event.key() == Qt.Key.Key_Escape:
            escape_fn()
            event.accept()
            return
        QLineEdit.keyPressEvent(line_edit, event)
    line_edit.keyPressEvent = _key_press

class _OverlayStack(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._overlay_children = []
        self.setStyleSheet("background:transparent;")

    def add_overlay_child(self, child):
        child.setParent(self)
        self._overlay_children.append(child)
        child.setGeometry(self.rect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        for child in self._overlay_children:
            child.setGeometry(rect)

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

def _ocr_debug_annotate(topbar_img, ode_hit=None, plus_hit=None, roi_rect=None):
    if topbar_img is None:
        return None
    from PIL import ImageDraw as _ImageDraw

    annotated = topbar_img.copy()
    draw = _ImageDraw.Draw(annotated)

    def _draw_rect(hit, color):
        if hit is None:
            return
        x, y, w, h, _ = hit
        draw.rectangle((x, y, x + w, y + h), outline=color, width=3)

    _draw_rect(ode_hit, (255, 64, 64))
    _draw_rect(plus_hit, (255, 64, 64))

    if roi_rect is not None:
        x1, y1, x2, y2 = roi_rect
        draw.rectangle((x1, y1, x2, y2), outline=(255, 180, 0), width=2)

    return annotated

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

def _ocr_cleanup_text(text):
    """OCR 결과에서 형식에 맞지 않는 잡문자를 정리한다."""
    if not text:
        return ""
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[^0-9(),+/]", "", text)
    # 정상 형식은 "(+123)"이므로, '(' 바로 뒤에 끼어든 숫자는 제거한다.
    text = re.sub(r"\(\d+\+", "(+", text)
    return text

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
        _ocr_debug_save(topbar, "ocr_debug_topbar.png")

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

        annotated = _ocr_debug_annotate(topbar, ode_hit, plus_hit, (x1, y1, x2, y2))
        _ocr_debug_save(annotated, "ocr_debug_detected.png")

        roi = topbar.crop((x1, y1, x2, y2))
        _ocr_debug_save(roi, "ocr_debug_roi.png")

        processed = _ocr_preprocess(roi)
        if processed is None:
            _ocr_log("전처리 실패 → 종료")
            return None
        _ocr_debug_save(processed, "ocr_debug_processed.png")

        config = r"--psm 7 -c tessedit_char_whitelist=0123456789()+/,"
        raw_text = pytesseract.image_to_string(processed, config=config, lang="eng").strip()
        text = _ocr_cleanup_text(raw_text)
        _ocr_log(f"결과 텍스트: '{raw_text}'")
        if text != raw_text:
            _ocr_log(f"정리 텍스트: '{text}'")

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
CORRIDOR_RESET_WEEKDAYS = (2, 5)  # 수/토
CORRIDOR_RESET_HOUR = 22

DEFAULT_CHAR_TASKS = [
    {"id": "corridor_abyss",     "name": "어비스 회랑",       "reset": "corridor", "max": 1, "short_name": "회랑"},
    {"id": "weekly_akmong",      "name": "악몽",              "reset": "daily",    "max": 14, "short_name": "악몽"},
    {"id": "weekly_awakening",   "name": "각성전",            "reset": "weekly",   "max": 3, "short_name": "각성"},
    {"id": "weekly_abyss_rec",   "name": "심연의 재련",       "reset": "sanctuary","max": 4, "short_name": "심연"},
    {"id": "weekly_erosion",     "name": "침식의 정화소",     "reset": "sanctuary","max": 4, "short_name": "침식"},
]

DEFAULT_SERVER_TASKS = [
    {"id": "server_daily_samyeong",     "name": "사명",          "reset": "daily",  "max": 1,  "short_name": "사명"},
    {"id": "server_daily_dungeon",      "name": "일일던전",      "reset": "weekly", "max": 1,  "short_name": "일던"},
    {"id": "server_material_transform", "name": "물질변환",      "reset": "weekly", "max": 1,  "short_name": "물변"},
    {"id": "server_sandwind_shop",      "name": "산들바람",      "reset": "weekly", "max": 1,  "short_name": "상점"},
    {"id": "server_altcard_order",      "name": "지령서",        "reset": "directive","max": 1, "short_name": "지령서"},
    {"id": "server_abyss_order",        "name": "어비스지령서",  "reset": "directive","max": 1, "short_name": "어비스"},
]

LEGACY_REMOVED_TASK_IDS = {"daily_samyeong", "weekly_raid", "weekly_dungeon", "weekly_ode_shop", "weekly_altcard", "weekly_abyss_order"}

def _task_default_value(task):
    return False if task.get("max", 1) == 1 else 0

def _is_akmong_task(task_or_id):
    if isinstance(task_or_id, dict):
        task_id = task_or_id.get("id")
    else:
        task_id = task_or_id
    return task_id == "weekly_akmong"

def _summary_click_delta(button):
    if button == Qt.MouseButton.LeftButton:
        return -1
    if button == Qt.MouseButton.RightButton:
        return 1
    return 0

def _apply_summary_click_value(current, max_val, button):
    delta = _summary_click_delta(button)
    if delta == 0:
        return current
    if int(max_val or 0) <= 1:
        return delta > 0
    return max(0, min(int(max_val or 0), int(current or 0) + delta))

def _server_name_key(server_name):
    return server_name or "공통"

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
    코너/테두리 책임을 위젯 단위로 고정하기 위해
    코너 4개와 테두리 4변을 각각 제어한다.
    """
    def __init__(self, parent=None, *, bg="#0d0f14", border="#363d52",
                 radius=10, bottom_corners=True, corners=None, border_sides=None):
        super().__init__(parent)
        self._bg     = QColor(bg)
        self._border = QColor(border) if border else None
        self._radius = radius
        if corners is None:
            corners = (True, True, True, True) if bottom_corners else (True, True, False, False)
        self._corners = tuple(bool(v) for v in corners)
        self._border_sides = tuple(bool(v) for v in (border_sides or (True, True, True, True)))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    def set_frame_style(self, *, bg=None, border=None, corners=None, border_sides=None):
        if bg is not None:
            self._bg = QColor(bg) if not isinstance(bg, QColor) else bg
        if border is not None:
            self._border = QColor(border) if border else None
        if corners is not None:
            self._corners = tuple(bool(v) for v in corners)
        if border_sides is not None:
            self._border_sides = tuple(bool(v) for v in border_sides)
        self.update()

    def _make_path(self):
        from PyQt6.QtGui import QPainterPath
        w, h, r = self.width(), self.height(), self._radius
        tl, tr, br, bl = self._corners
        r = max(0.0, min(float(r), max(0.0, min((w - 1) / 2.0, (h - 1) / 2.0))))
        left, top = 0.5, 0.5
        right, bottom = w - 0.5, h - 0.5
        path = QPainterPath()
        path.moveTo(left + (r if tl else 0), top)
        path.lineTo(right - (r if tr else 0), top)
        if tr and r > 0:
            path.arcTo(right - 2 * r, top, 2 * r, 2 * r, 90, -90)
        else:
            path.lineTo(right, top)
        path.lineTo(right, bottom - (r if br else 0))
        if br and r > 0:
            path.arcTo(right - 2 * r, bottom - 2 * r, 2 * r, 2 * r, 0, -90)
        else:
            path.lineTo(right, bottom)
        path.lineTo(left + (r if bl else 0), bottom)
        if bl and r > 0:
            path.arcTo(left, bottom - 2 * r, 2 * r, 2 * r, 270, -90)
        else:
            path.lineTo(left, bottom)
        path.lineTo(left, top + (r if tl else 0))
        if tl and r > 0:
            path.arcTo(left, top, 2 * r, 2 * r, 180, -90)
        else:
            path.lineTo(left, top)
        path.closeSubpath()
        return path

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.update()  # paintEvent 재호출로 안티앨리어싱 경로 갱신

    def paintEvent(self, event):
        path = self._make_path()
        w, h = self.width(), self.height()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(self._bg))
        p.drawPath(path)
        p.end()
        if self._border:
            p2 = QPainter(self)
            p2.setRenderHint(QPainter.RenderHint.Antialiasing)
            p2.setBrush(Qt.BrushStyle.NoBrush)
            p2.setPen(QPen(self._border, 1.0))
            p2.drawPath(path)
            if self._border_sides != (True, True, True, True):
                erase = QPen(self._bg, 2.2)
                p2.setPen(erase)
                left, top = 0.5, 0.5
                right, bottom = w - 0.5, h - 0.5
                top_on, right_on, bottom_on, left_on = self._border_sides
                if not top_on:
                    p2.drawLine(QPointF(left, top), QPointF(right, top))
                if not right_on:
                    p2.drawLine(QPointF(right, top), QPointF(right, bottom))
                if not bottom_on:
                    p2.drawLine(QPointF(left, bottom), QPointF(right, bottom))
                if not left_on:
                    p2.drawLine(QPointF(left, top), QPointF(left, bottom))
            p2.end()

# ─────────────────────────────────────────────
# ODE / KINA CONSTANTS
# ─────────────────────────────────────────────
ODE_SCHEDULE  = [2, 5, 8, 11, 14, 17, 20, 23]   # 매일 이 시각 정각 +15
ODE_AMT       = 15
ODE_MAX       = 840
ODE_EXTRA_MAX = 2000
ODE_COST      = 80
AKMONG_MAX    = 14
AKMONG_DAILY_CHARGE = 2
AKMONG_CHARGE_HOUR = 5


KINA_STEPS = {
    "jeongbok": [
        {"label":"100%","max":63,       "color":"#64dca0"},
        {"label":"80%", "max":77,      "color":"#60c8ff"},
        {"label":"60%", "max":91,      "color":"#ffe566"},
        {"label":"40%", "max":105,      "color":"#ffaa44"},
        {"label":"20%", "max":float("inf"),"color":"#ff6060"},
    ],
    "choweol": [
        {"label":"100%","max":42,       "color":"#64dca0"},
        {"label":"80%", "max":49,       "color":"#60c8ff"},
        {"label":"60%", "max":56,       "color":"#ffe566"},
        {"label":"40%", "max":63,       "color":"#ffaa44"},
        {"label":"20%", "max":float("inf"),"color":"#ff6060"},
    ],
}

def get_kina_tier(kina_id, value):
    steps = KINA_STEPS.get(kina_id, [])
    if not steps or value == 0: return None
    for s in steps:
        if value <= s["max"]: return s
    return steps[-1]

def _ode_default():
    return {
        "base": 0,
        "extra": 0,
        "recorded_at": None,
        "akmong_stock": 0,
        "akmong_recorded_at": None,
        "memo": "",
    }

def _now_ms():
    return int(datetime.now().timestamp() * 1000)

def _clamp_akmong_stock(value):
    try:
        value = int(value)
    except Exception:
        value = 0
    return max(0, min(AKMONG_MAX, value))

def count_daily_charges(from_ms, to_ms, hour):
    if not from_ms or to_ms <= from_ms:
        return 0
    count = 0
    from_dt = datetime.fromtimestamp(from_ms / 1000)
    to_dt = datetime.fromtimestamp(to_ms / 1000)
    cur = from_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end = to_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    while cur <= end:
        t = cur.replace(hour=hour, minute=0, second=0, microsecond=0)
        if from_dt < t <= to_dt:
            count += 1
        cur += timedelta(days=1)
    return count

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
    to_ms = _now_ms()
    changed = False
    ode_data = state.setdefault("ode", {})
    for c in state["chars"]:
        od = ode_data.setdefault(c, _ode_default())
        for k, v in _ode_default().items():
            od.setdefault(k, v)
        from_ode = od.get("recorded_at")
        n_ode    = count_ode_charges(from_ode, to_ms)
        if n_ode > 0:
            od["base"] = min(ODE_MAX, od.get("base", 0) + n_ode * ODE_AMT)
            changed = True
        od["recorded_at"] = to_ms

        from_akmong = od.get("akmong_recorded_at")
        n_akmong = count_daily_charges(from_akmong, to_ms, AKMONG_CHARGE_HOUR)
        if n_akmong > 0:
            od["akmong_stock"] = min(
                AKMONG_MAX,
                _clamp_akmong_stock(od.get("akmong_stock", 0)) + n_akmong * AKMONG_DAILY_CHARGE,
            )
            changed = True
        od["akmong_recorded_at"] = to_ms

        if from_ode is None or from_akmong is None:
            changed = True
    return changed

# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────
def default_state():
    chars = ["캐릭터1","캐릭터2","캐릭터3","캐릭터4"]
    tasks = [dict(t) for t in DEFAULT_CHAR_TASKS]
    server_tasks = [dict(t) for t in DEFAULT_SERVER_TASKS]
    checks = {c: {} for c in chars}
    server_checks = {_server_name_key(""): {t["id"]: _task_default_value(t) for t in server_tasks}}
    # 오드 에너지 (캐릭터별)
    ode = {c: _ode_default() for c in chars}
    # 키나 획득률 (서버별)  {"서버명": {"jeongbok": 0, "choweol": 0}}
    kina = {}
    return {
        "chars":  chars,
        "checks": checks,
        "tasks":  tasks,
        "server_tasks":   server_tasks,
        "server_checks":  server_checks,
        "servers":        {c: "" for c in chars},
        "ode":            ode,
        "kina":           kina,
        "hidden_tasks":   [],
        "daily_reset":    "", "weekly_reset": "", "corridor_reset": "",
        "opacity":        100,
        "ui_scale":       100,
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
            data.setdefault("server_tasks", [])
            data.setdefault("server_checks", {})
            data.setdefault("kina", {})
            data.setdefault("ode", {})
            data.setdefault("sync_hotkey", "Ctrl+R")
            data.setdefault("ui_scale", 100)

            # ── 컨텐츠는 고정 정의를 사용한다. 사용자 편집/정렬 상태는 더 이상 반영하지 않음. ──
            data["hidden_tasks"] = []
            data["tasks"] = [dict(t) for t in DEFAULT_CHAR_TASKS]
            data["server_tasks"] = [dict(t) for t in DEFAULT_SERVER_TASKS]

            # max 필드 없는 기존 task 보정
            id_to_default = {dt["id"]: dt for dt in DEFAULT_CHAR_TASKS}
            for t in data["tasks"]:
                if "max" not in t:
                    t["max"] = id_to_default.get(t["id"], {}).get("max", 1)
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
                        "weekly_awakening": "각성", "weekly_akmong": "악몽",
                        "weekly_abyss_rec": "심연", "weekly_erosion": "침식",
                    }
                    if t.get("id") in sn_map:
                        t["short_name"] = sn_map[t["id"]]
            tasks = data["tasks"]
            server_tasks = data["server_tasks"]
            ode_defaults = _ode_default()
            for c in data["chars"]:
                data["checks"].setdefault(c, {})
                data["servers"].setdefault(c, "")
                data["ode"].setdefault(c, dict(ode_defaults))
                for k, v in ode_defaults.items():
                    data["ode"][c].setdefault(k, v)
                for t in tasks:
                    data["checks"][c].setdefault(t["id"], _task_default_value(t))

                legacy_akmong = data["checks"][c].get("weekly_akmong", None)
                if (
                    legacy_akmong not in (None, False, "")
                    and not data["ode"][c].get("akmong_stock")
                    and not data["ode"][c].get("akmong_recorded_at")
                ):
                    try:
                        legacy_used = int(legacy_akmong)
                    except Exception:
                        legacy_used = 0
                    if legacy_used > 0:
                        data["ode"][c]["akmong_stock"] = max(0, AKMONG_MAX - legacy_used)
                if data["ode"][c].get("akmong_recorded_at") is None:
                    data["ode"][c]["akmong_recorded_at"] = data["ode"][c].get("recorded_at")

                # 레거시 서버 통합 데이터 마이그레이션
                srv = _server_name_key(data["servers"].get(c, ""))
                data["server_checks"].setdefault(srv, {})
                legacy_checks = data["checks"][c]
                legacy_samyeong = legacy_checks.pop("daily_samyeong", None)
                legacy_daily = legacy_checks.pop("weekly_dungeon", None)
                legacy_ode = legacy_checks.pop("weekly_ode_shop", None)
                legacy_alt = legacy_checks.pop("weekly_altcard", None)
                legacy_abyss_order = legacy_checks.pop("weekly_abyss_order", None)
                legacy_checks.pop("weekly_raid", None)

                if legacy_samyeong:
                    data["server_checks"][srv]["server_daily_samyeong"] = True
                if legacy_daily not in (None, False):
                    migrated = int(legacy_daily) if isinstance(legacy_daily, int) else (1 if legacy_daily else 0)
                    if migrated > 0:
                        data["server_checks"][srv]["server_daily_dungeon"] = True
                if legacy_ode:
                    data["server_checks"][srv]["server_material_transform"] = True
                if legacy_alt:
                    data["server_checks"][srv]["server_altcard_order"] = True
                if legacy_abyss_order:
                    data["server_checks"][srv]["server_abyss_order"] = True

            for srv in set(_server_name_key(v) for v in data.get("servers", {}).values()) | {_server_name_key("")}:
                data["server_checks"].setdefault(srv, {})
                for t in server_tasks:
                    if t.get("max", 1) == 1:
                        cur = data["server_checks"][srv].get(t["id"], _task_default_value(t))
                        data["server_checks"][srv][t["id"]] = bool(cur)
                        continue
                    data["server_checks"][srv].setdefault(t["id"], _task_default_value(t))
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
        if d.weekday() in CORRIDOR_RESET_WEEKDAYS:
            t = d.replace(hour=CORRIDOR_RESET_HOUR,minute=0,second=0,microsecond=0)
            if now >= t: return t.strftime("%Y-%m-%d-%H")
    return "never"

def check_auto_reset(state):
    changed = False
    tasks = state.get("tasks", [])
    server_tasks = state.get("server_tasks", [])
    for key_fn, reset_types, state_key in [
        (_key_daily,    {"daily"},                             "daily_reset"),
        (_key_weekly,   {"weekly", "sanctuary", "directive"},  "weekly_reset"),
        (_key_corridor, {"corridor"},                          "corridor_reset"),
    ]:
        k = key_fn()
        if state.get(state_key) != k:
            for c in state["chars"]:
                for t in tasks:
                    if _is_akmong_task(t):
                        continue
                    if t["reset"] in reset_types:
                        state["checks"][c][t["id"]] = _task_default_value(t)
            for srv, srv_data in state.get("server_checks", {}).items():
                for t in server_tasks:
                    if t["reset"] in reset_types:
                        srv_data[t["id"]] = _task_default_value(t)

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
        if isinstance(weekday, (list, tuple, set)):
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

def fmt_cd_compact(target):
    diff = target - datetime.now()
    if diff.total_seconds() <= 0:
        return "곧"
    total_m = int(diff.total_seconds() // 60)
    d = total_m // 1440
    h = (total_m % 1440) // 60
    m = total_m % 60
    if d > 0:
        return f"{d}d {h}h"
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
        self._base_metrics = {
            "HDR1_H": self.HDR1_H,
            "HDR2_H": self.HDR2_H,
            "ROW_H": self.ROW_H,
            "SRV_W": self.SRV_W,
            "CHAR_W": self.CHAR_W,
            "TASK1_W": self.TASK1_W,
            "TASKN_W": self.TASKN_W,
            "PAD": self.PAD,
            "DOT": self.DOT,
        }
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.setMouseTracking(True)
        self._apply_scale_metrics()
        self._recalc()

    def _apply_scale_metrics(self):
        scale = _ui_scale_factor(self._state)
        for name, base in self._base_metrics.items():
            setattr(self, name, _scaled(base, scale))

    def _font(self, family, size, weight=QFont.Weight.Normal):
        font = QFont(family, weight=weight)
        font.setPointSizeF(_scaled_font_size(size, _ui_scale_factor(self._state)))
        return font

    def _tasks(self):
        return [
            t for t in self._state.get("tasks", [])
            if t.get("reset") != "directive"
        ]

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
        self._apply_scale_metrics()
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
            ("회랑", RESET_COLOR["corridor"], fmt_cd(_next_time(CORRIDOR_RESET_HOUR, CORRIDOR_RESET_WEEKDAYS))),
            ("주간", RESET_COLOR["weekly"],   fmt_cd(_next_time(5, 2))),
        ]
        for si, (label, col, cd) in enumerate(TIMERS):
            sy = si * SLOT_H
            # 레이블
            p.setFont(self._font("Noto Sans KR", 7, QFont.Weight.Bold))
            p.setPen(QColor(col))
            p.drawText(self.PAD, sy, 24, SLOT_H, Qt.AlignmentFlag.AlignVCenter, label)
            # 카운트다운
            p.setFont(self._font("Rajdhani", 8))
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
            p.setFont(self._font("Noto Sans KR", 8, QFont.Weight.Bold))
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
            p.setFont(self._font("Noto Sans KR", 8, QFont.Weight.Bold if is_hov else QFont.Weight.Normal))

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

                p.setFont(self._font("Noto Sans KR", 10, QFont.Weight.Bold))
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
                p.setFont(self._font("Noto Sans KR", 8)); p.setPen(QColor(160,128,255,100))
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
                        p.setFont(self._font("Rajdhani", 10))
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
        p.setBrush(Qt.BrushStyle.NoBrush)
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
        button = e.button()
        if button not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton): return
        hit = self._hit(int(e.position().x()), int(e.position().y()))
        if not hit: return
        if hit[0] == "char":
            if button != Qt.MouseButton.LeftButton:
                return
            self.char_selected.emit(hit[1])
        elif hit[0] == "task":
            _, char, ci = hit
            t    = self._tasks()[ci]
            _max = t.get("max", 1)
            cc2  = self._state["checks"].setdefault(char, {})
            raw  = cc2.get(t["id"], 0)
            cnt  = 1 if (raw and _max==1) else (int(raw) if isinstance(raw,int) else 0)
            cc2[t["id"]] = _apply_summary_click_value(cnt, _max, button)
            self.check_toggled.emit(char, t["id"])
            self.update()


class _ServerSummaryView(QWidget):
    check_toggled = pyqtSignal(str, str)

    HDR1_H = 40
    HDR2_H = 0
    ROW_H = 36
    SERVER_W = 90
    TASK_W = 78
    PAD = 6
    BD = (255, 255, 255, 18)
    BDS = (255, 255, 255, 8)

    def __init__(self, state, _active_char=None, parent=None):
        super().__init__(parent)
        self._state = state
        self._hov_row = None
        self._hov_col = None
        self._base_metrics = {
            "HDR1_H": self.HDR1_H,
            "HDR2_H": self.HDR2_H,
            "ROW_H": self.ROW_H,
            "SERVER_W": self.SERVER_W,
            "TASK_W": self.TASK_W,
            "PAD": self.PAD,
        }
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.setMouseTracking(True)
        self._apply_scale_metrics()
        self._recalc()

    def _apply_scale_metrics(self):
        scale = _ui_scale_factor(self._state)
        for name, base in self._base_metrics.items():
            setattr(self, name, _scaled(base, scale))

    def _font(self, family, size, weight=QFont.Weight.Normal):
        font = QFont(family, weight=weight)
        font.setPointSizeF(_scaled_font_size(size, _ui_scale_factor(self._state)))
        return font

    def _tasks(self):
        return list(self._state.get("server_tasks", []))

    def _servers(self):
        order = []
        seen = set()
        for value in self._state.get("servers", {}).values():
            srv = _server_name_key(value)
            if srv not in seen:
                seen.add(srv)
                order.append(srv)
        for srv, data in self._state.get("server_checks", {}).items():
            if srv not in seen and any(bool(v) for v in data.values()):
                seen.add(srv)
                order.append(srv)
        if not order:
            order.append(_server_name_key(""))
        return order

    def _tasks_x(self):
        return [self.SERVER_W + i * self.TASK_W for i, _ in enumerate(self._tasks())]

    def _total_w(self):
        return self.SERVER_W + len(self._tasks()) * self.TASK_W

    def _total_h(self):
        return len(self._servers()) * self.ROW_H

    def _recalc(self):
        self.setFixedSize(self._total_w(), self._total_h())

    def refresh(self, state, _active_char=None):
        self._state = state
        self._apply_scale_metrics()
        self._recalc()
        self.update()

    def _paint_header(self, p):
        W = self._total_w()
        tasks = self._tasks()
        txs = self._tasks_x()
        bd_pen = QPen(QColor(*self.BD), 1)

        p.fillRect(0, 0, W, self.HDR1_H, QColor(C["surface"]))
        timer_label_w = min(_scaled(24, _ui_scale_factor(self._state)), max(18, self.SERVER_W // 3))
        timer_rows = []
        resets = {t.get("reset") for t in tasks}
        if "daily" in resets:
            timer_rows.append(("일간", RESET_COLOR["daily"], fmt_cd(_next_time(5))))
        if resets & {"weekly", "sanctuary", "directive"}:
            timer_rows.append(("주간", RESET_COLOR["weekly"], fmt_cd(_next_time(5, 2))))
        if not timer_rows:
            timer_rows.append(("주간", RESET_COLOR["weekly"], fmt_cd(_next_time(5, 2))))

        slot_h = max(1, self.HDR1_H // len(timer_rows))
        for idx, (label, color, countdown) in enumerate(timer_rows):
            sy = idx * slot_h
            cur_h = self.HDR1_H - sy if idx == len(timer_rows) - 1 else slot_h
            p.setFont(self._font("Noto Sans KR", 7, QFont.Weight.Bold))
            p.setPen(QColor(color))
            p.drawText(self.PAD, sy, timer_label_w, cur_h,
                       Qt.AlignmentFlag.AlignVCenter, label)
            p.setFont(self._font("Rajdhani", 8))
            p.setPen(QColor(255, 255, 255, 160))
            p.drawText(self.PAD + timer_label_w + 2, sy,
                       self.SERVER_W - self.PAD * 2 - timer_label_w - 2, cur_h,
                       Qt.AlignmentFlag.AlignVCenter, countdown)
            if idx < len(timer_rows) - 1:
                p.setPen(bd_pen)
                p.drawLine(0, sy + cur_h, self.SERVER_W, sy + cur_h)

        p.setPen(QPen(QColor(C["gold"]), 1))
        p.drawLine(self.SERVER_W, self.HDR1_H - 1, W, self.HDR1_H - 1)
        p.setPen(bd_pen)
        p.drawLine(self.SERVER_W, 0, self.SERVER_W, self.HDR1_H)

        for i, t in enumerate(tasks):
            if self._hov_col == i:
                p.fillRect(txs[i], 0, self.TASK_W, self.HDR1_H, QColor(130, 90, 255, 24))
            font_size = 8 if len(t["name"]) <= 4 else 7
            p.setFont(self._font("Noto Sans KR", font_size, QFont.Weight.Bold))
            p.setPen(QColor(255, 255, 255, 220) if self._hov_col == i else QColor(RESET_COLOR.get(t.get("reset"), C["text_dim"])))
            p.drawText(txs[i] + 3, 0, self.TASK_W - 6, self.HDR1_H,
                       Qt.AlignmentFlag.AlignCenter, t.get("short_name", t["name"]))
            p.setPen(bd_pen)
            p.drawLine(txs[i], 0, txs[i], self.HDR1_H)

        p.setPen(bd_pen)
        p.drawLine(0, self.HDR1_H, W, self.HDR1_H)

    def paintEvent(self, ev):
        from PyQt6.QtGui import QPainterPath
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        p.setClipPath(clip)
        p.fillRect(self.rect(), QColor(0, 0, 0, 0))

        tasks = self._tasks()
        txs = self._tasks_x()
        W = self.width()
        bd_pen = QPen(QColor(*self.BD), 1)
        y = 0
        for row_idx, srv in enumerate(self._servers()):
            is_hov = self._hov_row == row_idx
            if row_idx % 2 == 0:
                p.fillRect(0, y, W, self.ROW_H, QColor(255, 255, 255, 8))
            if is_hov:
                p.fillRect(0, y, W, self.ROW_H, QColor(130, 90, 255, 16))

            p.setFont(self._font("Noto Sans KR", 10, QFont.Weight.Bold))
            p.setPen(QColor("#ede6ff"))
            p.drawText(self.PAD, y, self.SERVER_W - self.PAD * 2, self.ROW_H,
                       Qt.AlignmentFlag.AlignVCenter, srv)
            p.setPen(bd_pen)
            p.drawLine(self.SERVER_W, y, self.SERVER_W, y + self.ROW_H)

            values = self._state.get("server_checks", {}).get(srv, {})
            for i, t in enumerate(tasks):
                value = values.get(t["id"], _task_default_value(t))
                cell_x = txs[i]
                if t.get("max", 1) == 1:
                    done = bool(value)
                    text = "완료" if done else "미완"
                    p.setFont(self._font("Noto Sans KR", 9, QFont.Weight.Bold if done else QFont.Weight.Normal))
                    p.setPen(QColor(C["gold"] if done else C["text_muted"]))
                    p.drawText(cell_x + 4, y, self.TASK_W - 8, self.ROW_H,
                               Qt.AlignmentFlag.AlignCenter, text)
                else:
                    cnt = int(value or 0)
                    done = cnt >= int(t.get("max", 0) or 0)
                    p.setFont(self._font("Rajdhani", 10, QFont.Weight.Bold))
                    p.setPen(QColor(C["gold"] if done else C["text_muted"]))
                    p.drawText(cell_x, y, self.TASK_W, self.ROW_H,
                               Qt.AlignmentFlag.AlignCenter, f"{cnt}/{t['max']}")
                p.setPen(bd_pen)
                p.drawLine(cell_x, y, cell_x, y + self.ROW_H)

            row_pen = QPen(QColor(*self.BD if row_idx == len(self._servers()) - 1 else self.BDS), 1)
            p.setPen(row_pen)
            p.drawLine(0, y + self.ROW_H - 1, W, y + self.ROW_H - 1)
            y += self.ROW_H

        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(bd_pen)
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        p.end()

    def _hit(self, mx, my):
        if not (0 <= my < self._total_h()):
            return None
        row_idx = my // self.ROW_H
        servers = self._servers()
        if row_idx < 0 or row_idx >= len(servers):
            return None
        if mx < self.SERVER_W:
            return ("server", servers[row_idx], row_idx)
        for i, x in enumerate(self._tasks_x()):
            if x <= mx < x + self.TASK_W:
                return ("task", servers[row_idx], i, row_idx)
        return None

    def mouseMoveEvent(self, e):
        hit = self._hit(int(e.position().x()), int(e.position().y()))
        new_row = hit[3] if hit and hit[0] == "task" else (hit[2] if hit and hit[0] == "server" else None)
        new_col = hit[2] if hit and hit[0] == "task" else None
        if new_row != self._hov_row or new_col != self._hov_col:
            self._hov_row = new_row
            self._hov_col = new_col
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor if hit else Qt.CursorShape.ArrowCursor))
            self.update()

    def leaveEvent(self, e):
        self._hov_row = None
        self._hov_col = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.update()

    def mousePressEvent(self, e):
        button = e.button()
        if button not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            return
        hit = self._hit(int(e.position().x()), int(e.position().y()))
        if not hit or hit[0] != "task":
            return
        _, srv, task_idx, _ = hit
        task = self._tasks()[task_idx]
        data = self._state.setdefault("server_checks", {}).setdefault(srv, {})
        if task.get("max", 1) == 1:
            cur = bool(data.get(task["id"], False))
        else:
            cur = int(data.get(task["id"], 0) or 0)
        data[task["id"]] = _apply_summary_click_value(cur, task.get("max", 1), button)
        self.check_toggled.emit(srv, task["id"])
        self.update()


def _summary_servers(state):
    order = []
    seen = set()
    for char in state.get("chars", []):
        srv = _server_name_key(state.get("servers", {}).get(char, ""))
        if srv not in seen:
            seen.add(srv)
            order.append(srv)
    for srv, data in state.get("server_checks", {}).items():
        if srv not in seen and any(bool(v) for v in data.values()):
            seen.add(srv)
            order.append(srv)
    if not order:
        order.append(_server_name_key(""))
    return order


class _ServerFocusedSummaryView(QWidget):
    char_selected = pyqtSignal(str)
    check_toggled = pyqtSignal(object, str)

    TOP_ROW_H = 28
    HDR_H = 28
    SERVER_ROW_H = 30
    CHAR_ROW_H = 36
    LABEL_W = 88
    SERVER_TASK1_W = 46
    SERVER_TASKN_W = 56
    CHAR_TASK1_W = 38
    CHAR_TASKN_W = 48
    PAD = 6
    DOT = 11
    GAP = 0
    BD = (255, 255, 255, 18)
    BDS = (255, 255, 255, 8)

    def __init__(self, state, active_char, selected_server, parent=None):
        super().__init__(parent)
        self._state = state
        self._active_char = active_char
        self._selected_server = _server_name_key(selected_server)
        self._hov_row = None
        self._hov_col = None
        self._base_metrics = {
            "TOP_ROW_H": self.TOP_ROW_H,
            "HDR_H": self.HDR_H,
            "SERVER_ROW_H": self.SERVER_ROW_H,
            "CHAR_ROW_H": self.CHAR_ROW_H,
            "LABEL_W": self.LABEL_W,
            "SERVER_TASK1_W": self.SERVER_TASK1_W,
            "SERVER_TASKN_W": self.SERVER_TASKN_W,
            "CHAR_TASK1_W": self.CHAR_TASK1_W,
            "CHAR_TASKN_W": self.CHAR_TASKN_W,
            "PAD": self.PAD,
            "DOT": self.DOT,
            "GAP": self.GAP,
        }
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.setMouseTracking(True)
        self._apply_scale_metrics()
        self._recalc()

    def _apply_scale_metrics(self):
        scale = _ui_scale_factor(self._state)
        for name, base in self._base_metrics.items():
            setattr(self, name, _scaled(base, scale))
        if scale <= 1.0:
            self.LABEL_W = max(self.LABEL_W, 98)
            self.TOP_ROW_H = max(self.TOP_ROW_H, 30)
            self.PAD = max(self.PAD, 7)

    def _font(self, family, size, weight=QFont.Weight.Normal):
        font = QFont(family, weight=weight)
        font.setPointSizeF(_scaled_font_size(size, _ui_scale_factor(self._state)))
        return font

    def _server_tasks(self):
        return list(self._state.get("server_tasks", []))

    def _char_tasks(self):
        return [
            t for t in self._state.get("tasks", [])
            if t.get("reset") != "directive"
        ]

    def _server_chars(self):
        chars = []
        for char in self._state.get("chars", []):
            srv = _server_name_key(self._state.get("servers", {}).get(char, ""))
            if srv == self._selected_server:
                chars.append(char)
        return chars

    def _server_task_w(self, task):
        return self.SERVER_TASK1_W if task.get("max", 1) == 1 else self.SERVER_TASKN_W

    def _char_task_w(self, task):
        return self.CHAR_TASK1_W if task.get("max", 1) == 1 else self.CHAR_TASKN_W

    def _char_task_value(self, char, task, char_values=None, ode_data=None):
        if _is_akmong_task(task):
            ode_values = ode_data if ode_data is not None else self._state.get("ode", {})
            return _clamp_akmong_stock(ode_values.get(char, {}).get("akmong_stock", 0))
        values = char_values if char_values is not None else self._state.get("checks", {}).get(char, {})
        raw = values.get(task["id"], 0)
        max_val = task.get("max", 1)
        return 1 if (raw and max_val == 1) else (int(raw) if isinstance(raw, int) else 0)

    def _server_tasks_x(self):
        return self._task_layout(self._server_tasks(), self._server_task_w)[0]

    def _char_tasks_x(self):
        return self._task_layout(self._char_tasks(), self._char_task_w)[0]

    def _task_layout(self, tasks, width_fn, total_width=None):
        widths = [width_fn(task) for task in tasks]
        target_w = total_width if total_width is not None else (self.LABEL_W + sum(widths))
        extra = max(0, target_w - self.LABEL_W - sum(widths))
        if widths and extra > 0:
            per = extra // len(widths)
            rem = extra % len(widths)
            widths = [w + per + (1 if i < rem else 0) for i, w in enumerate(widths)]
        xs = []
        x = self.LABEL_W
        for w in widths:
            xs.append(x)
            x += w
        return xs, widths

    def _server_total_w(self):
        return self.LABEL_W + sum(self._server_task_w(t) for t in self._server_tasks())

    def _char_total_w(self):
        return self.LABEL_W + sum(self._char_task_w(t) for t in self._char_tasks())

    def _total_w(self):
        return max(self._server_total_w(), self._char_total_w())

    def _char_rows_h(self):
        rows = len(self._server_chars()) or 1
        return rows * self.CHAR_ROW_H

    def _layout_y(self):
        top_row_y = 0
        server_hdr_y = top_row_y
        server_row_y = server_hdr_y + self.TOP_ROW_H
        char_hdr_y = server_row_y + self.SERVER_ROW_H + self.GAP
        char_rows_y = char_hdr_y + self.HDR_H
        timer_y = server_row_y
        return {
            "top_row_y": top_row_y,
            "server_hdr_y": server_hdr_y,
            "server_row_y": server_row_y,
            "char_hdr_y": char_hdr_y,
            "char_rows_y": char_rows_y,
            "timer_y": timer_y,
        }

    def _total_h(self):
        ys = self._layout_y()
        return ys["char_rows_y"] + self._char_rows_h()

    def _recalc(self):
        self.setFixedSize(self._total_w(), self._total_h())

    def set_server(self, server_name):
        self._selected_server = _server_name_key(server_name)
        self._recalc()
        self.update()

    def refresh(self, state, active_char, selected_server=None):
        self._state = state
        self._active_char = active_char
        if selected_server is not None:
            self._selected_server = _server_name_key(selected_server)
        self._apply_scale_metrics()
        self._recalc()
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        outer_path = _rounded_rect_path(self.width(), self.height(), 10)
        p.setClipPath(outer_path)
        p.fillPath(outer_path, QColor(C["bg"]))

        ys = self._layout_y()
        W = self.width()
        bd_pen = QPen(QColor(*self.BD), 1)
        bds_pen = QPen(QColor(*self.BDS), 1)

        server_tasks = self._server_tasks()
        server_xs, server_ws = self._task_layout(server_tasks, self._server_task_w, self._total_w())
        char_tasks = self._char_tasks()
        char_xs, char_ws = self._task_layout(char_tasks, self._char_task_w, self._total_w())
        server_bg = {
            "daily": QColor(79, 156, 249, 10),
            "weekly": QColor(201, 168, 76, 10),
            "sanctuary": QColor(201, 168, 76, 8),
            "directive": QColor(201, 168, 76, 8),
        }
        char_bg = {
            "daily": QColor(79, 156, 249, 10),
            "corridor": QColor(176, 111, 255, 10),
            "weekly": QColor(201, 168, 76, 10),
            "sanctuary": QColor(201, 168, 76, 7),
        }
        chars = self._server_chars()

        # 상단 행: 좌측 서버 선택 영역 + 우측 서버 공용 헤더
        p.fillRect(0, ys["top_row_y"], self.LABEL_W, self.TOP_ROW_H, QColor(C["surface"]))
        timer_items = [
            ("일간", RESET_COLOR["daily"], fmt_cd(_next_time(5))),
            ("회랑", RESET_COLOR["corridor"], fmt_cd(_next_time(CORRIDOR_RESET_HOUR, CORRIDOR_RESET_WEEKDAYS))),
            ("주간", RESET_COLOR["weekly"], fmt_cd(_next_time(5, 2))),
        ]
        scale = _ui_scale_factor(self._state)
        timer_label_w = max(_scaled(22, scale), min(_scaled(28, scale), max(24, self.LABEL_W // 3)))
        timer_total_h = self.SERVER_ROW_H + self.HDR_H
        slot_h = max(1, timer_total_h // len(timer_items))
        for idx, (label, color, countdown) in enumerate(timer_items):
            sy = ys["timer_y"] + idx * slot_h
            cur_h = timer_total_h - idx * slot_h if idx == len(timer_items) - 1 else slot_h
            if idx > 0:
                p.setPen(bd_pen)
                p.drawLine(0, sy, self.LABEL_W, sy)
            p.setFont(self._font("Noto Sans KR", 7, QFont.Weight.Bold))
            p.setPen(QColor(color))
            p.drawText(self.PAD, sy, timer_label_w, cur_h, Qt.AlignmentFlag.AlignVCenter, label)
            p.setFont(self._font("Rajdhani", 8))
            p.setPen(QColor(255, 255, 255, 160))
            p.drawText(self.PAD + timer_label_w + 2, sy, self.LABEL_W - self.PAD * 2 - timer_label_w - 2, cur_h,
                       Qt.AlignmentFlag.AlignVCenter, countdown)

        p.setPen(bd_pen)
        p.drawLine(self.LABEL_W, ys["top_row_y"], self.LABEL_W, ys["char_rows_y"])
        for i, task in enumerate(server_tasks):
            x = server_xs[i]
            w = server_ws[i]
            header_col = QColor(RESET_COLOR.get(task.get("reset"), C["text_dim"]))
            if self._hov_col == ("server", i):
                p.fillRect(x, ys["server_hdr_y"], w, self.TOP_ROW_H, QColor(130, 90, 255, 24))
            else:
                p.fillRect(x, ys["server_hdr_y"], w, self.TOP_ROW_H, server_bg.get(task.get("reset"), QColor(0, 0, 0, 0)))
            p.setFont(self._font("Noto Sans KR", 8 if len(task.get("short_name", task["name"])) <= 4 else 7, QFont.Weight.Bold))
            p.setPen(QColor(255, 255, 255, 220) if self._hov_col == ("server", i) else header_col)
            p.drawText(x + 3, ys["server_hdr_y"], w - 6, self.TOP_ROW_H,
                       Qt.AlignmentFlag.AlignCenter, task.get("short_name", task["name"]))
            p.setPen(bd_pen)
            p.drawLine(x, ys["server_hdr_y"], x, ys["server_hdr_y"] + self.TOP_ROW_H)
        p.drawLine(0, ys["server_row_y"] - 1, W, ys["server_row_y"] - 1)

        # 서버 공용 데이터 행
        row_is_hov = self._hov_row == ("server", self._selected_server)
        if row_is_hov:
            p.fillRect(self.LABEL_W, ys["server_row_y"], W - self.LABEL_W, self.SERVER_ROW_H, QColor(130, 90, 255, 16))
        server_values = self._state.setdefault("server_checks", {}).setdefault(self._selected_server, {})
        for i, task in enumerate(server_tasks):
            x = server_xs[i]
            w = server_ws[i]
            value = server_values.get(task["id"], _task_default_value(task))
            if task.get("max", 1) == 1:
                done = bool(value)
                p.setFont(self._font("Noto Sans KR", 9, QFont.Weight.Bold if done else QFont.Weight.Normal))
                p.setPen(QColor(C["gold"] if done else C["text_muted"]))
                p.drawText(x + 4, ys["server_row_y"], w - 8, self.SERVER_ROW_H,
                           Qt.AlignmentFlag.AlignCenter, "완료" if done else "미완")
            else:
                cnt = int(value or 0)
                done = cnt >= int(task.get("max", 0) or 0)
                p.setFont(self._font("Rajdhani", 10, QFont.Weight.Bold))
                p.setPen(QColor(C["gold"] if done else C["text_muted"]))
                p.drawText(x, ys["server_row_y"], w, self.SERVER_ROW_H,
                           Qt.AlignmentFlag.AlignCenter, f"{cnt}/{task['max']}")
            p.setPen(bd_pen)
            p.drawLine(x, ys["server_row_y"], x, ys["server_row_y"] + self.SERVER_ROW_H)
        p.drawLine(self.LABEL_W, ys["server_row_y"] + self.SERVER_ROW_H - 1, W, ys["server_row_y"] + self.SERVER_ROW_H - 1)

        # 캐릭터 헤더
        p.setPen(bd_pen)
        p.drawLine(self.LABEL_W, ys["char_hdr_y"], self.LABEL_W, ys["char_hdr_y"] + self.HDR_H)
        for i, task in enumerate(char_tasks):
            x = char_xs[i]
            w = char_ws[i]
            header_col = QColor(RESET_COLOR.get(task.get("reset"), C["text_dim"]))
            if self._hov_col == ("char", i):
                p.fillRect(x, ys["char_hdr_y"], w, self.HDR_H, QColor(130, 90, 255, 24))
            else:
                p.fillRect(x, ys["char_hdr_y"], w, self.HDR_H, char_bg.get(task.get("reset"), QColor(0, 0, 0, 0)))
            p.setFont(self._font("Noto Sans KR", 8, QFont.Weight.Bold))
            p.setPen(QColor(255, 255, 255, 220) if self._hov_col == ("char", i) else header_col)
            p.drawText(x, ys["char_hdr_y"], w, self.HDR_H,
                       Qt.AlignmentFlag.AlignCenter, task.get("short_name", task["name"]))
            p.setPen(bd_pen)
            p.drawLine(x, ys["char_hdr_y"], x, ys["char_hdr_y"] + self.HDR_H)
        p.drawLine(0, ys["char_hdr_y"] + self.HDR_H, W, ys["char_hdr_y"] + self.HDR_H)

        y = ys["char_rows_y"]
        if not chars:
            p.setFont(self._font("Noto Sans KR", 9))
            p.setPen(QColor(C["text_muted"]))
            p.drawText(self.PAD, y, W - self.PAD * 2, self.CHAR_ROW_H,
                       Qt.AlignmentFlag.AlignVCenter, "캐릭터 없음")
            p.setPen(bd_pen)
            p.drawRect(0, ys["char_hdr_y"], W - 1, self.HDR_H + self.CHAR_ROW_H)
            p.end()
            return

        checks = self._state.get("checks", {})
        ode_d = self._state.get("ode", {})
        for row_idx, char in enumerate(chars):
            is_hov = self._hov_row == ("char", char)
            if row_idx % 2 == 0:
                p.fillRect(0, y, W, self.CHAR_ROW_H, QColor(255, 255, 255, 8))
            if is_hov:
                p.fillRect(0, y, W, self.CHAR_ROW_H, QColor(130, 90, 255, 16))

            is_act = char == self._active_char
            base_ode = int(ode_d.get(char, {}).get("base", 0) or 0)
            bar_h = max(4, _scaled(4, scale))
            gap_h = max(2, _scaled(3, scale))
            name_h = max(15, _scaled(16, scale))
            block_h = name_h + gap_h + bar_h
            block_y = y + max(0, ((self.CHAR_ROW_H - block_h) // 2) - max(1, _scaled(1, scale)))
            text_y = block_y
            bar_y = block_y + name_h + gap_h
            bar_x = self.PAD
            bar_w = self.LABEL_W - self.PAD * 2
            p.setFont(self._font("Noto Sans KR", 10, QFont.Weight.Bold))
            p.setPen(QColor(C["accent"] if is_act else "#ede6ff"))
            p.drawText(self.PAD, text_y, self.LABEL_W - self.PAD * 2, name_h,
                       Qt.AlignmentFlag.AlignVCenter, char)
            ratio = min(base_ode / 840, 1.0)
            fill_w = int(bar_w * ratio)
            bar_color = (
                QColor("#f95f5f") if ratio >= 0.8 else
                QColor("#f9c74f") if ratio >= 0.4 else
                QColor("#4dbd74")
            )
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 255, 255, 18))
            p.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 2, 2)
            if fill_w > 0:
                p.setBrush(bar_color)
                p.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 2, 2)
            p.setPen(bd_pen)
            p.drawLine(self.LABEL_W, y, self.LABEL_W, y + self.CHAR_ROW_H)

            char_values = checks.get(char, {})
            for i, task in enumerate(char_tasks):
                x = char_xs[i]
                w = char_ws[i]
                max_val = task.get("max", 1)
                cnt = self._char_task_value(char, task, char_values=char_values, ode_data=ode_d)
                if _is_akmong_task(task):
                    is_full = cnt >= AKMONG_MAX
                    tc = QColor(C["red"] if is_full else (C["text"] if cnt > 0 else C["text_muted"]))
                    p.setFont(self._font("Noto Sans KR", 8, QFont.Weight.Bold if cnt > 0 else QFont.Weight.Medium))
                    p.setPen(tc)
                    p.drawText(x, y, w, self.CHAR_ROW_H, Qt.AlignmentFlag.AlignCenter, f"{cnt}장")
                elif max_val == 1:
                    done = cnt >= max_val
                    tc = RESET_COLOR.get(task.get("reset"), C["border2"])
                    ds = self.DOT
                    cx = x + (w - ds) // 2
                    cy = y + (self.CHAR_ROW_H - ds) // 2
                    p.setPen(QPen(QColor(tc if done else C["border2"]), 1.2))
                    p.setBrush(QColor(tc) if done else Qt.BrushStyle.NoBrush)
                    p.drawRoundedRect(cx, cy, ds, ds, 2, 2)
                else:
                    done = cnt >= max_val
                    tc = RESET_COLOR.get(task.get("reset"), C["border2"])
                    p.setFont(self._font("Rajdhani", 10))
                    p.setPen(QColor(tc if done else C["text_muted"]))
                    p.drawText(x, y, w, self.CHAR_ROW_H, Qt.AlignmentFlag.AlignCenter, f"{cnt}/{max_val}")
                p.setPen(bd_pen)
                p.drawLine(x, y, x, y + self.CHAR_ROW_H)
            p.setPen(bd_pen if row_idx == len(chars) - 1 else bds_pen)
            p.drawLine(0, y + self.CHAR_ROW_H - 1, W, y + self.CHAR_ROW_H - 1)
            y += self.CHAR_ROW_H

        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(bd_pen)
        p.drawPath(outer_path)
        p.end()

    def _hit(self, mx, my):
        ys = self._layout_y()
        if ys["server_row_y"] <= my < ys["server_row_y"] + self.SERVER_ROW_H:
            server_tasks = self._server_tasks()
            server_xs, server_ws = self._task_layout(server_tasks, self._server_task_w, self.width())
            for i, x in enumerate(server_xs):
                if x <= mx < x + server_ws[i]:
                    return ("server_task", self._selected_server, i)

        if ys["char_rows_y"] <= my < ys["char_rows_y"] + self._char_rows_h():
            row_idx = (my - ys["char_rows_y"]) // self.CHAR_ROW_H
            chars = self._server_chars()
            if not chars or row_idx < 0 or row_idx >= len(chars):
                return None
            char = chars[row_idx]
            if mx < self.LABEL_W:
                return ("char", char)
            char_tasks = self._char_tasks()
            char_xs, char_ws = self._task_layout(char_tasks, self._char_task_w, self.width())
            for i, x in enumerate(char_xs):
                if x <= mx < x + char_ws[i]:
                    return ("char_task", char, i)
        return None

    def mouseMoveEvent(self, e):
        hit = self._hit(int(e.position().x()), int(e.position().y()))
        new_row = None
        new_col = None
        if hit:
            if hit[0] == "server_task":
                new_row = ("server", hit[1])
                new_col = ("server", hit[2])
            elif hit[0] == "char":
                new_row = ("char", hit[1])
            elif hit[0] == "char_task":
                new_row = ("char", hit[1])
                new_col = ("char", hit[2])
        if new_row != self._hov_row or new_col != self._hov_col:
            self._hov_row = new_row
            self._hov_col = new_col
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor if hit else Qt.CursorShape.ArrowCursor))
            self.update()

    def leaveEvent(self, e):
        self._hov_row = None
        self._hov_col = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.update()

    def mousePressEvent(self, e):
        button = e.button()
        if button not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            return
        hit = self._hit(int(e.position().x()), int(e.position().y()))
        if not hit:
            return
        if hit[0] == "char":
            if button != Qt.MouseButton.LeftButton:
                return
            self.char_selected.emit(hit[1])
            return
        if hit[0] == "server_task":
            _, srv, idx = hit
            task = self._server_tasks()[idx]
            data = self._state.setdefault("server_checks", {}).setdefault(srv, {})
            if task.get("max", 1) == 1:
                cur = bool(data.get(task["id"], False))
            else:
                cur = int(data.get(task["id"], 0) or 0)
            data[task["id"]] = _apply_summary_click_value(cur, task.get("max", 1), button)
            self.check_toggled.emit(srv, task["id"])
            self.update()
            return
        if hit[0] == "char_task":
            _, char, idx = hit
            task = self._char_tasks()[idx]
            if _is_akmong_task(task):
                od = self._state.setdefault("ode", {}).setdefault(char, _ode_default())
                od["akmong_stock"] = _clamp_akmong_stock(
                    _apply_summary_click_value(od.get("akmong_stock", 0), AKMONG_MAX, button)
                )
                od["akmong_recorded_at"] = _now_ms()
            else:
                max_val = task.get("max", 1)
                data = self._state.setdefault("checks", {}).setdefault(char, {})
                raw = data.get(task["id"], 0)
                cur = 1 if (raw and max_val == 1) else (int(raw) if isinstance(raw, int) else 0)
                data[task["id"]] = _apply_summary_click_value(cur, max_val, button)
            self.check_toggled.emit(char, task["id"])
            self.update()
            return


# ─────────────────────────────────────────────
# PROGRESS BAR
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# SETTINGS DIALOG
# ─────────────────────────────────────────────
def _rounded_rect_path(w, h, radius):
    from PyQt6.QtGui import QPainterPath
    path = QPainterPath()
    path.addRoundedRect(0.5, 0.5, w - 1, h - 1, radius, radius)
    return path

def _paint_rounded_window(widget, radius=10):
    """FramelessHint QDialog/QWidget의 paintEvent에서 호출.
    배경+클리핑+테두리를 안티앨리어싱으로 그린다."""
    w, h = widget.width(), widget.height()
    path = _rounded_rect_path(w, h, radius)

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
    live_ui_scale = pyqtSignal(int)

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self._rec  = False
        self._rec_target = None
        self._orig_opacity = state.get("opacity", 100)   # restore on cancel
        self._orig_ui_scale = _clamp_ui_scale(state.get("ui_scale", 100))

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
        self._apply_live_scale(self._orig_ui_scale)

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

        scale_hdr = QHBoxLayout()
        scale_hdr.addWidget(self._lbl("UI 크기"), 1)
        self._scale_val = QLabel(_ui_scale_label(self.state.get("ui_scale", 100)))
        self._scale_val.setFont(QFont("Rajdhani", 12, QFont.Weight.Bold))
        self._scale_val.setStyleSheet(f"color:{C['gold']};background:transparent;")
        scale_hdr.addWidget(self._scale_val); bv.addLayout(scale_hdr)

        current_scale = _clamp_ui_scale(self.state.get("ui_scale", 100))
        self._scale_buttons = {}
        scale_row = QHBoxLayout(); scale_row.setSpacing(6)
        for label, preset in UI_SCALE_PRESETS:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setFixedHeight(30)
            btn.clicked.connect(lambda checked=False, p=preset: self._on_scale_change(p))
            self._scale_buttons[preset] = btn
            scale_row.addWidget(btn, 1)
        bv.addLayout(scale_row)
        self._set_scale_buttons(current_scale)

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

    def _scale_btn_css(self, active):
        if active:
            return f"""
                QPushButton{{background:{C['gold']}22;color:{C['gold']};border:1px solid {C['gold']}88;
                    border-radius:5px;font-family:'Noto Sans KR';font-size:11px;font-weight:500;}}
                QPushButton:hover{{background:{C['gold']}33;border-color:{C['gold']};}}
            """
        return f"""
            QPushButton{{background:{C['surface2']};color:{C['text_muted']};border:1px solid {C['border']};
                border-radius:5px;font-family:'Noto Sans KR';font-size:11px;}}
            QPushButton:hover{{border-color:{C['border2']};color:{C['text']};}}
        """

    def _set_scale_buttons(self, preset):
        preset = _clamp_ui_scale(preset)
        self._scale_val.setText(_ui_scale_label(preset))
        for value, btn in getattr(self, "_scale_buttons", {}).items():
            btn.blockSignals(True)
            btn.setChecked(value == preset)
            btn.setStyleSheet(self._scale_btn_css(value == preset))
            btn.blockSignals(False)

    def _apply_live_scale(self, preset):
        _ = _clamp_ui_scale(preset)
        # 설정창 자체는 UI 스케일 영향을 받지 않으므로
        # 프리셋 변경 중에도 현재 위치를 유지한다.
        return

    def _sl_css(self):
        return f"""
            QSlider::groove:horizontal{{height:4px;background:{C['surface2']};border-radius:2px;}}
            QSlider::handle:horizontal{{background:{C['accent']};width:14px;height:14px;border-radius:7px;margin:-5px 0;}}
            QSlider::sub-page:horizontal{{background:{C['accent']};border-radius:2px;}}
        """

    def _on_opacity_change(self, v):
        self._op_val.setText(f"{v}%")
        self.live_opacity.emit(v)   # live preview

    def _on_scale_change(self, preset):
        preset = _clamp_ui_scale(preset)
        self._set_scale_buttons(preset)
        self._apply_live_scale(preset)
        self.live_ui_scale.emit(preset)

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
        self._set_scale_buttons(self._orig_ui_scale)
        self._apply_live_scale(self._orig_ui_scale)
        self.live_ui_scale.emit(self._orig_ui_scale)
        self.reject()

    def _apply(self):
        self.applied.emit({
            "opacity": self._op_sl.value(),
            "ui_scale": next((value for value, btn in self._scale_buttons.items() if btn.isChecked()), self._orig_ui_scale),
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
        num_stack = _OverlayStack(); num_stack.setFixedSize(VAL_W, 22)

        val_lbl = QLabel("0"); val_lbl.setFont(QFont("Rajdhani",11,QFont.Weight.Bold))
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_lbl.setStyleSheet(f"color:{C['text']};background:transparent;"
                              f"border-bottom:1px solid {C['border2']};")
        val_lbl.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        num_stack.add_overlay_child(val_lbl)

        val_edit = QLineEdit("0"); val_edit.setFixedSize(VAL_W, 22)
        val_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_edit.setFont(QFont("Rajdhani",11,QFont.Weight.Bold))
        val_edit.setStyleSheet(f"""
            QLineEdit{{color:{C['text']};background:{C['surface2']};
                border:1px solid {C['border2']};border-radius:3px;
                font-family:'Rajdhani';font-size:11px;padding:0;}}
            QLineEdit:focus{{border:1px solid {C['border2']};outline:0;}}
        """)
        num_stack.add_overlay_child(val_edit); val_edit.hide()

        def _start(e, k=kid, lbl=val_lbl, edit=val_edit):
            edit.setText(str(self._kina_data().get(k, 0)))
            lbl.hide(); edit.show(); edit.setFocus(); edit.selectAll()
        def _commit(k=kid, lbl=val_lbl, edit=val_edit):
            try: v2 = max(0, int(edit.text()))
            except ValueError: v2 = self._kina_data().get(k, 0)
            self._kina_data()[k] = v2
            edit.hide(); lbl.show()
            self.refresh(); self.changed.emit()
        def _cancel(k=kid, lbl=val_lbl, edit=val_edit):
            edit.hide(); lbl.show()
            self.refresh()

        val_lbl.mousePressEvent = _start
        val_edit.returnPressed.connect(_commit)
        val_edit.editingFinished.connect(_commit)
        _bind_lineedit_commit_on_focus_out(val_edit, _commit)
        _bind_lineedit_escape(val_edit, _cancel)
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
            od = self.state.setdefault("ode", {}).setdefault(char_key, _ode_default())
            for k, v in _ode_default().items():
                od.setdefault(k, v)
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
        od = self.state.setdefault("ode", {}).setdefault(self.char_key, _ode_default())
        for k, v in _ode_default().items():
            od.setdefault(k, v)
        return od

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(8,4,8,4); root.setSpacing(4)

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

        # 기본 / 추가 슬라이더
        root.addWidget(self._make_ode_row("base",  "기본",      ODE_MAX,       "#4dbd74"))
        root.addWidget(self._make_ode_row("extra", "추가(수동)", ODE_EXTRA_MAX, "#ff9040"))
        self.apply_scale_style()

    def _make_akmong_row(self):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        top = QHBoxLayout(w); top.setContentsMargins(0, 0, 0, 0); top.setSpacing(0)

        lbl = QLabel("악몽 티켓"); lbl.setFont(QFont("Noto Sans KR", 9, QFont.Weight.Medium))
        lbl.setStyleSheet(f"color:{C['text']};background:transparent;")
        top.addWidget(lbl, 1)

        self._akmong_timer_lbl = QLabel("")
        self._akmong_timer_lbl.setFont(QFont("Rajdhani", 10, QFont.Weight.Bold))
        self._akmong_timer_lbl.setStyleSheet(f"color:{RESET_COLOR['daily']};background:transparent;")
        top.addWidget(self._akmong_timer_lbl)

        charge_hint = QLabel(f"+{AKMONG_DAILY_CHARGE}")
        charge_hint.setFont(QFont("Noto Sans KR", 8))
        charge_hint.setStyleSheet(f"color:{C['text_muted']};background:transparent;")
        top.addWidget(charge_hint)

        RIGHT_W = 86
        right = QWidget(); right.setFixedWidth(RIGHT_W)
        right.setStyleSheet("background:transparent;")
        rh = QHBoxLayout(right); rh.setContentsMargins(0, 0, 0, 0); rh.setSpacing(4)

        btn_minus = QPushButton("−"); btn_minus.setFixedSize(22, 22)
        btn_minus.setStyleSheet(self._btn_style())
        btn_minus.clicked.connect(lambda: self._adjust_akmong(-1))
        rh.addWidget(btn_minus)

        num_stack = _OverlayStack(); num_stack.setFixedSize(38, 22)

        self._akmong_val = QLabel("0")
        self._akmong_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._akmong_val.setFont(QFont("Rajdhani", 11, QFont.Weight.Bold))
        self._akmong_val.setStyleSheet(f"color:{C['gold']};background:transparent;border-bottom:1px solid {C['gold']}33;")
        self._akmong_val.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        num_stack.add_overlay_child(self._akmong_val)

        self._akmong_edit = QLineEdit("0")
        self._akmong_edit.setFixedSize(38, 22)
        self._akmong_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._akmong_edit.setFont(QFont("Rajdhani", 11, QFont.Weight.Bold))
        self._akmong_edit.setStyleSheet(f"""
            QLineEdit{{color:{C['gold']};background:{C['surface2']};
                border:1px solid {C['border2']};border-radius:3px;
                font-family:'Rajdhani';font-size:11px;padding:0;}}
            QLineEdit:focus{{border:1px solid {C['border2']};outline:0;}}
        """)
        num_stack.add_overlay_child(self._akmong_edit)
        self._akmong_edit.hide()

        self._akmong_val.mousePressEvent = self._start_akmong_edit
        self._akmong_edit.returnPressed.connect(self._commit_akmong_edit)
        self._akmong_edit.editingFinished.connect(self._commit_akmong_edit)
        _bind_lineedit_commit_on_focus_out(self._akmong_edit, self._commit_akmong_edit)
        _bind_lineedit_escape(self._akmong_edit, self._cancel_akmong_edit)
        rh.addWidget(num_stack)

        btn_plus = QPushButton("+"); btn_plus.setFixedSize(22, 22)
        btn_plus.setStyleSheet(self._btn_style())
        btn_plus.clicked.connect(lambda: self._adjust_akmong(+1))
        rh.addWidget(btn_plus)

        top.addWidget(right)
        return w

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
        num_stack = _OverlayStack(); num_stack.setFixedSize(NUM_W, 22)

        val_lbl = QLabel("0"); val_lbl.setFont(QFont("Rajdhani",11,QFont.Weight.Bold))
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_lbl.setStyleSheet(f"color:{color};background:transparent;"
                              f"border-bottom:1px solid {color}33;")
        val_lbl.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        num_stack.add_overlay_child(val_lbl)

        val_edit = QLineEdit("0"); val_edit.setFixedSize(NUM_W,22)
        val_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_edit.setFont(QFont("Rajdhani",11,QFont.Weight.Bold))
        val_edit.setStyleSheet(f"""
            QLineEdit{{color:{color};background:{C['surface2']};
                border:1px solid {C['border2']};border-radius:3px;
                font-family:'Rajdhani';font-size:11px;padding:0;}}
            QLineEdit:focus{{border:1px solid {C['border2']};outline:0;}}
        """)
        num_stack.add_overlay_child(val_edit); val_edit.hide()

        def start_edit(e, f=field, mv=max_val, lbl=val_lbl, edit=val_edit):
            edit.setText(str(self._od().get(f, 0)))
            lbl.hide(); edit.show(); edit.setFocus(); edit.selectAll()
        def commit_edit(f=field, mv=max_val, lbl=val_lbl, edit=val_edit):
            try: v2 = max(0, min(mv, int(edit.text())))
            except ValueError: v2 = self._od().get(f, 0)
            self._od()[f] = v2; edit.hide(); lbl.show()
            self.refresh(); self.changed.emit()
        def cancel_edit(f=field, lbl=val_lbl, edit=val_edit):
            edit.hide(); lbl.show()
            self.refresh()

        val_lbl.mousePressEvent = start_edit
        val_edit.returnPressed.connect(commit_edit)
        val_edit.editingFinished.connect(commit_edit)
        _bind_lineedit_commit_on_focus_out(val_edit, commit_edit)
        _bind_lineedit_escape(val_edit, cancel_edit)
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
        slider.valueChanged.connect(lambda val, f=field, mv=max_val: self._set_ode(f, mv, round(val/5)*5))
        v.addWidget(slider)

        setattr(self, f"_val_{field}",    val_lbl)
        setattr(self, f"_edit_{field}",   val_edit)
        setattr(self, f"_slider_{field}", slider)
        setattr(self, f"_max_{field}",    max_val)
        setattr(self, f"_slider_color_{field}", color)
        return w

    def _ode_slider_style(self, color, scale):
        groove_h = _scaled(4, scale)
        handle_d = _scaled(12, scale)
        handle_r = handle_d // 2
        groove_r = max(2, groove_h // 2)
        margin_v = -max(0, (handle_d - groove_h) // 2)
        return (
            max(_scaled(16, scale), handle_d + 4),
            f"""
                QSlider::groove:horizontal{{height:{groove_h}px;background:{C['surface2']};border-radius:{groove_r}px;}}
                QSlider::handle:horizontal{{background:{color};width:{handle_d}px;height:{handle_d}px;
                    border-radius:{handle_r}px;margin:{margin_v}px 0;}}
                QSlider::sub-page:horizontal{{background:{color};border-radius:{groove_r}px;}}
            """
        )

    def apply_scale_style(self):
        scale = _ui_scale_factor(self.state)
        for field in ("base", "extra"):
            slider = getattr(self, f"_slider_{field}", None)
            color = getattr(self, f"_slider_color_{field}", None)
            if slider is None or color is None:
                continue
            slider_h, style = self._ode_slider_style(color, scale)
            slider.setFixedHeight(slider_h)
            slider.setStyleSheet(style)

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

    def _set_akmong_stock(self, value):
        od = self._od()
        od["akmong_stock"] = _clamp_akmong_stock(value)
        od["akmong_recorded_at"] = _now_ms()

    def _adjust_akmong(self, delta):
        self._set_akmong_stock(self._od().get("akmong_stock", 0) + delta)
        self.refresh()
        self.changed.emit()

    def _start_akmong_edit(self, _event):
        self._akmong_edit.setText(str(_clamp_akmong_stock(self._od().get("akmong_stock", 0))))
        self._akmong_val.hide()
        self._akmong_edit.show()
        self._akmong_edit.setFocus()
        self._akmong_edit.selectAll()

    def _commit_akmong_edit(self):
        if not self._akmong_edit.isVisible():
            return
        try:
            value = int(self._akmong_edit.text())
        except ValueError:
            value = self._od().get("akmong_stock", 0)
        self._set_akmong_stock(value)
        self._akmong_edit.hide()
        self._akmong_val.show()
        self.refresh()
        self.changed.emit()

    def _cancel_akmong_edit(self):
        if not self._akmong_edit.isVisible():
            return
        self._akmong_edit.hide()
        self._akmong_val.show()
        self.refresh()

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
        if hasattr(self, "_akmong_timer_lbl"):
            self._akmong_timer_lbl.setText(_next_charge_str(now, [AKMONG_CHARGE_HOUR]))

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
        if hasattr(self, "_akmong_edit") and not self._akmong_edit.isVisible():
            self._akmong_val.setText(f"{_clamp_akmong_stock(od.get('akmong_stock', 0))}")
        self._upd_timer_labels()


class _CountAdjustRow(QWidget):
    toggled = pyqtSignal(str)

    def __init__(self, task, value, parent=None):
        super().__init__(parent)
        self.task_id = task["id"]
        self._max = int(task.get("max", 0) or 0)
        self.count = int(value or 0)
        self.setStyleSheet("background:transparent;")
        self.setFixedHeight(30)

        h = QHBoxLayout(self); h.setContentsMargins(14, 0, 14, 0); h.setSpacing(6)
        lbl = QLabel(task["name"]); lbl.setFont(QFont("Noto Sans KR", 10))
        lbl.setStyleSheet(f"color:{C['text']};background:transparent;")
        h.addWidget(lbl, 1)

        def _btn(text):
            b = QPushButton(text)
            b.setFixedSize(20, 20)
            b.setStyleSheet(_sbtn() + "QPushButton{padding:0;font-size:11px;}")
            return b

        self._btn_m = _btn("−")
        NUM_W = 50
        num_stack = _OverlayStack()
        num_stack.setFixedSize(NUM_W, 22)

        self._value_label = QLabel("")
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_label.setFont(QFont("Rajdhani", 10, QFont.Weight.Bold))
        self._value_label.setStyleSheet(
            f"color:{RESET_COLOR.get(task['reset'], C['text'])};background:transparent;"
            f"border-bottom:1px solid {C['border2']};")
        self._value_label.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        num_stack.add_overlay_child(self._value_label)

        self._value_edit = QLineEdit("0")
        self._value_edit.setFixedSize(NUM_W, 22)
        self._value_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_edit.setFont(QFont("Rajdhani", 10, QFont.Weight.Bold))
        self._value_edit.setStyleSheet(f"""
            QLineEdit{{color:{RESET_COLOR.get(task['reset'], C['text'])};background:{C['surface2']};
                border:1px solid {C['border2']};border-radius:3px;
                font-family:'Rajdhani';font-size:10px;padding:0;}}
            QLineEdit:focus{{border:1px solid {C['border2']};outline:0;}}
        """)
        num_stack.add_overlay_child(self._value_edit)
        self._value_edit.hide()
        self._btn_p = _btn("+")

        self._btn_m.clicked.connect(lambda: self._adjust(-1))
        self._btn_p.clicked.connect(lambda: self._adjust(+1))
        self._value_label.mousePressEvent = self._start_edit
        self._value_edit.returnPressed.connect(self._commit_edit)
        self._value_edit.editingFinished.connect(self._commit_edit)
        _bind_lineedit_commit_on_focus_out(self._value_edit, self._commit_edit)
        _bind_lineedit_escape(self._value_edit, self._cancel_edit)

        h.addWidget(self._btn_m)
        h.addWidget(num_stack)
        h.addWidget(self._btn_p)
        self.refresh()

    def _adjust(self, delta):
        self.count = max(0, min(self._max, self.count + delta))
        self.refresh()
        self.toggled.emit(self.task_id)

    def _start_edit(self, _event):
        self._value_edit.setText(str(self.count))
        self._value_label.hide()
        self._value_edit.show()
        self._value_edit.setFocus()
        self._value_edit.selectAll()

    def _commit_edit(self):
        if not self._value_edit.isVisible():
            return
        try:
            value = int(self._value_edit.text())
        except ValueError:
            value = self.count
        self.count = max(0, min(self._max, value))
        self._value_edit.hide()
        self._value_label.show()
        self.refresh()
        self.toggled.emit(self.task_id)

    def _cancel_edit(self):
        if not self._value_edit.isVisible():
            return
        self._value_edit.hide()
        self._value_label.show()
        self.refresh()

    def refresh(self):
        self._value_label.setText(f"{self.count}/{self._max}")


class ServerSharedPanel(QWidget):
    changed = pyqtSignal()

    def __init__(self, state, server_name, parent=None):
        super().__init__(parent)
        self.state = state
        self.server_name = _server_name_key(server_name)
        self._rows = {}
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background:transparent;")
        self._build()
        self.refresh()

    def _server_data(self):
        data = self.state.setdefault("server_checks", {}).setdefault(self.server_name, {})
        for task in self.state.get("server_tasks", []):
            data.setdefault(task["id"], _task_default_value(task))
        return data

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(8, 6, 8, 6); root.setSpacing(6)

        hdr = QHBoxLayout()
        title = QLabel("서버 공용"); title.setFont(QFont("Noto Sans KR", 9, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{C['accent']};background:transparent;")
        hdr.addWidget(title)
        badge = QLabel(self.server_name); badge.setFont(QFont("Noto Sans KR", 8))
        badge.setStyleSheet(f"color:{C['text_muted']};background:transparent;")
        hdr.addWidget(badge)
        hdr.addStretch()
        root.addLayout(hdr)

        for task in self.state.get("server_tasks", []):
            row = CheckRow(task, self._server_data().get(task["id"], _task_default_value(task)), show_badge=False)
            row.toggled.connect(self._on_toggle)
            self._rows[task["id"]] = row
            root.addWidget(row)

    def _on_toggle(self, tid):
        sender = self.sender()
        data = self._server_data()
        if hasattr(sender, "count"):
            data[tid] = sender.count
        else:
            data[tid] = not bool(data.get(tid, False))
        self.changed.emit()

    def refresh(self):
        data = self._server_data()
        for task in self.state.get("server_tasks", []):
            row = self._rows.get(task["id"])
            if not row:
                continue
            value = data.get(task["id"], _task_default_value(task))
            row.count = (1 if value else 0) if task.get("max", 1) == 1 else int(value or 0)
            if hasattr(row, "_refresh"):
                row._refresh()
                row.update()


class _SelectButton(QPushButton):
    changed = pyqtSignal(object)

    def __init__(self, color, min_chars=6, parent=None):
        super().__init__(parent)
        self._accent = color
        self._items = []
        self._current_data = None
        self._current_label = ""
        self._min_chars = min_chars
        self._menu = QMenu(self)
        self._menu.setStyleSheet(self._menu_style())
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(28)
        self.setMinimumWidth(max(60, min_chars * 10))
        self._text_label = QLabel("", self)
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._text_label.setStyleSheet("background:transparent;border:none;")
        self._arrow = QLabel("▾", self)
        self._arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._arrow.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._arrow.setStyleSheet(f"color:{self._accent};background:transparent;border:none;")
        self.setStyleSheet(self._button_style())
        self.clicked.connect(self._show_menu)
        self._sync_arrow_font()
        self._refresh_label()

    def sizeHint(self):
        hint = super().sizeHint()
        if self.width() > 0:
            hint.setWidth(self.width())
        if self.height() > 0:
            hint.setHeight(self.height())
        return hint

    def minimumSizeHint(self):
        hint = super().minimumSizeHint()
        if self.width() > 0:
            hint.setWidth(self.width())
        else:
            hint.setWidth(max(60, self._min_chars * 10))
        if self.height() > 0:
            hint.setHeight(self.height())
        return hint

    def _button_style(self):
        return f"""
            QPushButton {{
                background:{C['surface2']};
                border:1px solid {C['border2']};
                border-radius:5px;
                padding:0;
            }}
            QPushButton:hover {{
                border-color:{self._accent}88;
            }}
        """

    def _menu_style(self):
        return f"""
            QMenu {{
                background:{C['surface2']};
                color:{C['text']};
                border:1px solid {C['border2']};
                padding:2px 0;
                font-family:'Noto Sans KR';
                font-size:10px;
            }}
            QMenu::item {{
                padding:6px 10px;
                margin:0;
            }}
            QMenu::item:selected {{
                background:{self._accent}22;
            }}
        """

    def _show_menu(self):
        if not self._items:
            return
        self._menu.setFixedWidth(self.width())
        self._menu.exec(self.mapToGlobal(self.rect().bottomLeft()))

    def _refresh_label(self):
        label = self._current_label or ""
        self.setText("")
        self.setToolTip(label)
        self._sync_label_styles()
        self._sync_text_label()
        self._arrow.setVisible(bool(self._items))
        self._layout_contents()

    def _sync_arrow_font(self):
        arrow_font = QFont(self.font())
        arrow_font.setBold(True)
        self._arrow.setFont(arrow_font)

    def _sync_label_styles(self):
        text_color = self._accent if self.isEnabled() else C["text_muted"]
        self._text_label.setStyleSheet(f"color:{text_color};background:transparent;border:none;")
        self._arrow.setStyleSheet(f"color:{text_color};background:transparent;border:none;")

    def _sync_text_label(self):
        left_pad = max(8, self.height() // 3)
        right_pad = max(24, self.height() - 4)
        available_w = max(10, self.width() - left_pad - right_pad)
        metrics = self._text_label.fontMetrics()
        display = metrics.elidedText(self._current_label or "", Qt.TextElideMode.ElideRight, available_w)
        self._text_label.setText(display)

    def _layout_contents(self):
        left_pad = max(8, self.height() // 3)
        right_pad = max(6, self.height() // 4)
        arrow_w = max(14, self.fontMetrics().horizontalAdvance("▾") + max(2, self.height() // 8))
        self._arrow.setGeometry(self.width() - arrow_w - right_pad, 0, arrow_w, self.height())
        text_right = self._arrow.x() - 4
        self._text_label.setGeometry(left_pad, 0, max(10, text_right - left_pad), self.height())
        self._sync_text_label()

    def set_items(self, items):
        cleaned = []
        seen = set()
        for label, data in items:
            text = str(label).strip() if label is not None else ""
            if not text:
                continue
            key = (text, data)
            if key in seen:
                continue
            seen.add(key)
            cleaned.append((text, data))
        self._items = cleaned

        self._menu.clear()
        for text, data in self._items:
            act = self._menu.addAction(text)
            act.triggered.connect(lambda checked=False, value=data: self.set_current_data(value, emit=True))

        if self._current_data not in [data for _, data in self._items]:
            self._current_data = self._items[0][1] if self._items else None

        self.setEnabled(bool(self._items))
        self._update_current_label()

    def _update_current_label(self):
        self._current_label = ""
        for text, data in self._items:
            if data == self._current_data:
                self._current_label = text
                break
        self._refresh_label()

    def set_current_data(self, data, emit=False):
        if data not in [item_data for _, item_data in self._items]:
            data = self._items[0][1] if self._items else None
        if data == self._current_data and not emit:
            self._update_current_label()
            return
        self._current_data = data
        self._update_current_label()
        if emit:
            self.changed.emit(self._current_data)

    def current_data(self):
        return self._current_data

    def set_popup_font(self, font):
        self.setFont(font)
        self._menu.setFont(font)
        self._text_label.setFont(font)
        self._sync_arrow_font()
        self._sync_text_label()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_contents()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange:
            self._sync_label_styles()



class _CellSelectButton(_SelectButton):
    def __init__(self, color, min_chars=6, parent=None):
        self._hovering = False
        super().__init__(color, min_chars=min_chars, parent=parent)

    def _button_style(self):
        return f"""
            QPushButton {{
                background:transparent;
                border:none;
                border-radius:0px;
                padding:0;
            }}
            QPushButton:hover {{
                background:transparent;
            }}
            QPushButton:pressed {{
                background:transparent;
            }}
        """

    def _sync_label_styles(self):
        if not self.isEnabled():
            text_color = C["text_muted"]
            arrow_color = C["text_muted"]
        elif self._hovering:
            text_color = C["accent"]
            arrow_color = C["text"]
        else:
            text_color = C["text"]
            arrow_color = C["accent"]
        self._text_label.setStyleSheet(f"color:{text_color};background:transparent;border:none;")
        self._arrow.setStyleSheet(f"color:{arrow_color};background:transparent;border:none;")

    def _layout_contents(self):
        left_pad = max(8, self.height() // 3)
        right_pad = max(8, self.height() // 3)
        arrow_w = max(14, self.fontMetrics().horizontalAdvance("▾") + max(3, self.height() // 7))
        self._arrow.setGeometry(self.width() - arrow_w - right_pad, 0, arrow_w, self.height())
        text_right = self._arrow.x() - 2
        self._text_label.setGeometry(left_pad, 0, max(10, text_right - left_pad), self.height())
        self._sync_text_label()

    def enterEvent(self, event):
        self._hovering = True
        self._sync_label_styles()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovering = False
        self._sync_label_styles()
        super().leaveEvent(event)


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
    check_toggled = pyqtSignal(object, str)

    RADIUS = 10
    TOP_BAR_H = 0

    def __init__(self, state, active_char, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._state = state
        self._active_char = active_char
        self._selected_server = _server_name_key(state.get("servers", {}).get(active_char, ""))
        self._apply_scale_metrics()

        rl = QVBoxLayout(self)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self._view = _ServerFocusedSummaryView(state, active_char, self._selected_server)
        self._view.char_selected.connect(self.char_selected)
        self._view.check_toggled.connect(self._emit_check_toggled)
        self._server_picker = _CellSelectButton(C["accent"], min_chars=4, parent=self._view)
        self._server_picker.changed.connect(self._on_server_changed)

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
        self._scroll.setWidget(self._view)

        rl.addWidget(self._scroll)

        self._refresh_server_picker(sync_to_active=True)
        self.setFixedWidth(self._view._total_w())
        self.snap_height()
        self._layout_server_picker()

    def _apply_scale_metrics(self):
        self._top_bar_h = _scaled(self.TOP_BAR_H, _ui_scale_factor(self._state))

    def paintEvent(self, e):
        _paint_rounded_window(self, radius=self.RADIUS)

    def snap_height(self, _unused=None):
        self.layout().setContentsMargins(0, 0, 0, 0)
        screen = QApplication.screenAt(self.pos()) or QApplication.primaryScreen()
        available_h = screen.availableGeometry().height() if screen else 900
        max_body_h = max(140, available_h - 32)
        body_h = min(self._view._total_h(), max_body_h)

        self._scroll.setFixedHeight(body_h)
        self.setFixedHeight(body_h)
        _apply_rounded_mask(self, self.RADIUS)

    def refresh(self, state, active_char):
        self._state = state
        self._active_char = active_char
        self._apply_scale_metrics()
        self._view.refresh(state, active_char, self._selected_server)
        self._refresh_server_picker(sync_to_active=False)
        self.setFixedWidth(self._view._total_w())
        self.snap_height()
        self._layout_server_picker()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        _apply_rounded_mask(self, self.RADIUS)
        self._layout_server_picker()

    def _available_servers(self):
        return _summary_servers(self._state)

    def _refresh_server_picker(self, sync_to_active):
        servers = self._available_servers()
        active_server = _server_name_key(self._state.get("servers", {}).get(self._active_char, ""))
        if sync_to_active or self._selected_server not in servers:
            self._selected_server = active_server if active_server in servers else (servers[0] if servers else _server_name_key(""))
        items = [(srv, srv) for srv in servers]
        self._server_picker.set_items(items)
        self._server_picker.set_current_data(self._selected_server, emit=False)
        picker_font = QFont("Noto Sans KR")
        picker_font.setPointSizeF(max(1.0, _scaled_font_size(9, _ui_scale_factor(self._state))))
        self._server_picker.set_popup_font(picker_font)
        self._server_picker.setVisible(bool(items))

    def _layout_server_picker(self):
        if not hasattr(self, "_server_picker"):
            return
        scale = _ui_scale_factor(self._state)
        row_h = max(_scaled(24, scale), getattr(self._view, "TOP_ROW_H", _scaled(28, scale)))
        inset = max(2, _scaled(2, scale))
        picker_h = max(_scaled(20, scale), row_h - inset * 2)
        picker_w = max(_scaled(56, scale), self._view.LABEL_W - inset * 2)
        x = inset
        y = max(1, (row_h - picker_h) // 2)
        self._server_picker.setGeometry(x, y, picker_w, picker_h)
        self._server_picker.raise_()

    def _on_server_changed(self, server_name):
        self._selected_server = _server_name_key(server_name)
        self._view.set_server(self._selected_server)
        self.setFixedWidth(self._view._total_w())
        self.snap_height()
        self._refresh_server_picker(sync_to_active=False)
        self._layout_server_picker()
        self.update()

    def _emit_check_toggled(self, key, tid):
        self.check_toggled.emit(key, tid)

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
        self.setFixedWidth(453)
        self.setMinimumHeight(max(416, self.height()))

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
        tabs.addTab(self._char_tab(), "캐릭터 관리")
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
        server_key = _server_name_key(srv)
        self.state.setdefault("server_checks", {}).setdefault(server_key, {})
        for task in self.state.get("server_tasks", []):
            self.state["server_checks"][server_key].setdefault(task["id"], _task_default_value(task))
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
        server_key = _server_name_key(srv)
        self.state.setdefault("server_checks", {}).setdefault(server_key, {})
        for task in self.state.get("server_tasks", []):
            self.state["server_checks"][server_key].setdefault(task["id"], _task_default_value(task))
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
        v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(8)

        hint = QLabel("⠿ 핸들 드래그로 같은 초기화 타입 내 순서 변경")
        hint.setStyleSheet(f"color:{C['text_muted']};font-size:9px;background:transparent;")
        v.addWidget(hint)

        shared_strip = QWidget()
        shared_strip.setStyleSheet(
            f"background:{C['surface']};border:1px solid {C['border']};border-radius:5px;")
        sh = QHBoxLayout(shared_strip); sh.setContentsMargins(8, 7, 8, 7); sh.setSpacing(8)
        badge = QLabel("서버 공용")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedWidth(66)
        badge.setStyleSheet(f"""
            background:{C['accent_dim']};
            color:{C['accent']};
            border:1px solid {C['accent']}44;
            border-radius:4px;
            font-size:9px;
            font-weight:500;
            padding:2px 6px;
        """)
        sh.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)

        shared_info = QWidget(); shared_info.setStyleSheet("background:transparent;border:none;")
        siv = QVBoxLayout(shared_info); siv.setContentsMargins(0, 0, 0, 0); siv.setSpacing(2)
        info_title = QLabel("요약뷰의 서버 탭에서 함께 관리됩니다.")
        info_title.setStyleSheet(f"color:{C['text']};background:transparent;border:none;font-size:10px;")
        shared_names = " · ".join(
            [t.get("name", "") for t in self.state.get("server_tasks", []) if t.get("name")]
        )
        info_meta = QLabel(shared_names or "서버 공용 항목 없음")
        info_meta.setWordWrap(True)
        info_meta.setStyleSheet(
            f"color:{C['text_muted']};font-size:9px;background:transparent;border:none;")
        siv.addWidget(info_title)
        siv.addWidget(info_meta)
        sh.addWidget(shared_info, 1)
        v.addWidget(shared_strip)

        # ── 2열 레이아웃: 좌(개인 일간/회랑) | 우(주간) ──
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
        self._task_cont_daily = None
        self._task_cont_corridor = None
        task_reset_types = {t.get("reset") for t in self.state.get("tasks", [])}
        if "daily" in task_reset_types:
            daily_col, self._task_cont_daily = _make_section("daily")
            lv.addWidget(daily_col, 1)
        if "corridor" in task_reset_types:
            corridor_col, self._task_cont_corridor = _make_section("corridor")
            lv.addWidget(corridor_col, 1)
        if lv.count() == 0:
            lv.addStretch(1)

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
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.rebuild(self.state)

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
    BASE_LEFT_W = 255
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
        self._drag_origin_cursor = None
        self._drag_origin_window_pos = None
        self._drag_axis_lock = None
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
        self._screen_hook_handle = None
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

    # ── Window ──
    def _setup_window(self):
        flags = (Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(self.BASE_LEFT_W)
        self.adjustSize()
        px,py=self.state.get("overlay_pos",[None,None])
        if px is not None: self.move(int(px),int(py))
        else:
            scr=QApplication.primaryScreen().geometry()
            self.move(scr.width() - (self.BASE_LEFT_W + 39), 20)

    def _apply_ui_scale(self):
        scale = _ui_scale_factor(self.state)
        self.MODE_LEFT_W = _scaled(self.BASE_LEFT_W, scale)
        metrics = self._topbar_metrics(scale)
        self._topbar_h = metrics["frame_h"]
        self._mini_topbar_h = metrics["mini_h"]

        if hasattr(self, "card"):
            _apply_widget_scale(self.card, scale)

        icon_sz = _scaled(22, scale)
        icon_path = _resource_path("odeframe_icon.png")
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QPixmap
            pix = QPixmap(icon_path).scaled(
                icon_sz, icon_sz,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            if hasattr(self, "_icon_lbl"):
                self._icon_lbl.setPixmap(pix)
                self._icon_lbl.setFixedSize(icon_sz, icon_sz)
            if hasattr(self, "_mini_icon_lbl"):
                self._mini_icon_lbl.setPixmap(pix)
                self._mini_icon_lbl.setFixedSize(icon_sz, icon_sz)

        self._apply_topbar_frame(adjust_window=True)

        if hasattr(self, "_ode_panel") and self._ode_panel:
            self._ode_panel.apply_scale_style()

        if getattr(self, "_summary_win", None):
            self._summary_win.refresh(self.state, self.active_char)
            self._summary_win.setWindowOpacity(self.state.get("opacity", 100) / 100)

    def _apply_cfg(self):
        self.state["ui_scale"] = _clamp_ui_scale(self.state.get("ui_scale", 100))
        self._apply_ui_scale()
        opacity = self.state.get("opacity", 100) / 100
        self.setWindowOpacity(opacity)
        if self._summary_win:
            self._summary_win.setWindowOpacity(opacity)
        self._hotkey_str = self.state.get("hotkey", "Ctrl+Shift+H")
        self._hotkey_seq = QKeySequence(self._hotkey_str)
        self._sync_hotkey_str = self.state.get("sync_hotkey", "Ctrl+R")
        self._sync_hotkey_seq = QKeySequence(self._sync_hotkey_str)
        self._set_global_hotkeys_active(getattr(self, "_global_hotkeys_active", False))

    def _bind_screen_change_hook(self):
        handle = self.windowHandle()
        if not handle or handle is self._screen_hook_handle:
            return
        handle.screenChanged.connect(self._on_screen_changed)
        self._screen_hook_handle = handle

    def _on_screen_changed(self, _screen=None):
        # 모니터 간 이동(특히 DPI/배율 차이) 시 고정 치수와 레이아웃을 다시 계산한다.
        QTimer.singleShot(0, self._refresh_after_screen_change)

    def _refresh_after_screen_change(self):
        self._apply_ui_scale()
        if getattr(self, "_is_mini", False):
            self._upd_mini_labels()
        elif self._content_dirty:
            self._render_tasks()
        if self._summary_win:
            self._summary_win.refresh(self.state, self.active_char)
            self._snap_summary_win()

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

    # ── UI ──
    def _build_ui(self):
        self.card = _RoundedCard(self, bg=C["bg"], border=C["border"], radius=10)
        self.card.setObjectName("card")
        rl = QVBoxLayout(self)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(self.card)

        # 외곽은 self.card 하나만 담당하고, 내부는 topbar + content만 쌓는다.
        self._left_widget = self.card
        self._vb = QVBoxLayout(self.card)
        self._vb.setContentsMargins(1, 1, 1, 1)
        self._vb.setSpacing(0)

        # 탑바
        self._build_topbar()

        # 콘텐츠 영역
        self._content_widget = QWidget(self.card)
        self._content_widget.setStyleSheet("background:transparent;")
        self._cvb = QVBoxLayout(self._content_widget)
        self._cvb.setContentsMargins(0, 0, 0, 0)
        self._cvb.setSpacing(0)
        self._vb.addWidget(self._content_widget)

        # 상태 초기화
        self._summary_win = None   # 요약 창
        self._content_dirty = False
        self._summary_resume_on_restore = False

        self._build_char_row()
        self._build_content_area()

    def _build_topbar(self):
        metrics = self._topbar_metrics()
        self._topbar_h = metrics["frame_h"]
        self._mini_topbar_h = metrics["mini_h"]
        self._bar = _RoundedCard(
            self.card,
            bg=C["surface"],
            border=None,
            radius=10,
            corners=(True, True, False, False),
            border_sides=(False, False, False, False),
        )
        self._bar.setFixedHeight(self._topbar_h)
        bar = self._bar
        h = QHBoxLayout(bar)
        h.setContentsMargins(8, 0, 10, 0)
        h.setSpacing(8)

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
        self._mini_char_lbl.setFont(QFont("Noto Sans KR", 10, QFont.Weight.Bold))
        self._mini_char_lbl.setStyleSheet(f"color:{C['text']};background:transparent;")
        self._mini_char_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._mini_char_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._mini_char_lbl.setGeometry(36, 0, 107, self._topbar_h)  # 아이콘(22) + 간격(6) = x:36
        self._mini_char_lbl.hide()

        self._mini_ode_lbl = QLabel("", bar)
        self._mini_ode_lbl.setFont(QFont("Rajdhani", 10, QFont.Weight.Bold))
        self._mini_ode_lbl.setStyleSheet(f"color:#4dbd74;background:transparent;")
        self._mini_ode_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._mini_ode_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._mini_ode_lbl.setGeometry(143, 0, 44, self._topbar_h)
        self._mini_ode_lbl.hide()

        # ── 버튼 3개: 우측 기준 재배치 ──
        def _mk_btn(text, accent=None):
            b = QPushButton(text, bar)
            b.setFixedSize(24, 20)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            b.setFont(QFont("Noto Sans KR", 10, QFont.Weight.Bold))
            b.setStyleSheet(self._topbar_btn_style(accent or C["accent"]))
            return b

        # 최소화 버튼
        self._btn_minimize = _mk_btn("−")
        self._btn_minimize.clicked.connect(self._toggle_minimize)

        # 오드 동기화 버튼
        self._btn_sync_ode = _mk_btn("↻", "#4dbd74")
        self._btn_sync_ode.setToolTip("게임 오드값 OCR 동기화")
        self._btn_sync_ode.clicked.connect(self._sync_ode_from_game)

        # 확장 버튼
        self._btn_expand = _mk_btn("▷")
        self._btn_expand.clicked.connect(self._toggle_summary)

        # ── 설정·관리 버튼 (우클릭 메뉴용) ──
        self._btn_settings = QPushButton(); self._btn_settings.setVisible(False)
        self._btn_settings.clicked.connect(self._open_settings)
        self._btn_manager = QPushButton(); self._btn_manager.setVisible(False)
        self._btn_manager.clicked.connect(self._open_manager)
        bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        bar.customContextMenuRequested.connect(self._show_topbar_menu)

        self._layout_topbar_controls()
        self._vb.addWidget(bar)

    def _topbar_btn_style(self, accent):
        return f"""
            QPushButton {{
                color:{C['text_dim']};
                background:transparent;
                border:1px solid {C['border2']};
                border-radius:4px;
                padding:0;
                margin:0;
                text-align:center;
                font-family:'Noto Sans KR';
            }}
            QPushButton:hover {{
                color:{accent};
                border-color:{accent};
                background:{accent}22;
            }}
            QPushButton:disabled {{
                color:{C['text_muted']}77;
                border-color:{C['border']}77;
                background:transparent;
            }}
        """

    def _layout_topbar_controls(self):
        if not hasattr(self, "_bar"):
            return
        scale = _ui_scale_factor(self.state)
        metrics = self._topbar_metrics(scale)
        bar_h = self._bar.height() or (self._mini_topbar_h if getattr(self, "_is_mini", False) else self._topbar_h)
        bar_w = self._bar.width() or self.MODE_LEFT_W
        btn_w = metrics["btn_w"]
        btn_h = metrics["btn_h"]
        gap = metrics["btn_gap"]
        right_pad = metrics["right_pad"]
        btn_y = max(0, (bar_h - btn_h) // 2)

        x = bar_w - right_pad - btn_w
        for btn in (self._btn_minimize, self._btn_sync_ode, self._btn_expand):
            btn.setFixedSize(btn_w, btn_h)
            btn.move(x, btn_y)
            x -= btn_w + gap

        icon_x = metrics["icon_x"]
        icon_sz = metrics["icon_sz"]
        if hasattr(self, "_mini_icon_lbl"):
            self._mini_icon_lbl.setGeometry(icon_x, max(0, (bar_h - icon_sz) // 2), icon_sz, icon_sz)

        label_gap = metrics["label_gap"]
        char_x = icon_x + icon_sz + label_gap
        right_anchor = self._btn_sync_ode.x() - label_gap
        ode_min_w = metrics["mini_ode_min_w"]
        ode_x = max(char_x + metrics["mini_char_min_w"] + metrics["mini_label_gap"], right_anchor - ode_min_w)
        ode_w = max(ode_min_w, right_anchor - ode_x)
        char_w = max(metrics["mini_char_min_w"], ode_x - char_x - metrics["mini_label_gap"])
        if hasattr(self, "_mini_char_lbl"):
            self._mini_char_lbl.setGeometry(char_x, 0, char_w, bar_h)
        if hasattr(self, "_mini_ode_lbl"):
            self._mini_ode_lbl.setGeometry(ode_x, 0, ode_w, bar_h)

    def _topbar_metrics(self, scale=None):
        scale = _ui_scale_factor(self.state) if scale is None else scale
        frame_h = _scaled(36, scale)
        return {
            "frame_h": frame_h,
            "mini_h": frame_h,
            "btn_w": _scaled(24, scale),
            "btn_h": _scaled(20, scale),
            "btn_gap": _scaled(4, scale),
            "right_pad": _scaled(10, scale),
            "icon_x": _scaled(8, scale),
            "icon_sz": _scaled(22, scale),
            "label_gap": _scaled(8, scale),
            "mini_char_min_w": _scaled(58, scale),
            "mini_ode_min_w": _scaled(42, scale),
            "mini_label_gap": _scaled(4, scale),
        }

    def _apply_topbar_frame(self, *, adjust_window=False):
        if not hasattr(self, "card") or not hasattr(self, "_bar"):
            return
        mini = bool(getattr(self, "_is_mini", False))
        topbar_h = self._mini_topbar_h if mini else self._topbar_h
        inner_w = max(1, self.MODE_LEFT_W - 2)

        self.card.setFixedWidth(self.MODE_LEFT_W)
        self.card.set_frame_style(
            bg=C["surface"] if mini else C["bg"],
            border=C["border"],
            corners=(True, True, True, True),
            border_sides=(True, True, True, True),
        )
        self._vb.setContentsMargins(1, 1, 1, 1)

        # 탑바는 full 모드에서는 표면만, mini 모드에서는 투명 호스트로만 사용한다.
        self._bar.setFixedWidth(inner_w)
        self._bar.setFixedHeight(topbar_h)
        self._bar.set_frame_style(
            bg=QColor(0, 0, 0, 0) if mini else C["surface"],
            border=None,
            corners=(True, True, True, True) if mini else (True, True, False, False),
            border_sides=(False, False, False, False),
        )

        if hasattr(self, "_crow"):
            self._crow.setMaximumWidth(inner_w if not mini else 0)
        if hasattr(self, "_content_widget"):
            self._content_widget.setVisible(not mini)
            self._content_widget.setMinimumHeight(0)
            self._content_widget.setMaximumHeight(0 if mini else 16777215)

        self.setFixedWidth(self.MODE_LEFT_W)
        if mini:
            self.setFixedHeight(topbar_h + 2)
        else:
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
            if adjust_window:
                QTimer.singleShot(0, self._adj_height)

        self._layout_topbar_controls()

    # ── 모드 전환 ──
    MODE_LEFT_W = BASE_LEFT_W
    MINI_FRAME_PAD = 0
    SUMMARY_GAP = 2
    SUMMARY_EDGE_SNAP_THRESHOLD = 16
    OVERLAY_EDGE_SNAP_THRESHOLD = 14

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
        self._summary_win.check_toggled.connect(self._on_summary_toggle)
        # show() 전에 위치/높이를 미리 지정 — OS가 show() 시점에 덮어쓰는 것을 방지
        self._summary_win.snap_height(self.height())
        target_x, target_y = self._summary_target_pos()
        self._summary_win.move(target_x, target_y)
        self._summary_win.show()
        self._summary_win.setWindowOpacity(self.state.get("opacity", 100) / 100)
        # show() 후 OS 재배치에 대비해 한 프레임 뒤에 한 번 더 snap
        QTimer.singleShot(0, self._snap_summary_win)

    def _on_summary_win_closed(self):
        self._summary_win = None
        self._upd_mode_btns()

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
            self._btn_expand.setStyleSheet(self._topbar_btn_style(C["gold"]))
        else:
            self._btn_expand.setStyleSheet(self._topbar_btn_style(C["accent"]))

    def _build_char_row(self):
        self._crow = QWidget(); self._crow.setFixedHeight(36)
        self._crow.setMaximumWidth(self.MODE_LEFT_W)
        self._crow.setStyleSheet(f"border-bottom:1px solid {C['border']};")
        self._ch = QHBoxLayout(self._crow)
        self._ch.setContentsMargins(6, 0, 6, 0); self._ch.setSpacing(6)

        self._srv_combo = _SelectButton(C["gold"], min_chars=4)
        self._srv_combo.setFixedWidth(75)
        self._srv_combo.changed.connect(self._on_srv_combo_changed)
        self._ch.addWidget(self._srv_combo)

        # 구분선
        self._sep = QFrame(); self._sep.setFrameShape(QFrame.Shape.VLine)
        self._sep.setStyleSheet(f"color:{C['border2']};"); self._sep.setFixedWidth(1)
        self._ch.addWidget(self._sep)

        self._char_combo = _SelectButton(C["accent"], min_chars=8)
        self._char_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._char_combo.changed.connect(self._on_char_combo_changed)
        self._ch.addWidget(self._char_combo, 1)

        self._cvb.addWidget(self._crow)

    def _apply_combo_fonts(self):
        combo_size = _scaled_font_size(9, _ui_scale_factor(self.state))
        popup_font = QFont("Noto Sans KR")
        popup_font.setPointSizeF(max(1.0, combo_size))
        self._srv_combo.set_popup_font(popup_font)
        self._char_combo.set_popup_font(popup_font)

    def _render_chars(self):
        valid_chars = []
        seen_chars = set()
        for value in self.state.get("chars", []):
            if not isinstance(value, str):
                continue
            name = value.strip()
            if not name or name in seen_chars:
                continue
            seen_chars.add(name)
            valid_chars.append(name)
        if valid_chars != self.state.get("chars", []):
            self.state["chars"] = valid_chars
            if self.active_char not in valid_chars and valid_chars:
                self.active_char = valid_chars[0]
            save_state(self.state)

        # ── 서버 목록 추출 ──
        seen = []; servers = []
        for c in valid_chars:
            srv = (self.state.get("servers", {}).get(c, "") or "").strip()
            if srv and srv not in seen:
                seen.append(srv); servers.append(srv)

        # ── 서버 드롭다운 갱신 ──
        if servers:
            if self.active_server not in servers:
                self.active_server = servers[0]
            self._srv_combo.set_items([(s, s) for s in servers])
            self._srv_combo.set_current_data(self.active_server)
            self._srv_combo.setVisible(True)
            self._sep.setVisible(True)
        else:
            self.active_server = None
            self._srv_combo.set_items([])
            self._srv_combo.setVisible(False)
            self._sep.setVisible(False)

        # ── 캐릭터 드롭다운 갱신 ──
        visible_chars = [
            c for c in valid_chars
            if self.active_server is None or
               (self.state.get("servers", {}).get(c, "") or "").strip() == self.active_server
        ]
        if self.active_char not in visible_chars:
            self.active_char = visible_chars[0] if visible_chars else None

        self._char_combo.set_items([(c, c) for c in visible_chars])
        self._char_combo.set_current_data(self.active_char)
        self._apply_combo_fonts()

    def _on_srv_combo_changed(self, key):
        self.active_server = key
        self._render_chars()
        self._render_tasks()

    def _on_char_combo_changed(self, key):
        if key and key != self.active_char:
            self.active_char = key
            self._render_tasks()

    def _build_content_area(self):
        # 메인 UI 본문은 키나/오드 패널만 유지한다.
        self._cvb.setContentsMargins(0, 2, 0, 2)
        self._cvb.setSpacing(0)
        self._p0v = self._cvb
        self._kina_panel = None
        self._ode_panel = None
        self._p0_divider = None

    def _ensure_page0_panels(self):
        if self._kina_panel is None:
            srv = self.state.get("servers", {}).get(self.active_char, "") or "공통"
            self._kina_panel = KinaPanel(self.state, srv, self)
            self._kina_panel.changed.connect(lambda: save_state(self.state))
            self._p0v.addWidget(self._kina_panel)

        if self._p0_divider is None:
            div = QFrame()
            div.setFrameShape(QFrame.Shape.HLine)
            div.setStyleSheet(f"color:{C['border']};margin:0 8px;")
            self._p0_divider = div
            self._p0v.addWidget(div)

        if self._ode_panel is None:
            self._ode_panel = OdePanel(self.state, self.active_char)
            self._ode_panel.changed.connect(self._on_ode_panel_changed)
            self._p0v.addWidget(self._ode_panel)

    def _schedule_content_relayout(self):
        if getattr(self, "_is_mini", False):
            self._content_dirty = True
            return
        QTimer.singleShot(0, self._adj_height)


    def _render_tasks(self):
        # 메인 UI 본문은 키나 획득률 + 오드 에너지 패널만 갱신한다.
        self._ensure_page0_panels()
        srv = self.state.get("servers", {}).get(self.active_char, "") or "공통"
        self._kina_panel.state = self.state
        self._kina_panel.server_name = srv
        self._kina_panel.refresh()
        self._ode_panel.state = self.state
        self._ode_panel.char_key = self.active_char
        self._ode_panel.refresh()
        self._content_dirty = False
        self._schedule_content_relayout()

    def _on_ode_panel_changed(self):
        save_state(self.state)
        if self._summary_win and self._summary_win.isVisible():
            self._summary_win.refresh(self.state, self.active_char)
        if getattr(self, "_is_mini", False):
            self._upd_mini_labels()

    def _on_summary_char_select(self, char):
        """요약뷰 캐릭터 클릭 → 해당 캐릭터+서버 선택."""
        self.active_char = char
        self.active_server = self.state.get("servers", {}).get(char, "") or None
        self._render_chars()
        self._render_tasks()
        # 요약창도 갱신
        if self._summary_win:
            self._summary_win.refresh(self.state, self.active_char)

    def _on_summary_toggle(self, key, tid):
        save_state(self.state)
        if key == self.active_char:
            self._render_tasks()
        else:
            active_srv = _server_name_key(self.state.get("servers", {}).get(self.active_char, ""))
            if key == active_srv:
                self._render_tasks()
        if self._summary_win and self._summary_win.isVisible():
            self._summary_win.refresh(self.state, self.active_char)

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
            od = self.state.setdefault("ode", {}).setdefault(char, _ode_default())
            for k, v in _ode_default().items():
                od.setdefault(k, v)
            od["base"]  = max(0, min(ODE_MAX,       base))
            od["extra"] = max(0, min(ODE_EXTRA_MAX, extra))
            od["recorded_at"] = _now_ms()
            _ocr_log(f"상태 반영 완료 — char={char}, base={od['base']}, extra={od['extra']}")
            save_state(self.state)
            # OdePanel 갱신
            if getattr(self, "_is_mini", False):
                self._content_dirty = True
            elif hasattr(self, "_ode_panel") and self._ode_panel:
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
        self._crow.setVisible(vis)
        self._crow.setMaximumWidth(max(1, self.MODE_LEFT_W - 2) if vis else 0)
        if not vis:
            self._srv_combo.setVisible(False)
        else:
            self._render_chars()
            if self._content_dirty:
                self._render_tasks()

        # 아이콘 + 타이틀: 미니모드 시 숨김
        self._icon_lbl.setVisible(vis)
        self._tl.setVisible(vis)

        # 탑바 버튼: 최소화 시 숨김
        for btn in [self._btn_expand]:
            btn.setVisible(vis)

        # 콘텐츠 숨김/표시
        if not vis:
            self._summary_resume_on_restore = bool(self._summary_win and self._summary_win.isVisible())
            if self._summary_resume_on_restore:
                self._summary_win.hide()
        else:
            if self._summary_resume_on_restore and self._summary_win:
                self._summary_win.refresh(self.state, self.active_char)
                self._summary_win.show()
                self._snap_summary_win()
            self._summary_resume_on_restore = False

        # 미니모드 라벨
        self._mini_icon_lbl.setVisible(not vis)
        self._mini_char_lbl.setVisible(not vis)
        self._mini_ode_lbl.setVisible(not vis)
        if not vis:
            self._upd_mini_labels()

        self._btn_minimize.setText("+" if not vis else "−")
        self._apply_topbar_frame(adjust_window=True)

        if vis:
            self._set_game_polling_active(False)
            self._upd_mode_btns()
        else:
            self._set_game_polling_active(True)
        if not vis:  # 최소화 애니메이션/리레이아웃 직후 1회 감지
            QTimer.singleShot(150, lambda: self._poll_game_window() if getattr(self, "_is_mini", False) else None)

    def _upd_mini_labels(self):
        """미니모드 캐릭터명 + 기본 오드 에너지 갱신."""
        char = self.active_char
        self._mini_char_lbl.setText(char)
        od   = self.state.get("ode", {}).get(char, {})
        base = od.get("base", 0)
        self._mini_ode_lbl.setText(f"⚡{base}")

    def _show_topbar_menu(self, pos):
        from PyQt6.QtWidgets import QMenu
        scale = _ui_scale_factor(self.state)
        menu_font_size = _scaled_font_size(10, scale)
        menu_radius = _scaled(6, scale)
        menu_padding = _scaled(3, scale)
        item_pad_v = _scaled(5, scale)
        item_pad_r = _scaled(14, scale)
        item_pad_l = _scaled(10, scale)
        item_radius = _scaled(4, scale)
        item_min_w = _scaled(90, scale)
        sep_margin_v = _scaled(3, scale)
        sep_margin_h = _scaled(8, scale)

        menu = QMenu(self)
        menu_font = QFont("Noto Sans KR")
        menu_font.setPointSizeF(max(1.0, menu_font_size))
        menu.setFont(menu_font)
        menu.setStyleSheet(f"""
            QMenu {{
                background:{C['surface2']}; color:{C['text']};
                border:1px solid {C['border2']}; border-radius:{menu_radius}px;
                padding:{menu_padding}px; font-family:'Noto Sans KR'; font-size:{menu_font_size}px;
            }}
            QMenu::item {{
                padding:{item_pad_v}px {item_pad_r}px {item_pad_v}px {item_pad_l}px;
                border-radius:{item_radius}px; min-width:{item_min_w}px;
            }}
            QMenu::item:selected {{
                background:{C['accent_dim']}; color:{C['accent']};
            }}
            QMenu::separator {{
                height: 1px; background: {C['border']}; margin: {sep_margin_v}px {sep_margin_h}px;
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
        def _live_ui_scale(v):
            self.state["ui_scale"] = _clamp_ui_scale(v)
            self._apply_cfg()
        dlg.live_opacity.connect(_live_opacity)
        dlg.live_ui_scale.connect(_live_ui_scale)
        dlg.exec()

    def _on_cfg(self, cfg):
        self.state.update(cfg); save_state(self.state)
        flags = (Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.Tool |
                 Qt.WindowType.WindowStaysOnTopHint)
        pos=self.pos(); self.setWindowFlags(flags); self.move(pos); self.show()
        self._apply_cfg()

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

    def _on_overlay_resized(self):
        self._layout_topbar_controls()
        self._snap_summary_win()

    def moveEvent(self, e):
        super().moveEvent(e)
        self._snap_summary_win()

    def _summary_target_pos(self):
        p = self.pos()
        target_y = p.y()
        default_x = p.x() + self.width() + self.SUMMARY_GAP

        if not self._summary_win:
            return default_x, target_y

        frame = self.frameGeometry()
        probe = frame.center() if not frame.isNull() else p
        screen = QApplication.screenAt(probe) or QApplication.screenAt(p) or QApplication.primaryScreen()
        if not screen:
            return default_x, target_y

        available = screen.availableGeometry()
        summary_w = max(1, self._summary_win.width())
        right_gap = available.right() - frame.right()
        left_x = p.x() - summary_w - self.SUMMARY_GAP
        right_x = default_x

        should_open_left = (
            right_gap <= self.SUMMARY_EDGE_SNAP_THRESHOLD or
            right_x + summary_w > available.right() + 1
        )
        if should_open_left and left_x >= available.left():
            return left_x, target_y

        return right_x, target_y

    def _snap_summary_win(self):
        """요약창을 메인 창 기준 좌/우 적절한 쪽에 snap, 높이를 메인 창에 맞춤."""
        if self._summary_win and self._summary_win.isVisible():
            self._summary_win.snap_height(self.height())
            target_x, target_y = self._summary_target_pos()
            self._summary_win.move(target_x, target_y)
            QTimer.singleShot(0, lambda: self._summary_win.move(target_x, target_y) if self._summary_win else None)

    def _snap_overlay_target_pos(self, target_pos, cursor_pos=None):
        frame = self.frameGeometry()
        width = max(1, frame.width() or self.width())
        height = max(1, frame.height() or self.height())
        probe = cursor_pos or QPoint(target_pos.x() + width // 2, target_pos.y() + height // 2)
        screen = QApplication.screenAt(probe) or QApplication.screenAt(target_pos) or QApplication.primaryScreen()
        if not screen:
            return target_pos

        available = screen.availableGeometry()
        threshold = self.OVERLAY_EDGE_SNAP_THRESHOLD
        x = target_pos.x()
        y = target_pos.y()
        right_edge = available.x() + available.width()
        bottom_edge = available.y() + available.height()

        if abs(x - available.x()) <= threshold:
            x = available.x()
        elif abs((x + width) - right_edge) <= threshold:
            x = right_edge - width

        if abs(y - available.y()) <= threshold:
            y = available.y()
        elif abs((y + height) - bottom_edge) <= threshold:
            y = bottom_edge - height

        return QPoint(x, y)

    def _apply_drag_axis_lock(self, target_pos, cursor_pos, modifiers):
        if not (modifiers & Qt.KeyboardModifier.ShiftModifier):
            self._drag_axis_lock = None
            return target_pos

        if not self._drag_origin_cursor or not self._drag_origin_window_pos:
            return target_pos

        delta = cursor_pos - self._drag_origin_cursor
        if self._drag_axis_lock is None:
            if abs(delta.x()) < 3 and abs(delta.y()) < 3:
                return target_pos
            self._drag_axis_lock = "x" if abs(delta.x()) >= abs(delta.y()) else "y"

        locked_pos = QPoint(target_pos)
        if self._drag_axis_lock == "x":
            locked_pos.setY(self._drag_origin_window_pos.y())
        elif self._drag_axis_lock == "y":
            locked_pos.setX(self._drag_origin_window_pos.x())
        return locked_pos

    def _apply_card_mask(self):
        pass  # outer shell handles painting directly; no mask needed

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            y = e.position().y(); x = e.position().x()
            topbar_h = self._mini_topbar_h if getattr(self, "_is_mini", False) else self._topbar_h
            in_topbar_y = y <= topbar_h
            in_topbar_x = x <= self.MODE_LEFT_W
            if in_topbar_y and in_topbar_x:
                cursor_pos = e.globalPosition().toPoint()
                self._drag_pos = cursor_pos - self.frameGeometry().topLeft()
                self._drag_origin_cursor = cursor_pos
                self._drag_origin_window_pos = self.pos()
                self._drag_axis_lock = None
    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            cursor_pos = e.globalPosition().toPoint()
            target_pos = cursor_pos - self._drag_pos
            target_pos = self._apply_drag_axis_lock(target_pos, cursor_pos, e.modifiers())
            self.move(self._snap_overlay_target_pos(target_pos, cursor_pos))
    def mouseReleaseEvent(self, e):
        if self._drag_pos:
            p = self.pos(); self.state["overlay_pos"] = [p.x(), p.y()]; save_state(self.state)
        self._drag_pos = None
        self._drag_origin_cursor = None
        self._drag_origin_window_pos = None
        self._drag_axis_lock = None

    # ── Timers ──
    def _start_timers(self):
        self._poll_tmr = QTimer(self)
        self._poll_tmr.timeout.connect(self._poll_game_window)
        self._poll_tmr.setInterval(3000)

    def _set_game_polling_active(self, active):
        if not getattr(self, "_poll_tmr", None):
            return
        if active:
            if not self._poll_tmr.isActive():
                self._poll_tmr.start()
        else:
            self._poll_tmr.stop()

    def _poll_game_window(self):
        """미니모드에서만 게임 창을 감지해 활성 캐릭터를 동기화."""
        try:
            info = _find_aion2_window_info()
        except Exception:
            self._set_global_hotkeys_active(False)
            return   # 예외 → 조용히 무시

        self._set_global_hotkeys_active(bool(info["hwnd"]))

        if info["hwnd"]:
            self._game_hwnd = info["hwnd"]
        if not getattr(self, "_is_mini", False):
            return

        char_name = info["char_name"]
        if not char_name:
            return
        chars = self.state.get("chars", [])
        if char_name not in chars or char_name == self.active_char:
            return

        self.active_char = char_name
        srv = self.state.get("servers", {}).get(char_name, "")
        if srv and srv != self.active_server:
            self.active_server = srv
        self._content_dirty = True
        self._upd_mini_labels()
    def update_all_logic(self):
        """1분마다 실행되는 통합 로직: 자동 초기화, 오드 충전, 라벨 갱신 등"""
        changed = check_auto_reset(self.state)
        if apply_charges(self.state): 
            changed = True
        
        if changed: 
            save_state(self.state)
            if getattr(self, "_is_mini", False):
                self._content_dirty = True
            else:
                self._render_tasks()
            if self._summary_win and self._summary_win.isVisible():
                self._summary_win.refresh(self.state, self.active_char)

        # 미니모드일 경우 라벨 갱신
        if getattr(self, "_is_mini", False):
            self._upd_mini_labels()

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

    def showEvent(self, e):
        super().showEvent(e)
        QTimer.singleShot(0, self._bind_screen_change_hook)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._on_overlay_resized()

    def _update_mask(self):
        pass

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
