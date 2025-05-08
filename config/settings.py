import os
from pathlib import Path

# 项目基础配置
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"

# 用户可定制的LLM设置（优先使用自定义配置）
LLM_SETTINGS = {
    "provider": "openai",        # 服务商标识 (openai|mock)
    "api_key": None,             # 默认为环境变量
    "model": "gpt-3.5-turbo",    # 模型版本
    "base_url": None,            # 私有化部署地址
    "max_retries": 3,            # 重试次数
    "timeout": 30,               # 请求超时(秒)
    "temperature": 0.2,          # 生成温度
    "stream_interval": 0.1       # 流式响应间隔
}

class LLMConfig:
    """LLM配置加载中心（整合环境变量和用户配置）"""
    def __init__(self):
        # 优先从用户设置获取，其次环境变量，最后用默认值
        self.provider = LLM_SETTINGS.get("provider") or os.getenv("LLM_PROVIDER", "openai")
        self.api_key = LLM_SETTINGS.get("api_key") or os.getenv("LLM_API_KEY")
        self.model = LLM_SETTINGS.get("model") or os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.base_url = LLM_SETTINGS.get("base_url") or os.getenv("LLM_BASE_URL")
        self.max_retries = LLM_SETTINGS.get("max_retries") or int(os.getenv("LLM_MAX_RETRIES", 3))
        self.timeout = LLM_SETTINGS.get("timeout") or int(os.getenv("LLM_TIMEOUT", 30))
        self.temperature = LLM_SETTINGS.get("temperature") or float(os.getenv("LLM_TEMP", 0.2))
