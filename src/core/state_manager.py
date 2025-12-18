"""状态管理模块"""

from enum import Enum
from typing import Set, Callable, List

from src.utils.logger import get_logger


class SystemState(Enum):
    """系统状态枚举"""
    IDLE = "idle"           # 空闲
    BUSY = "busy"           # 忙碌（正在执行指令）
    OFFLINE = "offline"     # 离线（硬件未连接）
    ERROR = "error"         # 错误状态
    MAINTENANCE = "maintenance" # 维护模式


class StateManager:
    """
    状态管理器
    维护系统和设备的当前状态
    """
    
    def __init__(self):
        self.logger = get_logger()
        self._current_state = SystemState.OFFLINE
        self._observers: List[Callable[[SystemState], None]] = []
        
        self.logger.info("状态管理器初始化完成")
    
    @property
    def state(self) -> SystemState:
        """获取当前状态"""
        return self._current_state
    
    @state.setter
    def state(self, new_state: SystemState):
        """设置新状态"""
        if self._current_state != new_state:
            old_state = self._current_state
            self._current_state = new_state
            self.logger.info(f"系统状态变更: {old_state.value} -> {new_state.value}")
            self._notify_observers()
    
    def is_ready(self) -> bool:
        """系统是否准备好接收指令"""
        return self._current_state == SystemState.IDLE
    
    def set_busy(self):
        """设置为忙碌状态"""
        if self._current_state == SystemState.IDLE:
            self.state = SystemState.BUSY
            
    def set_idle(self):
        """设置为闲置状态"""
        if self._current_state == SystemState.BUSY:
            self.state = SystemState.IDLE
            
    def add_observer(self, callback: Callable[[SystemState], None]):
        """添加状态观察者"""
        self._observers.append(callback)
        
    def _notify_observers(self):
        """通知所有观察者"""
        for callback in self._observers:
            try:
                callback(self._current_state)
            except Exception as e:
                self.logger.error(f"状态通知回调出错: {e}")
