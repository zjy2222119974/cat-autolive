
import ctypes
from typing import List, Tuple

# Win32 API Definitions
User32 = ctypes.windll.User32

def is_window_visible(hwnd) -> bool:
    return User32.IsWindowVisible(hwnd)

def get_window_text(hwnd) -> str:
    length = User32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buff = ctypes.create_unicode_buffer(length + 1)
        User32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    return ""

def list_windows() -> List[Tuple[int, str]]:
    """
    List all visible top-level windows.
    Returns: List of (hwnd, title) tuples.
    """
    windows = []
    
    def enum_handler(hwnd, ctx):
        if is_window_visible(hwnd):
            title = get_window_text(hwnd)
            if title:
                windows.append((hwnd, title))
        return True
    
    # Callback type definition
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    
    User32.EnumWindows(WNDENUMPROC(enum_handler), 0)
    
    # Filter out some common system windows/empty titles if needed, 
    # but for now we return all visible named windows.
    return sorted(windows, key=lambda x: x[1])

def get_hwnd_by_title(title_part: str) -> int:
    """Find a window by partial title match."""
    windows = list_windows()
    for hwnd, title in windows:
        if title_part.lower() in title.lower():
            return hwnd
    return 0
