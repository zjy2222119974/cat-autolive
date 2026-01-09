"""模拟器驱动"""

import time
import numpy as np
from typing import Any, Dict, Optional
from src.drivers.base_driver import BaseDriver

class SimulatorDriver(BaseDriver):
    """
    模拟器设备驱动
    用于控制安卓模拟器或APP
    """
    
    def __init__(self, name: str, app_package: str = None, window_title: str = None):
        super().__init__(name)
        self.app_package = app_package
        self.window_title = window_title
        self._connected = False
        
    def connect(self, hwnd: int = None) -> bool:
        """连接模拟器/APP"""
        self.logger.info(f"正在连接模拟器设备 [{self.name}] ...")
        
        if hwnd:
            self.hwnd = hwnd
            self.logger.info(f"绑定窗口句柄: {hwnd}")
        
        # TODO: 检查 ADB 连接或 窗口句柄
        if self.app_package:
             self.logger.info(f"目标应用包名: {self.app_package}")
             
        time.sleep(0.5)
        self._connected = True
        self.logger.info(f"模拟器设备 [{self.name}] 连接成功")
        return True
    
    def disconnect(self):
        """断开连接"""
        self._connected = False
        self.logger.info(f"模拟器设备 [{self.name}] 已断开")
        
    def execute(self, cmd_type: str, args: Dict[str, Any] = None) -> bool:
        """执行指令"""
        if not self._connected:
            self.logger.warning(f"设备 [{self.name}] 未连接，无法执行指令")
            return False
            
        self.logger.info(f"模拟器设备 [{self.name}] 执行指令: {cmd_type}, 参数: {args}")
        # TODO: 发送 ADB 指令 或 模拟点击
        time.sleep(0.2)
        return True
    
    def capture_window(self) -> Optional[np.ndarray]:
        """捕获窗口截图
        
        Returns:
            图像数组 (numpy.ndarray) 或 None
        """
        if not hasattr(self, 'hwnd') or not self.hwnd:
            self.logger.warning(f"[{self.name}] 未绑定窗口句柄，无法截图")
            return None
        
        try:
            from src.utils.window_capture import WindowCapture
            
            # 创建捕获对象
            capture = WindowCapture(self.hwnd)
            
            # 捕获图像
            pixmap = capture.capture()
            if pixmap and not pixmap.isNull():
                # 转换为 numpy 数组
                from PyQt6.QtGui import QImage
                import cv2
                
                # 转换为 QImage
                image = pixmap.toImage()
                
                # 转换为 numpy数组
                width = image.width()
                height = image.height()
                ptr = image.bits()
                ptr.setsize(height * width * 4)
                arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
                
                # 转换为 BGR (为OCR做准备)
                arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
                
                return arr
            else:
                self.logger.warning(f"[{self.name}] 截图失败")
                return None
                
        except Exception as e:
            self.logger.error(f"[{self.name}] 截图异常: {e}")
            return None
