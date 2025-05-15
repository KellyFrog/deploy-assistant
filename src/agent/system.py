class SystemAgent:
    @staticmethod
    def get_context() -> dict:
        """
        返回当前环境上下文（实时信息）
        返回格式：
        {
            "cwd": "当前工作目录路径",
            "dir_contents": ["当前目录文件列表"],
            "env_vars": {"关键环境变量键值对"},
            "system_info": {"os": "操作系统类型"}
        }
        """
    
    @staticmethod
    def execute_safe_command(cmd: str) -> dict:
        """
        执行安全等级验证过的命令
        返回：
        {
            "status": "success|error",
            "output": "命令输出",
            "error": "错误信息（如果有）"
        }
        """