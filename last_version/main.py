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
    from src.core.dispatcher import Dispatcher
    from src.utils.device_manager import load_devices, create_driver
    
    dispatcher = Dispatcher()
    
    # 加载并注册所有设备
    devices_config = load_devices()
    for name, config in devices_config.items():
        driver = create_driver(name, config)
        if driver:
            # IoT 设备通常需要 host 配置，模拟器需要包名
            # 这里统一注册，connect 由用户手动触发或后续逻辑处理
            dispatcher.register_driver(name, driver)
            logger.info(f"已加载设备: {name} ({config.get('type')})")
        else:
            logger.error(f"无法创建驱动: {name}, 配置: {config}")

    
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
