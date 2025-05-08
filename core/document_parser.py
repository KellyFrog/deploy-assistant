"""
Markdown文档解析引擎，支持结构化提取部署要素
整合安全过滤机制，防止恶意内容注入
"""

import re
from pathlib import Path
from typing import Dict, List, Union
from utils.security import CommandSanitizer
from utils.error_handling import exception_handler, ErrorCode, BaseAppException

class DocumentParseException(BaseAppException):
    """文档解析异常基类"""
    def __init__(self, error_code: ErrorCode, file_path: str, message: str):
        super().__init__(error_code, message)
        self.file_path = file_path

class MarkdownParser:
    """
    Markdown文档结构化解析器，实现以下功能：
    1. 章节识别（支持多级标题）
    2. 代码块提取（关联部署步骤）
    3. 关键要素识别（安装、配置、运行等）
    """
    
    # 标题层级匹配模式（支持ATX和Setext格式）
    HEADER_PATTERN = re.compile(
        r'^(#{1,6})\s+(.+?)$|^([-=])\1{2,}$', 
        re.MULTILINE
    )
    
    # 代码块识别（匹配围栏式和缩进式）
    CODEBLOCK_PATTERN = re.compile(
        r'(?:^```.*?$(.+?)^```$)|(?:^(?: {4,}|\t+).+?$)', 
        re.MULTILINE | re.DOTALL
    )
    
    def __init__(self, sanitize: bool = True):
        self.sanitize = sanitize
        self.current_section = None
        self._sections = {}

    @exception_handler(DocumentParseException)
    def parse_markdown(self, file_path: Union[str, Path]) -> Dict:
        """
        解析Markdown文档，返回结构化数据
        返回结构：
        {
            "sections": {
                "installation": {
                    "content": "纯净文本内容",
                    "commands": ["npm install", ...]
                },
                ...
            }
        }
        """
        if not Path(file_path).exists():
            raise DocumentParseException(
                ErrorCode.FILE_NOT_FOUND,
                str(file_path),
                "文档不存在"
            )
            
        content = Path(file_path).read_text(encoding='utf-8')
        if self.sanitize:
            content = self.sanitize_content(content)
            
        self._parse_structure(content)
        return self._build_output()

    def sanitize_content(self, raw_text: str) -> str:
        """
        输入内容净化处理：
        1. 移除危险HTML标签
        2. 过滤非法字符
        3. 标准化换行符
        """
        # 基础消毒
        sanitized = re.sub(r'<script.*?>.*?</script>', '', raw_text, flags=re.DOTALL)
        sanitized = re.sub(r'[^\x00-\x7F]+', '', sanitized)
        # 命令安全检查
        lines = []
        for line in sanitized.splitlines():
            if CommandSanitizer.detect_injection(line):
                line = f"# SECURITY BLOCKED: {line[:50]}..."
            lines.append(line)
        return '\n'.join(lines)

    def _parse_structure(self, content: str) -> None:
        """解析文档结构"""
        current_header = None
        code_blocks = []
        
        for match in self.HEADER_PATTERN.finditer(content):
            header_text = match.group(2) or match.group(3)
            if header_text:
                current_header = self._normalize_header(header_text)
                self._sections[current_header] = []
                
        for code_match in self.CODEBLOCK_PATTERN.finditer(content):
            code = code_match.group(1) or code_match.group(0)
            if current_header and code.strip():
                self._sections[current_header].extend(
                    self._extract_commands(code)
                )

    def _normalize_header(self, header: str) -> str:
        """标准化标题作为字典键"""
        return re.sub(r'\W+', '_', header.lower()).strip('_')

    def _extract_commands(self, code_block: str) -> List[str]:
        """从代码块中提取有效命令"""
        commands = []
        for line in code_block.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                commands.append(line)
        return commands

    def _build_output(self) -> Dict:
        """构建结构化输出"""
        return {
            "metadata": {
                "section_count": len(self._sections),
                "command_count": sum(len(v) for v in self._sections.values())
            },
            "sections": self._sections
        }
