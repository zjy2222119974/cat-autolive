"""冻干喂食器自动化脚本"""

import time
import logging
import numpy as np
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class FeederState(Enum):
    """喂食器状态"""
    UNKNOWN = "unknown"
    HOME_PAGE = "home"  # 首页
    FEEDER_PAGE = "feeder"  # 可视喂食器页面
    FEEDING_DIALOG = "feeding"  # 喂食份数弹窗
    COMPLETED = "completed"  # 完成

class FreezeDriedFeederAutomation:
    """冻干喂食器自动化控制"""
    
    def __init__(self, ocr_detector, click_simulator):
        """初始化
        
        Args:
            ocr_detector: OCR检测器实例
            click_simulator: 点击模拟器实例
        """
        self.ocr = ocr_detector
        self.clicker = click_simulator
        self.current_state = FeederState.UNKNOWN
        self.max_retries = 3
    
    def feed(self, hwnd: int, capture_func, portions: int = 1) -> bool:
        """执行喂食操作
        
        Args:
            hwnd: 窗口句柄
            capture_func: 窗口截图函数，返回numpy数组
            portions: 喂食份数（默认1份）
            
        Returns:
            是否成功
        """
        logger.info(f"开始自动喂食流程，目标份数: {portions}")
        
        try:
            # 步骤1: 导航到喂食份数弹窗
            if not self._navigate_to_feeding_dialog(hwnd, capture_func):
                logger.error("导航到喂食份数弹窗失败")
                return False
            
            # 步骤2: 选择份数并确认
            if not self._select_portions_and_confirm(hwnd, capture_func, portions):
                logger.error("选择份数并确认失败")
                return False
            
            logger.info("自动喂食流程完成")
            self.current_state = FeederState.COMPLETED
            return True
            
        except Exception as e:
            logger.error(f"自动喂食流程异常: {e}")
            return False
    
    def _navigate_to_feeding_dialog(self, hwnd: int, capture_func) -> bool:
        """导航到喂食份数弹窗
        
        逻辑：
        1. 优先查找"喂食份数"按钮，找到直接点击
        2. 如果没找到，判断当前页面状态：
           a) 首页场景：检测到"常用"+"首页" → 点击监控画面 → 点击"查看设备" → 找"喂食份数"
           b) 按钮隐藏场景：检测到"高清"或"清" → 点击画面中心 → 显示"喂食份数"
        
        Returns:
            是否成功
        """
        logger.info("="*60)
        logger.info("开始导航到喂食份数弹窗")
        logger.info("="*60)
        
        for attempt in range(self.max_retries):
            logger.info(f">>> 导航尝试 {attempt + 1}/{self.max_retries} <<<")
            
            # 截图
            screenshot = capture_func()
            if screenshot is None:
                logger.error("截图失败")
                time.sleep(1)
                continue
            
            # 执行一次OCR，获取所有文字
            all_text = self.ocr.get_all_text(screenshot)
            all_text_list = [t[0] for t in all_text]
            logger.info(f"当前页面识别到的文字: {all_text_list}")
            
            # 保存调试截图
            self._save_debug_screenshot(screenshot, attempt)
            
            # 【优先级1】直接查找"喂食份数" - 最高优先级
            logger.info("【优先级1】查找'喂食份数'按钮...")
            feeding_portions_pos = self._find_text_in_results(all_text, "喂食份数")
            
            if feeding_portions_pos:
                logger.info(f"✓✓✓ 找到'喂食份数'按钮，位置: {feeding_portions_pos} ✓✓✓")
                logger.info(f"准备点击位置: ({feeding_portions_pos[0]}, {feeding_portions_pos[1]})")
                self.clicker.click_at_position(hwnd, feeding_portions_pos[0], feeding_portions_pos[1], delay=0.5)
                logger.info("已发送点击指令")
                self.current_state = FeederState.FEEDING_DIALOG
                logger.info("="*60)
                logger.info("成功进入喂食份数弹窗")
                logger.info("="*60)
                return True
            else:
                logger.warning("✗ 未找到'喂食份数'按钮，开始判断页面状态...")
            
            # 【场景A】检测是否在首页
            # 主要标识："常用"（"首页"经常被OCR识别错误，不作为必要条件）
            # 辅助验证：底部导航按钮
            logger.info("【场景A】检测是否在首页...")
            has_changyong = self._find_text_in_results(all_text, "常用") is not None
            
            # 检测底部导航（作为辅助验证）
            has_xiaoxi = self._find_text_in_results(all_text, "消息") is not None
            has_paizhao = self._find_text_in_results(all_text, "拍照") is not None
            has_shezhi = self._find_text_in_results(all_text, "设置") is not None
            has_zhineng = self._find_text_in_results(all_text, "智能") is not None
            has_zhushou = self._find_text_in_results(all_text, "助手") is not None
            
            # 底部导航按钮数量
            bottom_nav_count = sum([has_xiaoxi, has_paizhao, has_shezhi, has_zhineng, has_zhushou])
            
            logger.info(f"  检测结果: 常用={has_changyong}")
            logger.info(f"  底部导航: 消息={has_xiaoxi}, 拍照={has_paizhao}, 设置={has_shezhi}, 智能={has_zhineng}, 助手={has_zhushou}")
            logger.info(f"  底部导航按钮数量: {bottom_nav_count}/5")
            
            # 判断：有"常用"且至少有2个底部导航按钮
            if has_changyong and bottom_nav_count >= 2:
                logger.info(f"✓ 检测到'常用'且有{bottom_nav_count}个底部导航按钮，确认当前在首页")
                
                # 点击监控画面区域（在底部按钮上方）
                # 假设画面在屏幕中上部，点击中心偏上位置
                logger.info("  点击监控画面区域...")
                screenshot_height, screenshot_width = screenshot.shape[:2]
                click_x = screenshot_width // 2
                click_y = screenshot_height // 3  # 上方1/3处
                
                self.clicker.click_at_position(hwnd, click_x, click_y, delay=1.0)
                time.sleep(1)
                
                # 重新截图，查找"查看设备"按钮
                screenshot = capture_func()
                all_text = self.ocr.get_all_text(screenshot)
                all_text_list = [t[0] for t in all_text]
                logger.info(f"  点击后识别到的文字: {all_text_list}")
                
                view_device_pos = self._find_text_in_results(all_text, "查看设备")
                if view_device_pos:
                    logger.info(f"  ✓ 找到'查看设备'按钮，位置: {view_device_pos}")
                    self.clicker.click_at_position(hwnd, view_device_pos[0], view_device_pos[1], delay=1.0)
                    time.sleep(2)
                    
                    # 进入设备页面后，再次查找"喂食份数"
                    screenshot = capture_func()
                    all_text = self.ocr.get_all_text(screenshot)
                    all_text_list = [t[0] for t in all_text]
                    logger.info(f"  进入设备页面后识别到的文字: {all_text_list}")
                    
                    feeding_portions_pos = self._find_text_in_results(all_text, "喂食份数")
                    if feeding_portions_pos:
                        logger.info(f"  ✓ 在设备页面找到'喂食份数'，位置: {feeding_portions_pos}")
                        self.clicker.click_at_position(hwnd, feeding_portions_pos[0], feeding_portions_pos[1], delay=0.5)
                        self.current_state = FeederState.FEEDING_DIALOG
                        return True
                    else:
                        logger.warning("  ✗ 进入设备页面后仍未找到'喂食份数'")
                        continue
                else:
                    logger.warning("  ✗ 未找到'查看设备'按钮")
                    continue
            
            # 【场景B】检测按钮是否被隐藏（静止太久，检测"高清"或"清"）
            logger.info("【场景B】检测按钮是否被隐藏...")
            has_gaoqing = self._find_text_in_results(all_text, "高清") is not None
            has_qing = self._find_text_in_results(all_text, "清") is not None
            
            if has_gaoqing or has_qing:
                logger.info(f"✓ 检测到画质标识（高清={has_gaoqing}, 清={has_qing}），判断按钮可能被隐藏")
                logger.info("  点击画面中心以显示按钮...")
                
                # 点击画面中心
                screenshot_height, screenshot_width = screenshot.shape[:2]
                click_x = screenshot_width // 2
                click_y = screenshot_height // 2
                
                self.clicker.click_at_position(hwnd, click_x, click_y, delay=1.0)
                time.sleep(1)
                
                # 重新截图，查找"喂食份数"
                screenshot = capture_func()
                all_text = self.ocr.get_all_text(screenshot)
                all_text_list = [t[0] for t in all_text]
                logger.info(f"  点击后识别到的文字: {all_text_list}")
                
                feeding_portions_pos = self._find_text_in_results(all_text, "喂食份数")
                if feeding_portions_pos:
                    logger.info(f"  ✓ 按钮已显示，找到'喂食份数'，位置: {feeding_portions_pos}")
                    self.clicker.click_at_position(hwnd, feeding_portions_pos[0], feeding_portions_pos[1], delay=0.5)
                    self.current_state = FeederState.FEEDING_DIALOG
                    return True
                else:
                    logger.warning("  ✗ 点击后仍未找到'喂食份数'")
                    continue
            
            # 所有场景都未匹配
            logger.warning(f"✗ 无法识别当前页面状态")
            logger.warning(f"第 {attempt + 1} 次尝试失败，等待后重试...")
            time.sleep(2)
        
        logger.error("导航失败，已达最大重试次数")
        logger.error("请确保APP已打开并位于以下页面之一：")
        logger.error("  1. 首页（能看到'常用'和'首页'）")
        logger.error("  2. 设备监控页面（能看到'喂食份数'或'高清'/'清'）")
        return False
    
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
            self.clicker.click_at_position(hwnd, pos[0], pos[1], delay=0.5)
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
            self.clicker.click_at_position(hwnd, pos[0], pos[1], delay=1.0)
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
