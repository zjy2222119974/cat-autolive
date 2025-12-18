"""Cat AutoLive - 应用主入口"""

import sys
from PyQt6.QtWidgets import QApplication

from src.config.settings import get_settings
from src.utils.logger import setup_logger, get_logger
from src.ui.main_window import MainWindow


def main():
    """应用主函数"""
    # 加载配置
    settings = get_settings()
    settings.load()
    
    # 初始化日志系统
    log_config = {
        'log_file': settings.get('logging.file', 'logs/app.log'),
        'level': settings.get('logging.level', 'INFO'),
        'max_bytes': settings.get('logging.max_bytes', 10485760),
        'backup_count': settings.get('logging.backup_count', 5)
    }
    setup_logger(**log_config)
    
    logger = get_logger()
    logger.info("=" * 50)
    logger.info(f"应用启动: {settings.get('app.name', 'Cat AutoLive')}")
    logger.info(f"版本: {settings.get('app.version', '1.0.0')}")
    logger.info("=" * 50)
    
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName(settings.get('app.name', 'Cat AutoLive'))
    app.setApplicationVersion(settings.get('app.version', '1.0.0'))
    
    # 初始化核心中枢
    from src.core.dispatcher import Dispatcher
    from src.drivers.devices import (
        PasteFeederDriver, KibbleFeederDriver, FreezeDriedFeederDriver,
        CannedFeederDriver, HakimiCarDriver, LaserBallDriver
    )
    
    dispatcher = Dispatcher()
    
    # 1. 猫条/化毛膏喂食器 (物联网)
    feeder_paste = PasteFeederDriver("feeder_paste", host="192.168.1.101", port=80)
    feeder_paste.connect() # 立即连接
    dispatcher.register_driver("feeder_paste", feeder_paste)
    
    # 2. 猫粮喂食器 (模拟器)
    feeder_kibble = KibbleFeederDriver("feeder_kibble", app_package="com.feeder.kibble")
    feeder_kibble.connect()
    dispatcher.register_driver("feeder_kibble", feeder_kibble)
    
    # 3. 冻干喂食器 (模拟器)
    feeder_freeze_dried = FreezeDriedFeederDriver("feeder_freeze_dried", app_package="com.feeder.freeze")
    feeder_freeze_dried.connect()
    dispatcher.register_driver("feeder_freeze_dried", feeder_freeze_dried)
    
    # 4. 猫罐喂食器 (物联网)
    feeder_canned = CannedFeederDriver("feeder_canned", host="192.168.1.102", port=80)
    feeder_canned.connect()
    dispatcher.register_driver("feeder_canned", feeder_canned)
    
    # 5. 哈基米车 (物联网)
    car_hakimi = HakimiCarDriver("car_hakimi", host="192.168.1.103", port=80)
    car_hakimi.connect()
    dispatcher.register_driver("car_hakimi", car_hakimi)
    
    # 6. 激光灯球 (物联网)
    laser_ball = LaserBallDriver("laser_ball", host="192.168.1.104", port=80)
    laser_ball.connect()
    dispatcher.register_driver("laser_ball", laser_ball)
    
    # 启动中枢
    dispatcher.start()
    window = MainWindow(
        dispatcher=dispatcher,
        width=settings.get('window.width', 1200),
        height=settings.get('window.height', 800)
    )
    
    # 应用退出时停止中枢
    def on_exit():
        logger.info("正在停止中枢服务...")
        dispatcher.stop()
        
    app.aboutToQuit.connect(on_exit)
    
    # 设置最小窗口大小
    window.setMinimumSize(
        settings.get('window.min_width', 800),
        settings.get('window.min_height', 600)
    )
    
    window.show()
    logger.info("主窗口已显示")
    
    # 运行应用
    try:
        exit_code = app.exec()
        logger.info(f"应用正常退出，退出码: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"应用异常退出: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
