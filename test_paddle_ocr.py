"""测试 PaddleOCR - 更好的中文识别"""

import cv2
import numpy as np
import ctypes
from ctypes import wintypes
from PIL import ImageGrab

# 窗口句柄
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
    print("测试 PaddleOCR 中文识别")
    print("="*60)
    
    # 检查是否安装了 PaddleOCR
    try:
        from paddleocr import PaddleOCR
        print("✓ PaddleOCR 已安装")
    except ImportError:
        print("✗ PaddleOCR 未安装")
        print("\n安装命令:")
        print("  pip install paddleocr paddlepaddle")
        return
    
    # 获取窗口
    rect = get_window_rect(HWND)
    print(f"\n窗口尺寸: {rect['width']}x{rect['height']}")
    
    # 捕获窗口
    screenshot = ImageGrab.grab(
        bbox=(rect['left'], rect['top'], rect['right'], rect['bottom']),
        all_screens=True
    )
    
    # 转换为numpy数组
    arr = np.array(screenshot)
    if arr.shape[2] == 4:
        arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    else:
        arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    
    # 保存原始图像
    cv2.imwrite("g:/CODE/cat-autolive/debug_screenshots/paddle_input.png", arr_bgr)
    
    # 初始化 PaddleOCR
    print("\n初始化 PaddleOCR...")
    ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False, show_log=False)
    
    # 执行OCR
    print("\n执行OCR识别...")
    result = ocr.ocr(arr_bgr, cls=True)
    
    # 显示结果
    print("\n识别结果:")
    print("="*60)
    
    if result and result[0]:
        for line in result[0]:
            bbox, (text, confidence) = line
            print(f"文字: '{text}' | 置信度: {confidence:.3f}")
            print(f"  位置: {bbox}")
    else:
        print("未识别到任何文字")
    
    # 搜索目标文字
    print("\n" + "="*60)
    print("搜索目标文字:")
    print("="*60)
    
    target_texts = ["可视喂食器", "喂食份数", "喂食计划", "喂食记录", "喂食"]
    
    if result and result[0]:
        for target in target_texts:
            found = False
            for line in result[0]:
                bbox, (text, confidence) = line
                if target in text or text in target:
                    # 计算中心点
                    bbox_array = np.array(bbox)
                    center_x = int(np.mean(bbox_array[:, 0]))
                    center_y = int(np.mean(bbox_array[:, 1]))
                    print(f"✓ 找到 '{target}': 实际文字='{text}', 位置=({center_x}, {center_y}), 置信度={confidence:.3f}")
                    found = True
                    break
            
            if not found:
                print(f"✗ 未找到 '{target}'")

if __name__ == "__main__":
    main()
