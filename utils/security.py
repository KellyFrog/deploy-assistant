"""
安全处理核心模块，包含命令消毒和注入攻击检测机制
包含线程安全的方法集合，用于处理用户输入和命令执行前的净化操作
"""

import re
from typing import Optional
from html import escape

class CommandSanitizer:
    """
    命令行安全处理类，提供静态方法集
    实现策略：输入验证 + 输出编码双机制
    """
    
    # 注入攻击检测模式（定期更新）
    INJECTION_PATTERNS = (
        (r'(;|\||&)', '命令链检测'),          # 命令分隔符
        (r'\b(rm|del|shutdown)\b', '危险命令'),  
        (r'>{1,2}\s*\w+', '重定向攻击'),
        (r'\$\(.*?\)', '子命令执行'),
        (r'\b(wget|curl)\s+http', '远程资源获取')
    )
    
    # 允许的基础命令白名单（可扩展）
    ALLOWED_COMMANDS = {
        'git', 'npm', 'pip', 'python',
        'docker', 'make', 'mvn', 'gradle'
    }

    @classmethod
    def detect_injection(cls, input_str: str) -> bool:
        """
        检测输入中是否包含潜在的危险模式
        返回布尔值表示是否存在注入风险
        
        参数：
            input_str: 待检测的原始输入字符串
            
        返回：
            bool: 是否检测到危险模式
        """
        if not isinstance(input_str, str):
            raise TypeError("输入必须为字符串类型")
            
        normalized = input_str.strip().lower()
        for pattern, _ in cls.INJECTION_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                return True
        return False

    @classmethod
    def sanitize_command(cls, raw_command: str) -> Optional[str]:
        """
        消毒处理命令行输入，包含以下步骤：
        1. 检测命令注入模式
        2. 转义特殊字符
        3. 验证基础命令在白名单内
        
        参数：
            raw_command: 用户输入的原始命令
            
        返回：
            str: 消毒后的安全命令，若存在高风险则返回None
        """
        if cls.detect_injection(raw_command):
            return None
            
        # 提取基础命令验证白名单
        base_cmd = re.split(r'\s+', raw_command.strip())[0]
        if base_cmd not in cls.ALLOWED_COMMANDS:
            return None
            
        # 转义HTML特殊字符（防御XSS）
        sanitized = escape(raw_command)
        # 处理命令行特殊字符转义
        return re.sub(r'([!"&\'()*;<>?\\`{|}~])', r'\\\1', sanitized)

    @classmethod
    def sanitize_path(cls, raw_path: str) -> str:
        """
        消毒路径输入，防止目录遍历攻击
        返回规范化的绝对路径
        
        参数：
            raw_path: 用户输入的原始路径
            
        返回：
            str: 规范化后的安全路径
        """
        # 保留路径中的合法字符（根据系统调整）
        cleaned = re.sub(r'[^\w./\\:-]', '', raw_path)
        # 防止路径遍历
        return re.sub(r'\.{2,}', '', cleaned)
