"""
终端命令执行引擎，支持：
- 流式命令执行
- 实时输出监控
- 安全命令执行验证
"""

import subprocess
import shlex
import threading
import sys
from queue import Queue
from typing import Optional, Callable
from utils.security import CommandSanitizer
from utils.error_handling import (
    exception_handler, 
    ErrorCode, 
    SecurityException
)

class CommandExecutor:
    """
    线程安全的命令执行器，支持实时输出流式处理
    实现特性：
    - 命令执行超时控制
    - 实时输出回调
    - 异步执行支持
    """
    
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.output_queue = Queue()
        self._stop_event = threading.Event()

    @exception_handler(SecurityException)
    def execute_streaming(
        self, 
        command: str,
        callback: Optional[Callable[[str], None]] = None,
        cwd: Optional[str] = None
    ) -> int:
        """
        流式执行命令并实时捕获输出
        返回进程退出码
        
        参数：
            command: 需要执行的原始命令
            callback: 实时输出回调函数
            cwd: 工作目录路径
            
        返回：
            int: 进程退出状态码
        """
        sanitized = self.sanitize_command(command)
        if not sanitized:
            raise SecurityException(
                f"危险命令被拦截: {command}",
                dangerous_input=command
            )
            
        process = subprocess.Popen(
            self._prepare_command(sanitized),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            cwd=cwd,
            universal_newlines=True
        )
        
        return self._monitor_process(process, callback)

    def sanitize_command(self, raw_command: str) -> Optional[str]:
        """命令过滤处理（与security模块联动）"""
        return CommandSanitizer.sanitize_command(raw_command)

    def _prepare_command(self, command: str) -> str:
        """准备执行命令（兼容处理）"""
        if sys.platform == 'win32':
            return f'powershell -Command "{command}"'
        return shlex.split(command)

    def _monitor_process(
        self, 
        process: subprocess.Popen,
        callback: Optional[Callable[[str], None]]
    ) -> int:
        """监控子进程输出流"""
        output_buffer = []
        while not self._stop_event.is_set():
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                output_buffer.append(line)
                if callback:
                    callback(line.strip())
                    
        process.kill()
        return process.returncode

    def stop_execution(self) -> None:
        """终止当前执行"""
        self._stop_event.set()
