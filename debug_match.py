"""调试OCR匹配逻辑"""

# 模拟实际情况
ocr_results = [
    ('涂鸦', 0.85),
    ('3.28', 0.90),
    ('可视嗯', 0.75),
    ('喂食计划', 0.92),
    ('喂食份数', 0.88),
    ('喂食记录', 0.90),
]

target = "喂食份数"

print(f"目标文字: '{target}'")
print(f"OCR结果: {[t[0] for t, _ in ocr_results]}")
print("\n" + "="*60)

# 测试匹配逻辑
target_stripped = target.replace(" ", "").replace("\u3000", "")
print(f"目标文字(去空格): '{target_stripped}'")

for text, confidence in ocr_results:
    text_stripped = text.replace(" ", "").replace("\u3000", "")
    
    print(f"\n测试: '{text}' (置信度={confidence})")
    print(f"  去空格后: '{text_stripped}'")
    
    # 测试各种匹配条件
    cond1 = target_stripped in text_stripped
    cond2 = text_stripped in target_stripped
    cond3 = target in text
    cond4 = text in target
    
    print(f"  target_stripped in text_stripped: {cond1}")
    print(f"  text_stripped in target_stripped: {cond2}")
    print(f"  target in text: {cond3}")
    print(f"  text in target: {cond4}")
    
    matched = cond1 or cond2 or cond3 or cond4
    print(f"  匹配结果: {matched}")
    
    if matched and confidence >= 0.5:
        print(f"  ✓ 应该找到！")
