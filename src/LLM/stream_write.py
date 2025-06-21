import os
import sys
import shutil
from collections import deque
import re

class StreamLineWriter:
    def __init__(self, header="", scroll_width=None, auto_clear=True):
        """
        :param header: 固定显示的头部字符串
        :param scroll_width: 滚动窗口的字符宽度（保留多少尾部字符）
        :param auto_clear: 是否自动清除末尾空格
        """
        self.header = header
        self.auto_clear = auto_clear
        self.buffer = deque(maxlen=200)  # 滚动缓冲区
        self.truncated = False  # 是否已截断过内容
        
        # 计算实际可用宽度（考虑头部）
        self.term_width = self.get_term_width()
        self.avail_width = max(5, int(self.term_width - len(header.encode('utf-8')) - 3))
        if scroll_width == None:
            self.scroll_width = self.avail_width // 2
        else:
            self.scroll_width = scroll_width
    
    def get_term_width(self):
        """获取当前终端宽度"""
        try:
            return shutil.get_terminal_size().columns
        except OSError:
            return 80
    
    def refresh_width(self):
        """刷新终端宽度信息"""
        self.term_width = self.get_term_width()
        self.avail_width = max(5, self.term_width - len(self.header) - 3)
    
    def clean_text(self, text):
        """清理文本：替换控制字符和换行符"""
        # 替换换行符和制表符
        cleaned = re.sub(r'[\r\n\t]', ' ', text)
        # 移除不可打印的ASCII控制字符（除\t外）
        cleaned = re.sub(r'[\x00-\x1F\x7F]', ' ', cleaned)
        return cleaned
    
    def write(self, text, end='', flush=True):
        """写入文本并刷新显示"""
        if not text:
            return
        
        # 清理输入文本
        text = self.clean_text(text)
        
        # 添加到缓冲区
        for char in text:
            self.buffer.append(char)
        
        # 刷新显示
        self.refresh_display(end, flush)
    
    def append(self, text, end='', flush=True):
        """在尾部追加文本"""
        self.write(text, end, flush)
    
    def refresh_display(self, end='', flush=True):
        """刷新终端显示内容"""
        # 获取缓冲区内容
        content = ''.join(self.buffer)
        
        # 检查是否需要滚动截断
        content_bytes = content.encode('utf-8')
        if len(content_bytes) > self.avail_width and self.scroll_width > 0:
            # 需要截断：只保留尾部字符
            self.truncated = True
            start_index = max(0, len(content) - self.scroll_width)
            display_content = content[start_index:]
            # 如果头部被截断则添加省略号
            if start_index > 0:
                display_content = '…' + display_content
        else:
            # 完整显示内容
            self.truncated = False
            display_content = content
        
        # 自动清除尾部空格
        if self.auto_clear and display_content.endswith(' ') and not end:
            clean_content = display_content.rstrip() + ' '
        else:
            clean_content = display_content
        
        # 构建完整输出行
        full_line = self.header + clean_content + end
        
        # 使用ANSI控制序列更新行
        sys.stdout.write('\033[2K\r')  # 清除当前行
        sys.stdout.write(full_line)
        
        if flush:
            sys.stdout.flush()
    
    def end_line(self, text='', end='\n', flush=True):
        """结束当前行，添加最后内容并换行"""
        if text:
            self.write(text, end='', flush=False)
        self.refresh_display(end, flush)
