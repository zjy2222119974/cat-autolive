"""测试修复后的OCR文字匹配"""

import cv2
import numpy as np
from PIL import Image

# 模拟OCR识别结果
mock_ocr_results = [
    ('可视喂', 0.85),
    ('喂食计划', 0.92),
    ('喂食份数', 0.88),  # 注意这里有空格
    (' 喂食记录', 0.90),
]

def test_text_matching():
    """测试文字匹配逻辑"""
    
    target_texts = ["喂食份数", "可视喂食器", "喂食计划", "喂食记录"]
    
    print("测试文字匹配逻辑")
    print("="*60)
    print(f"\nOCR识别结果: {[text for text, _ in mock_ocr_results]}")
    print(f"\n目标文字: {target_texts}")
    print("\n" + "="*60)
    
    for target in target_texts:
        print(f"\n搜索: '{target}'")
        
        # 去除目标文字的空格
        target_stripped = target.replace(" ", "").replace("\u3000", "")
        
        found = False
        for text, confidence in mock_ocr_results:
            # 去除识别文字的空格
            text_stripped = text.replace(" ", "").replace("\u3000", "")
            
            # 模糊匹配
            matched = (target_stripped in text_stripped or 
                      text_stripped in target_stripped or
                      target in text or 
                      text in target)
            
            if matched and confidence >= 0.5:
                print(f"  ✓ 找到匹配: '{text}' (置信度: {confidence:.3f})")
                found = True
                break
        
        if not found:
            print(f"  ✗ 未找到匹配")

if __name__ == "__main__":
    test_text_matching()
    
    print("\n" + "="*60)
    print("现在测试实际的OCR工具...")
    print("="*60)
    
    # 加载最新的调试截图
    try:
        img_path = "g:/CODE/cat-autolive/debug_screenshots/nav_fail_20260109_151001_attempt2.png"
        img = cv2.imread(img_path)
        
        if img is not None:
            print(f"\n加载图像: {img_path}")
            print(f"图像尺寸: {img.shape}")
            
            from src.utils.ocr_utils import OCRDetector
            ocr = OCRDetector()
            
            # 测试查找
            target_texts = ["喂食份数", "喂食计划", "喂食记录", "可视喂食器"]
            
            print("\n开始OCR识别...")
            all_text = ocr.get_all_text(img)
            print(f"识别到的所有文字: {[t[0] for t in all_text]}")
            
            print("\n查找目标文字:")
            for target in target_texts:
                pos = ocr.find_text(img, target, fuzzy=True, confidence_threshold=0.5)
                if pos:
                    print(f"  ✓ '{target}': 位置 {pos}")
                else:
                    print(f"  ✗ '{target}': 未找到")
        else:
            print(f"无法加载图像: {img_path}")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
