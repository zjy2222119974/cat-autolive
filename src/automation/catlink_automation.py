
import time
import os
import logging
import numpy as np
from typing import Optional, Tuple
from src.utils.click_simulator import ClickSimulator # Added this import

logger = logging.getLogger(__name__)

class CatlinkAutomation:
    """Catlink喂食器自动化（模拟器版）"""
    
    def __init__(self, ocr_engine, device_config=None):
        """初始化
        
        Args:
            ocr_engine: OCR检测器实例
            device_config: 设备配置字典，包含模拟器路径和ADB端口等
        """
        self.ocr = ocr_engine
        self.clicker = ClickSimulator()
        self.device_config = device_config or {}
        self.target_size = (720, 1280)
        self.target_portions = 3
        
        # 准备ADB配置
        self.adb_config = {
            'emulator_path': self.device_config.get('emulator_path', ''),
            'adb_port': self.device_config.get('adb_port', 16384)
        }
        
    def _click_scaled(self, hwnd: int, x: int, y: int, actual_width: int, actual_height: int, delay: float = 0.5):
        """点击坐标 (支持ADB坐标缩放)
        
        ADB点击时会自动将Windows窗口坐标缩放到模拟器内部分辨率。
        例如：窗口444x830 → 模拟器720x1280
        """
        # 准备包含窗口尺寸的ADB配置
        adb_config_with_size = self.adb_config.copy()
        adb_config_with_size['window_width'] = actual_width
        adb_config_with_size['window_height'] = actual_height
        adb_config_with_size['target_width'] = self.device_config.get('target_width', 720)
        adb_config_with_size['target_height'] = self.device_config.get('target_height', 1280)
        
        logger.info(f"点击坐标: ({x}, {y}) [Window: {actual_width}x{actual_height}]")
        self.clicker.click_at_position(hwnd, x, y, delay=delay, adb_config=adb_config_with_size)
    
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
            # 已确认在One-标准版页面
            return True
        
        # 也可以检查是否有手动出粮
        manual_pos = self.ocr.find_text(screenshot, "手动出粮", fuzzy=True)
        if manual_pos:
             logger.info(f"✓ 找到 '手动出粮' (坐标: {manual_pos})，确认为操作页面")
             # 找到手动出粮，确认为操作页面
             return True
        
        # 打印当前所有文字
        all_text = self.ocr.get_all_text(screenshot)
        texts = [t[0] for t in all_text]
        logger.warning(f"页面检查失败。当前识别到的文字: {texts}")
        return False
        
    def _click_manual_feed(self, hwnd, capture_func) -> bool:
        """点击手动出粮按钮 (优先使用图片匹配)"""
        logger.info("查找 '手动出粮'...")
        screenshot = capture_func()
        
        # --- 方案A: 图片匹配 (优先) ---
        # 模板路径: src/resources/templates/catlink/BTN-shoudongchuliang.png
        # 注意：运行时路径可能需要根据 CWD 调整，这里假设 CWD 是项目根目录
        template_path = os.path.join("src", "resources", "templates", "catlink", "BTN-shoudongchuliang.png")
        
        # 转换 screenshot (PIL Image) 到 cv2 格式 (numpy)
        # capture_func 返回的是 numpy array (OpenCV格式) 还是 PIL? 
        # 查看 window_capture.py -> capture() 返回 QPixmap ? 
        # 等等，window_capture.py 返回的是 QPixmap。
        # 但是 simulator_driver.py 的 capture_window 可能做了转换。
        # 让我们检查一下传入的 screenshot 是什么类型。
        # 在 feeder_automation.py 中 screenshot.shape 被使用，说明是 numpy array (cv2 format).
        # 是的，SimulatorDriver.capture_window 返回 cv2 image.
        
        from src.utils.image_utils import ImageMatcher
        
        h, w = screenshot.shape[:2]
        
        # 为了加快速度，还是可以切 ROI，或者直接全屏找（图片匹配通常很快）
        # 既然用户担心按钮位置变动，我们先尝试全屏找，如果太慢再优化
        pos = ImageMatcher.find_image(screenshot, template_path, threshold=0.8)
        
        if pos:
            real_x, real_y = pos
            msg = f"✓ [图片匹配] 找到 '手动出粮', 坐标: ({real_x}, {real_y})"
            logger.info(msg)
            
            self._click_scaled(hwnd, real_x, real_y, w, h, delay=0.3)
            return True
            
        logger.warning("图片匹配未找到，尝试OCR兜底...")
        
        # --- 方案B: OCR 兜底 (全屏) ---
        # 虽然用户说文字识别不行，但作为最后一道防线还是留着吧
        pos = self.ocr.find_text(screenshot, "手动出粮", fuzzy=True)
        if pos:
            msg = f"✓ [OCR兜底] 找到 '手动出粮', 坐标: {pos}"
            logger.info(msg)
            self._click_scaled(hwnd, pos[0], pos[1], w, h, delay=0.3)
            return True
            
        # 打印所有识别到的文字，帮助调试
        all_text = self.ocr.get_all_text(screenshot)
        texts = [t[0] for t in all_text]
        logger.error(f"✗ 未找到 '手动出粮' 按钮 (图片+OCR均失败)。当前文字: {texts}")
        return False
        
    def _adjust_portions_and_confirm(self, hwnd, capture_func) -> bool:
        """调整份数并确认"""
        logger.info("等待出粮弹窗...")
        time.sleep(0.8)  # 等待弹窗加载
        
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
            
            time.sleep(0.2)
            
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
        """点击加号（使用图片匹配）"""
        from src.utils.image_utils import ImageMatcher
        
        # 使用传入的 ROI 避免重新截图
        if roi_info:
            offset_y, img = roi_info
        else:
            screenshot = capture_func()
            h, w = screenshot.shape[:2]
            offset_y = 0
            img = screenshot
            
        template_path = os.path.join("src", "resources", "templates", "catlink", "BTN-plus.png")
        pos = ImageMatcher.find_image(img, template_path, threshold=0.7)
        
        if pos:
            real_x = pos[0]
            real_y = pos[1] + offset_y
            h, w = img.shape[:2] if not roi_info else capture_func().shape[:2]
            logger.info(f"✓ [图片匹配] 找到加号按钮: ({real_x}, {real_y})")
            self._click_scaled(hwnd, real_x, real_y, w, h, delay=0.2)
            return True
        else:
            logger.warning("未找到加号按钮（图片匹配）")
            return False


    def _click_minus(self, hwnd, capture_func, roi_info=None) -> bool:
        """点击减号（使用图片匹配）"""
        from src.utils.image_utils import ImageMatcher
        
        # 使用传入的 ROI 避免重新截图
        if roi_info:
            offset_y, img = roi_info
        else:
            screenshot = capture_func()
            h, w = screenshot.shape[:2]
            offset_y = 0
            img = screenshot
            
        template_path = os.path.join("src", "resources", "templates", "catlink", "BTN-minus.png")
        pos = ImageMatcher.find_image(img, template_path, threshold=0.7)
        
        if pos:
            real_x = pos[0]
            real_y = pos[1] + offset_y
            h, w = img.shape[:2] if not roi_info else capture_func().shape[:2]
            logger.info(f"✓ [图片匹配] 找到减号按钮: ({real_x}, {real_y})")
            self._click_scaled(hwnd, real_x, real_y, w, h, delay=0.2)
            return True
        else:
            logger.warning("未找到减号按钮（图片匹配）")
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
            self._click_scaled(hwnd, real_x, real_y, w, h, delay=0.5)
            return True
        logger.error("未找到 '立即出粮'")
        return False
