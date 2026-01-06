
import json
import os
from typing import Dict
from src.drivers.devices import (
    PasteFeederDriver, KibbleFeederDriver, FreezeDriedFeederDriver,
    CannedFeederDriver, HakimiCarDriver, LaserBallDriver, IntegratedAppDriver
)

CONFIG_PATH = "src/config/devices.json"

def load_devices() -> Dict[str, dict]:
    """Load devices from configuration file."""
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading devices config: {e}")
        return {}

def save_device(name: str, config: dict):
    """Save a new device to configuration."""
    devices = load_devices()
    devices[name] = config
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(devices, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving device config: {e}")

def create_driver(name: str, config: dict):
    """Factory to create driver instance from config."""
    driver_type = config.get("type")
    
    if driver_type == "PasteFeederDriver":
        return PasteFeederDriver(name, host=config.get("host"), port=config.get("port"))
    elif driver_type == "KibbleFeederDriver":
        return KibbleFeederDriver(name, app_package=config.get("app_package"))
    elif driver_type == "FreezeDriedFeederDriver":
        return FreezeDriedFeederDriver(name, app_package=config.get("app_package"))
    elif driver_type == "CannedFeederDriver":
        return CannedFeederDriver(name, host=config.get("host"), port=config.get("port"))
    elif driver_type == "HakimiCarDriver":
        return HakimiCarDriver(name, host=config.get("host"), port=config.get("port"))
    elif driver_type == "LaserBallDriver":
        return LaserBallDriver(name, host=config.get("host"), port=config.get("port"))
    elif driver_type == "IntegratedAppDriver":
        return IntegratedAppDriver(name, app_package=config.get("app_package"))
    
    return None
