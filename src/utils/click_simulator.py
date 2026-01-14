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
    def click_at_position(hwnd: int, x: int, y: int, delay: float = 0.1, adb_config=None):
        """在窗口的指定位置点击（支持ADB和Windows消息）
        
        Args:
            hwnd: 窗口句柄
            x: 客户区x坐标
            y: 客户区y坐标
            delay: 点击后延迟时间（秒）
            adb_config: ADB配置字典，包含 {'emulator_path': str, 'adb_port': int}
        """
        # 如果提供了ADB配置且模拟器路径不为空，使用ADB
        if adb_config and adb_config.get('emulator_path'):
            return ClickSimulator._click_via_adb(x, y, delay, adb_config)
        else:
            # 降级到Windows消息
            return ClickSimulator._click_via_windows_message(hwnd, x, y, delay)
    
    @staticmethod
    def _click_via_adb(x: int, y: int, delay: float, adb_config: dict):
        """使用ADB发送点击命令（真正的后台点击）"""
        import subprocess
        import os
        
        try:
            # 获取ADB路径
            adb_path_file = "adb_path.txt"
            if os.path.exists(adb_path_file):
                with open(adb_path_file, 'r', encoding='utf-8') as f:
                    adb_exe = f.read().strip()
            else:
                # 默认使用项目内的ADB
                adb_exe = os.path.join("platform-tools", "adb.exe")
            
            if not os.path.exists(adb_exe):
                logger.error(f"ADB not found: {adb_exe}")
                return False
            
            # 坐标转换：从Windows窗口尺寸 → 模拟器内部分辨率
            window_width = adb_config.get('window_width', 1)
            window_height = adb_config.get('window_height', 1)
            target_width = adb_config.get('target_width', 720)
            target_height = adb_config.get('target_height', 1280)
            
            # 计算缩放比例
            scale_x = target_width / window_width
            scale_y = target_height / window_height
            
            # 转换坐标
            scaled_x = int(x * scale_x)
            scaled_y = int(y * scale_y)
            
            adb_port = adb_config.get('adb_port', 16384)
            device_addr = f"127.0.0.1:{adb_port}"
            
            logger.info(f"ADB点击: Device={device_addr}")
            logger.info(f"  原始坐标: ({x}, {y}) [窗口: {window_width}x{window_height}]")
            logger.info(f"  缩放坐标: ({scaled_x}, {scaled_y}) [模拟器: {target_width}x{target_height}]")
            
            # 1. 确保连接到设备
            connect_cmd = [adb_exe, "connect", device_addr]
            subprocess.run(connect_cmd, capture_output=True, timeout=2)
            
            # 2. 发送点击命令（使用缩放后的坐标）
            tap_cmd = [adb_exe, "-s", device_addr, "shell", "input", "tap", str(scaled_x), str(scaled_y)]
            result = subprocess.run(tap_cmd, capture_output=True, text=True, timeout=1.5)
            
            if result.returncode == 0:
                logger.info(f"✓ ADB点击成功")
                time.sleep(delay)
                return True
            else:
                logger.error(f"ADB点击失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"ADB点击出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def _click_via_windows_message(hwnd: int, x: int, y: int, delay: float):
        """使用Windows消息发送点击（兼容性fallback）"""
        try:
            lparam = (y << 16) | (x & 0xFFFF)
            
            logger.info(f"Windows消息点击: HWND={hwnd} Pos=({x}, {y})")
            
            # 发送完整的消息序列
            try:
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.05)
            except:
                pass
            
            win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
            time.sleep(0.02)
            
            win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
            time.sleep(0.05)
            
            win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
            time.sleep(0.02)
            
            logger.info("Windows消息点击完成")
            time.sleep(delay)
            return True
            
        except Exception as e:
            logger.error(f"Windows消息点击失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
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
