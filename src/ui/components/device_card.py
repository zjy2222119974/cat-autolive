from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class DeviceCard(QFrame):
    """设备状态卡片"""
    
    def __init__(self, name: str, device_type: str, driver=None, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.setFixedSize(160, 160)
        
        # 设置样式
        self.setStyleSheet("""
            DeviceCard {
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 8px;
            }
            DeviceCard:hover {
                background-color: #3e3e42;
                border: 1px solid #007acc;
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 30, 10, 10)  # 顶部留出空间给状态灯
        
        # 状态指示灯 (圆形) - 使用绝对定位放在右上角
        self.status_light = QLabel(self)
        self.status_light.setFixedSize(20, 20)
        self.status_light.setStyleSheet("background-color: #ff4d4f; border-radius: 10px;") # 默认红色
        self.status_light.move(130, 10)  # 放置在右上角（160-20-10=130）
        
        layout.addStretch()
        
        # 设备名称
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # 设备类型
        type_label = QLabel(device_type)
        type_label.setStyleSheet("font-size: 12px; color: #888888;")
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(type_label)
        
        # 队列信息区域
        info_widget = QFrame()
        info_widget.setStyleSheet("background-color: #252526; border-radius: 4px; margin-top: 5px;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(2)
        
        self.user_label = QLabel("空闲")
        self.user_label.setStyleSheet("font-size: 11px; color: #cccccc;")
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.user_label)
        
        self.time_label = QLabel("0s")
        self.time_label.setStyleSheet("font-size: 11px; color: #007acc;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.time_label)
        
        layout.addWidget(info_widget)
        
        layout.addStretch()
        
        # 如果有驱动，初始化状态
        if self.driver:
            self.update_status()

    def update_queue_info(self, current_user: str, time_left: int):
        """更新队列信息"""
        self.user_label.setText(current_user if current_user else "空闲")
        if time_left > 0:
            self.time_label.setText(f"剩余: {time_left}s")
            self.time_label.setStyleSheet("font-size: 11px; color: #007acc;")
        else:
            self.time_label.setText("0s")
            self.time_label.setStyleSheet("font-size: 11px; color: #666666;")

    def update_status(self):
        """更新连接状态"""
        if self.driver and self.driver.is_connected:
            self.set_connected(True)
        else:
            self.set_connected(False)
            
    def set_connected(self, connected: bool):
        if connected:
            self.status_light.setStyleSheet("""
                background-color: #52c41a; 
                border-radius: 10px;
                border: 2px solid #2b5c12;
            """)
        else:
            self.status_light.setStyleSheet("""
                background-color: #ff4d4f; 
                border-radius: 10px;
                border: 2px solid #5c1b1c;
            """)
