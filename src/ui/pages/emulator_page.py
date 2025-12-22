"""模拟器控制器页面"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QComboBox, QScrollArea, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class EmulatorPage(QWidget):
    """模拟器控制器页面"""
    
    def __init__(self, dispatcher=None):
        super().__init__()
        self.dispatcher = dispatcher
        self.current_device = None
        self._init_ui()
        
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title = QLabel("控制器 (模拟器)")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(title)
        
        # 设备列表区域（顶部）
        devices_section = self._create_devices_section()
        main_layout.addWidget(devices_section)
        
        # 控制模块区域（底部，红框部分）
        control_section = self._create_control_section()
        main_layout.addWidget(control_section, 1)  # 给予更多空间
        
    def _create_devices_section(self):
        """创建设备列表区域"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 设备卡片容器（横向滚动）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(150)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # 设备列表容器
        devices_widget = QWidget()
        devices_layout = QHBoxLayout(devices_widget)
        devices_layout.setContentsMargins(0, 0, 0, 0)
        devices_layout.setSpacing(10)
        
        if self.dispatcher:
            from src.drivers.simulator_driver import SimulatorDriver
            from src.ui.components.device_card import DeviceCard
            
            # 名字映射
            name_map = {
                "feeder_paste": "湿粮喂食器",
                "feeder_kibble": "猫粮喂食器",
                "feeder_freeze_dried": "冻干喂食器",
                "feeder_canned": "猫罐喂食器",
                "car_hakimi": "哈基米车",
                "laser_ball": "激光灯球"
            }
            
            # 列出所有模拟器设备
            found = False
            for name, driver in self.dispatcher.drivers.items():
                if isinstance(driver, SimulatorDriver):
                    found = True
                    display_name = name_map.get(name, name)
                    card = DeviceCard(display_name, "模拟器", driver)
                    devices_layout.addWidget(card)
            
            if not found:
                no_device_label = QLabel("未检测到模拟器设备")
                no_device_label.setStyleSheet("color: #888888; font-size: 14px;")
                devices_layout.addWidget(no_device_label)
        else:
            error_label = QLabel("中枢未连接")
            error_label.setStyleSheet("color: #ff4d4f; font-size: 14px;")
            devices_layout.addWidget(error_label)
        
        devices_layout.addStretch()
        scroll_area.setWidget(devices_widget)
        layout.addWidget(scroll_area)
        
        return section
    
    def _create_control_section(self):
        """创建控制模块区域（红框部分）"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(section)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 左侧：实时画面区域（带标签页）
        preview_area = self._create_preview_area()
        layout.addWidget(preview_area, 3)  # 占60%宽度
        
        # 右侧：控制面板区域
        control_panel = self._create_control_panel()
        layout.addWidget(control_panel, 2)  # 占40%宽度
        
        return section
    
    def _create_preview_area(self):
        """创建左侧实时画面区域"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标签页（猫粮喂食器、冻干喂食器）
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #3e3e42;
            }
        """)
        
        # 猫粮喂食器标签页
        kibble_tab = QWidget()
        kibble_layout = QVBoxLayout(kibble_tab)
        kibble_layout.setContentsMargins(10, 10, 10, 10)
        kibble_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        kibble_placeholder = QLabel("等待窗口捕捉...")
        kibble_placeholder.setStyleSheet("""
            font-size: 16px; 
            color: #666666;
            background-color: #1e1e1e;
            padding: 50px;
        """)
        kibble_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        kibble_layout.addWidget(kibble_placeholder)
        
        tab_widget.addTab(kibble_tab, "猫粮喂食器")
        
        # 冻干喂食器标签页
        freeze_tab = QWidget()
        freeze_layout = QVBoxLayout(freeze_tab)
        freeze_layout.setContentsMargins(10, 10, 10, 10)
        freeze_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        freeze_placeholder = QLabel("等待窗口捕捉...")
        freeze_placeholder.setStyleSheet("""
            font-size: 16px; 
            color: #666666;
            background-color: #1e1e1e;
            padding: 50px;
        """)
        freeze_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        freeze_layout.addWidget(freeze_placeholder)
        
        tab_widget.addTab(freeze_tab, "冻干喂食器")
        
        layout.addWidget(tab_widget)
        
        return container
    
    def _create_control_panel(self):
        """创建右侧控制面板"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #2d2d30;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 设备选择下拉框
        device_combo = QComboBox()
        device_combo.setStyleSheet("""
            QComboBox {
                background-color: #3e3e42;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 1px solid #007acc;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #cccccc;
                margin-right: 5px;
            }
        """)
        device_combo.addItem("模拟器已捕捉 ▼")
        layout.addWidget(device_combo)
        
        # 状态显示面板
        status_panel = self._create_status_display()
        layout.addWidget(status_panel)
        
        # 控制按钮
        feed_button = QPushButton("手动出粮")
        feed_button.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
        """)
        feed_button.setMinimumHeight(45)
        layout.addWidget(feed_button)
        
        # 添加弹性空间，将控件推到顶部
        layout.addStretch()
        
        return panel
    
    def _create_status_display(self):
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
