"""
部署步骤可视化组件
包含：
- 流式打印机（类似teletype效果）
- 步骤进度跟踪
"""

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

class StepStatus(Enum):
    """步骤状态枚举"""
    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3

class StreamPrinter(tk.LabelFrame):
    """流式文本打印机组件"""
    
    def __init__(
        self, 
        master, 
        stream_speed: int = 50,
        **kwargs
    ):
        super().__init__(master, text="AI 建议", **kwargs)
        self.stream_speed = stream_speed
        self.buffer = []
        self.after_id = None
        
        self.text = tk.Text(
            self, 
            wrap=tk.WORD,
            height=5,
            state='disabled'
        )
        self.text.pack(fill=tk.BOTH)
        
    def feed(self, chunk: str):
        """接收文本块加入缓冲"""
        self.buffer.extend(chunk)
        if not self.after_id:
            self._schedule_flush()
            
    def _schedule_flush(self):
        """调度缓冲内容刷新"""
        self.after_id = self.after(
            self.stream_speed,
            self._flush_buffer
        )
        
    def _flush_buffer(self):
        """刷新缓冲到界面"""
        if self.buffer:
            self.text['state'] = 'normal'
            self.text.insert(tk.END, self.buffer.pop(0))
            self.text['state'] = 'disabled'
            self._schedule_flush()
        else:
            self.after_id = None

class StepProgress(tk.Frame):
    """部署步骤进度跟踪组件"""
    
    def __init__(self, master):
        super().__init__(master)
        self.current_step = 0
        self.steps = []
        self.callback = None
        
    def load_workflow(self, steps: List):
        """加载部署工作流"""
        for step in steps:
            frame = tk.Frame(self)
            label = tk.Label(frame, text=step.name)
            status = tk.Label(frame, text="○", fg="gray")
            
            label.pack(side=tk.LEFT)
            status.pack(side=tk.RIGHT)
            frame.pack(fill=tk.X)
            
            self.steps.append({
                "widget": frame,
                "status": status,
                "data": step
            })
            
    def update_step_status(
        self, 
        step_name: str, 
        status: StepStatus
    ):
        """更新步骤状态指示器"""
        for step in self.steps:
            if step["data"].name == step_name:
                step["status"].config(
                    text={
                        StepStatus.PENDING: "○",
                        StepStatus.RUNNING: "▶",
                        StepStatus.SUCCESS: "✓",
                        StepStatus.FAILED: "✗"
                    }[status],
                    fg={
                        StepStatus.PENDING: "gray",
                        StepStatus.RUNNING: "blue",
                        StepStatus.SUCCESS: "green",
                        StepStatus.FAILED: "red"
                    }[status]
                )
                break
    # 在StepProgress中添加状态保存
    def get_current_state(self) -> Dict[str, StepStatus]:
        return {step["data"].name: step["status"] 
                for step in self.steps}
