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
        """获取窗口客户区屏幕坐标 (Client Area)"""
        # 1. 获取客户区大小
        client_rect = wintypes.RECT()
        user32.GetClientRect(self.hwnd, ctypes.byref(client_rect))
        width = client_rect.right - client_rect.left
        height = client_rect.bottom - client_rect.top
        
        # 2. 获取客户区左上角在屏幕上的位置
        pt = wintypes.POINT()
        pt.x = 0
        pt.y = 0
        user32.ClientToScreen(self.hwnd, ctypes.byref(pt))
        
        return {
            'left': pt.x,
            'top': pt.y,
            'right': pt.x + width,
            'bottom': pt.y + height,
            'width': width,
            'height': height
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
                # print(f"开始捕获窗口 (HWND: {self.hwnd})")
                # print(f"窗口位置: ({rect['left']}, {rect['top']}, {rect['right']}, {rect['bottom']})")
                # print(f"窗口尺寸: {rect['width']}x{rect['height']}")
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
