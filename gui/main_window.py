"""
主窗口框架和核心交互逻辑
实现功能：
- 多标签页布局
- 部署工作流可视化
- 实时终端模拟
- AI建议交互
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Callable
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from core.terminal_interface import CommandExecutor
from gui.terminal_emulator import PowerShellEmulator
from gui.step_widgets import StreamPrinter, StepProgress, StepStatus
from ai_processing.llm_integration import create_llm_client

class MainApplication(tk.Tk):
    """主应用窗口，继承自Tk根窗口"""
    
    def __init__(self, executor: CommandExecutor):
        super().__init__()
        self.executor = executor
        self._setup_ui()
        self._bind_events()
        
        # 流式处理队列
        self.stream_queue = Queue()
        self.after(100, self._process_stream_queue)
        
    def _setup_ui(self):
        """界面布局构建"""
        self.title("DeployHelper v0.1")
        self.geometry("1200x800")
        
        # 主面板布局
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 部署步骤面板
        self.step_panel = ttk.Frame(main_frame, width=300)
        self.step_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        # 终端模拟器
        self.terminal = PowerShellEmulator(main_frame)
        self.terminal.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 步骤进度控制
        self.progress = StepProgress(self.step_panel)
        self.progress.pack(fill=tk.X)
        
        # AI建议面板
        self.suggestion_printer = StreamPrinter(
            self.step_panel, 
            height=10,
            stream_speed=50
        )
        self.suggestion_printer.pack(fill=tk.X)

    def _bind_events(self):
        """事件绑定"""
        pass
        # self.terminal.on_command_entered(self.execute_user_command)
        # self.progress.on_step_click(self.execute_deployment_step)
        
    def execute_deployment_step(self, step):
        """执行部署工作流步骤"""
        def _run_step():
            # 设置步骤状态为运行中
            self.progress.update_step_status(
                step.name, 
                StepStatus.RUNNING
            )
            
            # 流式执行回调
            def _output_callback(line: str):
                self.stream_queue.put((
                    'terminal',
                    f"{line}\n"
                ))
                
            # 执行命令
            exit_code = self.executor.execute_streaming(
                step.command,
                callback=_output_callback,
                cwd='./'
            )
            
            # 处理结果
            status = StepStatus.SUCCESS if exit_code == 0 else StepStatus.FAILED
            self.progress.update_step_status(
                step.name, 
                status
            )
            if exit_code != 0:
                self._handle_execution_error(step)
        
        Thread(target=_run_step, daemon=True).start()

    def _handle_execution_error(self, step):
        """处理执行错误触发AI分析"""
        error_log = self.terminal.get_last_error()
        client = create_llm_client()
        
        def _process_response(chunk: str):
            self.stream_queue.put((
                'suggestion',
                chunk
            ))
            
        Thread(
            target=lambda: client.safe_request({
                "error_log": error_log,
                "current_step": step.name
            }, callback=_process_response),
            daemon=True
        ).start()

    def _process_stream_queue(self):
        """处理流式更新队列（每100ms）"""
        while not self.stream_queue.empty():
            target, data = self.stream_queue.get()
            if target == 'terminal':
                self.terminal.insert_stream_data(data)
            elif target == 'suggestion':
                self.suggestion_printer.feed(data)
        self.after(100, self._process_stream_queue)
