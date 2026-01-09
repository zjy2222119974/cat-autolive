"""增强版OCR调试 - 测试不同的图像预处理方法"""

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

def preprocess_for_ocr(image):
    """预处理图像以提高OCR识别率"""
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 方法1: 简单二值化
    _, binary1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # 方法2: 自适应二值化
    binary2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
    
    # 方法3: OTSU二值化
    _, binary3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 方法4: 增强对比度
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    return {
        'original': image,
        'gray': gray,
        'binary_simple': binary1,
        'binary_adaptive': binary2,
        'binary_otsu': binary3,
        'enhanced': enhanced
    }

def main():
    print(f"开始增强版OCR调试 (HWND: {HWND})")
    
    # 获取窗口信息
    rect = get_window_rect(HWND)
    print(f"窗口位置: ({rect['left']}, {rect['top']}, {rect['right']}, {rect['bottom']})")
    print(f"窗口尺寸: {rect['width']}x{rect['height']}")
    
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
    
    # 预处理
    print("\n预处理图像...")
    processed = preprocess_for_ocr(arr_bgr)
    
    # 保存预处理后的图像
    debug_dir = "g:/CODE/cat-autolive/debug_screenshots"
    import os
    os.makedirs(debug_dir, exist_ok=True)
    
    for name, img in processed.items():
        filepath = os.path.join(debug_dir, f"preprocessed_{name}.png")
        cv2.imwrite(filepath, img)
        print(f"已保存: {filepath}")
    
    # 初始化OCR
    print("\n初始化OCR引擎...")
    from src.utils.ocr_utils import OCRDetector
    ocr = OCRDetector()
    
    # 测试不同的图像和置信度阈值
    target_texts = ["可视喂食器", "喂食", "可视", "喂食器", "份数", "喂食份数"]
    thresholds = [0.3, 0.4, 0.5, 0.6]
    
    print("\n" + "="*80)
    print("测试不同的图像预处理方法和置信度阈值")
    print("="*80)
    
    for img_name, img in processed.items():
        print(f"\n【{img_name}】")
        
        # 获取所有文字（不设置置信度阈值）
        try:
            results = ocr.reader.readtext(img)
            print(f"  识别到 {len(results)} 个文本区域")
            
            # 显示所有识别结果
            for bbox, text, confidence in results:
                print(f"    文字: '{text}' | 置信度: {confidence:.3f}")
            
            # 测试不同的目标文字和置信度
            print(f"\n  目标文字搜索结果:")
            for target in target_texts:
                for threshold in thresholds:
                    pos = ocr.find_text(img, target, fuzzy=True, confidence_threshold=threshold)
                    if pos:
                        print(f"    ✓ '{target}' (阈值={threshold}): 找到于 {pos}")
                        break
                else:
                    print(f"    ✗ '{target}': 未找到")
        
        except Exception as e:
            print(f"  OCR失败: {e}")
    
    # 特别测试：只处理顶部区域（标题栏）
    print("\n" + "="*80)
    print("测试顶部标题区域（前100像素）")
    print("="*80)
    
    top_region = arr_bgr[:100, :]
    cv2.imwrite(os.path.join(debug_dir, "top_region.png"), top_region)
    
    try:
        results = ocr.reader.readtext(top_region)
        print(f"识别到 {len(results)} 个文本区域")
        for bbox, text, confidence in results:
            print(f"  文字: '{text}' | 置信度: {confidence:.3f}")
    except Exception as e:
        print(f"OCR失败: {e}")

if __name__ == "__main__":
    main()
