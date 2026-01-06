from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QHBoxLayout, QMessageBox
)

class AddSimulatorDialog(QDialog):
    """新增模拟器对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增模拟器")
        self.setFixedWidth(300)
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d30;
                color: #d4d4d4;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            }
            QLabel {
                color: #d4d4d4;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                background-color: #3e3e42;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Name
        name_layout = QVBoxLayout()
        name_layout.setSpacing(5)
        name_layout.addWidget(QLabel("控制器名称:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入控制器名称")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Type
        type_layout = QVBoxLayout()
        type_layout.setSpacing(5)
        type_layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        # Map nice names to internal identifiers or just use text
        # We will use text here and map it in the main window or here
        self.type_combo.addItems(["猫粮喂食器", "冻干喂食器", "整合APP"]) 
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_reset = QPushButton("重置")
        self.btn_reset.setStyleSheet("""
            background-color: #3e3e42;
            border: 1px solid #555555;
        """)
        self.btn_reset.clicked.connect(self.reset_form)
        btn_layout.addWidget(self.btn_reset)
        
        self.btn_add = QPushButton("添加")
        self.btn_add.clicked.connect(self._on_add)
        btn_layout.addWidget(self.btn_add)
        
        layout.addLayout(btn_layout)
        
    def reset_form(self):
        self.name_input.clear()
        self.type_combo.setCurrentIndex(0)
        
    def _on_add(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "提示", "请输入控制器名称")
            return
        self.accept()
        
    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "type_label": self.type_combo.currentText()
        }
