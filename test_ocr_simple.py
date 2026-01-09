"""简化的OCR测试 - 直接输出结果"""

import cv2
import sys

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("简化OCR测试")
    print("="*60)
    
    # 加载图像
    img_path = "g:/CODE/cat-autolive/debug_screenshots/nav_fail_20260109_151001_attempt2.png"
    img = cv2.imread(img_path)
    
    if img is None:
        print(f"无法加载图像: {img_path}")
        return
    
    print(f"图像尺寸: {img.shape}")
    
    # 初始化OCR
    from src.utils.ocr_utils import OCRDetector
    print("\n初始化OCR...")
    ocr = OCRDetector()
    
    # 获取所有文字
    print("\n执行OCR识别...")
    all_text = ocr.get_all_text(img)
    
    print(f"\n识别到 {len(all_text)} 个文本区域:")
    for i, (text, pos, conf) in enumerate(all_text, 1):
        print(f"{i}. 文字='{text}' 位置={pos} 置信度={conf:.3f}")
    
    # 测试查找
    print("\n"+ "="*60)
    print("测试查找功能:")
    print("="*60)
    
    targets = ["喂食份数", "喂食计划", "喂食记录"]
    
    for target in targets:
        print(f"\n查找: '{target}'")
        pos = ocr.find_text(img, target, fuzzy=True, confidence_threshold=0.3)
        if pos:
            print(f"  找到于: {pos}")
        else:
            print(f"  未找到")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
