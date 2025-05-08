"""
LLM 集成模块，实现以下核心功能：
1. 安全可控的API请求
2. 流式响应处理
3. 多模型提供商兼容
4. 结构化输出验证
"""

import json
import os
import re
from abc import ABC, abstractmethod
from typing import Generator, Optional, Dict, Any
from pathlib import Path
import openai
from jinja2 import Environment, FileSystemLoader
from utils.error_handling import (
    exception_handler,
    ErrorCode,
    LLMException,
    BaseAppException
)

class LLMConfig:
    """LLM配置基类（通过 config/settings.py 扩展）"""
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.api_key = os.getenv("LLM_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", 3))
        self.timeout = int(os.getenv("LLM_TIMEOUT", 30))
        self.base_url = os.getenv("LLM_BASE_URL")  # 支持本地代理

class SafeLLMClient(ABC):
    """
    LLM客户端抽象基类，实现以下通用功能：
    - 请求重试机制
    - 输出结构校验
    - 流式响应处理
    - 安全审计追踪
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.env = Environment(
            loader=FileSystemLoader(
                Path(__file__).parent / "prompt_templates"
            ),
            autoescape=True
        )

    @exception_handler(LLMException)
    def safe_request(self, prompt_context: Dict) -> Generator[str, None, None]:
        """
        安全请求入口方法，实现：
        1. 模板渲染
        2. 流式请求
        3. 结构验证
        """
        template = self.env.get_template("error_analysis.jinja2")
        rendered_prompt = template.render(**prompt_context)
        
        retry_count = 0
        while retry_count < self.config.max_retries:
            try:
                for chunk in self._streaming_request(rendered_prompt):
                    if self._validate_chunk(chunk):
                        yield chunk
                break
            except (openai.APITimeoutError, openai.APIError) as e:
                retry_count += 1
                if retry_count >= self.config.max_retries:
                    raise LLMException(
                        ErrorCode.LLM_TIMEOUT,
                        f"API请求超过最大重试次数: {str(e)}"
                    )

    @abstractmethod
    def _streaming_request(self, prompt: str) -> Generator[str, None, None]:
        """具体流式请求实现（子类重写）"""
        pass

    def _validate_schema(self, response: str) -> Dict:
        """验证响应结构（可根据需要扩展）"""
        try:
            data = json.loads(response)
            if not isinstance(data.get("suggestion"), str):
                raise ValueError("Invalid suggestion format")
            if not isinstance(data.get("commands"), list):
                raise ValueError("Invalid commands format")
            return data
        except json.JSONDecodeError as e:
            raise LLMException(
                ErrorCode.INVALID_JSON,
                "响应不是合法的JSON格式",
                llm_response=response
            ) from e

    def _validate_chunk(self, chunk: str) -> bool:
        """增强的安全验证"""
        forbidden_patterns = [
            r"```(bash|powershell|zsh)\s*\n\s*(rm|del|wget|curl)",  # 危险命令
            r"(\$\(|`|&&|\|\|)\s*\w+",      # 命令拼接符
            r">\s*[/\\\w]+\.(txt|log|bat)", # 重定向操作
            r"(wget|curl)\s+-\S*O\s",       # 下载指令
            r"((?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)"  # IP地址
        ]
        return not any(re.search(p, chunk, re.IGNORECASE) for p in forbidden_patterns)

class OpenAIClient(SafeLLMClient):
    def _streaming_request(self, prompt: str) -> Generator[str, None, None]:
        client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url or "https://api.openai.com/v1"
        )
        
        stream = client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            temperature=self.config.temperature,
            response_format={"type": "json_object"}
        )
        
        buffer = ""
        brace_count = 0
        for chunk in stream:
            if content := chunk.choices[0].delta.content:
                buffer += content
                brace_count += content.count('{') - content.count('}')
                
                # 检测完整JSON对象（平衡花括号）
                if brace_count == 0 and buffer.strip().startswith('{'):
                    clean_buffer = buffer.strip().replace("```json", "").replace("```", "")
                    try:
                        self._validate_schema(clean_buffer)
                        yield clean_buffer
                        buffer = ""
                    except LLMException:
                        buffer = ""  # 重置缓冲区跳过无效数据

class MockLLMClient(SafeLLMClient):
    """本地调试用的Mock客户端"""
    
    def _streaming_request(self, prompt: str) -> Generator[str, None, None]:
        sample_response = {
            "suggestion": "请检查Node.js是否安装",
            "commands": ["node -v", "npm install"],
            "confidence": 0.85
        }
        # 模拟流式响应
        chunks = [
            '{"suggestion": "请检查', 
            'Node.js是否安装","commands": ["node -v", ',
            '"npm install"],"confidence":0.85}'
        ]
        for chunk in chunks:
            yield chunk

PROVIDERS = {}  # 提供商注册表
def register_provider(name: str, client_cls: type):
    """动态注册LLM提供商"""
    if not issubclass(client_cls, SafeLLMClient):
        raise TypeError("Provider must be a SafeLLMClient subclass")
    PROVIDERS[name.lower()] = client_cls
def create_llm_client(config: Optional[LLMConfig] = None) -> SafeLLMClient:
    """增强的工厂方法"""
    config = config or LLMConfig()
    
    if not PROVIDERS:
        # 初始化默认提供商
        register_provider("openai", OpenAIClient)
        register_provider("mock", MockLLMClient)
    
    provider_class = PROVIDERS.get(config.provider.lower())
    if not provider_class:
        raise LLMException(
            ErrorCode.LLM_CONFIG_ERROR,
            f"Unsupported provider: {config.provider}"
        )
    
    return provider_class(config)
