"""
窗口捕获工具 - 优化的 PIL 方案
支持多显示器和彩色显示
"""

import ctypes
from ctypes import wintypes
from PIL import ImageGrab
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

# Windows API
user32 = ctypes.windll.user32

class WindowCapture:
    """窗口捕获类 - 使用 PIL"""
    
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.error_count = 0
        
    def get_window_rect(self):
        """获取窗口屏幕坐标"""
        rect = wintypes.RECT()
        user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
        return {
            'left': rect.left,
            'top': rect.top,
            'right': rect.right,
            'bottom': rect.bottom,
            'width': rect.right - rect.left,
            'height': rect.bottom - rect.top
        }
    
    def capture(self):
        """捕获窗口内容"""
        try:
            # 检查窗口是否可见
            if not user32.IsWindowVisible(self.hwnd):
                if self.error_count == 0:
                    print(f"窗口不可见 (HWND: {self.hwnd})")
                    self.error_count += 1
                return None
            
            # 获取窗口位置和尺寸
            rect = self.get_window_rect()
            
            if rect['width'] <= 0 or rect['height'] <= 0:
                if self.error_count == 0:
                    print(f"窗口尺寸无效: {rect['width']}x{rect['height']}")
                    self.error_count += 1
                return None
            
            # 第一次捕获时输出调试信息
            if self.error_count == 0:
                print(f"开始捕获窗口 (HWND: {self.hwnd})")
                print(f"窗口位置: ({rect['left']}, {rect['top']}, {rect['right']}, {rect['bottom']})")
                print(f"窗口尺寸: {rect['width']}x{rect['height']}")
                self.error_count = -1
            
            # 使用 PIL 捕获整个屏幕区域（包括所有显示器）
            # all_screens=True 确保捕获所有显示器
            screenshot = ImageGrab.grab(
                bbox=(rect['left'], rect['top'], rect['right'], rect['bottom']),
                all_screens=True
            )
            
            # 确保是 RGBA 格式（彩色）
            if screenshot.mode != 'RGBA':
                screenshot = screenshot.convert('RGBA')
            
            # 获取图像数据
            data = screenshot.tobytes('raw', 'RGBA')
            
            # 创建 QImage
            qimage = QImage(
                data,
                screenshot.width,
                screenshot.height,
                screenshot.width * 4,
                QImage.Format.Format_RGBA8888
            )
            
            # 转换为 QPixmap
            pixmap = QPixmap.fromImage(qimage.copy())
            
            return pixmap
            
        except Exception as e:
            if self.error_count < 3 and self.error_count >= 0:
                print(f"窗口捕获失败: {e}")
                import traceback
                traceback.print_exc()
                self.error_count += 1
            return None
