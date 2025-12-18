# Cat AutoLive

一个基于 PyQt6 的现代化 Python 客户端应用框架。

## ✨ 特性

- 🎨 **现代化 UI** - 深色主题，美观的用户界面
- 📁 **清晰的项目结构** - 模块化设计，易于维护和扩展
- ⚙️ **完善的配置管理** - 支持 JSON 配置文件
- 📝 **强大的日志系统** - 支持控制台和文件输出，带日志轮转
- 🔧 **易于扩展** - 组件化架构，方便添加新功能

## 📦 项目结构111

```
cat-autolive/
├── main.py                 # 应用入口
├── requirements.txt        # Python依赖
├── config.json            # 应用配置
├── src/
│   ├── ui/
│   │   ├── main_window.py      # 主窗口
│   │   └── components/         # UI组件
│   ├── utils/
│   │   └── logger.py          # 日志工具
│   └── config/
│       └── settings.py        # 配置管理
└── resources/             # 资源文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python main.py
```

## 🛠️ 开发指南

### 添加新的 UI 组件

1. 在 `src/ui/components/` 目录下创建新的组件文件
2. 继承 PyQt6 的相应控件类
3. 在主窗口或其他页面中导入使用

示例：

```python
# src/ui/components/custom_button.py
from PyQt6.QtWidgets import QPushButton

class CustomButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
            }
        """)
```

### 配置管理

应用配置存储在 `config.json` 文件中，可以通过 `Settings` 类访问：

```python
from src.config.settings import get_settings

settings = get_settings()
app_name = settings.get('app.name')
window_width = settings.get('window.width', 1200)
```

### 日志系统

使用日志记录器记录应用运行信息：

```python
from src.utils.logger import get_logger

logger = get_logger()
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
```

日志会同时输出到控制台和文件（`logs/app.log`）。

## 🎨 自定义主题

主窗口的样式定义在 `src/ui/main_window.py` 中的 `setStyleSheet()` 方法中。您可以修改颜色、字体、间距等样式属性来自定义界面外观。

## 📋 待办事项

- [ ] 添加数据库支持
- [ ] 实现网络请求功能
- [ ] 添加图表展示组件
- [ ] 实现插件系统
- [ ] 添加单元测试

## 📝 许可证

MIT License

## 👨‍💻 作者

Your Name

---

**注意**：这是一个项目框架，您可以根据实际需求进行扩展和修改。
