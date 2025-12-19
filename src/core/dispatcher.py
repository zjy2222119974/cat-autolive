"""中枢分发器模块"""

import time
import threading
from typing import Dict, Optional

from src.utils.logger import get_logger
from src.core.command_queue import CommandQueue, Command
from src.core.cooldown import CooldownManager
from src.core.state_manager import StateManager, SystemState
from src.core.error_handler import ErrorHandler
from src.drivers.base_driver import BaseDriver


class Dispatcher:
    """
    中枢分发器 (Controller)
    系统的核心大脑，负责协调各个模块和驱动
    """
    
    
    def __init__(self):
        self.logger = get_logger()
        
        # 初始化核心模块
        # 每个驱动对应一个队列
        self.queues: Dict[str, CommandQueue] = {}
        
        # 记录每个设备当前的执行状态 (Device -> timeout timestamp)
        self.device_busy_until: Dict[str, float] = {}
        # 记录每个设备当前正在服务的用户(用于UI显示)
        self.device_current_user: Dict[str, str] = {}
        
        # 权限管理
        # user -> { "tokens": ["#冻干", ...], "vehicle_expiry": timestamp }
        self.user_permissions: Dict[str, Dict] = {}
        
        # VIP包场状态管理
        self.vip_user: Optional[str] = None           # 当前VIP用户
        self.vip_expiry: float = 0                     # VIP到期时间戳
        self.vip_used_devices: set = set()             # VIP已使用过的设备（单次限制）
        self.vip_waiting: bool = False                 # VIP是否在等待设备释放
        self.vip_waiting_start: float = 0              # VIP等待开始时间
        self.vip_saved_queues: Dict[str, list] = {}    # VIP激活时保存的队列
        
        # 加载礼物配置
        self.gift_config = self._load_gift_config()
        
        self.cooldown = CooldownManager()
        self.state_manager = StateManager()
        self.error_handler = ErrorHandler(self.state_manager)
        
        # 驱动注册表
        self.drivers: Dict[str, BaseDriver] = {}
        
        # 模拟流
        self.mock_stream_running = False
        self.mock_thread = None
        
        # 运行控制
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        self.logger.info("中枢分发器初始化完成")

    def _load_gift_config(self) -> dict:
        """加载礼物配置"""
        import json
        import os
        try:
            # 简单起见，默认加载 douyin.json
            path = "src/config/giftShop/douyin.json"
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"加载礼物配置失败: {e}")
        return {}
    
    def register_driver(self, driver_name: str, driver: BaseDriver):
        """注册驱动，并分配独立队列"""
        self.drivers[driver_name] = driver
        self.queues[driver_name] = CommandQueue()
        self.device_busy_until[driver_name] = 0
        self.device_current_user[driver_name] = None
        
        self.logger.info(f"注册驱动: {driver_name} (分配独立队列)")
        
        self.error_handler.register_recovery_strategy(
            driver_name, 
            lambda: self._recover_driver(driver)
        )
    
    def _recover_driver(self, driver: BaseDriver) -> bool:
        """驱动恢复逻辑"""
        self.logger.info(f"正在尝试重连驱动: {driver.name}")
        driver.disconnect()
        time.sleep(1)
        return driver.connect()
    
    def start(self):
        """启动分发循环"""
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.state_manager.state = SystemState.IDLE
        self.logger.info("中枢分发器已启动")
    
    def stop(self):
        """停止分发循环"""
        self._running = False
        self.stop_mock_stream()
        if self._thread:
            self._thread.join(timeout=2.0)
        self.state_manager.state = SystemState.OFFLINE
        self.logger.info("中枢分发器已停止")
        
    def start_mock_stream(self, file_path: str):
        """启动模拟弹幕流"""
        if self.mock_stream_running:
            return
            
        import threading
        import json
        
        def _mock_reader():
            self.logger.info(f"开始读取模拟文件: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                start_time = time.time()
                
                for item in data:
                    if not self.mock_stream_running:
                        break
                        
                    offset = item.get('offset_sec', 0)
                    now_offset = time.time() - start_time
                    
                    if offset > now_offset:
                        time.sleep(offset - now_offset)
                        
                    # 处理单条消息
                    self._handle_input_message(item)
                        
                self.logger.info("模拟流播放结束")
                self.mock_stream_running = False
                
            except Exception as e:
                self.logger.error(f"模拟流异常: {e}")
                self.mock_stream_running = False

        self.mock_stream_running = True
        self.mock_thread = threading.Thread(target=_mock_reader, daemon=True)
        self.mock_thread.start()

    def stop_mock_stream(self):
        """停止模拟流"""
        self.mock_stream_running = False
        if self.mock_thread:
            self.mock_thread.join(timeout=1.0)
    
    def _handle_input_message(self, item: dict):
        """处理输入的弹幕/礼物消息"""
        msg_type = item.get('type', 'chat')
        user = item.get('user', 'unknown')
        content = item.get('content', '')
        
        self.logger.info(f"[DANMAKU] 用户[{user}] 消息[{msg_type}]: {content}")
        
        if msg_type == 'gift':
            self._process_gift(user, item)
        elif msg_type == 'chat':
            self._process_chat(user, content)
            
    def _process_gift(self, user: str, item: dict):
        """处理礼物逻辑：授权"""
        gift_name = item.get('gift_name')
        if not gift_name or gift_name not in self.gift_config:
            return
            
        config = self.gift_config[gift_name]
        g_type = config.get('type')
        
        # 初始化用户权限
        if user not in self.user_permissions:
            self.user_permissions[user] = {"tokens": [], "vehicle_expiry": 0}
            
        if g_type == 'command_token':
            # 授予令牌
            actions = config.get('actions', [])
            allowed_cmds = [act['command'] for act in actions]
            
            # VIP期间检查（非等待状态）
            if self.vip_user and not self.vip_waiting:
                if user != self.vip_user:
                    # 非VIP用户在VIP期间刷令牌礼物，被阻塞
                    self.logger.info(f"🚫 VIP包场中，用户[{user}]的礼物[{gift_name}]被阻塞")
                    return
            
            self.user_permissions[user]["tokens"].append({
                "cmds": allowed_cmds,
                "config": actions
            })
            self.logger.info(f"用户[{user}] 获得令牌: {allowed_cmds}")
            
        elif g_type == 'vehicle_time':
            # 增加驾驶时间
            duration = config.get('duration', 0)
            now = time.time()
            
            # VIP期间检查（非等待状态）
            if self.vip_user and not self.vip_waiting:
                if user != self.vip_user:
                    # 非VIP用户在VIP期间刷车辆礼物，被阻塞
                    self.logger.info(f"🚫 VIP包场中，用户[{user}]的礼物[{gift_name}]被阻塞，哈基米车为VIP专属")
                    return
            
            current_expiry = max(now, self.user_permissions[user]["vehicle_expiry"])
            self.user_permissions[user]["vehicle_expiry"] = current_expiry + duration
            self.logger.info(f"用户[{user}] 获得驾驶时间 {duration}s")
            
        elif g_type == 'direct_trigger' or g_type == 'duration_event':
            # 直接触发
            device = config.get('device')
            action = config.get('action')
            duration = config.get('duration', 0)
            
            # VIP期间检查（非等待状态）
            if self.vip_user and not self.vip_waiting:
                if user != self.vip_user and device != "laser_ball":
                    # 非VIP用户在VIP期间刷礼物，被阻塞（激光球除外）
                    self.logger.info(f"🚫 VIP包场中，用户[{user}]的礼物[{gift_name}]被阻塞，设备[{device}]为VIP专属")
                    return
            
            if device:
                cmd = Command(
                    priority=30, # 礼物触发优先级更高
                    content=f"礼物触发: {gift_name}",
                    user=user,
                    cmd_type=action if action else "trigger", # 使用 action 作为 cmd_type
                    args={"duration": duration, "raw": item}
                )
                self.push_command(device, cmd)
                
        elif g_type == 'vip_pass':
            # VIP包场
            self._activate_vip_pass(user, config, gift_name)
    
    def _activate_vip_pass(self, user: str, config: dict, gift_name: str):
        """激活VIP包场模式"""
        duration = config.get('duration', 900)  # 默认15分钟
        
        # 检查5个设备（除了激光球）是否有正在运行的
        non_laser_devices = [name for name in self.device_busy_until.keys() if name != "laser_ball"]
        busy_devices = []
        now = time.time()
        
        for device_name in non_laser_devices:
            if now < self.device_busy_until.get(device_name, 0):
                busy_devices.append(device_name)
                remaining = self.device_busy_until[device_name] - now
                self.logger.info(f"[VIP等待] 设备 [{device_name}] 还在运行，剩余 {remaining:.1f}秒")
        
        # 设置VIP状态
        self.vip_user = user
        self.vip_expiry = time.time() + duration
        self.vip_used_devices.clear()  # 清空已使用设备记录
        
        if busy_devices:
            # 有设备在运行，进入等待模式
            self.vip_waiting = True
            self.vip_waiting_start = time.time()
            self.logger.info(f"⏳ VIP包场激活: 用户[{user}]需要等待设备释放...")
            self.logger.info(f"[VIP等待] 正在等待设备: {', '.join(busy_devices)}")
            
            # 保存所有设备的当前队列（除了激光球）
            self._save_queues_for_vip()
        else:
            # 没有设备在运行，直接开始VIP
            self.vip_waiting = False
            self.logger.info(f"🎉 VIP包场立即开始: 用户[{user}], 持续{duration}秒")
            self._start_vip_session(user, duration)
    
    def _save_queues_for_vip(self):
        """保存当前所有设备的队列（VIP插队时使用）"""
        self.vip_saved_queues.clear()
        for device_name, queue in self.queues.items():
            if device_name == "laser_ball":
                continue  # 激光球不需要保存
            
            # 保存队列中的所有指令
            saved_commands = []
            while True:
                cmd = queue.get()
                if not cmd:
                    break
                saved_commands.append(cmd)
            
            if saved_commands:
                self.vip_saved_queues[device_name] = saved_commands
                self.logger.info(f"[VIP插队] 保存了 [{device_name}] 的 {len(saved_commands)} 条指令")
    
    def _start_vip_session(self, user: str, duration: int):
        """真正开始VIP会话"""
        self.vip_waiting = False
        self.logger.info(f"🎉 VIP包场正式开始: 用户[{user}], 持续{duration}秒")
        
        # 启动激光雨持续运行（整个VIP期间）
        laser_cmd = Command(
            priority=40,  # CRITICAL优先级
            content=f"VIP包场: 激光雨持续运行",
            user=user,
            cmd_type="start_laser_ball",
            args={"duration": duration}
        )
        self.push_command("laser_ball", laser_cmd)
        self.logger.info(f"[VIP] 激光雨已启动，持续{duration}秒")
    
    def _process_vip_command(self, user: str, content: str):
        """处理VIP用户的指令"""
        # VIP用户可以使用所有设备
        # 哈基米车：无限次使用
        # 激光雨：一直运行，不需要额外指令
        # 其他设备：单次使用限制
        
        # 判断指令类型并找到目标设备
        device = None
        action = None
        
        # 车辆指令
        if content.startswith("#") and any(c in content for c in ['w', 'a', 's', 'd', 'r']):
            device = "car_hakimi"
            action = content
        # 喂食指令
        elif content == "#冻干":
            device = "feeder_freeze_dried"
            action = "feed_freeze_dried"
        elif content == "#猫条" or content == "#膏膏":
            device = "feeder_paste"
            action = "feed_snack" if content == "#猫条" else "feed_nutritional_paste"
        elif content == "#猫粮":
            device = "feeder_kibble"
            action = "feed_dry_food"
        
        if not device:
            return
        
        # 哈基米车和激光雨不受单次限制
        if device not in ["car_hakimi", "laser_ball"]:
            if device in self.vip_used_devices:
                self.logger.info(f"[VIP] 设备[{device}]已使用过，跳过")
                return
            # 标记已使用
            self.vip_used_devices.add(device)
        
        # 创建高优先级指令
        cmd = Command(
            priority=40,  # CRITICAL优先级
            content=content,
            user=user,
            cmd_type=action,
            args={}
        )
        self.push_command(device, cmd)
        self.logger.info(f"[VIP] 用户[{user}] 执行指令: {content} -> {device}")

    def _process_chat(self, user: str, content: str):
        """处理弹幕逻辑：消耗权限"""
        content = content.strip()
        
        # ========== VIP包场优先处理 ==========
        # 检查VIP是否到期
        if time.time() >= self.vip_expiry:
            if self.vip_user:
                self.logger.info(f"✅ VIP包场结束: 用户[{self.vip_user}]")
                # 恢复保存的队列
                self._restore_queues_after_vip()
                self.vip_user = None
                self.vip_used_devices.clear()
                self.vip_waiting = False
        
        # 如果当前有VIP用户
        if self.vip_user:
            # VIP等待期间，所有指令都被阻塞（包括VIP自己）
            if self.vip_waiting:
                if content.startswith("#"):
                    wait_time = time.time() - self.vip_waiting_start
                    self.logger.info(f"⏳ VIP等待设备释放中({wait_time:.1f}s)，指令暂时阻塞: [{user}] {content}")
                return
            
            if user == self.vip_user:
                # VIP用户的指令，全部处理
                self._process_vip_command(user, content)
                return
            else:
                # 非VIP用户，VIP期间指令被阻塞
                if content.startswith("#"):
                    self.logger.info(f"🚫 VIP包场中，用户[{user}]的指令被阻塞: {content}")
                return
        
        # ========== 正常权限处理 ==========
        if user not in self.user_permissions:
            return
            
        perms = self.user_permissions[user]
        
        # 1. 检查车辆权限
        if time.time() < perms["vehicle_expiry"]:
            # 检查是否是车辆指令 (简单判断 #开头)
            # 实际应该检查 allowed_commands，这里简化
            if content.startswith("#"): 
                # 发送给小车
                cmd = Command(
                    priority=20,
                    content=content,
                    user=user,
                    cmd_type=content,
                    args={}
                )
                self.push_command("car_hakimi", cmd)
                return

        # 2. 检查令牌权限
        matched_token_index = -1
        target_action = None
        
        for idx, token in enumerate(perms["tokens"]):
            # token["cmds"] 包含 ["#冻干", "#猫条"]
            # 检查内容是否匹配其中一个 (允许前缀匹配或精确匹配)
            for cmd_str in token["cmds"]:
                if content == cmd_str: # 精确匹配指令
                    matched_token_index = idx
                    # 找到对应的 device 配置
                    for act_conf in token["config"]:
                        if act_conf["command"] == cmd_str:
                            target_action = act_conf
                            break
                    break
            if matched_token_index != -1:
                break
                
        if matched_token_index != -1 and target_action:
            # 消耗令牌
            perms["tokens"].pop(matched_token_index)
            self.logger.info(f"用户[{user}] 消耗令牌执行: {content}")
            
            device = target_action["device"]
            action = target_action["action"]
            
            cmd = Command(
                priority=20,
                content=content,
                user=user,
                cmd_type=action,
                args={}
            )
            self.push_command(device, cmd)

    def push_command(self, driver_name: str, cmd: Command):
        """推送指令到指定队列"""
        if driver_name in self.queues:
            self.queues[driver_name].put(cmd)
        else:
            self.logger.warning(f"尝试推送到不存在的设备队列: {driver_name}")

    def _loop(self):
        """主循环：轮询所有队列"""
        while self._running:
            try:
                if self.state_manager.state in [SystemState.ERROR, SystemState.OFFLINE]:
                    time.sleep(0.5)
                    continue
                
                # 检查VIP等待状态
                if self.vip_waiting and self.vip_user:
                    self._check_vip_waiting_status()
                
                # 遍历所有设备队列
                active_work = False
                
                for name, queue in self.queues.items():
                    # 1. 检查设备是否忙碌
                    if time.time() < self.device_busy_until.get(name, 0):
                        continue
                    
                    # 设备空闲，清空当前用户
                    if self.device_current_user.get(name):
                        self.device_current_user[name] = None
                    
                    # 2. 获取指令
                    cmd = queue.get()
                    if not cmd:
                        continue
                        
                    active_work = True
                    self._process_command(name, cmd)
                
                if not active_work:
                    time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"分发循环异常: {e}", exc_info=True)
                time.sleep(1.0)
    
    def _check_vip_waiting_status(self):
        """检查VIP等待状态，如果所有设备都空闲了，开始VIP会话"""
        now = time.time()
        non_laser_devices = [name for name in self.device_busy_until.keys() if name != "laser_ball"]
        
        # 检查是否所有设备都空闲了
        all_idle = True
        for device_name in non_laser_devices:
            if now < self.device_busy_until.get(device_name, 0):
                all_idle = False
                break
        
        if all_idle:
            # 所有设备都空闲，开始VIP会话
            duration = int(self.vip_expiry - now)
            self._start_vip_session(self.vip_user, duration)
    
    def _restore_queues_after_vip(self):
        """VIP结束后，恢复保存的队列"""
        if not self.vip_saved_queues:
            return
        
        self.logger.info("📋 恢复VIP之前的队列...")
        for device_name, saved_commands in self.vip_saved_queues.items():
            if device_name in self.queues:
                # 将保存的指令重新放回队列（按原顺序）
                for cmd in saved_commands:
                    self.queues[device_name].put(cmd)
                self.logger.info(f"[队列恢复] 设备 [{device_name}] 恢复了 {len(saved_commands)} 条指令")
        
        self.vip_saved_queues.clear()
    
    def _process_command(self, driver_name: str, cmd: Command):
        """处理单个指令"""
        # self.logger.info(f"[{driver_name}] 处理指令: {cmd}") 
        # 移除了这里的日志，因为驱动内部会打印，避免重复
        
        target_driver = self.drivers.get(driver_name)
        if not target_driver:
            return
            
        # 2. 执行指令
        # self.state_manager.set_busy() # 不全局 busy，只设备 busy
        try:
            # 解析耗时
            duration = 3
            if cmd.args and "duration" in cmd.args:
                duration = cmd.args["duration"]
            elif cmd.cmd_type == "open_can": # 罐头特定
                duration = 60
            elif "car" in driver_name: # 车辆移动
                duration = 1
            
            self.device_busy_until[driver_name] = time.time() + duration
            self.device_current_user[driver_name] = cmd.user
            
            # 调用驱动
            success = target_driver.execute(cmd.cmd_type, cmd.args)
            
            if not success:
               self.device_busy_until[driver_name] = 0 # 失败立即释放
                
        except Exception as e:
            self.logger.error(f"指令执行出错: {e}")
            self.device_busy_until[driver_name] = 0
            
        finally:
            pass


if __name__ == "__main__":
    import sys
    import os
    # 将项目根目录添加到 python path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    
    from src.utils.logger import setup_logger
    setup_logger()
    
    dispatcher = Dispatcher()
    dispatcher.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        dispatcher.stop()
