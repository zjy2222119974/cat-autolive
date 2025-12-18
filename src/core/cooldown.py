"""冷却与频率限制模块"""

import time
from collections import defaultdict
from typing import Dict

from src.utils.logger import get_logger


class CooldownManager:
    """
    冷却管理器
    负责管理全局冷却、用户冷却和指令冷却
    """
    
    def __init__(self):
        self.logger = get_logger()
        
        # 冷却配置 (秒)
        self.global_cooldown = 1.0        # 全局指令间隔
        self.user_cooldown = 3.0          # 单个用户指令间隔
        self.cmd_cooldowns: Dict[str, float] = {
            "feed": 10.0,    # 喂食指令冷却
            "laser": 5.0,    # 激光笔指令冷却
            "move": 0.5      # 移动指令冷却
        }
        
        # 状态记录
        self._last_global_time = 0.0
        self._last_user_time: Dict[str, float] = defaultdict(float)
        self._last_cmd_time: Dict[str, float] = defaultdict(float)
        
        self.logger.info("冷却管理器初始化完成")
    
    def is_allowed(self, user: str, cmd_type: str) -> bool:
        """
        检查指令是否允许执行（未在冷却中）
        
        Args:
            user: 用户ID
            cmd_type: 指令类型
            
        Returns:
            bool: True 如果允许执行，False 如果在冷却中
        """
        now = time.time()
        
        # 1. 检查全局冷却
        if now - self._last_global_time < self.global_cooldown:
            return False
            
        # 2. 检查用户冷却 (管理员可豁免，这里暂不处理权限，由上层处理)
        if now - self._last_user_time[user] < self.user_cooldown:
            return False
            
        # 3. 检查特定指令冷却
        cooldown = self.cmd_cooldowns.get(cmd_type, 0.0)
        if now - self._last_cmd_time[cmd_type] < cooldown:
            return False
            
        return True
    
    def update(self, user: str, cmd_type: str):
        """
        更新冷却时间（指令执行成功后调用）
        """
        now = time.time()
        self._last_global_time = now
        self._last_user_time[user] = now
        self._last_cmd_time[cmd_type] = now
        
    def reset(self):
        """重置所有冷却状态"""
        self._last_global_time = 0.0
        self._last_user_time.clear()
        self._last_cmd_time.clear()
        self.logger.info("冷却状态已重置")
