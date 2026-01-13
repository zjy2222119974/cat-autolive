"""冻干喂食器自动化脚本"""

import time
import logging
import numpy as np
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class FeederState(Enum):
    UNKNOWN = 0
    MAIN_PAGE = 1
    FEEDING_DIALOG = 2

class FreezeDriedFeederAutomation:
    """冻干喂食器自动化控制"""
    
    def __init__(self, ocr_detector, click_simulator, target_size: Tuple[int, int] = (720, 1280)):
        """初始化
        
        Args:
            ocr_detector: OCR检测器实例
            click_simulator: 点击模拟器实例
            target_size: 目标分辨率 (暂不强制缩放)
        """
        self.ocr = ocr_detector
        self.clicker = click_simulator
        self.target_size = target_size
        self.current_state = FeederState.UNKNOWN
        self.max_retries = 3
    
    def feed_manual(self, hwnd: int, portions: int, capture_func) -> bool:
        """执行手动喂食流程"""
        try:
            logger.info(f"=== 开始冻干喂食器自动喂食流程 (目标: {portions}份) ===")
            self.current_state = FeederState.UNKNOWN
            
            # 1. 确保在设备详情页或进入设备详情页
            if not self._ensure_device_page(hwnd, capture_func):
                logger.error("未能进入设备详情页")
                return False
                
            # 2. 点击喂食按钮，弹出选择框
            # 查找 "喂食份数" 或 "手动投喂" 按钮
            if not self._navigate_to_feeding_dialog(hwnd, capture_func):
                logger.error("未能打开喂食对话框")
                return False
                
            # 3. 选择份数
            if not self._select_portions(hwnd, portions, capture_func):
                logger.error("选择份数失败")
                return False
                
            # 4. 确认喂食
            if not self._confirm_feeding(hwnd, capture_func):
                logger.error("确认喂食失败")
                return False
                
            logger.info("=== 冻干喂食器自动喂食成功 ===")
            return True
            
        except Exception as e:
            logger.error(f"自动喂食流程异常: {e}")
            return False
    
    def _click_scaled(self, hwnd: int, x: int, y: int, actual_width: int, actual_height: int, delay: float = 0.5):
        """点击坐标 (针对 PostMessage 优化: 不强制缩放)"""
        # 不再使用 target_size 强制缩放，直接使用识别到的坐标
        target_x = x
        target_y = y
        logger.info(f"点击坐标: ({x}, {y})")
        self.clicker.click_at_position(hwnd, target_x, target_y, delay=delay)

    def _navigate_to_feeding_dialog(self, hwnd: int, capture_func) -> bool:
        """导航到喂食份数弹窗"""
        logger.info("寻找喂食入口...")
        
        screenshot = capture_func()
        if screenshot is None:
            return False
            
        h, w = screenshot.shape[:2]
        
        # 优化：优先检查下半部分
        roi_y = int(h * 0.4)
        roi = screenshot[roi_y:, :]
        
        # 尝试查找 "喂食份数"
        pos = self.ocr.find_text(roi, "喂食份数", fuzzy=True)
        if pos:
            real_x, real_y = pos[0], pos[1] + roi_y
            logger.info(f"✓ 找到 '喂食份数'，点击: ({real_x}, {real_y})")
            self._click_scaled(hwnd, real_x, real_y, w, h, delay=0.5)
            self.current_state = FeederState.FEEDING_DIALOG
            return True
            
        # 尝试 "手动投喂"
        pos = self.ocr.find_text(roi, "手动投喂", fuzzy=True)
        if pos:
            real_x, real_y = pos[0], pos[1] + roi_y
            logger.info(f"✓ 找到 '手动投喂'，点击: ({real_x}, {real_y})")
            self._click_scaled(hwnd, real_x, real_y, w, h, delay=0.5)
            self.current_state = FeederState.FEEDING_DIALOG
            return True

        logger.warning("未找到喂食入口")
        return False
    
    def _ensure_device_page(self, hwnd: int, capture_func) -> bool:
        """确保在设备页面"""
        # 简单实现：我们假设已经在设备页面，或者通过"查看设备"进入
        # 这里简化处理，直接返回True，因为 _navigate_to_feeding_dialog 会做实际检查
        # 如果需要更复杂的导航逻辑，参考 Catlink 实现
        return True

    def _select_portions(self, hwnd: int, portions: int, capture_func) -> bool:
        """选择份数"""
        logger.info(f"选择份数: {portions}")
        time.sleep(1.0) # 等待弹窗
        
        screenshot = capture_func()
        h, w = screenshot.shape[:2]
        
        # 假设份数选项在底部弹窗
        roi_y = int(h * 0.5)
        roi = screenshot[roi_y:, :]
        
        # 查找对应数字的选项
        target_text = f"{portions}份" # 或者只是数字 "1", "2"
        
        # 先试带单位的
        pos = self.ocr.find_text(roi, target_text, fuzzy=True)
        if not pos:
             # 再试纯数字 (需要精确匹配)
             # 这里比较难，单纯找 "1" 可能会找到时间或者其他数字
             # 假设界面上有 "1份" "2份"...
             pass
             
        if not pos:
             # 尝试直接找 "portions" 数字
             # 这部分逻辑需要根据实际UI调整
             logger.warning(f"未找到 '{target_text}'，尝试模糊查找")
             pass
        
        if pos:
            real_x, real_y = pos[0], pos[1] + roi_y
            logger.info(f"✓ 找到选项 '{target_text}'，点击: ({real_x}, {real_y})")
            self._click_scaled(hwnd, real_x, real_y, w, h, delay=0.5)
            return True
            
        # 如果还没找到，可能是滑轮选择？
        # 暂时只支持点击式选择
        logger.error(f"无法选择份数 {portions}")
        return False
        
    def _confirm_feeding(self, hwnd: int, capture_func) -> bool:
        """点击确认/投喂"""
        logger.info("查找确认按钮...")
        screenshot = capture_func()
        h, w = screenshot.shape[:2]
        roi_y = int(h * 0.6)
        roi = screenshot[roi_y:, :]
        
        # 常见的确认文字
        confirm_texts = ["投喂", "确认", "确定", "立即投喂", "出粮"]
        
        for text in confirm_texts:
            pos = self.ocr.find_text(roi, text, fuzzy=True)
            if pos:
                real_x, real_y = pos[0], pos[1] + roi_y
                logger.info(f"✓ 找到确认按钮 '{text}'，点击: ({real_x}, {real_y})")
                self._click_scaled(hwnd, real_x, real_y, w, h, delay=0.2)
                return True

    
    def _find_text_in_results(self, all_text: list, target: str) -> Optional[Tuple[int, int]]:
        """在OCR结果中查找目标文字
        
        Args:
            all_text: OCR结果列表 [(文字, (x, y), 置信度), ...]
            target: 目标文字
            
        Returns:
            文字位置 (x, y) 或 None
        """
        # 去除目标文字的空格
        target_stripped = target.replace(" ", "").replace("\u3000", "")
        
        for text, pos, confidence in all_text:
            # 去除识别文字的空格
            text_stripped = text.replace(" ", "").replace("\u3000", "")
            
            # 模糊匹配
            matched = (target_stripped in text_stripped or 
                      text_stripped in target_stripped or
                      target in text or 
                      text in target)
            
            if matched and confidence >= 0.3:  # 降低置信度阈值
                logger.info(f"  匹配成功: 目标='{target}' 实际='{text}' 置信度={confidence:.3f}")
                return pos
        
        return None
    
    def _save_debug_screenshot(self, screenshot: np.ndarray, attempt: int):
        """保存调试截图
        
        Args:
            screenshot: 截图数组
            attempt: 尝试次数
        """
        try:
            import cv2
            import os
            from datetime import datetime
            
            # 创建调试目录
            debug_dir = "g:/CODE/cat-autolive/debug_screenshots"
            os.makedirs(debug_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nav_fail_{timestamp}_attempt{attempt + 1}.png"
            filepath = os.path.join(debug_dir, filename)
            
            # 保存截图
            cv2.imwrite(filepath, screenshot)
            logger.info(f"调试截图已保存: {filepath}")
            
        except Exception as e:
            logger.error(f"保存调试截图失败: {e}")
    
    def _select_portions_and_confirm(self, hwnd: int, capture_func, portions: int) -> bool:
        """选择份数并确认
        
        Args:
            portions: 份数
            
        Returns:
            是否成功
        """
        logger.info("="*60)
        logger.info(f">>> 步骤2: 选择份数并确认 (目标份数: {portions}) <<<")
        logger.info("="*60)
        
        # 等待弹窗完全显示
        logger.info("等待弹窗完全显示（1秒）...")
        time.sleep(1)
        
        # 截图
        screenshot = capture_func()
        if screenshot is None:
            logger.error("截图失败")
            return False
        
        # 获取所有识别的文字
        all_text = self.ocr.get_all_text(screenshot)
        all_text_list = [t[0] for t in all_text]
        logger.info(f"弹窗中识别到的文字: {all_text_list}")
        logger.info(f"详细信息: {[(text, conf) for text, pos, conf in all_text]}")
        
        # 查找份数选项（例如"1 份"、"2 份"等）
        portion_str = str(portions)
        pos = None
        
        # 首先尝试完整匹配 "X 份"
        portion_text = f"{portions} 份"
        logger.info(f"方法1: 尝试查找完整文字 '{portion_text}'...")
        pos = self.ocr.find_text(screenshot, portion_text, fuzzy=True)
        
        if not pos:
            logger.info(f"✗ 未找到'{portion_text}'")
            # 如果没找到，尝试只搜索数字
            logger.info(f"方法2: 尝试搜索数字 '{portion_str}'...")
            
            # 在所有识别的文字中查找包含数字的项
            for text, (x, y), confidence in all_text:
                logger.info(f"  检查文字: '{text}' (置信度={confidence:.3f})")
                if portion_str in text:
                    pos = (x, y)
                    logger.info(f"  ✓ 在文字'{text}'中找到数字{portion_str}，位置: ({x}, {y})")
                    break
                else:
                    logger.info(f"  ✗ '{portion_str}' 不在 '{text}' 中")
        else:
            logger.info(f"✓ 找到完整文字 '{portion_text}'，位置: {pos}")
        
        if pos:
            logger.info(f">>> 找到份数选项，准备点击位置: ({pos[0]}, {pos[1]}) <<<")
            h, w = screenshot.shape[:2]
            self._click_scaled(hwnd, pos[0], pos[1], w, h, delay=0.5)
            logger.info("已发送点击指令")
        else:
            logger.error(f"✗✗✗ 未找到份数选项'{portions}' ✗✗✗")
            logger.error("可能的原因:")
            logger.error("  1. OCR未能识别到份数文字")
            logger.error("  2. 弹窗未完全显示")
            logger.error("  3. 页面状态不正确")
            return False
        
        # 等待一下
        logger.info("等待0.5秒...")
        time.sleep(0.5)
        
        # 重新截图查找"确认"按钮
        logger.info("查找'确认'按钮...")
        screenshot = capture_func()
        pos = self.ocr.find_text(screenshot, "确认", fuzzy=True)
        
        if pos:
            logger.info(f"✓ 找到'确认'按钮，位置: {pos}")
            logger.info(f"✓ 找到'确认'按钮，位置: {pos}")
            h, w = screenshot.shape[:2]
            self._click_scaled(hwnd, pos[0], pos[1], w, h, delay=1.0)
            logger.info("已点击'确认'按钮")
            logger.info("="*60)
            logger.info("份数选择并确认完成")
            logger.info("="*60)
            return True
        else:
            logger.error("✗ 未找到'确认'按钮")
            return False
    
    def detect_current_state(self, screenshot: np.ndarray) -> FeederState:
        """检测当前界面状态
        
        Args:
            screenshot: 截图
            
        Returns:
            当前状态
        """
        # 检测关键词
        if self.ocr.find_text(screenshot, "喂食份数", fuzzy=True):
            return FeederState.FEEDING_DIALOG
        elif self.ocr.find_text(screenshot, "可视喂食器", fuzzy=True):
            return FeederState.FEEDER_PAGE
        elif self.ocr.find_text(screenshot, "首页", fuzzy=True):
            return FeederState.HOME_PAGE
        else:
            return FeederState.UNKNOWN
