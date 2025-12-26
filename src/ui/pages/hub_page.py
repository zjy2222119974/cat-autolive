"""中枢页面"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout
from PyQt6.QtCore import Qt

class HubPage(QWidget):
    """中枢控制页面"""
    
    
    def __init__(self, dispatcher=None):
        super().__init__()
        self.dispatcher = dispatcher
        self._init_ui()
        
        # 启动定时器更新状态
        if self.dispatcher:
            from PyQt6.QtCore import QTimer
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._update_status)
            self.timer.start(1000)
    
    def _update_status(self):
        """更新状态显示"""
"""中枢页面"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QGridLayout, QScrollArea, QTextEdit, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QTimer, QMetaObject, Q_ARG
import logging
import time

from src.ui.components.device_card import DeviceCard
from src.drivers.simulator_driver import SimulatorDriver

class HubPage(QWidget):
    """中枢控制页面"""
    
    
    
    def __init__(self, dispatcher=None):
        super().__init__()
        self.dispatcher = dispatcher
        self.mock_file = "mockData/mockDanmaku.txt"  # 默认弹幕文件
        self._init_ui()
        
        # 启动定时器更新状态
        if self.dispatcher:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._update_status)
            self.timer.start(1000)
    
    def set_mock_file(self, file_path: str):
        """设置要使用的弹幕文件"""
        self.mock_file = file_path
        logging.info(f"HubPage: 弹幕文件已更新为 {file_path}")
            
    def _update_status(self):
        """更新状态显示"""
        if not self.dispatcher:
            return
            
        # 更新设备卡片状态和队列信息
        for card in self.device_cards:
            if not card.driver:
                continue
            
            driver_name = card.driver.name
            card.update_status()
            
            # 获取队列信息
            # 1. 正在服务的用户
            current_user = self.dispatcher.device_current_user.get(driver_name)
            
            # 2. 剩余时间
            busy_until = self.dispatcher.device_busy_until.get(driver_name, 0)
            time_left = max(0, int(busy_until - time.time()))
            
            card.update_queue_info(current_user, time_left)
            
    def _on_connect_clicked(self):
        """连接直播间"""
        if not self.dispatcher:
            return
            
        import os
        mock_file = self.mock_file  # 使用选择的弹幕文件
        if not os.path.exists(mock_file):
            self.log_console.append(f"错误: 找不到模拟数据文件 {mock_file}")
            return
            
        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(True)
        self.log_console.append("开始连接直播间...")
        
        # 启动模拟流
        self.dispatcher.start_mock_stream(mock_file)
        
    def _on_disconnect_clicked(self):
        """断开连接"""
        if not self.dispatcher:
            return
            
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.log_console.append("正在断开连接...")
        
        self.dispatcher.stop_mock_stream()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 1. 标题
        title = QLabel("中枢控制台")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #d4d4d4;")
        layout.addWidget(title)
        
        # 2. 设备网格区域
        # 使用 FlowLayout + ScrollArea
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea { background-color: transparent; }
            QWidget#scroll_content { background-color: transparent; }
        """)
        
        # 自定义内容容器，确保 resize 时重新布局
        class ResizableScrollContent(QWidget):
            def resizeEvent(self, event):
                super().resizeEvent(event)
                # 强制布局更新
                if self.layout():
                    self.layout().activate()
        
        # 内容容器
        scroll_content = ResizableScrollContent()
        scroll_content.setObjectName("scroll_content")
        
        # 使用自定义的流式布局
        from src.ui.components.flow_layout import FlowLayout
        self.flow_layout = FlowLayout(scroll_content, margin=10, spacing=20)
        
        scroll_area.setWidget(scroll_content)
        
        self.device_cards = []
        
        if self.dispatcher:
            # 获取所有设备并创建卡片
            # 我们按照固定顺序或名字排序
            drivers = list(self.dispatcher.drivers.items())
            
            # 手动映射中文名称
            name_map = {
                "feeder_paste": "湿粮喂食器",
                "feeder_kibble": "猫粮喂食器",
                "feeder_freeze_dried": "冻干喂食器",
                "feeder_canned": "猫罐喂食器",
                "car_hakimi": "哈基米车",
                "laser_ball": "激光灯球"
            }
            
            device_infos = [
                ("feeder_paste", "物联网"),
                ("feeder_kibble", "模拟器"),
                ("feeder_freeze_dried", "模拟器"),
                ("feeder_canned", "物联网"),
                ("car_hakimi", "物联网"),
                ("laser_ball", "物联网"),
            ]
            
            for key, type_label in device_infos:
                driver = self.dispatcher.drivers.get(key)
                display_name = name_map.get(key, key)
                
                # 如果是模拟器，类型显示模拟器，否则显示物联网(默认)
                # 为了更准确，可以检查 driver 类型
                real_type = "物联网"
                if driver and isinstance(driver, SimulatorDriver):
                    real_type = "模拟器"
                
                card = DeviceCard(display_name, real_type, driver)
                self.device_cards.append(card)
                
                self.flow_layout.addWidget(card)
                    
        layout.addWidget(scroll_area, 1)
        
        # 弹簧
        # layout.addStretch() # ScrollArea now takes the space
        
        # 4. 控制按钮区域（底部）
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        self.btn_connect = QPushButton("连接直播间 (模拟)")
        self.btn_connect.setFixedSize(150, 40)
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0062a3;
            }
            QPushButton:disabled {
                background-color: #2d2d30;
                color: #555555;
            }
        """)
        self.btn_connect.clicked.connect(self._on_connect_clicked)
        btn_layout.addWidget(self.btn_connect)
        
        self.btn_disconnect = QPushButton("断开连接")
        self.btn_disconnect.setFixedSize(120, 40)
        self.btn_disconnect.setStyleSheet("""
            QPushButton {
                background-color: #d83b01;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a82e01;
            }
            QPushButton:disabled {
                background-color: #2d2d30;
                color: #555555;
            }
        """)
        self.btn_disconnect.clicked.connect(self._on_disconnect_clicked)
        self.btn_disconnect.setEnabled(False)
        # 设置自定义日志处理器
        # self._setup_log_handler() # Removed old log setup
            
    # def _setup_log_handler(self): # Removed old log setup
    #     """设置日志处理器，将日志输出到界面"""
        
    #     class QTextEditLogger(logging.Handler):
    #         def __init__(self, widget):
    #             super().__init__()
    #             self.widget = widget
    #             self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S'))
                
    #         def emit(self, record):
    #             msg = self.format(record)
    #             # 确保在主线程更新UI
    #             QMetaObject.invokeMethod(self.widget, "append", Qt.ConnectionType.QueuedConnection, Q_ARG(str, msg))
                
    #     # 获取根日志记录器
    #     logger = logging.getLogger()
        
    #     # 创建并添加处理器
    #     log_handler = QTextEditLogger(self.log_console)
    #     logger.addHandler(log_handler)
    
    def _update_status(self):
        """更新状态显示"""
        if not self.dispatcher:
            return
            
        # 更新设备卡片状态和队列信息
        for card in self.device_cards:
            if not card.driver:
                continue
            
            driver_name = card.driver.name
            card.update_status()
            
            # 获取队列信息
            # 1. 正在服务的用户
            current_user = self.dispatcher.device_current_user.get(driver_name)
            
            # 2. 剩余时间
            busy_until = self.dispatcher.device_busy_until.get(driver_name, 0)
            time_left = max(0, int(busy_until - time.time()))
            
            card.update_queue_info(current_user, time_left)
            
    def _on_connect_clicked(self):
        """连接直播间"""
        if not self.dispatcher:
            return
            
        import os
        mock_file = self.mock_file  # 使用选择的弹幕文件
        if not os.path.exists(mock_file):
            logging.error(f"错误: 找不到模拟数据文件 {mock_file}") # Changed from self.log_console.append
            return
            
        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(True)
        logging.info("开始连接直播间...") # Changed from self.log_console.append
        
        # 启动模拟流
        self.dispatcher.start_mock_stream(mock_file)
        
    def _on_disconnect_clicked(self):
        """断开连接"""
        if not self.dispatcher:
            return
            
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        logging.info("正在断开连接...") # Changed from self.log_console.append
        
        self.dispatcher.stop_mock_stream()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 1. 标题
        title = QLabel("中枢控制台")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #d4d4d4;")
        layout.addWidget(title)
        
        # 2. 设备网格区域
        # 使用 FlowLayout 或者简单的 GridLayout
        # 这里为了简单对齐，使用 GridLayout
        
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(20)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.device_cards = []
        
        if self.dispatcher:
            # 获取所有设备并创建卡片
            # 我们按照固定顺序或名字排序
            drivers = list(self.dispatcher.drivers.items())
            
            # 手动映射中文名称
            name_map = {
                "feeder_paste": "湿粮喂食器",
                "feeder_kibble": "猫粮喂食器",
                "feeder_freeze_dried": "冻干喂食器",
                "feeder_canned": "猫罐喂食器",
                "car_hakimi": "哈基米车",
                "laser_ball": "激光灯球"
            }
            
            device_infos = [
                ("feeder_paste", "物联网"),
                ("feeder_kibble", "模拟器"),
                ("feeder_freeze_dried", "模拟器"),
                ("feeder_canned", "物联网"),
                ("car_hakimi", "物联网"),
                ("laser_ball", "物联网"),
            ]
            
            row = 0
            col = 0
            max_cols = 4 # 每行4个
            
            for key, type_label in device_infos:
                driver = self.dispatcher.drivers.get(key)
                display_name = name_map.get(key, key)
                
                # 如果是模拟器，类型显示模拟器，否则显示物联网(默认)
                # 为了更准确，可以检查 driver 类型
                real_type = "物联网"
                if driver and isinstance(driver, SimulatorDriver):
                    real_type = "模拟器"
                
                card = DeviceCard(display_name, real_type, driver)
                self.device_cards.append(card)
                
                grid_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
        layout.addWidget(grid_widget)
        
        # 弹簧
        layout.addStretch()
        
        # 4. 控制按钮区域（底部）
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        self.btn_connect = QPushButton("连接直播间 (模拟)")
        self.btn_connect.setFixedSize(150, 40)
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0062a3;
            }
            QPushButton:disabled {
                background-color: #2d2d30;
                color: #555555;
            }
        """)
        self.btn_connect.clicked.connect(self._on_connect_clicked)
        btn_layout.addWidget(self.btn_connect)
        
        self.btn_disconnect = QPushButton("断开连接")
        self.btn_disconnect.setFixedSize(120, 40)
        self.btn_disconnect.setStyleSheet("""
            QPushButton {
                background-color: #d83b01;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a82e01;
            }
            QPushButton:disabled {
                background-color: #2d2d30;
                color: #555555;
            }
        """)
        self.btn_disconnect.clicked.connect(self._on_disconnect_clicked)
        self.btn_disconnect.setEnabled(False)
        btn_layout.addWidget(self.btn_disconnect)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 5. 日志区域 (三列布局)
        log_layout = QHBoxLayout()
        
        # 5.1 系统日志
        sys_log_group = QGroupBox("💻 系统日志")
        sys_layout = QVBoxLayout()
        self.sys_console = QTextEdit()
        self.sys_console.setReadOnly(True)
        self.sys_console.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas;")
        sys_layout.addWidget(self.sys_console)
        sys_log_group.setLayout(sys_layout)
        log_layout.addWidget(sys_log_group, 1) # 比例 1
        
        # 5.2 弹幕/互动日志
        dm_log_group = QGroupBox("💬 直播间弹幕")
        dm_layout = QVBoxLayout()
        self.dm_console = QTextEdit()
        self.dm_console.setReadOnly(True)
        self.dm_console.setStyleSheet("background-color: #1e1e1e; color: #569cd6; font-family: 'Microsoft YaHei UI';")
        dm_layout.addWidget(self.dm_console)
        dm_log_group.setLayout(dm_layout)
        log_layout.addWidget(dm_log_group, 1) # 比例 1
        
        # 5.3 硬件设备日志
        dev_log_group = QGroupBox("🤖 设备执行")
        dev_layout = QVBoxLayout()
        self.dev_console = QTextEdit()
        self.dev_console.setReadOnly(True)
        self.dev_console.setStyleSheet("background-color: #1e1e1e; color: #4ec9b0; font-family: Consolas;")
        dev_layout.addWidget(self.dev_console)
        dev_log_group.setLayout(dev_layout)
        log_layout.addWidget(dev_log_group, 1) # 比例 1
        
        layout.addLayout(log_layout)
        
        # 设置窗口日志处理
        self.log_handler = QtLogHandler(self.sys_console, self.dm_console, self.dev_console)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
        logging.getLogger().addHandler(self.log_handler)

class QtLogHandler(logging.Handler):
    """自定义日志处理器，支持多列分发"""
    def __init__(self, sys_widget, dm_widget, dev_widget):
        super().__init__()
        self.sys_widget = sys_widget
        self.dm_widget = dm_widget
        self.dev_widget = dev_widget
        
    def emit(self, record):
        msg = self.format(record)
        # 根据日志内容简单分流
        try:
            if "[DANMAKU]" in msg:
                self._append_to_widget(self.dm_widget, msg)
            elif any(x in msg for x in ["[feeder_", "[car_", "[laser_"]):
                self._append_to_widget(self.dev_widget, msg)
            else:
                self._append_to_widget(self.sys_widget, msg)
        except:
            pass
            
    def _append_to_widget(self, widget, msg):
        # 必须在主线程更新 UI
        QMetaObject.invokeMethod(widget, "append", Qt.ConnectionType.QueuedConnection, Q_ARG(str, msg))
