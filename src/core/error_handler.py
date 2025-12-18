"""异常处理模块"""

import time
from typing import Dict, Callable, Optional

from src.utils.logger import get_logger
from src.core.state_manager import StateManager, SystemState


class ErrorHandler:
    """
    异常处理中心
    负责捕获异常、统计错误频率、触发自愈策略
    """
    
    def __init__(self, state_manager: StateManager):
        self.logger = get_logger()
        self.state_manager = state_manager
        
        # 错误计数
        self._error_counts: Dict[str, int] = {}
        self._last_error_time: Dict[str, float] = {}
        
        # 阈值配置
        self.error_threshold = 3      # 连续错误阈值
        self.reset_interval = 60.0    # 错误计数重置时间(秒)
        
        # 自愈回调
        self._recovery_strategies: Dict[str, Callable[[], bool]] = {}
        
        self.logger.info("异常处理中心初始化完成")
    
    def report_error(self, source: str, error_msg: str):
        """
        报告错误
        
        Args:
            source: 错误源（如 "wifi_driver", "adb_driver"）
            error_msg: 错误信息
        """
        self.logger.error(f"[{source}] 发生错误: {error_msg}")
        
        now = time.time()
        
        # 检查是否需要重置计数
        if now - self._last_error_time.get(source, 0) > self.reset_interval:
            self._error_counts[source] = 0
            
        self._error_counts[source] = self._error_counts.get(source, 0) + 1
        self._last_error_time[source] = now
        
        # 检查是否超过阈值
        if self._error_counts[source] >= self.error_threshold:
            self.logger.critical(f"[{source}] 错误次数超过阈值 ({self.error_threshold})，触发自愈策略")
            self._trigger_recovery(source)
            
        # 如果是关键错误，设置系统状态为 ERROR
        # 这里简化处理，任何报告的错误都暂时不改变全局状态，除非自愈失败
    
    def register_recovery_strategy(self, source: str, strategy: Callable[[], bool]):
        """
        注册自愈策略
        
        Args:
            source: 错误源
            strategy: 自愈函数，返回 True 表示成功
        """
        self._recovery_strategies[source] = strategy
    
    def _trigger_recovery(self, source: str):
        """触发自愈流程"""
        strategy = self._recovery_strategies.get(source)
        
        if strategy:
            self.logger.info(f"正在尝试修复 [{source}]...")
            try:
                success = strategy()
                if success:
                    self.logger.info(f"[{source}] 修复成功")
                    self._error_counts[source] = 0
                    # 如果系统处于错误状态，尝试恢复
                    if self.state_manager.state == SystemState.ERROR:
                        self.state_manager.state = SystemState.IDLE
                else:
                    self.logger.error(f"[{source}] 修复失败")
                    self.state_manager.state = SystemState.ERROR
            except Exception as e:
                self.logger.error(f"执行自愈策略时发生异常: {e}")
                self.state_manager.state = SystemState.ERROR
        else:
            self.logger.warning(f"未找到 [{source}] 的自愈策略")
            self.state_manager.state = SystemState.ERROR
