"""调试窗口捕获 - 保存截图到文件"""

import cv2
import numpy as np
import ctypes
from ctypes import wintypes
from PIL import ImageGrab

# 窗口句柄 (从日志中获取)
HWND = 133536

user32 = ctypes.windll.user32

def get_window_rect(hwnd):
    """获取窗口屏幕坐标"""
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return {
        'left': rect.left,
        'top': rect.top,
        'right': rect.right,
        'bottom': rect.bottom,
        'width': rect.right - rect.left,
        'height': rect.bottom - rect.top
    }

def main():
    print(f"开始调试窗口捕获 (HWND: {HWND})")
    
    # 获取窗口信息
    rect = get_window_rect(HWND)
    print(f"窗口位置: ({rect['left']}, {rect['top']}, {rect['right']}, {rect['bottom']})")
    print(f"窗口尺寸: {rect['width']}x{rect['height']}")
    
    # 检查窗口是否可见
    is_visible = user32.IsWindowVisible(HWND)
    print(f"窗口可见: {bool(is_visible)}")
    
    # 使用 PIL 捕获窗口
    print("使用 PIL ImageGrab 捕获窗口...")
    screenshot = ImageGrab.grab(
        bbox=(rect['left'], rect['top'], rect['right'], rect['bottom']),
        all_screens=True
    )
    
    print(f"PIL 捕获成功，图像模式: {screenshot.mode}, 尺寸: {screenshot.size}")
    
    # 转换为 numpy 数组
    arr = np.array(screenshot)
    print(f"Numpy 数组形状: {arr.shape}")
    
    # 如果是 RGBA，转换为 BGR
    if arr.shape[2] == 4:
        arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    elif arr.shape[2] == 3:
        arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    else:
        arr_bgr = arr
    
    # 保存图像
    output_path = "g:/CODE/cat-autolive/debug_screenshot.png"
    cv2.imwrite(output_path, arr_bgr)
    print(f"截图已保存到: {output_path}")
    
    # 显示图像的一些统计信息
    print(f"像素值范围: {arr_bgr.min()} - {arr_bgr.max()}")
    print(f"平均像素值: {arr_bgr.mean():.2f}")
    
    # 测试 OCR
    print("\n测试 OCR 识别...")
    try:
        from src.utils.ocr_utils import OCRDetector
        ocr = OCRDetector()
        all_text = ocr.get_all_text(arr_bgr)
        print(f"识别到的文字: {[t[0] for t in all_text]}")
    except Exception as e:
        print(f"OCR 测试失败: {e}")

if __name__ == "__main__":
    main()
