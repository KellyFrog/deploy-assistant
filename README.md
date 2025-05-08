# Deployer assistant

使用大语言模型帮你安装/部署 git repo，再也不用费心解决依赖和版本问题了！

现在还(xin)在(jian)开(wen)发(jian)中(jia)，计划使用 Python + Tkinter 进行开发，目前计划先支持 windows。

项目通过 GPL 3.0 许可证开源。

大部分代码由 AI 生成，整体架构如下：

以下是 AI 的对目前工作的总结（同时也是使用的 prompt）：

```text
我想通过大语言模型写一个应用程序，下面是我的需求：
应用将通过阅读本地git仓库的README文件和其他文档来给用户部署仓库提供帮助。
在阅读文件后，应用需要给出详细的部署指南。
应用需要通过GUI和终端交互，使得用户可以直接通过GUI按钮向终端发送要执行的命令。
应用需要读取终端命令的输出和结果，并分别命令是否执行失败或未获得预期结果，如是，应用应当分析问题并给出修改建议（如需要安装的依赖、需要执行的命令等）。
我计划在windows下进行开发，最终应用也在windows下使用，将来可能会增加linux版本，因此需要注意兼容性。
我想让我的应用尽量轻量级，优先使用已经有的开源项目进行二次开发以减少工作量。
我决定采用 Python + Tkinter 进行开发，下面是架构的文件树，其中包括主要的文件和每个文件需要实现的主要方法：
📦DeployHelper
├── 📂core
│   ├── 📜document_parser.py      
│   │   - parse_markdown() -> Dict   # 返回结构化部署要素
│   │   - sanitize_content() -> str  # 新增输入净化方法
│   ├── 📜deployment_steps.py
│   │   - generate_workflow() -> List[Step]
│   │   - validate_step() -> bool    # 步骤有效性验证
│   ├── 📜terminal_interface.py
│   │   - CommandExecutor
│   │     ├── execute_streaming()    # 流式执行接口
│   │     ├── sanitize_command()     # 命令过滤方法
│   │     └── monitor_process()      # 子进程监控
│   └── 📜error_analyzer.py
│       - analyze_stream() -> str    # 实时错误分析
│       - generate_fix() -> List     # 修复建议生成
│
├── 📂ai_processing
│   ├── 📜llm_integration.py
│   │   - SafeLLMClient
│   │     ├── safe_request()         # 带重试机制的请求
│   │     └── validate_schema()      # 输出结构校验
│   └── 📜prompt_templates
│       └── 📜error_analysis.jinja2  # 改进安全过滤指令
│
├── 📂gui
│   ├── 📜terminal_emulator.py
│   │   - PowerShellEmulator   # 实现特性：
│   │     ├── 模拟PS提示符
│   │     ├── 命令历史记录
│   │     └── ANSI颜色支持
│   ├── 📜step_widgets.py
│   │   - 新增StreamPrinter组件      # 打字机效果实现
│   │     ├── flush_buffer()         # 文本缓冲控制
│   │     └── set_stream_speed()     # 输出速度调节
│
├── 📂utils
│   ├── 📜security.py          # 安全模块
│   │   - CommandSanitizer
│   └── 📜error_handling.py    # 统一异常处理
│       - ErrorCode 枚举类
│       - exception_handler装饰器

我已经完成了 core 和 utils 模块的开发，下面是已经实现代码的接口：

core/document_parser.py
├── MarkdownParser
│   ├── parse_markdown(file_path: str)
│   │   └→ 返回: {
│   │       "metadata": {总章节数, 总命令数},
│   │       "sections": {
│   │           "section_name": {
│   │               "content": "处理后的文本",
│   │               "commands": [有效命令列表]
│   │           }
│   │       }
│   │   }
│   └── sanitize_content(raw_input: str)
│       └→ 返回: 安全处理后的文本
└── DocumentParseException
    └── 含 error_code, file_path, message
	
core/deployment_steps.py
├── DeploymentStep 数据结构
│   └→ 包含: 
│       - 步骤名称
│       - 执行命令
│       - 预期输出
│       - 依赖步骤
├── DeploymentWorkflow
│   ├── generate_workflow() → 有序步骤列表
│   ├── validate_step(step) → 有效性布尔
│   └── 私有方法实现:
│       - 文档结构解析
│       - 依赖解析
│       - 环路检测
└── CycleDependencyError → 依赖异常

core/terminal_interface.py
└── CommandExecutor
    ├── execute_streaming(command, callback, cwd)
    │   └→ 返回: 进程退出码
    ├── sanitize_command(raw) → 安全命令或None
    └── stop_execution() → 终止当前进程
	
utils/error_handling.py
├── ErrorCode 枚举
│   └→ 包含七种错误类型
├── BaseAppException
│   └→ 含 code, message, detail
├── SecurityException → 危险操作异常
├── LLMException → AI处理异常
└── exception_handler 装饰器
    └→ 功能:
        - 异常捕获
        - 上下文记录
        - 自动日志
		
utils/security.py
└── CommandSanitizer
    ├── detect_injection(input) → 风险布尔
    ├── sanitize_command(raw) → 安全命令
    └── sanitize_path(raw) → 安全路径

现在请帮我完成 ai_processing 部分的代码。
请注意接口的一致性，用户可能使用不同的大语言模型，要留出供用户设置的文件，可以使用openai库。
注意需要 GUI 部分需要流式响应，因此在代码中需要有对应的写法。
```