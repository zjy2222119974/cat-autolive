"""多平台入口页面"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class PlatformPage(QWidget):
    """多平台入口页面"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("多平台入口")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        content = QLabel("此处将显示 Bilibili/抖音 等平台的连接配置")
        content.setStyleSheet("color: #888888; font-size: 14px;")
        layout.addWidget(content)
        
        layout.addStretch()
