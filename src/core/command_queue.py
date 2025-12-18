"""指令队列系统"""

import queue
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import IntEnum

from src.utils.logger import get_logger


class Priority(IntEnum):
    """指令优先级"""
    LOW = 10      # 普通弹幕
    NORMAL = 20   # 礼物/付费弹幕
    HIGH = 30     # 管理员/舰长
    CRITICAL = 40 # 紧急指令/系统指令


@dataclass(order=True)
class Command:
    """指令对象"""
    priority: int
    content: str = field(compare=False)
    user: str = field(compare=False)
    timestamp: float = field(compare=False, default_factory=time.time)
    cmd_type: str = field(compare=False, default="unknown")
    args: dict = field(compare=False, default_factory=dict)

    def __str__(self):
        return f"[{Priority(self.priority).name}] {self.user}: {self.content}"


class CommandQueue:
    """
    指令队列管理器
    基于优先级的线程安全队列
    """
    
    def __init__(self, max_size: int = 100):
        self.logger = get_logger()
        self._queue = queue.PriorityQueue(maxsize=max_size)
        self.logger.info(f"指令队列初始化完成，最大容量: {max_size}")
    
    def put(self, cmd: Command):
        """
        添加指令到队列
        注意：PriorityQueue 是最小堆，所以数字越小优先级越高。
        为了让 Priority.HIGH (30) 比 Priority.LOW (10) 优先，
        我们需要在存储时对优先级取反，或者调整 Priority 定义。
        这里我们调整 Priority 定义：数字越大优先级越高。
        但是 Python 的 PriorityQueue 是数字越小越先出队。
        所以我们需要存储 (-priority, timestamp, cmd) 或者重写 Command 的比较逻辑。
        
        这里我们在 Command dataclass 中使用了 order=True，它会按字段顺序比较。
        为了实现"数字越大优先级越高"，我们在存储时将 priority 取反。
        """
        try:
            # 存储时取反 priority，这样原始优先级高的（数字大的）变成负数后更小，从而先出队
            # 例如：HIGH(30) -> -30, LOW(10) -> -10。-30 < -10，所以 HIGH 先出。
            # 我们创建一个新的 Command 对象或者修改它，但 dataclass 默认比较第一个字段。
            # 为了不混淆，我们直接在 Command 定义时就约定：
            # 这里的 Priority 枚举值越大代表越重要。
            # 但为了配合 PriorityQueue (最小堆)，我们需要在放入队列时做处理。
            
            # 更好的做法是：Command.priority 存储原始值。
            # dataclass 比较时，我们希望 priority 大的排在前面。
            # 但 dataclass 默认是按字段值从小到大排序。
            # 所以我们可以在 Command 中增加一个 sort_index 字段用于排序。
            
            # 简化方案：直接存 (-priority, cmd) 元组进队列，或者修改 Command 的 __lt__。
            # 这里采用修改 Command 的 priority 含义：数字越小优先级越高。
            # 让我们重新定义 Priority：
            # CRITICAL = 0
            # HIGH = 10
            # NORMAL = 20
            # LOW = 30
            
            # 既然已经定义了 Priority (数字越大越重要)，我们在 put 时包装一下
            self._queue.put((-cmd.priority, cmd.timestamp, cmd), block=False)
            self.logger.debug(f"指令入队: {cmd}")
            
        except queue.Full:
            self.logger.warning("指令队列已满，丢弃指令")
    
    def get(self) -> Optional[Command]:
        """获取下一个指令"""
        try:
            _, _, cmd = self._queue.get(block=False)
            return cmd
        except queue.Empty:
            return None
    
    def qsize(self) -> int:
        """获取当前队列大小"""
        return self._queue.qsize()
    
    def clear(self):
        """清空队列"""
        with self._queue.mutex:
            self._queue.queue.clear()
        self.logger.info("指令队列已清空")
