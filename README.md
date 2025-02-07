# 🧚‍♂️ DataSprite (数据精灵)

<p align="center">
  <em>基于AI的智能SKU生成工具，让数据创建充满魔力！</em>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/release/python-3910/">
    <img src="https://img.shields.io/badge/Python-3.9%2B-blue" alt="Python Version">
  </a>
  <img src="https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B" alt="Streamlit Version">
  <img src="https://img.shields.io/badge/DeepSeek-AI-9cf" alt="DeepSeek AI">
</p>

## ✨ 项目介绍

DataSprite是一个基于DeepSeek AI的智能SKU生成工具，专为电商从业者设计。它像一个勤劳的数据精灵，能够根据您输入的属性名称和产品描述，自动生成符合实际场景的SKU数据，让繁琐的数据录入工作变得轻松愉快。

### 核心功能

- 🎨 **自定义属性**：支持自由定义SKU属性（如颜色、尺寸、材质等）
- 🤖 **AI生成**：利用DeepSeek AI智能生成合理的属性组合
- 📊 **批量处理**：一次可生成多达50条SKU数据
- ✏️ **实时编辑**：支持在线编辑和调整生成的数据
- 📥 **数据导出**：支持导出为CSV和Excel格式

## 🚀 快速开始

### 环境要求

- Python 3.9+
- DeepSeek API密钥

### 安装步骤

```bash
# 克隆项目
git clone https://github.com/yourusername/datasprite.git
cd datasprite

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，设置DEEPSEEK_API_KEY
```

### 启动应用

```bash
python run.py
```

访问 http://localhost:8501 即可使用

## 💡 使用指南

1. **创建模板**
   - 在左侧边栏输入SKU属性名称（每行一个）
   - 点击"创建SKU模板"

2. **生成数据**
   - 输入产品描述或关键词
   - 设置需要生成的数据条数
   - 点击"生成SKU数据"

3. **编辑导出**
   - 在数据预览区域直接编辑数据
   - 使用"下载CSV"或"下载Excel"按钮导出

## 🛠️ 技术栈

- **前端框架**：Streamlit
- **AI能力**：DeepSeek API
- **数据处理**：Pandas
- **异步处理**：asyncio + aiohttp

## 📝 注意事项

- 首次使用需要配置DeepSeek API密钥
- 单次最多可生成50条数据
- 支持中文和英文输入
- 在以下情况会使用模拟数据：
  1. 未设置DeepSeek API密钥时
  2. 显式设置`use_mock=True`时

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用 MIT 许可证

## 🙏 致谢

- [DeepSeek](https://platform.deepseek.com/) - AI能力支持
- [Streamlit](https://streamlit.io/) - 优秀的Web框架

---

<p align="center">Made with ❤️ by DataSprite</p>
