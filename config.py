import os
from dotenv import load_dotenv
import warnings
from pathlib import Path

# 加载环境变量
load_dotenv()

# 项目根目录
ROOT_DIR = Path(__file__).parent

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 如果没有设置API密钥，发出警告而不是抛出异常
if not DEEPSEEK_API_KEY:
    warnings.warn(
        "\n"
        "DEEPSEEK_API_KEY未设置！请按照以下步骤操作：\n"
        "1. 访问 https://platform.deepseek.com/ 注册账号\n"
        "2. 在平台上获取API密钥\n"
        "3. 复制 .env.example 为 .env 文件\n"
        "4. 在 .env 文件中设置你的API密钥\n"
        "\n"
        "目前使用测试模式，将返回示例数据。"
    )
    DEEPSEEK_API_KEY = "dummy_key"

# 应用配置
MAX_RETRIES = 3  # API调用最大重试次数
MIN_ROWS = 1     # 最小生成行数
MAX_ROWS = 50    # 最大生成行数

# 模型配置
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000