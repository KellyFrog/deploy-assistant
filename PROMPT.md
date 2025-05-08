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
├── 📂config
│   ├── 📜settings.py	# 设置变量，如 LLM 提供方

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

我已经完成了 ai_processing 部分，下面是 ai_processing/llm_integration.py 的接口：
实现模式：
- 工厂模式（通过create_llm_client创建具体实现）
- 模板方法模式（SafeLLMClient定义处理流程）
核心类：
▨ SafeLLMClient（抽象基类）
├── safe_request(prompt_context) → Generator[str]
│   └→ 流式请求主入口，返回有序响应块
├── _streaming_request(prompt) → Generator[str]（抽象方法）
└── _validate_schema(response) → Dict
    └→ 验证完整JSON响应结构（抛出LLMException）
实现类：
▨ OpenAIClient(SafeLLMClient)
├── 特性：
│   - 通过OpenAI官方SDK实现
│   - 支持代码块自动过滤（清除`json`标记）
│   - HTTP代理支持（通过config.base_url）
└── 流式处理方式：按API原生流式响应处理
▨ MockLLMClient(SafeLLMClient)
└── 特性：返回预置响应（调试开发用）
配置模块：
▨ LLMConfig 
├── 默认配置源：os.environ环境变量
└── 核心参数：
    - provider：服务商标识（openai/mock）
    - model：模型版本名称
    - api_key：认证密钥
    - max_retries：最大重试次数
    - timeout：单次请求超时（秒）

我已经完成了 GUI 部分，下面是源文件的接口文档：

gui/main_window.py
▨ MainApplication
├── 继承关系：tk.Tk → MainApplication
├── 核心功能：
│   - 主窗口布局管理
│   - 命令执行与AI建议的流式处理
│   - 跨线程任务调度
├── 主要方法：
│   ├── execute_deployment_step(step: DeploymentStep)
│   │   └→ 启动异步步骤执行（更新状态+流式输出）
│   └── _handle_execution_error(step: DeploymentStep)
│       └→ 触发AI错误分析流程
└── 事件处理：
    - 终端命令输入（绑定execute_user_command）
    - 步骤快捷执行（绑定execute_deployment_step）

gui/terminal_emulator.py
▨ PowerShellEmulator
├── 继承关系：ScrolledText → PowerShellEmulator
├── 核心特性：
│   - ANSI转义序列渲染
│   - 命令历史导航（↑↓键支持）
│   - 智能滚动保持
├── 关键方法：
│   ├── insert_stream_data(data: str)
│   │   └→ 输入流式终端输出内容
│   └── get_last_error() → str
│       └→ 返回最近错误日志（用于AI分析）
└── 实现机制：
    - 基于pyte的屏幕模拟渲染
    - 正则匹配处理ANSI CSI序列

gui/step_widgets.py
▨ StepProgress
├── 功能描述：
│   - 部署步骤的可视化进度跟踪
│   - 点击步骤标题快速执行
├── 接口说明：
│   ├── load_workflow(steps: List[DeploymentStep])
│   │   └→ 加载部署步骤树形结构
│   └── update_step_status(step_name: str, status: StepStatus)
│       └→ 更新状态指示器图标与颜色
├── 可视化特性：
│   - 步骤依赖关系连线显示
│   - 错误步骤高亮闪烁
└── 事件绑定：on_step_click(callback)

▨ StreamPrinter
├── 功能描述：
│   - 流式文本展示组件
│   - 支持可调节输出速度
├── 核心方法：
│   ├── feed(chunk: str)
│   │   └→ 输入文本片段（立即加入缓冲）
│   └── set_stream_speed(ms_per_char: int)
│       └→ 设置字符输出间隔时间
└── 可视化效果：
    - 打字机输出效果
    - 自动滚动保持最新可视
```