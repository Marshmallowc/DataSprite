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
    DEEPSEEK_API_KEY = "sk_dummy_key_for_mock_mode"  # 使用更明确的默认密钥

# 应用配置
MAX_RETRIES = 3  # API调用最大重试次数
MIN_ROWS = 1     # 最小生成行数
MAX_ROWS = 500    # 最大生成行数

# 模型配置
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000

# 支持的模型配置
SUPPORTED_MODELS = {
    # DeepSeek 系列
    "DeepSeek-V3": {
        "id": "deepseek-ai/DeepSeek-V3",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "最新的V3版本，支持更强大的对话能力"
    },
    "DeepSeek-V2.5": {
        "id": "deepseek-ai/DeepSeek-V2.5",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "V2.5版本，稳定可靠"
    },
    "DeepSeek-R1": {
        "id": "deepseek-ai/DeepSeek-R1",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "基础版R1模型，适合通用对话"
    },
    "DeepSeek-R1-Llama-70B": {
        "id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "基于Llama-70B蒸馏的大型模型，性能强大"
    },
    "DeepSeek-R1-Qwen-32B": {
        "id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "基于Qwen-32B蒸馏的模型，平衡性能和效率"
    },
    "DeepSeek-R1-Qwen-14B": {
        "id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "基于Qwen-14B蒸馏的中型模型"
    },
    "DeepSeek-R1-Llama-8B": {
        "id": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "基于Llama-8B蒸馏的轻量级模型"
    },
    "DeepSeek-R1-Qwen-7B": {
        "id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "基于Qwen-7B蒸馏的轻量级模型"
    },
    "DeepSeek-R1-Qwen-1.5B": {
        "id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "基于Qwen-1.5B蒸馏的超轻量级模型，速度最快"
    },
    
    # Qwen 系列
    "Qwen2.5-72B-Instruct-128K": {
        "id": "Qwen/Qwen2.5-72B-Instruct-128K",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "通义千问2.5代72B大模型，支持128K上下文"
    },
    "Qwen2.5-72B-Instruct": {
        "id": "Qwen/Qwen2.5-72B-Instruct",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "通义千问2.5代72B大模型"
    },
    "Qwen2.5-32B-Instruct": {
        "id": "Qwen/Qwen2.5-32B-Instruct",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "通义千问2.5代32B模型"
    },
    "Qwen2.5-14B-Instruct": {
        "id": "Qwen/Qwen2.5-14B-Instruct",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "通义千问2.5代14B模型"
    },
    "Qwen2.5-7B-Instruct": {
        "id": "Qwen/Qwen2.5-7B-Instruct",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "通义千问2.5代7B模型"
    },
    "Qwen2.5-Coder-32B": {
        "id": "Qwen/Qwen2.5-Coder-32B-Instruct",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "通义千问2.5代32B编程模型"
    },
    "Qwen2.5-Coder-7B": {
        "id": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "通义千问2.5代7B编程模型"
    },
    
    # Yi 系列
    "Yi-34B-Chat": {
        "id": "01-ai/Yi-1.5-34B-Chat-16K",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "零一万物34B大模型"
    },
    "Yi-9B-Chat": {
        "id": "01-ai/Yi-1.5-9B-Chat-16K",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "零一万物9B模型"
    },
    "Yi-6B-Chat": {
        "id": "01-ai/Yi-1.5-6B-Chat",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "零一万物6B模型"
    },
    
    # InternLM 系列
    "InternLM2-20B": {
        "id": "internlm/internlm2_5-20b-chat",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "书生浦语2代20B模型"
    },
    "InternLM2-7B": {
        "id": "internlm/internlm2_5-7b-chat",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "书生浦语2代7B模型"
    },
    
    # Gemma 系列
    "Gemma-27B": {
        "id": "google/gemma-2-27b-it",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "Google Gemma 27B模型"
    },
    "Gemma-9B": {
        "id": "google/gemma-2-9b-it",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "Google Gemma 9B模型"
    },
    
    # GLM 系列
    "GLM4-9B": {
        "id": "THUDM/glm-4-9b-chat",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "description": "清华GLM4 9B模型"
    }
}

# 默认模型
DEFAULT_MODEL = "DeepSeek-V3"