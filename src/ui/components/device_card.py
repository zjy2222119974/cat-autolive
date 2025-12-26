from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class DeviceCard(QFrame):
    """设备状态卡片 - 紧凑型设计"""
    
    def __init__(self, name: str, device_type: str, driver=None, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.setFixedSize(240, 120)  # Fixed size for stability in FlowLayout


        
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
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(0)

        # 顶部区域：标题 + 状态灯
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # 设备名称
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0; border: none; background: transparent;")
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        top_layout.addWidget(self.name_label, 1)

        # 状态指示灯
        self.status_light = QLabel()
        self.status_light.setFixedSize(14, 14)
        self.status_light.setStyleSheet("background-color: #52c41a; border-radius: 7px;") 
        top_layout.addWidget(self.status_light, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(top_layout)
        
        main_layout.addStretch()
        
        # 底部区域
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(0)
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        
        # 左侧：设备类型
        type_label = QLabel(device_type)
        type_label.setStyleSheet("font-size: 12px; color: #888888; border: none; background: transparent;")
        type_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        bottom_layout.addWidget(type_label)
        
        bottom_layout.addStretch()
        
        # 右侧：状态信息容器 (深色背景)
        self.status_container = QFrame()
        self.status_container.setFixedSize(80, 50) # 固定大小以匹配设计感
        self.status_container.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 6px;
                border: none;
            }
        """)
        
        status_layout = QVBoxLayout(self.status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(2)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.user_label = QLabel("空闲")
        self.user_label.setStyleSheet("font-size: 12px; color: #cccccc; background: transparent;")
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.user_label)
        
        self.time_label = QLabel("0s")
        self.time_label.setStyleSheet("font-size: 14px; font-weight: normal; color: #e0e0e0; background: transparent;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.time_label)
        
        bottom_layout.addWidget(self.status_container)
        
        main_layout.addLayout(bottom_layout)
        
        # 如果有驱动，初始化状态
        if self.driver:
            self.update_status()

    def update_queue_info(self, current_user: str, time_left: int):
        """更新队列信息"""
        self.user_label.setText(current_user if current_user else "空闲")
        if time_left > 0:
            self.time_label.setText(f"{time_left}s")
            self.time_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3399ff; background: transparent;")
        else:
            self.time_label.setText("0s")
            self.time_label.setStyleSheet("font-size: 14px; font-weight: normal; color: #e0e0e0; background: transparent;")

    def update_status(self):
        """更新连接状态"""
        if self.driver and self.driver.is_connected:
            self.set_connected(True)
        else:
            self.set_connected(False)
            
    def set_connected(self, connected: bool):
        if connected:
            self.status_light.setStyleSheet("background-color: #52c41a; border-radius: 7px;")
        else:
            self.status_light.setStyleSheet("background-color: #ff4d4f; border-radius: 7px;")
