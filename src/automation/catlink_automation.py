
import time
import logging
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class CatlinkAutomation:
    """Catlink 喂食器自动化控制"""
    
    def __init__(self, ocr_detector, click_simulator, target_size: Tuple[int, int] = (720, 1280)):
        """初始化
        
        Args:
            ocr_detector: OCR检测器实例
            click_simulator: 点击模拟器实例
            target_size: 目标分辨率 (暂不用于 PostMessage 强制缩放，除非需要)
        """
        self.ocr = ocr_detector
        self.clicker = click_simulator
        self.target_size = target_size
        self.target_portions = 3
        
    def _click_scaled(self, hwnd: int, x: int, y: int, actual_width: int, actual_height: int, delay: float = 0.5):
        """点击坐标 (针对 PostMessage 优化)
        
        注意: PostMessage 通常使用窗口客户端坐标。
        如果截图也是来自 WindowCapture (基于 PrintWindow/BitBlt)，截图尺寸通常等于客户端尺寸。
        此时不应强制缩放到 'target_size' (如 720x1280)，否则会导致坐标偏移。
        除非截图是高DPI (2x) 而窗口坐标是 1x。
        """
        # 暂时禁用强制缩放到 target_size，因为观察到用户窗口只有 480x815，缩放到 720 会偏离
        # 如果需要处理 DPI 缩放，应该比较 actual_width 和 窗口实际 client_width
        
        target_x = x
        target_y = y
        
        # 简单的 DPI 处理逻辑: 如果截图非常大 (>2000)，可能是 2k/4k 屏，可能需要缩小
        # 但目前日志显示 Actual 480x815，这是逻辑像素，直接点击即可
        
        logger.info(f"点击坐标: ({x}, {y}) [Window Size: {actual_width}x{actual_height}]")
        self.clicker.click_at_position(hwnd, target_x, target_y, delay=delay)
    
    def feed(self, hwnd: int, capture_func) -> bool:
        """执行Catlink喂食流程
        
        Args:
            hwnd: 窗口句柄
            capture_func: 截图函数
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("=== 开始 Catlink 自动喂食流程 ===")
            
            # 1. 检查当前页面
            if not self._check_page(capture_func):
                logger.error("当前页面不对，终止操作")
                return False
                
            # 2. 点击 "手动出粮"
            if not self._click_manual_feed(hwnd, capture_func):
                logger.error("点击手动出粮失败")
                return False
                
            # 3. 调整份数并出粮
            if not self._adjust_portions_and_confirm(hwnd, capture_func):
                logger.error("调整份数或确认出粮失败")
                return False
                
            logger.info("=== Catlink 自动喂食成功 ===")
            return True
            
        except Exception as e:
            logger.error(f"Catlink 自动化异常: {e}")
            return False
            
    def _check_page(self, capture_func) -> bool:
        """检查当前页面"""
        logger.info("检查页面...")
        screenshot = capture_func()
        if screenshot is None:
            return False
            
        # 优化：只检查顶部区域
        h, w = screenshot.shape[:2]
        # top_roi = screenshot[0:int(h*0.3), 0:w] 
        
        pos = self.ocr.find_text(screenshot, "One-标准版", fuzzy=True)
        if pos:
            logger.info(f"✓ 确认在 One-标准版 页面 (坐标: {pos})")
            return True
        
        # 也可以检查是否有手动出粮
        manual_pos = self.ocr.find_text(screenshot, "手动出粮", fuzzy=True)
        if manual_pos:
             logger.info(f"✓ 找到 '手动出粮' (坐标: {manual_pos})，确认为操作页面")
             return True
        
        # 打印当前所有文字
        all_text = self.ocr.get_all_text(screenshot)
        texts = [t[0] for t in all_text]
        logger.warning(f"页面检查失败。当前识别到的文字: {texts}")
        return False
        
    def _click_manual_feed(self, hwnd, capture_func) -> bool:
        """点击手动出粮按钮"""
        logger.info("查找 '手动出粮'...")
        screenshot = capture_func()
        
        # 优化：通常在底部，裁剪下半部分进行识别，提高速度
        h, w = screenshot.shape[:2]
        roi_y = int(h * 0.4)
        roi = screenshot[roi_y:, :]
        
        pos = self.ocr.find_text(roi, "手动出粮", fuzzy=True)
        if pos:
            # 还原坐标
            real_x = pos[0]
            real_y = pos[1] + roi_y
            
            logger.info(f"✓ 找到 '手动出粮' (ROI), 原始坐标: {pos}, 全局坐标: ({real_x}, {real_y})")
            logger.info(f"  准备点击: ({real_x}, {real_y}) of {w}x{h}")
            
            self._click_scaled(hwnd, real_x, real_y, w, h, delay=0.8) # 减少延迟
            return True
            
        logger.warning(f"ROI区域 (y={roi_y}~{h}) 未找到 '手动出粮'，尝试全屏搜索...")
        
        # 尝试全屏搜索
        pos = self.ocr.find_text(screenshot, "手动出粮", fuzzy=True)
        if pos:
            logger.info(f"✓ 找到 '手动出粮' (全屏), 坐标: {pos}")
            self._click_scaled(hwnd, pos[0], pos[1], w, h, delay=0.8)
            return True
            
        # 打印所有识别到的文字，帮助调试
        all_text = self.ocr.get_all_text(screenshot)
        texts = [t[0] for t in all_text]
        logger.error(f"✗ 未找到 '手动出粮' 按钮。当前页面识别到的文字: {texts}")
        return False
        
    def _adjust_portions_and_confirm(self, hwnd, capture_func) -> bool:
        """调整份数并确认"""
        logger.info("等待出粮弹窗...")
        time.sleep(1.0) # 减少等待
        
        max_attempts = 8
        for i in range(max_attempts):
            screenshot = capture_func()
            h, w = screenshot.shape[:2]
            
            # ROI: 弹窗通常在屏幕中间，或者是下半部分
            # 截取中间区域以加速
            roi_y1 = int(h * 0.3)
            roi_y2 = int(h * 0.8)
            roi = screenshot[roi_y1:roi_y2, :]
            
            # 在 ROI 中查找
            current_portions_data = self._get_current_portions(roi)
            
            if current_portions_data is None:
                if i > 2: # 几次没找到再报错
                    logger.warning("无法识别份数")
                continue
                
            current_portions, center_pos = current_portions_data
            # 还原 center_pos
            center_pos = (center_pos[0], center_pos[1] + roi_y1)
            
            logger.info(f"当前份数: {current_portions}, 目标: {self.target_portions}")
            
            if current_portions == self.target_portions:
                logger.info("份数正确，点击 '立即出粮'")
                return self._click_feed_now(hwnd, capture_func)
                
            # 需要调整
            diff = self.target_portions - current_portions
            if diff > 0:
                logger.info("需要增加 (+)")
                if not self._click_plus(hwnd, capture_func, roi_info=(roi_y1, roi)):
                    return False
            else:
                logger.info("需要减少 (-)")
                if not self._click_minus(hwnd, capture_func, roi_info=(roi_y1, roi)):
                    return False
            
            time.sleep(0.3) 
            
        logger.error("调整份数超时")
        return False
        
    def _get_current_portions(self, img) -> Optional[Tuple[int, Tuple[int, int]]]:
        """识别当前份数
        Returns: (portions_count, (x, y))
        """
        all_text = self.ocr.get_all_text(img)
        
        # 打印调试信息
        texts_found = [t[0] for t in all_text]
        logger.info(f"  [份数识别] 弹窗区域文字: {texts_found}")
        
        candidates = []
        for text, pos, conf in all_text:
            text = text.strip()
            # 匹配 1-30 的数字
            if text.isdigit():
                val = int(text)
                if 1 <= val <= 30:
                    candidates.append((val, pos))
            elif "份" in text: # 例如 "5份"
                import re
                m = re.search(r'(\d+)', text)
                if m:
                    val = int(m.group(1))
                    if 1 <= val <= 30:
                        candidates.append((val, pos))
        
        if not candidates:
            return None
            
        # 找最靠近中心的数字
        h, w = img.shape[:2]
        cx, cy = w // 2, h // 2
        
        best_cand = None
        min_dist = float('inf')
        best_val = 0
        
        for val, (x, y) in candidates:
            dist = (x - cx)**2 + (y - cy)**2
            if dist < min_dist:
                min_dist = dist
                best_cand = (x, y)
                best_val = val
                
        if best_cand:
            return best_val, best_cand
        return None

    def _click_plus(self, hwnd, capture_func, roi_info=None) -> bool:
        """点击加号"""
        # 使用传入的 ROI 避免重新截图
        if roi_info:
            offset_y, img = roi_info
        else:
            screenshot = capture_func()
            h, w = screenshot.shape[:2]
            offset_y = 0
            img = screenshot
            
        pos = self.ocr.find_text(img, "+", fuzzy=True)
        if not pos:
             pos = self.ocr.find_text(img, "＋", fuzzy=True)
             
        if pos:
            # 还原坐标
            real_x = pos[0]
            real_y = pos[1] + offset_y
            # 为了获取全屏尺寸，我们需要 capture_func 或者保存
            # 优化：_click_scaled 不需要 actual_size 除非我们做 scaling. 
            # 既然我们禁用了 scaling，传 0,0 也行，但为了日志好看，我们重构下
            
            self._click_scaled(hwnd, real_x, real_y, 0, 0, delay=0.2)
            return True
            
        # 找不到 + 号，使用 Blind Click (基于数字位置右侧)
        # 获取数字位置
        curr = self._get_current_portions(img)
        if curr:
            _, (nx, ny) = curr
            # 假设 + 号在数字右侧 100 像素 (需要适配分辨率?)
            # 480 宽度的屏幕，100 像素很大。可能 60-80 够了
            offset = 80 
            target_x = nx + offset
            target_y = ny + offset_y
            self._click_scaled(hwnd, target_x, target_y, 0, 0, delay=0.2)
            return True
            
        return False

    def _click_minus(self, hwnd, capture_func, roi_info=None) -> bool:
        if roi_info:
            offset_y, img = roi_info
        else:
            screenshot = capture_func()
            offset_y = 0
            img = screenshot
        
        pos = self.ocr.find_text(img, "-", fuzzy=True)
        if not pos:
             pos = self.ocr.find_text(img, "－", fuzzy=True)
             
        if pos:
            real_x = pos[0]
            real_y = pos[1] + offset_y
            self._click_scaled(hwnd, real_x, real_y, 0, 0, delay=0.2)
            return True
            
        curr = self._get_current_portions(img)
        if curr:
            _, (nx, ny) = curr
            offset = 80
            target_x = nx - offset
            target_y = ny + offset_y
            self._click_scaled(hwnd, target_x, target_y, 0, 0, delay=0.2)
            return True
            
        return False
        
    def _click_feed_now(self, hwnd, capture_func) -> bool:
        """点击立即出粮"""
        screenshot = capture_func()
        
        # 优化：只看下半部分
        h, w = screenshot.shape[:2]
        roi_y = int(h * 0.5)
        roi = screenshot[roi_y:, :]
        
        pos = self.ocr.find_text(roi, "立即出粮", fuzzy=True)
        if pos:
            real_x = pos[0]
            real_y = pos[1] + roi_y
            self._click_scaled(hwnd, real_x, real_y, w, h, delay=1.0)
            return True
        logger.error("未找到 '立即出粮'")
        return False
