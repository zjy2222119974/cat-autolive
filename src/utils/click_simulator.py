"""点击模拟工具"""

import win32gui
import win32con
import win32api
import time
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class ClickSimulator:
    """模拟器窗口点击模拟器"""
    
    @staticmethod
    def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
        """获取窗口矩形区域
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            (left, top, right, bottom)
        """
        try:
            rect = win32gui.GetWindowRect(hwnd)
            return rect
        except Exception as e:
            logger.error(f"获取窗口矩形失败: {e}")
            return (0, 0, 0, 0)
    
    @staticmethod
    def get_client_rect(hwnd: int) -> Tuple[int, int, int, int]:
        """获取窗口客户区矩形
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            (left, top, right, bottom) 相对于窗口左上角
        """
        try:
            rect = win32gui.GetClientRect(hwnd)
            return rect
        except Exception as e:
            logger.error(f"获取客户区矩形失败: {e}")
            return (0, 0, 0, 0)
    
    @staticmethod
    def client_to_screen(hwnd: int, x: int, y: int) -> Tuple[int, int]:
        """将窗口客户区坐标转换为屏幕坐标
        
        Args:
            hwnd: 窗口句柄
            x: 客户区x坐标
            y: 客户区y坐标
            
        Returns:
            (screen_x, screen_y)
        """
        try:
            point = win32gui.ClientToScreen(hwnd, (x, y))
            return point
        except Exception as e:
            logger.error(f"坐标转换失败: {e}")
            return (x, y)
    
    @staticmethod
    def click_at_position(hwnd: int, x: int, y: int, delay: float = 0.1):
        """在窗口的指定位置点击（客户区坐标）
        
        Args:
            hwnd: 窗口句柄
            x: 客户区x坐标
            y: 客户区y坐标
            delay: 点击后延迟时间（秒）
        """
        try:
            # 转换为屏幕坐标
            screen_x, screen_y = ClickSimulator.client_to_screen(hwnd, x, y)
            
            logger.info(f"点击位置: 客户区({x}, {y}) -> 屏幕({screen_x}, {screen_y})")
            
            # 保存当前鼠标位置
            old_pos = win32api.GetCursorPos()
            
            # 移动鼠标到目标位置
            win32api.SetCursorPos((screen_x, screen_y))
            time.sleep(0.05)
            
            # 模拟鼠标左键按下和释放
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0)
            
            # 延迟
            time.sleep(delay)
            
            # 恢复鼠标位置
            win32api.SetCursorPos(old_pos)
            
            logger.info(f"点击完成")
            
        except Exception as e:
            logger.error(f"点击失败: {e}")
    
    @staticmethod
    def click_at_screen_position(screen_x: int, screen_y: int, delay: float = 0.1):
        """在屏幕的指定位置点击（屏幕坐标）
        
        Args:
            screen_x: 屏幕x坐标
            screen_y: 屏幕y坐标
            delay: 点击后延迟时间（秒）
        """
        try:
            logger.info(f"点击屏幕位置: ({screen_x}, {screen_y})")
            
            # 保存当前鼠标位置
            old_pos = win32api.GetCursorPos()
            
            # 移动鼠标到目标位置
            win32api.SetCursorPos((screen_x, screen_y))
            time.sleep(0.05)
            
            # 模拟鼠标左键按下和释放
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0)
            
            # 延迟
            time.sleep(delay)
            
            # 恢复鼠标位置
            win32api.SetCursorPos(old_pos)
            
            logger.info(f"点击完成")
            
        except Exception as e:
            logger.error(f"点击失败: {e}")
    
    @staticmethod
    def double_click_at_position(hwnd: int, x: int, y: int, delay: float = 0.1):
        """在窗口的指定位置双击
        
        Args:
            hwnd: 窗口句柄
            x: 客户区x坐标
            y: 客户区y坐标
            delay: 双击后延迟时间（秒）
        """
        ClickSimulator.click_at_position(hwnd, x, y, delay=0.05)
        ClickSimulator.click_at_position(hwnd, x, y, delay=delay)
