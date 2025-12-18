"""核心模块测试脚本"""

import time
import unittest
from typing import Dict, Any

from src.core.command_queue import CommandQueue, Command, Priority
from src.core.cooldown import CooldownManager
from src.core.state_manager import StateManager, SystemState
from src.core.error_handler import ErrorHandler
from src.core.dispatcher import Dispatcher
from src.drivers.base_driver import BaseDriver


class MockDriver(BaseDriver):
    """模拟驱动"""
    def connect(self) -> bool:
        self._connected = True
        return True
    
    def disconnect(self):
        self._connected = False
    
    def execute(self, cmd_type: str, args: Dict[str, Any] = None) -> bool:
        if cmd_type == "fail":
            return False
        if cmd_type == "error":
            raise Exception("模拟驱动异常")
        return True


class TestCoreModules(unittest.TestCase):
    
    def test_command_queue_priority(self):
        """测试指令队列优先级"""
        q = CommandQueue()
        
        # 插入不同优先级的指令
        cmd1 = Command(priority=Priority.LOW, content="low", user="user1")
        cmd2 = Command(priority=Priority.HIGH, content="high", user="admin")
        cmd3 = Command(priority=Priority.NORMAL, content="normal", user="user2")
        
        q.put(cmd1)
        q.put(cmd2)
        q.put(cmd3)
        
        # 验证出队顺序：HIGH -> NORMAL -> LOW
        self.assertEqual(q.get().content, "high")
        self.assertEqual(q.get().content, "normal")
        self.assertEqual(q.get().content, "low")
        
    def test_cooldown(self):
        """测试冷却机制"""
        cm = CooldownManager()
        cm.global_cooldown = 0.1
        cm.user_cooldown = 0.1
        
        # 第一次应该允许
        self.assertTrue(cm.is_allowed("user1", "test"))
        cm.update("user1", "test")
        
        # 立即再次请求应该被拒绝
        self.assertFalse(cm.is_allowed("user1", "test"))
        
        # 等待冷却后应该允许
        time.sleep(0.15)
        self.assertTrue(cm.is_allowed("user1", "test"))
        
    def test_state_manager(self):
        """测试状态管理"""
        sm = StateManager()
        self.assertEqual(sm.state, SystemState.OFFLINE)
        
        # 测试状态变更通知
        events = []
        sm.add_observer(lambda s: events.append(s))
        
        sm.state = SystemState.IDLE
        self.assertEqual(events[-1], SystemState.IDLE)
        
        sm.set_busy()
        self.assertEqual(sm.state, SystemState.BUSY)
        
        sm.set_idle()
        self.assertEqual(sm.state, SystemState.IDLE)
        
    def test_dispatcher_flow(self):
        """测试分发器完整流程"""
        dispatcher = Dispatcher()
        mock_driver = MockDriver("mock")
        dispatcher.register_driver("mock", mock_driver)
        dispatcher.cooldown.global_cooldown = 0.1
        dispatcher.cooldown.user_cooldown = 0.1
        
        # 启动分发器
        dispatcher.start()
        time.sleep(0.1)
        
        # 1. 测试正常指令
        cmd = Command(
            priority=Priority.NORMAL,
            content="test",
            user="test_user",
            cmd_type="mock:action"
        )
        dispatcher.queue.put(cmd)
        time.sleep(0.1)
        
        # 验证状态（应该很快变回 IDLE）
        self.assertEqual(dispatcher.state_manager.state, SystemState.IDLE)
        
        # 2. 测试失败指令
        cmd_fail = Command(
            priority=Priority.NORMAL,
            content="fail",
            user="test_user_2",
            cmd_type="mock:fail"
        )
        dispatcher.queue.put(cmd_fail)
        time.sleep(0.5)
        
        # 验证错误计数
        self.assertEqual(dispatcher.error_handler._error_counts.get("mock", 0), 1)
        
        dispatcher.stop()


if __name__ == "__main__":
    unittest.main()
