"""主窗口模块"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMenuBar, QMenu, QToolBar,
    QStatusBar, QTextEdit, QSplitter, QListWidget,
    QStackedWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QActionGroup
import os

from src.utils.logger import get_logger
from src.ui.pages.hub_page import HubPage
from src.ui.pages.emulator_page import EmulatorPage
from src.ui.pages.iot_page import IoTPage
from src.ui.pages.platform_page import PlatformPage
from src.ui.pages.avatar_page import AvatarPage
from src.ui.dialogs.gift_config_dialog import GiftConfigDialog


class MainWindow(QMainWindow):
    """应用主窗口"""
    
    
    def __init__(self, dispatcher=None, width: int = 1200, height: int = 800):
        super().__init__()
        self.dispatcher = dispatcher
        self.logger = get_logger()
        self.current_mock_file = "mockData/mockDanmaku.txt"  # 默认弹幕文件
        self.logger.info("初始化主窗口")
        
        self._init_ui(width, height)
        self._create_menu_bar()
        self._create_status_bar()
    
    def _init_ui(self, width: int, height: int):
        """初始化UI"""
        self.setWindowTitle("Cat AutoLive")
        self.resize(width, height)
        
        # 设置样式表 - 现代深色主题
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                font-size: 14px;
            }
            
            QMenuBar {
                background-color: #2d2d30;
                color: #d4d4d4;
                border-bottom: 1px solid #3e3e42;
            }
            
            QMenuBar::item:selected {
                background-color: #3e3e42;
            }
            
            QMenu {
                background-color: #2d2d30;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
            }
            
            QMenu::item:selected {
                background-color: #094771;
            }
            
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            
            /* 侧边栏样式 */
            QListWidget {
                background-color: #252526;
                border: none;
                border-right: 1px solid #3e3e42;
                outline: none;
            }
            
            QListWidget::item {
                height: 40px;
                padding-left: 10px;
                color: #cccccc;
            }
            
            QListWidget::item:selected {
                background-color: #094771;
                color: #ffffff;
                border-left: 3px solid #007acc;
            }
            
            QListWidget::item:hover:!selected {
                background-color: #2a2d2e;
            }
            
            QSplitter::handle {
                background-color: #3e3e42;
            }
        """)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧导航栏
        nav_widget = self._create_navigation()
        splitter.addWidget(nav_widget)
        
        # 右侧内容区 (使用 StackedWidget)
        self.content_stack = QStackedWidget()
        self._init_pages()
        splitter.addWidget(self.content_stack)
        
        # 设置分割比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setCollapsible(0, False)
        
        main_layout.addWidget(splitter)
    
    def _create_navigation(self) -> QWidget:
        """创建左侧导航栏"""
        self.nav_list = QListWidget()
        self.nav_list.setMaximumWidth(250)
        self.nav_list.setMinimumWidth(200)
        
        # 添加导航项
        nav_items = [
            "中枢",
            "控制器 (模拟器)",
            "控制器 (物联网)",
            "多平台入口",
            "数字人"
        ]
        
        self.nav_list.addItems(nav_items)
        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        
        return self.nav_list
    
    def _init_pages(self):
        """初始化所有页面"""
        self.pages = [
            HubPage(self.dispatcher),
            EmulatorPage(self.dispatcher),
            IoTPage(self.dispatcher),
            PlatformPage(),
            AvatarPage()
        ]
        
        for page in self.pages:
            self.content_stack.addWidget(page)
        
        # 设置 HubPage 的初始弹幕文件
        if len(self.pages) > 0:
            self.pages[0].set_mock_file(self.current_mock_file)
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 菜单
        menu_action = menubar.addMenu("菜单")
        settings_action = menubar.addMenu("设置")
        
        # 填充菜单项
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        menu_action.addAction(exit_action)
        
        # 添加控制器子菜单
        add_controller_menu = menu_action.addMenu("添加控制器")
        
        add_sim_action = QAction("模拟器", self)
        add_sim_action.triggered.connect(self._show_add_simulator_dialog)
        add_controller_menu.addAction(add_sim_action)
        
        add_iot_action = QAction("物联网", self)
        add_iot_action.setEnabled(False) # 暂未实现
        add_controller_menu.addAction(add_iot_action)
        
        # 测试弹幕子菜单
        mock_menu = menu_action.addMenu("测试弹幕")
        self._create_mock_file_menu(mock_menu)
        
        # 设置菜单项
        gift_config_action = QAction("配置节目单", self)
        gift_config_action.triggered.connect(self._show_gift_config_dialog)
        settings_action.addAction(gift_config_action)
        
        pref_action = QAction("首选项", self)
        settings_action.addAction(pref_action)
    
    def _create_mock_file_menu(self, menu: QMenu):
        """创建测试弹幕子菜单"""
        mock_dir = "mockData"
        
        # 检查目录是否存在
        if not os.path.exists(mock_dir):
            no_files_action = QAction("未找到测试文件", self)
            no_files_action.setEnabled(False)
            menu.addAction(no_files_action)
            return
        
        # 扫描 mockData 目录下的所有 .txt 文件
        mock_files = []
        try:
            for file in os.listdir(mock_dir):
                if file.endswith(".txt"):
                    mock_files.append(os.path.join(mock_dir, file))
        except Exception as e:
            self.logger.error(f"扫描测试弹幕文件失败: {e}")
            return
        
        if not mock_files:
            no_files_action = QAction("未找到测试文件", self)
            no_files_action.setEnabled(False)
            menu.addAction(no_files_action)
            return
        
        # 对文件名排序
        mock_files.sort()
        
        # 创建动作组（用于单选）
        action_group = QActionGroup(self)
        action_group.setExclusive(True)
        
        # 为每个文件创建菜单项
        for file_path in mock_files:
            file_name = os.path.basename(file_path)
            action = QAction(file_name, self)
            action.setCheckable(True)
            
            # 设置默认选中项
            if file_path == self.current_mock_file:
                action.setChecked(True)
            
            # 连接选择事件
            action.triggered.connect(lambda checked, path=file_path: self._on_mock_file_selected(path))
            
            action_group.addAction(action)
            menu.addAction(action)
        
        self.logger.info(f"加载了 {len(mock_files)} 个测试弹幕文件")
    
    def _on_mock_file_selected(self, file_path: str):
        """选择测试弹幕文件"""
        self.current_mock_file = file_path
        file_name = os.path.basename(file_path)
        self.logger.info(f"已选择测试弹幕文件: {file_name}")
        self.statusBar().showMessage(f"当前测试弹幕: {file_name}")
        
        # 如果 HubPage 已经初始化，更新其弹幕文件
        if hasattr(self, 'pages') and len(self.pages) > 0:
            hub_page = self.pages[0]  # HubPage 是第一个页面
            if hasattr(hub_page, 'set_mock_file'):
                hub_page.set_mock_file(file_path)
    
    def _create_status_bar(self):
        """创建状态栏"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        statusbar.showMessage("就绪")
    
    def _on_nav_changed(self, index: int):
        """导航栏切换事件"""
        if 0 <= index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)
            item = self.nav_list.item(index)
            self.logger.info(f"切换页面: {item.text()}")
            self.statusBar().showMessage(f"当前页面: {item.text()}")
            
    def _show_gift_config_dialog(self):
        """显示礼物配置对话框"""
        from src.config.settings import get_settings
        import os
        
        settings = get_settings()
        platform = settings.get("platform", "douyin")
        config_path = f"src/config/giftShop/{platform}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # If file doesn't exist, maybe copy from default or create empty? 
        # For now, just pass the path, the dialog handles loading (and might fail if missing, but we just moved it)
        
        dialog = GiftConfigDialog(config_path, self)
        dialog.exec()

    def _show_add_simulator_dialog(self):
        """显示新增模拟器对话框"""
        from src.ui.dialogs.add_simulator_dialog import AddSimulatorDialog
        from src.utils.device_manager import save_device, create_driver
        from PyQt6.QtWidgets import QMessageBox
        
        dialog = AddSimulatorDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            name = data['name']
            type_label = data['type_label']
            
            # 检查名称是否已存在
            if self.dispatcher and name in self.dispatcher.drivers:
                 QMessageBox.warning(self, "错误", f"设备名称 '{name}' 已存在！")
                 return
            
            # 准备配置
            config = {}
            if type_label == "猫粮喂食器":
                 config = {
                     "type": "KibbleFeederDriver", 
                     "app_package": f"com.feeder.kibble.{name}"
                 }
            elif type_label == "冻干喂食器":
                 config = {
                     "type": "FreezeDriedFeederDriver", 
                     "app_package": f"com.feeder.freeze.{name}"
                 }
            elif type_label == "整合APP":
                 config = {
                     "type": "IntegratedAppDriver", 
                     "app_package": f"com.app.integrated.{name}"
                 }
            
            # 保存到配置文件
            if config:
                save_device(name, config)
                self.logger.info(f"保存设备配置: {name}")

            # 实例化驱动
            driver = create_driver(name, config)
            
            if driver and self.dispatcher:
                # 注册驱动 (默认不连接，即红色圆点状态)
                self.dispatcher.register_driver(name, driver)
                
                # 刷新 UI
                # HubPage (Index 0)
                if len(self.pages) > 0 and hasattr(self.pages[0], 'refresh_devices'):
                    self.pages[0].refresh_devices()
                
                # EmulatorPage (Index 1)
                if len(self.pages) > 1 and hasattr(self.pages[1], 'refresh_all'):
                    self.pages[1].refresh_all()
                    
                self.logger.info(f"成功添加模拟器: {name} [{type_label}]")
                self.statusBar().showMessage(f"已添加设备: {name}")


