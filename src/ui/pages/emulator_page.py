"""模拟器控制器页面"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class EmulatorPage(QWidget):
    """模拟器控制器页面"""
    
    
    def __init__(self, dispatcher=None):
        super().__init__()
        self.dispatcher = dispatcher
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("控制器 (模拟器)")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        if self.dispatcher:
            from src.drivers.simulator_driver import SimulatorDriver
            
            
            # 名字映射
            name_map = {
                "feeder_paste": "湿粮喂食器",
                "feeder_kibble": "猫粮喂食器",
                "feeder_freeze_dried": "冻干喂食器",
                "feeder_canned": "猫罐喂食器",
                "car_hakimi": "哈基米车",
                "laser_ball": "激光灯球"
            }
            
            # 列出所有模拟器设备
            found = False
            for name, driver in self.dispatcher.drivers.items():
                if isinstance(driver, SimulatorDriver):
                    found = True
                    display_name = name_map.get(name, name)
                    # 创建设备卡片
                    target = driver.app_package if driver.app_package else driver.window_title
                    card = QLabel(f"📱 设备: {display_name} ({name})\nTarget: {target}")
                    card.setStyleSheet("""
                        background-color: #2d2d30;
                        padding: 10px;
                        border-radius: 5px;
                        margin-bottom: 5px;
                        color: #d4d4d4;
                    """)
                    layout.addWidget(card)
            
            if not found:
                layout.addWidget(QLabel("未检测到模拟器设备"))
        else:
            layout.addWidget(QLabel("中枢未连接"))
        
        layout.addStretch()
