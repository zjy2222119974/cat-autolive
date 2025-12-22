from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class DeviceCard(QFrame):
    """设备状态卡片 - 紧凑型设计"""
    
    def __init__(self, name: str, device_type: str, driver=None, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.setFixedSize(260, 140)  # 接近方形，但高度较小
        
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
        
        # 主布局：垂直排列
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 25, 15, 15)
        main_layout.setSpacing(10)
        
        # 设备名称（顶部居中）
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.name_label)
        
        main_layout.addStretch()
        
        # 底部信息区域：左右分栏
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # 左侧：设备类型
        left_widget = QFrame()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        type_label = QLabel(device_type)
        type_label.setStyleSheet("font-size: 14px; color: #888888;")
        type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_layout.addWidget(type_label)
        
        bottom_layout.addWidget(left_widget)
        
        # 右侧：状态信息
        right_widget = QFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.user_label = QLabel("空闲")
        self.user_label.setStyleSheet("font-size: 14px; color: #cccccc;")
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_layout.addWidget(self.user_label)
        
        self.time_label = QLabel("0s")
        self.time_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #007acc;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_layout.addWidget(self.time_label)
        
        bottom_layout.addWidget(right_widget)
        
        main_layout.addLayout(bottom_layout)
        
        # 状态指示灯 (圆形) - 使用绝对定位放在右上角
        self.status_light = QLabel(self)
        self.status_light.setFixedSize(20, 20)
        self.status_light.setStyleSheet("background-color: #ff4d4f; border-radius: 10px;") # 默认红色
        self.status_light.move(230, 10)  # 放置在右上角（260-20-10=230）
        
        # 如果有驱动，初始化状态
        if self.driver:
            self.update_status()

    def update_queue_info(self, current_user: str, time_left: int):
        """更新队列信息"""
        self.user_label.setText(current_user if current_user else "空闲")
        if time_left > 0:
            self.time_label.setText(f"{time_left}s")
            self.time_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #007acc;")
        else:
            self.time_label.setText("0s")
            self.time_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #666666;")

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
