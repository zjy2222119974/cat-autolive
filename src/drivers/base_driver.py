"""驱动基类定义"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from src.utils.logger import get_logger


class BaseDriver(ABC):
    """
    硬件驱动抽象基类
    所有具体驱动（WiFi, ADB等）都应继承此类
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger()
        self._connected = False
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected
    
    @abstractmethod
    def connect(self) -> bool:
        """
        连接设备
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开连接"""
        pass
    
    @abstractmethod
    def execute(self, cmd_type: str, args: Dict[str, Any] = None) -> bool:
        """
        执行指令
        
        Args:
            cmd_type: 指令类型
            args: 指令参数
            
        Returns:
            bool: 执行是否成功
        """
        pass
    
    def health_check(self) -> bool:
        """
        健康检查
        默认返回连接状态，子类可覆盖实现更复杂的检查
        """
        return self._connected
