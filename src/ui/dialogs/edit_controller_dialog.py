"""编辑控制器对话框"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QHBoxLayout, QMessageBox,
    QSpinBox
)
from PyQt6.QtCore import Qt
from src.utils.device_manager import load_devices, get_device_type_label


class EditControllerDialog(QDialog):
    """编辑控制器对话框"""
    
    def __init__(self, dispatcher=None, parent=None):
        super().__init__(parent)
        self.dispatcher = dispatcher
        self.devices = load_devices()
        self.current_device_name = None
        self.original_name = None
        
        self.setWindowTitle("编辑控制器")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
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
            QLineEdit, QComboBox, QSpinBox {
                background-color: #3e3e42;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
                min-height: 30px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
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
            QPushButton#deleteBtn {
                background-color: #c42b1c;
            }
            QPushButton#deleteBtn:hover {
                background-color: #e81123;
            }
        """)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 控制器选择
        select_layout = QVBoxLayout()
        select_layout.setSpacing(5)
        select_layout.addWidget(QLabel("选择控制器:"))
        self.device_combo = QComboBox()
        self.device_combo.addItem("-- 请选择控制器 --", None)
        for name in self.devices.keys():
            self.device_combo.addItem(name, name)
        self.device_combo.currentIndexChanged.connect(self._on_device_selected)
        select_layout.addWidget(self.device_combo)
        layout.addLayout(select_layout)
        
        # 名称
        name_layout = QVBoxLayout()
        name_layout.setSpacing(5)
        name_layout.addWidget(QLabel("控制器名称:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入控制器名称")
        self.name_input.setEnabled(False)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 类型
        type_layout = QVBoxLayout()
        type_layout.setSpacing(5)
        type_layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "猫粮喂食器", 
            "冻干喂食器", 
            "整合APP",
            "肉泥喂食器",
            "罐头喂食器",
            "哈基米小车",
            "激光逗猫球"
        ])
        self.type_combo.setEnabled(False)
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # 动态参数区域
        self.params_layout = QVBoxLayout()
        self.params_layout.setSpacing(10)
        layout.addLayout(self.params_layout)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_delete = QPushButton("删除")
        self.btn_delete.setObjectName("deleteBtn")
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_delete.setEnabled(False)
        btn_layout.addWidget(self.btn_delete)
        
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setStyleSheet("""
            background-color: #3e3e42;
            border: 1px solid #555555;
        """)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        self.btn_save = QPushButton("保存")
        self.btn_save.clicked.connect(self._on_save)
        self.btn_save.setEnabled(False)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        
    def _on_device_selected(self, index):
        """选择设备时的回调"""
        device_name = self.device_combo.currentData()
        
        if device_name is None:
            # 未选择设备
            self.current_device_name = None
            self.original_name = None
            self.name_input.clear()
            self.name_input.setEnabled(False)
            self.type_combo.setEnabled(False)
            self.btn_save.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self._clear_params()
            return
        
        # 加载设备配置
        self.current_device_name = device_name
        self.original_name = device_name
        config = self.devices[device_name]
        
        # 填充表单
        self.name_input.setText(device_name)
        self.name_input.setEnabled(True)
        self.type_combo.setEnabled(True)
        self.btn_save.setEnabled(True)
        self.btn_delete.setEnabled(True)
        
        # 设置类型
        type_label = get_device_type_label(config.get('type', ''))
        index = self.type_combo.findText(type_label)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # 加载参数
        self._load_params(config)
    
    def _on_type_changed(self, type_label):
        """类型改变时的回调"""
        if not self.current_device_name:
            return
        
        # 重新加载参数输入框
        config = self.devices.get(self.current_device_name, {})
        self._load_params(config)
    
    def _clear_params(self):
        """清空参数输入区域"""
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _load_params(self, config):
        """根据类型加载参数输入框"""
        self._clear_params()
        
        type_label = self.type_combo.currentText()
        
        # 根据类型显示不同的参数
        if type_label in ["猫粮喂食器", "冻干喂食器", "整合APP"]:
            # 模拟器类型 - 需要 app_package
            pkg_layout = QVBoxLayout()
            pkg_layout.setSpacing(5)
            pkg_layout.addWidget(QLabel("应用包名 (app_package):"))
            self.app_package_input = QLineEdit()
            self.app_package_input.setPlaceholderText("例如: com.example.app")
            self.app_package_input.setText(config.get('app_package', ''))
            pkg_layout.addWidget(self.app_package_input)
            self.params_layout.addLayout(pkg_layout)
            
        elif type_label in ["肉泥喂食器", "罐头喂食器", "哈基米小车", "激光逗猫球"]:
            # 物联网类型 - 需要 host 和 port
            host_layout = QVBoxLayout()
            host_layout.setSpacing(5)
            host_layout.addWidget(QLabel("主机地址 (host):"))
            self.host_input = QLineEdit()
            self.host_input.setPlaceholderText("例如: 192.168.1.100")
            self.host_input.setText(config.get('host', ''))
            host_layout.addWidget(self.host_input)
            self.params_layout.addLayout(host_layout)
            
            port_layout = QVBoxLayout()
            port_layout.setSpacing(5)
            port_layout.addWidget(QLabel("端口 (port):"))
            self.port_input = QSpinBox()
            self.port_input.setRange(1, 65535)
            self.port_input.setValue(config.get('port', 80))
            port_layout.addWidget(self.port_input)
            self.params_layout.addLayout(port_layout)
    
    def _on_save(self):
        """保存修改"""
        new_name = self.name_input.text().strip()
        
        # 验证名称
        if not new_name:
            QMessageBox.warning(self, "提示", "请输入控制器名称")
            return
        
        # 检查名称是否重复（排除自身）
        if new_name != self.original_name and new_name in self.devices:
            QMessageBox.warning(self, "提示", f"控制器名称 '{new_name}' 已存在！")
            return
        
        # 获取类型
        type_label = self.type_combo.currentText()
        
        # 构建配置
        config = self._build_config(type_label)
        
        if config is None:
            return
        
        # 保存数据供主窗口使用
        self.result_data = {
            'original_name': self.original_name,
            'new_name': new_name,
            'config': config
        }
        
        self.accept()
    
    def _build_config(self, type_label):
        """根据类型构建配置"""
        config = {}
        
        # 映射类型标签到驱动类型
        type_mapping = {
            "猫粮喂食器": "KibbleFeederDriver",
            "冻干喂食器": "FreezeDriedFeederDriver",
            "整合APP": "IntegratedAppDriver",
            "肉泥喂食器": "PasteFeederDriver",
            "罐头喂食器": "CannedFeederDriver",
            "哈基米小车": "HakimiCarDriver",
            "激光逗猫球": "LaserBallDriver"
        }
        
        driver_type = type_mapping.get(type_label)
        if not driver_type:
            QMessageBox.warning(self, "错误", f"未知的控制器类型: {type_label}")
            return None
        
        config['type'] = driver_type
        
        # 根据类型添加参数
        if type_label in ["猫粮喂食器", "冻干喂食器", "整合APP"]:
            app_package = self.app_package_input.text().strip()
            if not app_package:
                QMessageBox.warning(self, "提示", "请输入应用包名")
                return None
            config['app_package'] = app_package
            
        elif type_label in ["肉泥喂食器", "罐头喂食器", "哈基米小车", "激光逗猫球"]:
            host = self.host_input.text().strip()
            if not host:
                QMessageBox.warning(self, "提示", "请输入主机地址")
                return None
            config['host'] = host
            config['port'] = self.port_input.value()
        
        return config
    
    def _on_delete(self):
        """删除控制器"""
        if not self.current_device_name:
            return
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除控制器 '{self.current_device_name}' 吗？\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.result_data = {
                'action': 'delete',
                'original_name': self.original_name
            }
            self.accept()
    
    def get_data(self):
        """获取对话框结果数据"""
        return getattr(self, 'result_data', None)
