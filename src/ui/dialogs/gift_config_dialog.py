import json
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    QMessageBox, QAbstractItemView, QComboBox
)
from PyQt6.QtCore import Qt
from src.utils.logger import get_logger

class GiftConfigDialog(QDialog):
    def __init__(self, config_path: str, parent=None):
        super().__init__(parent)
        self.config_path = config_path
        self.logger = get_logger()
        self.data = {}
        self.gift_options = []
        
        self._load_gift_options()
        self._init_ui()
        self.load_data()

    def _load_gift_options(self):
        """加载礼物选项列表"""
        try:
            # 推断平台名称: src/config/giftShop/douyin.json -> douyin
            filename = os.path.basename(self.config_path)
            platform = os.path.splitext(filename)[0]
            
            # 寻找对应的礼物列表文件: src/config/giftList/douyin_gifts.json
            # 假设 giftList 在 config 目录下
            base_dir = os.path.dirname(os.path.dirname(self.config_path)) # src/config
            option_path = os.path.join(base_dir, "giftList", f"{platform}_gifts.json")
            
            if os.path.exists(option_path):
                with open(option_path, 'r', encoding='utf-8') as f:
                    self.gift_options = json.load(f)
                self.logger.info(f"Loaded {len(self.gift_options)} gift options from {option_path}")
            else:
                self.logger.warning(f"Gift options file not found: {option_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to load gift options: {e}")

    def _init_ui(self):
        self.setWindowTitle("配置节目单")
        self.resize(900, 600)
        
        layout = QVBoxLayout(self)
        
        # Tabs
        self.tabs = QTabWidget()
        self.gift_tab = QWidget()
        self.rule_tab = QWidget()
        
        self.tabs.addTab(self.gift_tab, "礼物配置")
        self.tabs.addTab(self.rule_tab, "指令规则")
        
        layout.addWidget(self.tabs)
        
        # Setup Tabs
        self._setup_gift_tab()
        self._setup_rule_tab()
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.reset_btn = QPushButton("重置")
        self.save_btn = QPushButton("保存")
        
        self.reset_btn.clicked.connect(self.reset_data)
        self.save_btn.clicked.connect(self.save_data)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        
        # Styling
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: #d4d4d4; }
            QTabWidget::pane { border: 1px solid #3e3e42; }
            QTabBar::tab { background: #2d2d30; color: #d4d4d4; padding: 8px 20px; }
            QTabBar::tab:selected { background: #3e3e42; }
            QTableWidget { background-color: #252526; color: #d4d4d4; gridline-color: #3e3e42; border: none; }
            QHeaderView::section { background-color: #2d2d30; color: #d4d4d4; padding: 4px; border: 1px solid #3e3e42; }
            QPushButton { background-color: #0e639c; color: white; border: none; padding: 6px 15px; border-radius: 2px; }
            QPushButton:hover { background-color: #1177bb; }
            QPushButton:pressed { background-color: #094771; }
            QComboBox { background-color: #3c3c3c; color: #d4d4d4; border: 1px solid #3e3e42; padding: 2px; }
            QComboBox QAbstractItemView { background-color: #252526; color: #d4d4d4; selection-background-color: #094771; }
        """)

    def _setup_gift_tab(self):
        layout = QVBoxLayout(self.gift_tab)
        self.gift_table = QTableWidget()
        self.gift_table.setColumnCount(5)
        self.gift_table.setHorizontalHeaderLabels(["礼物名称", "价格", "类型", "描述", "Key"])
        self.gift_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.gift_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.gift_table.hideColumn(4) # Hide Key column
        layout.addWidget(self.gift_table)

    def _setup_rule_tab(self):
        layout = QVBoxLayout(self.rule_tab)
        self.rule_table = QTableWidget()
        self.rule_table.setColumnCount(3)
        self.rule_table.setHorizontalHeaderLabels(["指令/规则", "描述", "Key"])
        self.rule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rule_table.hideColumn(2) # Hide Key column
        layout.addWidget(self.rule_table)

    def load_data(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # Populate Gifts
            gifts = self.data.get('gifts', {})
            self.gift_table.setRowCount(len(gifts))
            for i, (key, val) in enumerate(gifts.items()):
                # Gift Name (ComboBox)
                name = str(val.get('name', ''))
                combo = QComboBox()
                combo.setEditable(False)
                
                # Add options
                for opt in self.gift_options:
                    combo.addItem(opt['name'], opt['price'])
                
                combo.setCurrentText(name)
                # Connect signal using a closure to capture the row index
                combo.currentTextChanged.connect(lambda text, row=i: self._on_gift_changed(text, row))
                
                self.gift_table.setCellWidget(i, 0, combo)
                
                # Price
                price_item = QTableWidgetItem(str(val.get('price', 0)))
                price_item.setFlags(price_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.gift_table.setItem(i, 1, price_item)
                
                # Type
                type_item = QTableWidgetItem(str(val.get('type', '')))
                type_item.setFlags(type_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.gift_table.setItem(i, 2, type_item)
                
                # Description
                self.gift_table.setItem(i, 3, QTableWidgetItem(str(val.get('description', ''))))
                # Key (Hidden)
                self.gift_table.setItem(i, 4, QTableWidgetItem(key))

            # Populate Rules
            rules = self.data.get('command_rules', {})
            self.rule_table.setRowCount(len(rules))
            for i, (key, val) in enumerate(rules.items()):
                self.rule_table.setItem(i, 0, QTableWidgetItem(key))
                self.rule_table.setItem(i, 1, QTableWidgetItem(str(val.get('description', ''))))
                self.rule_table.setItem(i, 2, QTableWidgetItem(key))
                
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            QMessageBox.critical(self, "错误", f"加载配置文件失败: {e}")

    def _on_gift_changed(self, text, row):
        """当礼物名称改变时，自动更新价格"""
        for opt in self.gift_options:
            if opt['name'] == text:
                price = opt['price']
                self.gift_table.setItem(row, 1, QTableWidgetItem(str(price)))
                break

    def save_data(self):
        try:
            # Save Gifts
            for i in range(self.gift_table.rowCount()):
                key = self.gift_table.item(i, 4).text()
                if key in self.data['gifts']:
                    # Get name from ComboBox
                    combo = self.gift_table.cellWidget(i, 0)
                    if isinstance(combo, QComboBox):
                        self.data['gifts'][key]['name'] = combo.currentText()
                    
                    try:
                        self.data['gifts'][key]['price'] = float(self.gift_table.item(i, 1).text())
                    except ValueError:
                        pass # Keep original if invalid
                    self.data['gifts'][key]['type'] = self.gift_table.item(i, 2).text()
                    self.data['gifts'][key]['description'] = self.gift_table.item(i, 3).text()

            # Save Rules
            for i in range(self.rule_table.rowCount()):
                key = self.rule_table.item(i, 2).text()
                if key in self.data['command_rules']:
                    # Key (command) is not editable in this simple view, only description
                    self.data['command_rules'][key]['description'] = self.rule_table.item(i, 1).text()

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "成功", "配置已保存")
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            QMessageBox.critical(self, "错误", f"保存配置文件失败: {e}")

    def reset_data(self):
        self.load_data()
        QMessageBox.information(self, "提示", "已重置为文件中的状态")
