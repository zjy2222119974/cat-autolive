"""数字人页面"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class AvatarPage(QWidget):
    """数字人页面"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("数字人")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        content = QLabel("此处将显示 AI 数字人交互设置")
        content.setStyleSheet("color: #888888; font-size: 14px;")
        layout.addWidget(content)
        
        layout.addStretch()
