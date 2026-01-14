"""编辑控制器对话框"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QHBoxLayout, QMessageBox,
    QSpinBox, QFormLayout, QFrame, QScrollArea, QWidget
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
        self.resize(500, 600)  # 增加默认尺寸
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
                min-height: 20px;
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
            QGroupBox {
                border: 1px solid #3e3e42;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #aaaaaa;
            }
        """)
        self._init_ui()
        
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. 基础信息区域
        basic_info_layout = QFormLayout()
        basic_info_layout.setSpacing(10)
        
        # 控制器选择
        self.device_combo = QComboBox()
        self.device_combo.addItem("-- 请选择控制器 --", None)
        for name in self.devices.keys():
            self.device_combo.addItem(name, name)
        self.device_combo.currentIndexChanged.connect(self._on_device_selected)
        basic_info_layout.addRow("选择控制器:", self.device_combo)
        
        # 名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入控制器名称")
        self.name_input.setEnabled(False)
        basic_info_layout.addRow("控制器名称:", self.name_input)
        
        # 类型
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
        basic_info_layout.addRow("设备类型:", self.type_combo)
        
        main_layout.addLayout(basic_info_layout)
        
        # 2. 动态参数区域 (使用 ScrollArea 防止内容过多)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        self.params_layout.setSpacing(10)
        
        scroll_area.setWidget(self.params_container)
        main_layout.addWidget(scroll_area, 1) # 占据主要空间
        
        # 3. 按钮区域
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
        
        main_layout.addLayout(btn_layout)
        
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
            elif item.layout():
                # 递归清除布局
                self._clear_layout(item.layout())
    
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def _load_params(self, config):
        """根据类型加载参数输入框"""
        self._clear_params()
        
        type_label = self.type_combo.currentText()
        
        # 通用参数布局
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 根据类型显示不同的参数
        if type_label in ["猫粮喂食器", "冻干喂食器", "整合APP"]:
            # --- 模拟器设置 ---
            
            # 模拟器路径
            emulator_path_layout = QHBoxLayout()
            self.emulator_path_input = QLineEdit()
            self.emulator_path_input.setPlaceholderText("例如: D:\\MuMu Player 12")
            self.emulator_path_input.setText(config.get('emulator_path', ''))
            emulator_path_layout.addWidget(self.emulator_path_input)
            
            browse_btn = QPushButton("浏览...")
            browse_btn.setMaximumWidth(80)
            browse_btn.clicked.connect(self._browse_emulator_path)
            emulator_path_layout.addWidget(browse_btn)
            
            form_layout.addRow("模拟器路径:", emulator_path_layout)
            
            # 包名
            self.app_package_input = QLineEdit()
            self.app_package_input.setPlaceholderText("例如: com.example.app")
            self.app_package_input.setText(config.get('app_package', ''))
            form_layout.addRow("应用包名:", self.app_package_input)
            
            # 分辨率设置
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            separator.setStyleSheet("background-color: #3e3e42; margin-top: 10px; margin-bottom: 10px;")
            self.params_layout.addLayout(form_layout)
            self.params_layout.addWidget(separator)
            
            # 新的 FormLayout 用于分辨率设置
            res_layout = QFormLayout()
            res_layout.setSpacing(10)
            res_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            
            res_label = QLabel("分辨率设置 (用于坐标计算):")
            res_label.setStyleSheet("font-weight: bold; color: #cccccc;")
            self.params_layout.addWidget(res_label)
            
            # Width
            self.width_input = QSpinBox()
            self.width_input.setRange(100, 4000)
            self.width_input.setValue(config.get('target_width', 720))
            res_layout.addRow("宽 (Width):", self.width_input)
            
            # Height
            self.height_input = QSpinBox()
            self.height_input.setRange(100, 4000)
            self.height_input.setValue(config.get('target_height', 1280))
            res_layout.addRow("高 (Height):", self.height_input)
            
            # DPI
            self.dpi_input = QSpinBox()
            self.dpi_input.setRange(72, 640)
            self.dpi_input.setValue(config.get('dpi', 320))
            res_layout.addRow("DPI:", self.dpi_input)
            
            self.params_layout.addLayout(res_layout)
            
            # 添加说明
            hint_label = QLabel("注意: 请确保此分辨率与模拟器内部设置一致，否则自动化点击可能偏离。")
            hint_label.setStyleSheet("color: #888888; font-size: 12px; font-style: italic;")
            hint_label.setWordWrap(True)
            self.params_layout.addWidget(hint_label)
            
        elif type_label in ["肉泥喂食器", "罐头喂食器", "哈基米小车", "激光逗猫球"]:
            # --- 物联网设置 ---
            self.host_input = QLineEdit()
            self.host_input.setPlaceholderText("例如: 192.168.1.100")
            self.host_input.setText(config.get('host', ''))
            form_layout.addRow("主机地址:", self.host_input)
            
            self.port_input = QSpinBox()
            self.port_input.setRange(1, 65535)
            self.port_input.setValue(config.get('port', 80))
            form_layout.addRow("端口:", self.port_input)
            
            self.params_layout.addLayout(form_layout)
            
        self.params_layout.addStretch()

    
    def _browse_emulator_path(self):
        """浏览选择模拟器路径"""
        from PyQt6.QtWidgets import QFileDialog
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择模拟器安装目录",
            self.emulator_path_input.text() or "C:\\",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.emulator_path_input.setText(directory)
    
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
            config['emulator_path'] = self.emulator_path_input.text().strip()
            config['adb_port'] = 16384  # MuMu默认端口
            config['target_width'] = self.width_input.value()
            config['target_height'] = self.height_input.value()
            config['dpi'] = self.dpi_input.value()
            
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
