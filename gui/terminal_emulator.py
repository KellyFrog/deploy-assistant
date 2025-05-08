"""
终端模拟器组件
实现功能：
- PowerShell样式提示符
- ANSI转义码支持（基础颜色）
- 命令历史记录
"""

import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from pyte import Screen, Stream
from pyte.screens import Char

class PowerShellEmulator(ScrolledText):
    """带ANSI颜色支持的终端模拟组件"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master, 
            wrap=tk.WORD,
            state='disabled',
            **kwargs
        )
        self.screen = Screen(80, 24)
        self.stream = Stream(screen=self.screen)
        self.history = []
        self.history_idx = -1
        
        # ANSI颜色映射
        self.color_map = {
            30: 'black',
            31: 'red',
            32: 'green',
            33: 'yellow',
            34: 'blue',
            35: 'magenta',
            36: 'cyan',
            37: 'white'
        }
        # 更多颜色可扩展...
    
    def insert_stream_data(self, data: str):
        MAX_HISTORY_LINES = 1000  # 防止内存溢出
        if self.line_count > MAX_HISTORY_LINES:
            self.delete(1.0, f"{MAX_HISTORY_LINES//2}.0")
        self.stream.feed(data)
        self._update_display()
        
    def _update_display(self):
        """将pyte屏幕数据渲染到Tk组件"""
        self['state'] = 'normal'
        self.delete(1.0, tk.END)
        
        for line in self.screen.display:
            line_text = ''
            for char in reversed(line):
                if isinstance(char, Char):
                    fg = self._get_ansi_color(char.fg)
                    self.tag_config(fg, foreground=fg)
                    line_text = f"<{fg}>{char.data}</{fg}>" + line_text
            self.insert(tk.END, line_text + '\n')
            
        self['state'] = 'disabled'
        self.see(tk.END)
        
    def _get_ansi_color(self, code: int) -> str:
        """转换ANSI颜色码"""
        return self.color_map.get(code, 'white')
