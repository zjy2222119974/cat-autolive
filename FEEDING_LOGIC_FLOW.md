# 冻干喂食器自动化脚本 - 完整流程说明

## 📋 总体流程

### 主函数：`feed(hwnd, capture_func, portions=1)`

**入口参数：**
- `hwnd`: 模拟器窗口句柄
- `capture_func`: 窗口截图函数
- `portions`: 喂食份数（默认1份）

**执行步骤：**
```
1. 导航到喂食份数弹窗 (_navigate_to_feeding_dialog)
   ↓
2. 选择份数并确认 (_select_portions_and_confirm)
   ↓
3. 完成喂食
```

---

## 🎯 步骤1: 导航到喂食份数弹窗

### 函数：`_navigate_to_feeding_dialog(hwnd, capture_func)`

**目标：** 找到并点击"喂食份数"按钮，进入喂食弹窗

**最大重试次数：** 3次

### 每次尝试的流程：

#### 1️⃣ 截图并OCR识别
```python
screenshot = capture_func()  # 捕获当前窗口
all_text = self.ocr.get_all_text(screenshot)  # 执行OCR，获取所有文字
# 输出: ['涂鸦', '3.28', '可视嗯', '喂食计划', '喂食份数', '喂食记录']
```

#### 2️⃣ 保存调试截图
```python
self._save_debug_screenshot(screenshot, attempt)
# 保存到: debug_screenshots/nav_fail_YYYYMMDD_HHMMSS_attemptN.png
```

#### 3️⃣ 【优先级1】查找"喂食份数"按钮（最高优先级）
```python
feeding_portions_pos = self._find_text_in_results(all_text, "喂食份数")

if feeding_portions_pos:
    # ✓ 找到了！
    点击按钮 → 进入喂食弹窗 → 返回成功 ✅
else:
    # ✗ 没找到，继续下一步
```

**如果找到：**
- 点击"喂食份数"按钮
- 设置状态为 `FEEDING_DIALOG`
- **返回 True，导航成功** ✅

**如果没找到：** 继续优先级2

---

#### 4️⃣ 【优先级2】查找"可视喂食器"
```python
feeder_pos = self._find_text_in_results(all_text, "可视喂食器")

if feeder_pos:
    点击"可视喂食器" → 等待3秒 → 重新截图OCR
    
    再次查找"喂食份数":
        if 找到:
            点击 → 返回成功 ✅
        else:
            继续下一次重试
else:
    # 没找到，继续优先级3
```

**场景：** 当前在设备列表页面，需要先进入喂食器控制页面

**流程：**
1. 点击"可视喂食器"
2. 等待页面加载（3秒）
3. 重新截图并OCR
4. 再次查找"喂食份数"
   - 找到 → 点击 → 返回成功 ✅
   - 没找到 → 继续下一次重试

---

#### 5️⃣ 【优先级3】查找"首页"
```python
home_pos = self._find_text_in_results(all_text, "首页")

if home_pos:
    点击"首页" → 返回主页 → 等待2秒 → 继续下一次重试
else:
    # 没找到，继续检查其他情况
```

**场景：** 当前在某个子页面，需要返回主页重新开始

---

#### 6️⃣ 特殊处理：摄像头界面
```python
if any("涂鸦" in text for text in all_text_list):
    # 检测到摄像头界面
    点击左上角返回按钮(30, 30) → 等待2秒 → 继续下一次重试
```

**场景：** 当前在摄像头直播界面，需要返回

---

#### 7️⃣ 所有尝试都失败
```python
等待2秒 → 继续下一次重试
```

如果3次重试都失败：
```
❌ 导航失败
提示：请确保APP已打开并位于正确的页面
```

---

## 🔍 辅助函数：`_find_text_in_results(all_text, target)`

**功能：** 在OCR结果中查找目标文字

**输入：**
- `all_text`: OCR结果列表 `[(文字, (x, y), 置信度), ...]`
- `target`: 目标文字，如 `"喂食份数"`

**匹配逻辑：**
```python
# 1. 去除空格
target_stripped = "喂食份数"  # 去除空格后
text_stripped = "喂食份数"    # OCR识别的文字去除空格后

# 2. 模糊匹配（满足任一条件即可）
matched = (
    target_stripped in text_stripped or  # "喂食份数" in "喂食份数"
    text_stripped in target_stripped or  # "喂食份数" in "喂食份数"
    target in text or                     # "喂食份数" in "喂食份数 "
    text in target                        # "喂食份数 " in "喂食份数"
)

# 3. 置信度检查
if matched and confidence >= 0.3:  # 置信度阈值：0.3
    返回位置 (x, y)
```

**返回：**
- 找到：`(x, y)` 文字中心坐标
- 没找到：`None`

---

## 🎲 步骤2: 选择份数并确认

### 函数：`_select_portions_and_confirm(hwnd, capture_func, portions)`

**前提：** 已经成功进入喂食份数弹窗

**流程：**

#### 1️⃣ 等待弹窗显示
```python
time.sleep(1)  # 等待1秒，确保弹窗完全显示
```

#### 2️⃣ 截图并OCR
```python
screenshot = capture_func()
all_text = self.ocr.get_all_text(screenshot)
# 输出: ['1 份', '2 份', '3 份', '确认', '取消']
```

#### 3️⃣ 查找份数选项
**方法1：** 完整匹配 `"1 份"`
```python
portion_text = f"{portions} 份"  # 例如 "1 份"
pos = self.ocr.find_text(screenshot, portion_text, fuzzy=True)
```

**方法2：** 如果方法1失败，只搜索数字 `"1"`
```python
portion_str = str(portions)  # 例如 "1"

for text, (x, y), confidence in all_text:
    if portion_str in text:  # 在 "1 份" 中找到 "1"
        pos = (x, y)
        break
```

#### 4️⃣ 点击份数选项
```python
if pos:
    self.clicker.click_at_position(hwnd, pos[0], pos[1], delay=0.5)
else:
    ❌ 未找到份数选项，返回失败
```

#### 5️⃣ 等待并查找"确认"按钮
```python
time.sleep(0.5)  # 等待0.5秒
screenshot = capture_func()  # 重新截图
pos = self.ocr.find_text(screenshot, "确认", fuzzy=True)
```

#### 6️⃣ 点击"确认"按钮
```python
if pos:
    self.clicker.click_at_position(hwnd, pos[0], pos[1], delay=1.0)
    ✅ 返回成功
else:
    ❌ 未找到确认按钮，返回失败
```

---

## 🔧 关键技术细节

### 1. OCR文字匹配
- **去除空格：** 处理中英文空格差异
- **模糊匹配：** 支持部分匹配
- **置信度阈值：** 0.3（较低，提高识别率）

### 2. 单次OCR调用
每次尝试只调用一次OCR，避免：
- 重复计算浪费时间
- 不同调用结果不一致

### 3. 调试功能
- **自动保存截图：** 每次尝试都保存当前页面截图
- **详细日志：** 记录所有识别的文字和匹配结果
- **优先级标记：** 清晰显示当前执行的优先级

### 4. 点击延迟
- 点击后延迟 `0.5-1.0` 秒
- 等待页面响应和动画完成

---

## 📊 状态机

```
UNKNOWN (未知)
    ↓
HOME_PAGE (首页)
    ↓ 点击"可视喂食器"
FEEDER_PAGE (喂食器页面)
    ↓ 点击"喂食份数"
FEEDING_DIALOG (喂食弹窗)
    ↓ 选择份数并确认
COMPLETED (完成)
```

---

## 🎯 成功条件

### 导航成功的条件：
1. **直接找到"喂食份数"** - 最理想
2. **通过"可视喂食器"进入后找到"喂食份数"** - 需要导航
3. **通过"首页"返回后找到** - 需要多次导航

### 喂食成功的条件：
1. 成功导航到喂食弹窗
2. 找到并点击份数选项（如"1 份"）
3. 找到并点击"确认"按钮

---

## ⚠️ 失败场景

### 导航失败：
- 3次重试都无法找到"喂食份数"
- 截图失败
- OCR识别失败

### 喂食失败：
- 找不到份数选项
- 找不到"确认"按钮
- 点击失败

---

## 📝 日志示例

### 成功场景：
```
INFO: 开始自动喂食流程，目标份数: 1
INFO: 开始导航到喂食份数弹窗
INFO: 导航尝试 1/3
INFO: 当前页面识别到的文字: ['涂鸦', '3.28', '可视嗯', '喂食计划', '喂食份数', '喂食记录']
INFO: 【优先级1】查找'喂食份数'按钮...
INFO:   匹配成功: 目标='喂食份数' 实际='喂食份数' 置信度=0.713
INFO: ✓ 找到'喂食份数'按钮，位置: (194, 703)
INFO: 成功进入喂食份数弹窗
INFO: 选择份数: 1
INFO: 当前识别到的文字: ['1 份', '2 份', '3 份', '确认', '取消']
INFO: 找到份数选项，点击
INFO: 找到'确认'按钮，点击
INFO: 自动喂食流程完成
```

### 失败场景：
```
INFO: 开始自动喂食流程，目标份数: 1
INFO: 开始导航到喂食份数弹窗
INFO: 导航尝试 1/3
INFO: 当前页面识别到的文字: ['涂鸦', '设备列表']
INFO: 【优先级1】查找'喂食份数'按钮...
WARNING: ✗ 未找到'喂食份数'按钮
INFO: 【优先级2】查找'可视喂食器'...
WARNING: ✗ 未找到'可视喂食器'
INFO: 【优先级3】查找'首页'...
WARNING: ✗ 未找到'首页'
INFO: 检测到摄像头界面，尝试返回上一页
WARNING: 第 1 次尝试失败，等待后重试...
...
ERROR: 导航失败，已达最大重试次数
ERROR: 请确保APP已打开并位于正确的页面（设备列表或喂食器控制页面）
ERROR: 提示：页面上应该能看到'喂食份数'按钮
ERROR: 导航到喂食份数弹窗失败
ERROR: 自动喂食失败
```

---

## 🎨 优化亮点

1. **优先级明确** - "喂食份数"是最高优先级
2. **单次OCR** - 避免重复调用，提高效率和一致性
3. **智能匹配** - 去除空格、模糊匹配、低置信度阈值
4. **完善调试** - 自动保存截图、详细日志
5. **容错处理** - 多种导航路径、特殊场景处理
