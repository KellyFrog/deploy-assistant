"""
统一异常处理框架，包含：
- 错误代码枚举
- 异常基类
- 异常处理装饰器
- 错误上下文管理器
"""

from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Dict, Type
import logging
import sys
import threading

# 线程本地存储，用于传递错误上下文
_error_ctx = threading.local()

class ErrorCode(Enum):
    """应用级错误代码枚举"""
    SECURITY_BLOCKED = auto()
    LLM_TIMEOUT = auto()
    COMMAND_FAILED = auto()
    INVALID_JSON = auto()
    FILE_NOT_FOUND = auto()
    PERMISSION_DENIED = auto()

class BaseAppException(Exception):
    """应用异常基类"""
    def __init__(self, code: ErrorCode, message: str, detail: Dict[str, Any] = None):
        self.code = code
        self.message = message
        self.detail = detail or {}
        super().__init__(f"{code.name}: {message}")

class SecurityException(BaseAppException):
    """安全相关异常"""
    def __init__(self, message: str, dangerous_input: str):
        super().__init__(
            ErrorCode.SECURITY_BLOCKED,
            message,
            {'input': dangerous_input}
        )

class LLMException(BaseAppException):
    """LLM服务异常"""
    def __init__(self, code: ErrorCode, message: str, llm_response: str = None):
        super().__init__(code, message, {'llm_response': llm_response})

def exception_handler(*exceptions: Type[Exception]):
    """
    异常处理装饰器工厂，提供：
    - 异常类型捕获
    - 错误上下文存储
    - 自动日志记录
    - 安全异常特殊处理
    
    使用示例：
    @exception_handler(APIError, JSONDecodeError)
    def risky_function():
        ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple(exceptions) as e:
                _store_error_context(e)
                _handle_specific_errors(e)
                return None
        return wrapper
    return decorator

def _store_error_context(error: Exception) -> None:
    """存储错误上下文信息到线程本地"""
    if hasattr(error, 'code'):
        _error_ctx.last_error = {
            'code': error.code.name,
            'message': error.message,
            'detail': getattr(error, 'detail', None)
        }

def _handle_specific_errors(error: Exception) -> None:
    """根据错误类型执行特定处理逻辑"""
    logger = logging.getLogger(__name__)
    
    if isinstance(error, SecurityException):
        logger.critical(f"安全拦截: {error.message} 输入内容: {error.detail['input']}")
        sys.stderr.write("操作被安全策略阻止\n")
    elif isinstance(error, LLMException):
        logger.error(f"AI处理失败: {error.message}")
        if error.code == ErrorCode.LLM_TIMEOUT:
            logger.info("正在重试LLM请求...")
    else:
        logger.exception("未捕获的异常发生")

def get_last_error() -> Dict[str, Any]:
    """获取当前线程的最后一个错误上下文"""
    return getattr(_error_ctx, 'last_error', None)
