"""配置管理模块"""

import json
from pathlib import Path
from typing import Any, Dict


class Settings:
    """配置管理类"""
    
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
        self._config: Dict[str, Any] = {}
        self._default_config = {
            "app": {
                "name": "Cat AutoLive",
                "version": "1.0.0",
                "author": "Your Name"
            },
            "window": {
                "width": 1200,
                "height": 800,
                "min_width": 800,
                "min_height": 600
            },
            "logging": {
                "level": "INFO",
                "file": "logs/app.log",
                "max_bytes": 10485760,
                "backup_count": 5
            },
            "platform": "douyin"
        }
    
    def load(self, config_file: str = "config.json"):
        """
        加载配置文件
        
        Args:
            config_file: 配置文件路径
        """
        config_path = Path(config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                print(f"配置文件加载成功: {config_file}")
            except Exception as e:
                print(f"配置文件加载失败: {e}")
                self._config = self._default_config.copy()
        else:
            print(f"配置文件不存在，使用默认配置: {config_file}")
            self._config = self._default_config.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持点分隔的嵌套键）
        
        Args:
            key: 配置键，如 "app.name" 或 "window.width"
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值（支持点分隔的嵌套键）
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, config_file: str = "config.json"):
        """
        保存配置到文件
        
        Args:
            config_file: 配置文件路径
        """
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            print(f"配置文件保存成功: {config_file}")
        except Exception as e:
            print(f"配置文件保存失败: {e}")
    
    @property
    def all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()


# 全局配置实例
_settings_instance = Settings()


def get_settings() -> Settings:
    """获取全局配置实例"""
    return _settings_instance
