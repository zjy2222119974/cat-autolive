"""测试首页OCR识别"""

import cv2
import sys

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("测试首页OCR识别")
    print("="*60)
    
    # 加载最新的首页截图
    img_path = "g:/CODE/cat-autolive/debug_screenshots/nav_fail_20260109_161021_attempt1.png"
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
        print(f"{i}. '{text}' | 位置={pos} | 置信度={conf:.3f}")
    
    # 测试查找关键词
    print("\n"+ "="*60)
    print("测试查找关键词:")
    print("="*60)
    
    keywords = ["常用", "首页", "智能", "助手", "我的", "消息", "拍照", "设置"]
    
    for keyword in keywords:
        # 方法1: 使用 find_text
        pos1 = ocr.find_text(img, keyword, fuzzy=True, confidence_threshold=0.3)
        
        # 方法2: 手动在结果中查找
        found_manual = False
        for text, pos, conf in all_text:
            if keyword in text or text in keyword:
                print(f"✓ '{keyword}': find_text={pos1}, 手动找到='{text}' 位置={pos} 置信度={conf:.3f}")
                found_manual = True
                break
        
        if not found_manual:
            print(f"✗ '{keyword}': find_text={pos1}, 手动未找到")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
