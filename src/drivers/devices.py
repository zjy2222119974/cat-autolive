
import time
import threading
from typing import Dict, Any
from src.drivers.iot_driver import IoTDriver
from src.drivers.simulator_driver import SimulatorDriver

class DeviceMixin:
    """设备通用功能混入类"""
    def __init__(self):
        self._lock = threading.Lock()
        self._busy = False
    
    def _execute_with_lock(self, action_name: str, task_func):
        """带锁执行任务"""
        if self._busy:
            self.logger.warning(f"[{self.name}] 设备忙碌中，忽略指令")
            return False
            
        with self._lock:
            self._busy = True
            
        def _target():
            try:
                task_func()
            except Exception as e:
                self.logger.error(f"[{self.name}] 执行异常: {e}")
            finally:
                with self._lock:
                    self._busy = False
                self.logger.info(f"[{self.name}] 任务完成，解除锁定")
        
        # 启动独立线程执行耗时任务，不阻塞中枢
        t = threading.Thread(target=_target, daemon=True)
        t.start()
        return True

class PasteFeederDriver(IoTDriver, DeviceMixin):
    """猫条/化毛膏喂食器"""
    def __init__(self, name: str, host: str, port: int):
        IoTDriver.__init__(self, name, host, port)
        DeviceMixin.__init__(self)
        
    def execute(self, cmd_type: str, args: Dict[str, Any] = None) -> bool:
        if not self.is_connected:
            return False
            
        def task():
            self.logger.info(f"[{self.name}] >>> 正在挤出猫条/化毛膏...")
            # 模拟硬件动作耗时
            time.sleep(3)
            self.logger.info(f"[{self.name}] <<< 挤出完成")
            
        return self._execute_with_lock("feed_paste", task)

class KibbleFeederDriver(SimulatorDriver, DeviceMixin):
    """猫粮喂食器 (模拟器)"""
    def __init__(self, name: str, app_package: str):
        SimulatorDriver.__init__(self, name, app_package=app_package)
        DeviceMixin.__init__(self)
        
    def execute(self, cmd_type: str, args: Dict[str, Any] = None) -> bool:
        if not self.is_connected:
            return False
            
        def task():
            self.logger.info(f"[{self.name}] >>> 点击APP投喂按钮...")
            time.sleep(2)
            self.logger.info(f"[{self.name}] <<< 投喂指令已发送至APP")
            
        return self._execute_with_lock("feed_kibble", task)

class FreezeDriedFeederDriver(SimulatorDriver, DeviceMixin):
    """冻干喂食器 (模拟器)"""
    def __init__(self, name: str, app_package: str):
        SimulatorDriver.__init__(self, name, app_package=app_package)
        DeviceMixin.__init__(self)
        self._automation = None
        self._ocr_detector = None
        self._click_simulator = None
    
    def _init_automation(self):
        """初始化自动化组件"""
        if self._automation is not None:
            return
        
        try:
            from src.utils.ocr_utils import OCRDetector
            from src.utils.click_simulator import ClickSimulator
            from src.automation.feeder_automation import FreezeDriedFeederAutomation
            
            self.logger.info(f"[{self.name}] 初始化OCR自动化组件...")
            self._ocr_detector = OCRDetector()
            self._click_simulator = ClickSimulator()
            self._automation = FreezeDriedFeederAutomation(self._ocr_detector, self._click_simulator)
            self.logger.info(f"[{self.name}] 自动化组件初始化完成")
        except Exception as e:
            self.logger.error(f"[{self.name}] 自动化组件初始化失败: {e}")
            self._automation = None

    def execute(self, cmd_type: str, args: Dict[str, Any] = None) -> bool:
        if not self.is_connected:
            return False
        
        # 初始化自动化组件
        if self._automation is None:
            self._init_automation()
        
        # 如果自动化组件初始化失败，使用默认行为
        if self._automation is None:
            def task():
                self.logger.info(f"[{self.name}] >>> 触发冻干投喂...")
                time.sleep(2)
                self.logger.info(f"[{self.name}] <<< 冻干掉落")
            return self._execute_with_lock("feed_freeze", task)
        
        # 使用OCR自动化
        def task():
            try:
                self.logger.info(f"[{self.name}] >>> 开始自动喂食流程...")
                
                # 获取窗口句柄
                if not hasattr(self, 'hwnd') or not self.hwnd:
                    self.logger.error(f"[{self.name}] 未绑定窗口，无法执行自动化")
                    return
                
                # 执行喂食
                success = self._automation.feed(
                    hwnd=self.hwnd,
                    capture_func=self.capture_window,
                    portions=1
                )
                
                if success:
                    self.logger.info(f"[{self.name}] <<< 自动喂食完成")
                else:
                    self.logger.error(f"[{self.name}] <<< 自动喂食失败")
                    
            except Exception as e:
                self.logger.error(f"[{self.name}] 自动化执行异常: {e}")
        
        return self._execute_with_lock("feed_freeze", task)

class IntegratedAppDriver(SimulatorDriver, DeviceMixin):
    """整合APP (模拟器)"""
    def __init__(self, name: str, app_package: str):
        SimulatorDriver.__init__(self, name, app_package=app_package)
        DeviceMixin.__init__(self)

    def execute(self, cmd_type: str, args: Dict[str, Any] = None) -> bool:
        if not self.is_connected:
            return False
            
        def task():
            self.logger.info(f"[{self.name}] >>> 整合APP执行操作: {cmd_type}...")
            time.sleep(1.5)
            self.logger.info(f"[{self.name}] <<< 操作完成")
            
        return self._execute_with_lock(cmd_type, task)

class CannedFeederDriver(IoTDriver, DeviceMixin):
    """猫罐喂食器"""
    def __init__(self, name: str, host: str, port: int):
        IoTDriver.__init__(self, name, host, port)
        DeviceMixin.__init__(self)
    
    def execute(self, cmd_type: str, args: Dict[str, Any] = None) -> bool:
        if not self.is_connected:
            return False
            
        def task():
            self.logger.info(f"[{self.name}] >>> 打开罐头盖...")
            time.sleep(5) # 开罐头比较慢
            self.logger.info(f"[{self.name}] <<< 罐头已打开，请享用")
            
        return self._execute_with_lock("open_can", task)

class HakimiCarDriver(IoTDriver, DeviceMixin):
    """哈基米车"""
    def __init__(self, name: str, host: str, port: int):
        IoTDriver.__init__(self, name, host, port)
        DeviceMixin.__init__(self)
    
    def execute(self, cmd_type: str, args: Dict[str, Any] = None) -> bool:
        if not self.is_connected:
            return False
        
        # 解析指令
        # car_hakimi 可能会收到 #w 等指令作为 cmd_type 或 content
        # 这里为了演示，简单处理
        
        real_cmd = cmd_type
        if isinstance(args, dict) and args.get('raw'):
             content = args['raw'].get('content', '')
             if content.startswith('#'):
                 real_cmd = content
        
        def task():
            self.logger.info(f"[{self.name}] >>> 车辆移动: {real_cmd}")
            time.sleep(1) # 移动1秒
            self.logger.info(f"[{self.name}] <<< 停止移动")
            
        return self._execute_with_lock("move_car", task)

class LaserBallDriver(IoTDriver, DeviceMixin):
    """激光灯球"""
    def __init__(self, name: str, host: str, port: int):
        IoTDriver.__init__(self, name, host, port)
        DeviceMixin.__init__(self)

    def execute(self, cmd_type: str, args: Dict[str, Any] = None) -> bool:
        if not self.is_connected:
            return False
            
        def task():
            self.logger.info(f"[{self.name}] >>> 激光扫描中...")
            time.sleep(4)
            self.logger.info(f"[{self.name}] <<< 激光关闭")
            
        return self._execute_with_lock("laser_scan", task)
