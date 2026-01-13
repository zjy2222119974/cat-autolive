
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

def update_device(old_name: str, new_name: str, config: dict):
    """Update an existing device configuration."""
    devices = load_devices()
    
    # Remove old entry if name changed
    if old_name != new_name and old_name in devices:
        del devices[old_name]
    
    # Update with new configuration
    devices[new_name] = config
    
    # Save to file
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(devices, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error updating device config: {e}")

def delete_device(name: str):
    """Delete a device from configuration."""
    devices = load_devices()
    
    if name in devices:
        del devices[name]
        
        # Save to file
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(devices, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error deleting device config: {e}")

def get_device_type_label(driver_type: str) -> str:
    """Convert driver type to user-friendly label."""
    type_mapping = {
        "PasteFeederDriver": "肉泥喂食器",
        "KibbleFeederDriver": "猫粮喂食器",
        "FreezeDriedFeederDriver": "冻干喂食器",
        "CannedFeederDriver": "罐头喂食器",
        "HakimiCarDriver": "哈基米小车",
        "LaserBallDriver": "激光逗猫球",
        "IntegratedAppDriver": "整合APP"
    }
    return type_mapping.get(driver_type, driver_type)

def get_driver_type_from_label(label: str) -> str:
    """Convert user-friendly label to driver type."""
    label_mapping = {
        "肉泥喂食器": "PasteFeederDriver",
        "猫粮喂食器": "KibbleFeederDriver",
        "冻干喂食器": "FreezeDriedFeederDriver",
        "罐头喂食器": "CannedFeederDriver",
        "哈基米小车": "HakimiCarDriver",
        "激光逗猫球": "LaserBallDriver",
        "整合APP": "IntegratedAppDriver"
    }
    return label_mapping.get(label, label)

def create_driver(name: str, config: dict, ocr_detector=None):
    """Factory to create driver instance from config."""
    driver_type = config.get("type")
    
    # common settings for simulators
    target_width = config.get("target_width", 720)
    target_height = config.get("target_height", 1280)
    dpi = config.get("dpi", 320)
    
    if driver_type == "PasteFeederDriver":
        return PasteFeederDriver(name, host=config.get("host"), port=config.get("port"))
    elif driver_type == "KibbleFeederDriver":
        return KibbleFeederDriver(name, app_package=config.get("app_package"), 
                                 target_width=target_width, target_height=target_height, dpi=dpi)
    elif driver_type == "FreezeDriedFeederDriver":
        return FreezeDriedFeederDriver(name, app_package=config.get("app_package"), ocr_detector=ocr_detector,
                                      target_width=target_width, target_height=target_height, dpi=dpi)
    elif driver_type == "CannedFeederDriver":
        return CannedFeederDriver(name, host=config.get("host"), port=config.get("port"))
    elif driver_type == "HakimiCarDriver":
        return HakimiCarDriver(name, host=config.get("host"), port=config.get("port"))
    elif driver_type == "LaserBallDriver":
        return LaserBallDriver(name, host=config.get("host"), port=config.get("port"))
    elif driver_type == "IntegratedAppDriver":
        return IntegratedAppDriver(name, app_package=config.get("app_package"), ocr_detector=ocr_detector,
                                  target_width=target_width, target_height=target_height, dpi=dpi)
    
    return None
