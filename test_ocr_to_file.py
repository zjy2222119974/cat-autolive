"""简单OCR测试 - 输出到文件"""

import cv2

def main():
    # 加载图像
    img_path = "g:/CODE/cat-autolive/debug_screenshots/nav_fail_20260109_161021_attempt1.png"
    img = cv2.imread(img_path)
    
    # 初始化OCR
    from src.utils.ocr_utils import OCRDetector
    ocr = OCRDetector()
    
    # 获取所有文字
    all_text = ocr.get_all_text(img)
    
    # 输出到文件
    with open("g:/CODE/cat-autolive/ocr_result.txt", "w", encoding="utf-8") as f:
        f.write(f"识别到 {len(all_text)} 个文本区域:\n")
        f.write("="*60 + "\n")
        for i, (text, pos, conf) in enumerate(all_text, 1):
            f.write(f"{i}. '{text}' | 位置={pos} | 置信度={conf:.3f}\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("查找关键词:\n")
        f.write("="*60 + "\n")
        
        keywords = ["常用", "首页", "智能", "助手", "我的"]
        for keyword in keywords:
            found = False
            for text, pos, conf in all_text:
                text_stripped = text.replace(" ", "").replace("\u3000", "")
                keyword_stripped = keyword.replace(" ", "").replace("\u3000", "")
                if keyword_stripped in text_stripped or text_stripped in keyword_stripped:
                    f.write(f"✓ '{keyword}' 找到于 '{text}' 位置={pos} 置信度={conf:.3f}\n")
                    found = True
                    break
            if not found:
                f.write(f"✗ '{keyword}' 未找到\n")
    
    print("结果已保存到: g:/CODE/cat-autolive/ocr_result.txt")

if __name__ == "__main__":
    main()
