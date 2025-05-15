from config.settings import Settings

class MemoryManager:
    @staticmethod
    def __init__(self):
        self.short_history = Settings.SHORT_HISTORY

    def get_memory_context() -> dict:
        """
        返回综合记忆上下文
        格式：
        {
            "short_term": [
                {"cmd": "最近命令1", "result": "执行结果"},
                {"cmd": "最近命令2", "result": "执行结果"},
                ...,
                {"cmd": "最近命令SHORT_HISTORY"，"result"："执行结果}
            ],
            "medium_term": "总结后的历史模式描述，每SHORT_HISTORY条后可以进行更新",
            "long_term": {
                "env_profile": "系统环境简档",
                "user_profile": "用户习惯简档"
            }
        }
        long_term 需要存储在一个文件中，而short_term和medium_term在每次新开窗口的时候会清零。
        """
    
    @staticmethod
    def update_command_history(cmd: str, result: dict):
        """
        实时更新命令历史（在每次命令执行后调用）
        """