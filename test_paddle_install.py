"""测试PaddleOCR是否可用"""

import sys

print("测试PaddleOCR安装...")
print("="*60)

try:
    from paddleocr import PaddleOCR
    print("✓ PaddleOCR导入成功")
    
    print("\n初始化PaddleOCR...")
    ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False, show_log=False)
    print("✓ PaddleOCR初始化成功")
    
    print("\n测试OCR识别...")
    import cv2
    img_path = "g:/CODE/cat-autolive/debug_screenshots/nav_fail_20260109_161021_attempt1.png"
    img = cv2.imread(img_path)
    
    if img is None:
        print(f"✗ 无法加载图像: {img_path}")
        sys.exit(1)
    
    result = ocr.ocr(img, cls=True)
    
    if result and result[0]:
        print(f"✓ 识别成功，找到 {len(result[0])} 个文本区域")
        
        # 保存结果到文件
        with open("g:/CODE/cat-autolive/paddle_ocr_result.txt", "w", encoding="utf-8") as f:
            f.write(f"识别到 {len(result[0])} 个文本区域:\n")
            f.write("="*60 + "\n")
            for i, item in enumerate(result[0], 1):
                bbox, (text, confidence) = item
                f.write(f"{i}. '{text}' | 置信度={confidence:.3f}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("查找关键词:\n")
            f.write("="*60 + "\n")
            
            keywords = ["常用", "首页", "智能", "助手", "我的"]
            for keyword in keywords:
                found = False
                for item in result[0]:
                    bbox, (text, confidence) = item
                    if keyword in text:
                        f.write(f"✓ '{keyword}' 找到于 '{text}' 置信度={confidence:.3f}\n")
                        found = True
                        break
                if not found:
                    f.write(f"✗ '{keyword}' 未找到\n")
        
        print("\n结果已保存到: g:/CODE/cat-autolive/paddle_ocr_result.txt")
        print("\n✓✓✓ PaddleOCR工作正常！✓✓✓")
    else:
        print("✗ OCR识别失败")
        sys.exit(1)
        
except ImportError as e:
    print(f"✗ PaddleOCR导入失败: {e}")
    print("\n可能的原因:")
    print("  1. PaddleOCR未安装")
    print("  2. PaddlePaddle未安装")
    print("\n建议:")
    print("  pip install paddleocr")
    print("  pip install paddlepaddle")
    sys.exit(1)
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
