"""日志工具模块"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:
    """日志管理器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.logger = None
    
    def setup(self, log_file: str = "logs/app.log", 
              level: str = "INFO",
              max_bytes: int = 10485760,
              backup_count: int = 5):
        """
        配置日志系统
        
        Args:
            log_file: 日志文件路径
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的日志文件数量
        """
        # 创建日志目录
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建logger
        self.logger = logging.getLogger("CatAutoLive")
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（带日志轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info("日志系统初始化完成")
    
    def get_logger(self):
        """获取logger实例"""
        if self.logger is None:
            self.setup()
        return self.logger


# 全局logger实例
_logger_instance = Logger()


def get_logger():
    """获取全局logger实例"""
    return _logger_instance.get_logger()


def setup_logger(**kwargs):
    """配置全局logger"""
    _logger_instance.setup(**kwargs)
