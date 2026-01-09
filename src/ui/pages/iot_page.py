"""物联网控制器页面"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QScrollArea, QTabWidget, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class IoTPage(QWidget):
    """物联网控制器页面"""
    
    def __init__(self, dispatcher=None):
        super().__init__()
        self.dispatcher = dispatcher
        self._init_ui()
        
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title = QLabel("控制器 (物联网)")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(title)
        
        # 设备列表区域（固定高度，可滚动）
        devices_section = self._create_devices_section()
        main_layout.addWidget(devices_section)
        
        # 控制模块区域（标签页）
        control_tabs = self._create_control_tabs()
        main_layout.addWidget(control_tabs, 1)  # 给予更多空间
        
    def _create_devices_section(self):
        """创建设备列表区域（固定高度，可滚动）"""
        # 滚动区域容器
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(180)  # 固定高度
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # 设备列表容器
        devices_widget = QWidget()
        devices_layout = QVBoxLayout(devices_widget)
        devices_layout.setContentsMargins(0, 0, 0, 0)
        devices_layout.setSpacing(10)
        
        if self.dispatcher:
            from src.drivers.iot_driver import IoTDriver
            
            # 名字映射
            name_map = {
                "feeder_paste": "湿粮喂食器",
                "feeder_kibble": "猫粮喂食器",
                "feeder_freeze_dried": "冻干喂食器",
                "feeder_canned": "猫罐喂食器",
                "car_hakimi": "哈基米车",
                "laser_ball": "激光灯球"
            }
            
            # 列出所有 IoT 设备
            found = False
            for name, driver in self.dispatcher.drivers.items():
                if isinstance(driver, IoTDriver):
                    found = True
                    display_name = name_map.get(name, name)
                    # 创建设备卡片
                    card = QLabel(f"📡 设备: {display_name} ({name})\nHost: {driver.host}:{driver.port}")
                    card.setStyleSheet("""
                        background-color: #2d2d30;
                        padding: 10px;
                        border-radius: 5px;
                        color: #d4d4d4;
                    """)
                    devices_layout.addWidget(card)
            
            if not found:
                no_device_label = QLabel("未检测到 IoT 设备")
                no_device_label.setStyleSheet("color: #888888; font-size: 14px;")
                devices_layout.addWidget(no_device_label)
        else:
            error_label = QLabel("中枢未连接")
            error_label.setStyleSheet("color: #ff4d4f; font-size: 14px;")
            devices_layout.addWidget(error_label)
        
        devices_layout.addStretch()
        scroll_area.setWidget(devices_widget)
        
        return scroll_area
    
    def _create_control_tabs(self):
        """创建控制模块标签页"""
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background-color: #252526;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #252526;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #3e3e42;
            }
        """)
        
        # 湿粮喂食器标签页
        paste_feeder_tab = self._create_simple_control_panel("湿粮喂食器")
        tab_widget.addTab(paste_feeder_tab, "湿粮喂食器")
        
        # 猫罐喂食器标签页
        canned_feeder_tab = self._create_simple_control_panel("猫罐喂食器")
        tab_widget.addTab(canned_feeder_tab, "猫罐喂食器")
        
        # 哈基米车标签页（重点实现）
        hakimi_car_tab = self._create_hakimi_car_panel()
        tab_widget.addTab(hakimi_car_tab, "哈基米车")
        
        # 激光灯球标签页
        laser_ball_tab = self._create_simple_control_panel("激光灯球")
        tab_widget.addTab(laser_ball_tab, "激光灯球")
        
        return tab_widget
    
    def _create_simple_control_panel(self, device_name: str):
        """创建简单控制面板（占位）"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        placeholder = QLabel(f"{device_name} 控制面板\\n待实现...")
        placeholder.setStyleSheet("""
            font-size: 16px; 
            color: #666666;
            padding: 50px;
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        
        return panel
    
    def _create_hakimi_car_panel(self):
        """创建哈基米车控制面板"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 左侧：摄像头画面 + 指令操作记录
        left_section = self._create_car_left_section()
        layout.addWidget(left_section, 3)  # 占60%宽度
        
        # 右侧：状态信息 + 控制按钮
        right_section = self._create_car_right_section()
        layout.addWidget(right_section, 2)  # 占40%宽度
        
        return panel
    
    def _create_car_left_section(self):
        """创建哈基米车左侧区域（摄像头 + 指令记录）"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 摄像头画面区域
        camera_area = QFrame()
        camera_area.setStyleSheet("""
            QFrame {
                background-color: #0d0d0d;
                border-radius: 5px;
                min-height: 250px;
            }
        """)
        camera_layout = QVBoxLayout(camera_area)
        camera_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        camera_placeholder = QLabel("等待摄像头画面...")
        camera_placeholder.setStyleSheet("""
            font-size: 14px; 
            color: #555555;
        """)
        camera_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        camera_layout.addWidget(camera_placeholder)
        
        layout.addWidget(camera_area, 2)
        
        # 指令操作记录
        command_label = QLabel("设备执行")
        command_label.setStyleSheet("font-size: 14px; color: #cccccc; font-weight: bold;")
        layout.addWidget(command_label)
        
        command_log = QTextEdit()
        command_log.setReadOnly(True)
        command_log.setStyleSheet("""
            QTextEdit {
                background-color: #0d0d0d;
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 5px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """)
        command_log.setPlaceholderText("指令记录将显示在此...")
        # 添加示例日志
        command_log.setHtml("""
            <div style="color: #00ff00;">
                <span style="color: #888888;">引言: #a2</span><br>
                <span style="color: #00ff00;">08:21:45 - [ran_hakimi] <<< 向左移</span><br>
                <span style="color: #888888;">引</span><br>
                <span style="color: #00ff00;">08:21:45 - [ran_hakimi] 正在测试...</span><br>
            </div>
        """)
        layout.addWidget(command_log, 1)
        
        return container
    
    def _create_car_right_section(self):
        """创建哈基米车右侧区域（状态 + 控制）"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d30;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 设备选择下拉框样式标签
        device_label = QLabel("哈基米车已连接 ▼")
        device_label.setStyleSheet("""
            QLabel {
                background-color: #3e3e42;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(device_label)
        
        # 状态显示面板
        status_panel = self._create_car_status_display()
        layout.addWidget(status_panel)
        
        # 方向控制按钮组
        direction_controls = self._create_direction_controls()
        layout.addWidget(direction_controls)
        
        # 添加弹性空间
        layout.addStretch()
        
        return container
    
    def _create_car_status_display(self):
        """创建状态显示区域"""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(status_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 连接状态指示灯和文本
        status_row = QHBoxLayout()
        status_row.setSpacing(10)
        
        # 状态指示灯
        status_light = QLabel()
        status_light.setFixedSize(16, 16)
        status_light.setStyleSheet("""
            background-color: #52c41a;
            border-radius: 8px;
            border: 2px solid #2b5c12;
        """)
        status_row.addWidget(status_light)
        
        # 状态文本
        status_label = QLabel("空闲")
        status_label.setStyleSheet("font-size: 16px; color: #cccccc;")
        status_row.addWidget(status_label)
        status_row.addStretch()
        
        layout.addLayout(status_row)
        
        # 时间显示
        time_label = QLabel("0s")
        time_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #007acc;
        """)
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(time_label)
        
        return status_frame
    
    def _create_direction_controls(self):
        """创建方向控制按钮组"""
        controls_frame = QFrame()
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        button_style = """
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                border-radius: 50%;
                font-size: 16px;
                font-weight: bold;
                min-width: 50px;
                min-height: 50px;
                max-width: 50px;
                max-height: 50px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
        """
        
        # 第一行：上按钮
        top_row = QHBoxLayout()
        top_row.addStretch()
        up_btn = QPushButton("↑")
        up_btn.setStyleSheet(button_style)
        top_row.addWidget(up_btn)
        top_row.addStretch()
        controls_layout.addLayout(top_row)
        
        # 第二行：左、右按钮（中间留空）
        middle_row = QHBoxLayout()
        middle_row.setSpacing(15)
        
        left_btn = QPushButton("←")
        left_btn.setStyleSheet(button_style)
        middle_row.addWidget(left_btn)
        
        # 中间的圆圈按钮（Home/中心）
        center_btn = QPushButton("R")
        center_btn.setStyleSheet(button_style)
        middle_row.addWidget(center_btn)
        
        right_btn = QPushButton("→")
        right_btn.setStyleSheet(button_style)
        middle_row.addWidget(right_btn)
        
        controls_layout.addLayout(middle_row)
        
        # 第三行：下按钮
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()
        down_btn = QPushButton("↓")
        down_btn.setStyleSheet(button_style)
        bottom_row.addWidget(down_btn)
        bottom_row.addStretch()
        controls_layout.addLayout(bottom_row)
        
        return controls_frame
    
    def refresh_all(self):
        """刷新所有内容"""
        # 重新初始化UI以刷新设备列表
        # 这里简单实现，可以优化为只刷新设备列表部分
        pass
    
    def select_device(self, device_name: str):
        """根据设备名称选择对应的标签页
        
        Args:
            device_name: 设备驱动名称，例如 'feeder_paste', 'car_hakimi'
        """
        # IoT 设备名称到标签页索引的映射
        device_tab_map = {
            "feeder_paste": 0,      # 湿粮喂食器
            "feeder_canned": 1,     # 猫罐喂食器
            "car_hakimi": 2,        # 哈基米车
            "laser_ball": 3         # 激光灯球
        }
        
        # 获取对应的标签页索引
        tab_index = device_tab_map.get(device_name)
        
        if tab_index is not None:
            # 查找并切换到对应的标签页
            # 需要找到 tab_widget
            for child in self.findChildren(QTabWidget):
                child.setCurrentIndex(tab_index)
                break

