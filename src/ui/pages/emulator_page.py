"""模拟器控制器页面"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QComboBox, QScrollArea, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)

class EmulatorPage(QWidget):
    """模拟器控制器页面"""
    
    def __init__(self, dispatcher=None):
        super().__init__()
        self.dispatcher = dispatcher
        self.current_device = None
        self.capture_timers = {}  # 保存每个设备的定时器
        self.capture_objects = {}  # 保存每个设备的捕获对象
        self.capture_labels = {}  # 保存每个设备的显示标签
        self.device_window_selections = {}  # 保存每个设备选择的窗口索引
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
        self.devices_layout = QHBoxLayout(devices_widget)
        self.devices_layout.setContentsMargins(0, 0, 0, 0)
        self.devices_layout.setSpacing(10)
        
        self.refresh_devices_list()
        
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
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
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
                border-bottom: 2px solid #007acc;
            }
            QTabBar::tab:hover {
                background-color: #3e3e42;
            }
        """)
        
        self.refresh_preview_tabs()
        
        # 监听标签页切换事件
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        layout.addWidget(self.tab_widget)
        
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
        
        # 窗口选择标签
        window_label = QLabel("选择窗口:")
        window_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        layout.addWidget(window_label)
        
        # 窗口选择下拉框
        self.window_combo = QComboBox()
        self.window_combo.setStyleSheet("""
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
        layout.addWidget(self.window_combo)
        
        # 刷新窗口按钮
        refresh_btn = QPushButton("刷新窗口列表")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3e3e42;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4e4e52;
                border: 1px solid #007acc;
            }
        """)
        refresh_btn.clicked.connect(self._refresh_windows)
        layout.addWidget(refresh_btn)
        
        # 投射窗口按钮
        attach_btn = QPushButton("投射窗口")
        attach_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
        """)
        attach_btn.clicked.connect(self._attach_window)
        layout.addWidget(attach_btn)
        
        # 停止投射按钮
        self.stop_btn = QPushButton("停止投射")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.stop_btn.clicked.connect(self._stop_capture)
        self.stop_btn.hide()  # 初始隐藏
        layout.addWidget(self.stop_btn)
        
        # 初始化窗口列表
        self._refresh_windows()
        
        # 添加提示标签
        self.window_hint = QLabel("请先选择左侧的设备标签页")
        self.window_hint.setStyleSheet("color: #888888; font-size: 12px; font-style: italic;")
        self.window_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.window_hint)
        
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
        feed_button.clicked.connect(self._on_manual_feed_clicked)
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
    
    def refresh_devices_list(self):
        """刷新设备列表"""
        if not hasattr(self, 'devices_layout'):
            return
            
        # 清除现有内容
        while self.devices_layout.count():
            item = self.devices_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
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
                    self.devices_layout.addWidget(card)
            
            if not found:
                no_device_label = QLabel("未检测到模拟器设备")
                no_device_label.setStyleSheet("color: #888888; font-size: 14px;")
                self.devices_layout.addWidget(no_device_label)
        else:
            error_label = QLabel("中枢未连接")
            error_label.setStyleSheet("color: #ff4d4f; font-size: 14px;")
            self.devices_layout.addWidget(error_label)
        
        self.devices_layout.addStretch()

    def refresh_preview_tabs(self):
        """刷新预览标签页"""
        if not hasattr(self, 'tab_widget'):
            return
            
        self.tab_widget.clear()
        
        if not self.dispatcher:
            return
            
        from src.drivers.simulator_driver import SimulatorDriver
        
        name_map = {
            "feeder_paste": "湿粮喂食器",
            "feeder_kibble": "猫粮喂食器",
            "feeder_freeze_dried": "冻干喂食器",
            "feeder_canned": "猫罐喂食器",
            "car_hakimi": "哈基米车",
            "laser_ball": "激光灯球"
        }
        
        # 获取所有模拟器设备并按名称排序，确保标签页顺序一致
        simulator_devices = sorted(
            [(name, driver) for name, driver in self.dispatcher.drivers.items()
             if isinstance(driver, SimulatorDriver)],
            key=lambda x: x[0]
        )
        
        for name, driver in simulator_devices:
                display_name = name_map.get(name, name)
                
                # 创建简单的标签页内容（只有显示区域）
                tab = QWidget()
                tab_layout = QVBoxLayout(tab)
                tab_layout.setContentsMargins(0, 0, 0, 0)
                tab_layout.setSpacing(0)
                
                # 窗口显示容器
                display_container = QWidget()
                display_container.setStyleSheet("background-color: #000000;")
                display_layout = QVBoxLayout(display_container)
                display_layout.setContentsMargins(0, 0, 0, 0)
                
                placeholder = QLabel(f"等待投射 {display_name} 窗口...")
                placeholder.setStyleSheet("color: #666666; font-size: 16px;")
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                display_layout.addWidget(placeholder)
                
                tab_layout.addWidget(display_container)
                
                # 保存引用以便后续更新
                if not hasattr(self, 'tab_containers'):
                    self.tab_containers = {}
                self.tab_containers[name] = display_container
                
                self.tab_widget.addTab(tab, display_name)
    
    
    def refresh_all(self):
        """刷新所有动态内容"""
        self.refresh_devices_list()
        self.refresh_preview_tabs()
        self._refresh_windows()

    def _refresh_windows(self):
        """刷新窗口列表"""
        if not hasattr(self, 'window_combo'):
            return
            
        from src.utils.window_utils import list_windows
        
        # 获取当前选中的设备
        current_device_name = self._get_current_device_name()
        
        self.window_combo.clear()
        windows = list_windows()
        
        for hwnd, title in windows:
            if title:  # 只显示有标题的窗口
                self.window_combo.addItem(title, hwnd)
        
        # 尝试根据关键字自动选中模拟器窗口
        auto_selected = False
        for i in range(self.window_combo.count()):
            text = self.window_combo.itemText(i)
            # 常见模拟器关键字
            if any(keyword in text for keyword in ["雷电", "LDPlayer", "MuMu", "Nox", "模拟器", "BlueStacks"]):
                self.window_combo.setCurrentIndex(i)
                auto_selected = True
                break
        
        # 如果当前设备之前有保存的选择，恢复它
        if current_device_name and current_device_name in self.device_window_selections:
            saved_index = self.device_window_selections[current_device_name]
            if 0 <= saved_index < self.window_combo.count():
                self.window_combo.setCurrentIndex(saved_index)
    
    def _get_current_device_name(self):
        """获取当前标签页对应的设备名称"""
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index < 0 or not self.dispatcher:
            return None
        
        from src.drivers.simulator_driver import SimulatorDriver
        
        simulator_drivers = [(name, driver) for name, driver in self.dispatcher.drivers.items() 
                            if isinstance(driver, SimulatorDriver)]
        
        if current_tab_index >= len(simulator_drivers):
            return None
        
        device_name, _ = simulator_drivers[current_tab_index]
        return device_name
    
    def _on_tab_changed(self, index):
        """标签页切换事件处理"""
        if index < 0:
            return
        
        device_name = self._get_current_device_name()
        if not device_name:
            return
        
        # 更新提示文本
        if hasattr(self, 'window_hint'):
            from src.drivers.simulator_driver import SimulatorDriver
            
            name_map = {
                "feeder_paste": "湿粮喂食器",
                "feeder_kibble": "猫粮喂食器",
                "feeder_freeze_dried": "冻干喂食器",
                "feeder_canned": "猫罐喂食器",
                "car_hakimi": "哈基米车",
                "laser_ball": "激光灯球",
                "catlink": "catlink"
            }
            
            display_name = name_map.get(device_name, device_name)
            
            # 检查是否已经投射
            if device_name in self.capture_timers:
                self.window_hint.setText(f"当前设备: {display_name} (已投射)")
                self.window_hint.setStyleSheet("color: #52c41a; font-size: 12px; font-weight: bold;")
                if hasattr(self, 'stop_btn'):
                    self.stop_btn.show()
            else:
                self.window_hint.setText(f"当前设备: {display_name}")
                self.window_hint.setStyleSheet("color: #007acc; font-size: 12px; font-weight: bold;")
                if hasattr(self, 'stop_btn'):
                    self.stop_btn.hide()
        
        # 恢复该设备的窗口选择
        if device_name in self.device_window_selections:
            saved_index = self.device_window_selections[device_name]
            if hasattr(self, 'window_combo') and 0 <= saved_index < self.window_combo.count():
                self.window_combo.setCurrentIndex(saved_index)
    
    def _attach_window(self):
        """投射窗口到当前标签页（使用实时捕捉）"""
        from src.utils.window_capture import WindowCapture
        from src.drivers.simulator_driver import SimulatorDriver
        
        # 获取当前选中的窗口
        idx = self.window_combo.currentIndex()
        if idx < 0:
            return
        
        hwnd = self.window_combo.itemData(idx)
        if not hwnd:
            return
        
        # 获取当前激活的标签页索引
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index < 0:
            return
        
        # 获取当前标签页对应的设备名称
        if not hasattr(self, 'tab_containers') or not self.dispatcher:
            return
        
        # 找到当前 tab 对应的 driver
        simulator_drivers = [(name, driver) for name, driver in self.dispatcher.drivers.items() 
                            if isinstance(driver, SimulatorDriver)]
        
        if current_tab_index >= len(simulator_drivers):
            return
        
        device_name, driver = simulator_drivers[current_tab_index]
        
        # 更新驱动状态（连接）
        driver.connect(hwnd=hwnd)
        
        # 获取对应的显示容器
        if device_name not in self.tab_containers:
            return
        
        display_container = self.tab_containers[device_name]
        layout = display_container.layout()
        
        # 清除旧内容
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 停止之前的定时器（如果有）
        if device_name in self.capture_timers:
            self.capture_timers[device_name].stop()
            del self.capture_timers[device_name]
        
        try:
            # 创建窗口捕捉对象
            capture = WindowCapture(hwnd)
            self.capture_objects[device_name] = capture
            
            # 创建显示标签
            display_label = QLabel()
            display_label.setScaledContents(False)  # 不自动拉伸，保持宽高比
            display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中显示
            display_label.setStyleSheet("background-color: #000000;")
            layout.addWidget(display_label)
            self.capture_labels[device_name] = display_label
            
            # 创建定时器实现实时刷新（30fps）
            timer = QTimer()
            timer.timeout.connect(lambda: self._update_capture(device_name))
            timer.start(33)  # 33ms ≈ 30fps
            self.capture_timers[device_name] = timer
            
            # 立即捕捉一次
            self._update_capture(device_name)
            
            # 保存当前选择的窗口索引
            self.device_window_selections[device_name] = idx
            
            # 更新提示文本
            if hasattr(self, 'window_hint'):
                name_map = {
                    "feeder_paste": "湿粮喂食器",
                    "feeder_kibble": "猫粮喂食器",
                    "feeder_freeze_dried": "冻干喂食器",
                    "feeder_canned": "猫罐喂食器",
                    "car_hakimi": "哈基米车",
                    "laser_ball": "激光灯球",
                    "catlink": "catlink"
                }
                display_name = name_map.get(device_name, device_name)
                self.window_hint.setText(f"当前设备: {display_name} (已投射)")
                self.window_hint.setStyleSheet("color: #52c41a; font-size: 12px; font-weight: bold;")
            
            # 显示停止按钮
            if hasattr(self, 'stop_btn'):
                self.stop_btn.show()
            
            # 刷新设备列表状态（显示绿点）
            self.refresh_devices_list()
            
        except Exception as e:
            # 如果失败，显示错误信息
            error_label = QLabel(f"投射失败: {str(e)}")
            error_label.setStyleSheet("color: #ff4d4f; font-size: 14px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
    
    def _update_capture(self, device_name):
        """更新指定设备的捕捉画面"""
        if device_name not in self.capture_objects or device_name not in self.capture_labels:
            return
        
        capture = self.capture_objects[device_name]
        label = self.capture_labels[device_name]
        
        # 捕捉窗口内容
        pixmap = capture.capture()
        if pixmap and not pixmap.isNull():
            # 缩放到 label 大小，保持宽高比
            scaled_pixmap = pixmap.scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)
    
    def _stop_capture(self):
        """停止当前标签页的投射"""
        # 获取当前激活的标签页索引
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index < 0:
            return
        
        if not self.dispatcher:
            return
        
        from src.drivers.simulator_driver import SimulatorDriver
        
        # 找到当前 tab 对应的 driver
        simulator_drivers = [(name, driver) for name, driver in self.dispatcher.drivers.items() 
                            if isinstance(driver, SimulatorDriver)]
        
        if current_tab_index >= len(simulator_drivers):
            return
        
        device_name, driver = simulator_drivers[current_tab_index]
        
        # 停止定时器
        if device_name in self.capture_timers:
            self.capture_timers[device_name].stop()
            del self.capture_timers[device_name]
        
        # 清除捕获对象
        if device_name in self.capture_objects:
            del self.capture_objects[device_name]
        
        if device_name in self.capture_labels:
            del self.capture_labels[device_name]
        
        # 断开驱动连接
        driver.disconnect()
        
        # 清除显示区域
        if device_name in self.tab_containers:
            display_container = self.tab_containers[device_name]
            layout = display_container.layout()
            
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 显示占位符
            placeholder = QLabel(f"已停止投射")
            placeholder.setStyleSheet("color: #666666; font-size: 16px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder)
        
        # 隐藏停止按钮
        if hasattr(self, 'stop_btn'):
            self.stop_btn.hide()
        
        # 更新提示文本
        if hasattr(self, 'window_hint'):
            name_map = {
                "feeder_paste": "湿粮喂食器",
                "feeder_kibble": "猫粮喂食器",
                "feeder_freeze_dried": "冻干喂食器",
                "feeder_canned": "猫罐喂食器",
                "car_hakimi": "哈基米车",
                "laser_ball": "激光灯球",
                "catlink": "catlink"
            }
            display_name = name_map.get(device_name, device_name)
            self.window_hint.setText(f"当前设备: {display_name}")
            self.window_hint.setStyleSheet("color: #007acc; font-size: 12px; font-weight: bold;")
        
        # 刷新设备列表状态（显示红点）
        self.refresh_devices_list()

    def select_device(self, device_name: str):
        """根据设备名称选择对应的标签页
        
        Args:
            device_name: 设备驱动名称，例如 'feeder_freeze_dried'
        """
        import logging
        logger = logging.getLogger()
        logger.info(f"[EmulatorPage] select_device called with: {device_name}")
        
        if not self.dispatcher:
            logger.warning("[EmulatorPage] No dispatcher available")
            return
        
        from src.drivers.simulator_driver import SimulatorDriver
        
        # 获取所有模拟器设备列表（按字典顺序排序，确保与标签页顺序一致）
        simulator_drivers = sorted(
            [(name, driver) for name, driver in self.dispatcher.drivers.items() 
             if isinstance(driver, SimulatorDriver)],
            key=lambda x: x[0]
        )
        
        logger.info(f"[EmulatorPage] Found {len(simulator_drivers)} simulator devices")
        for idx, (name, _) in enumerate(simulator_drivers):
            logger.info(f"[EmulatorPage]   Index {idx}: {name}")
        
        # 查找设备在列表中的索引
        for index, (name, driver) in enumerate(simulator_drivers):
            if name == device_name:
                # 切换到对应的标签页
                if hasattr(self, 'tab_widget'):
                    logger.info(f"[EmulatorPage] Switching to tab index {index} for device {device_name}")
                    self.tab_widget.setCurrentIndex(index)
                else:
                    logger.warning("[EmulatorPage] tab_widget not found")
                break
        else:
            logger.warning(f"[EmulatorPage] Device {device_name} not found in simulator list")
    
    def _on_manual_feed_clicked(self):
        """手动出粮按钮点击事件"""
        logger.info("[EmulatorPage] ========== 手动出粮按钮被点击 ==========")
        
        # 获取当前标签页对应的设备
        device_name = self._get_current_device_name()
        logger.info(f"[EmulatorPage] 当前设备: {device_name}")
        
        if not device_name:
            logger.warning("[EmulatorPage] 未选择设备")
            return
        
        # 获取设备驱动
        if not self.dispatcher:
            logger.error("[EmulatorPage] dispatcher 为 None")
            return
            
        if device_name not in self.dispatcher.drivers:
            logger.warning(f"[EmulatorPage] 设备 {device_name} 不存在于 drivers 中")
            logger.info(f"[EmulatorPage] 可用设备: {list(self.dispatcher.drivers.keys())}")
            return
        
        driver = self.dispatcher.drivers[device_name]
        logger.info(f"[EmulatorPage] 获取到驱动: {type(driver).__name__}")
        
        # 调用设备的 execute 方法触发喂食
        logger.info(f"[EmulatorPage] 手动触发设备 {device_name} 喂食")
        result = driver.execute("feed")
        logger.info(f"[EmulatorPage] execute 返回结果: {result}")









