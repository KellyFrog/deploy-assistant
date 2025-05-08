"""
项目入口文件，实现：
- 环境初始化
- 命令行接口
- 调试模式支持
"""

import os
import sys
import logging
from dotenv import load_dotenv
from core.document_parser import DocumentParseException, MarkdownParser
from gui.main_window import MainApplication
from core.terminal_interface import CommandExecutor
from core.deployment_steps import DeploymentWorkflow, CycleDependencyError
# from utils.error_handling import configure_logging

def init_environment():
    """初始化运行环境"""
    load_dotenv()  # 加载.env文件
    
    # 设置Unicode控制台编码
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    # 配置日志系统
    # configure_logging()

def start_application():
    """启动GUI应用"""

    # 解析README（新增步骤）
    try:
        parser = MarkdownParser()
        doc_data = parser.parse_markdown("README.md")
    except DocumentParseException as e:
        logging.error(f"文档解析失败: {str(e)}")
        sys.exit(1)
    
    # 初始化核心服务
    executor = CommandExecutor()
    
    # 正确初始化工作流（传入文档数据）
    workflow = DeploymentWorkflow(config=doc_data)
    
    try:
        steps = workflow.generate_workflow()
    except CycleDependencyError as e:
        logging.error(f"工作流依赖错误: {str(e)}")
        sys.exit(1)
    
    # 启动主界面
    app = MainApplication(executor)
    app.progress.load_workflow(steps)
    app.mainloop()

if __name__ == '__main__':
    init_environment()
    start_application()
