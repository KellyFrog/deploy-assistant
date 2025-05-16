from config.settings import Settings
from LLM.LLM_core import LLMClient
import json
import os

class MemoryManager:
    def __init__(self):
        self.short_history = Settings.SHORT_HISTORY
        self.short_term = []
        self.medium_term = ""
        self.long_term = {
            "env_profile": "",
            "user_profile": ""
        }
        self.llm_client = LLMClient(model = 'Qwen/Qwen2.5-7B-Instruct')
        self._load_long_term_memory()
        self.update_counter = 0  # 用于控制中期记忆更新频率

    def _load_long_term_memory(self):
        """从文件加载长期记忆"""
        memory_file = "memory/long_term_memory.json"
        if os.path.exists(memory_file):
            with open(memory_file, 'r', encoding='utf-8') as f:
                self.long_term = json.load(f)

    def _save_long_term_memory(self):
        """保存长期记忆到文件"""
        memory_file = "memory/long_term_memory.json"
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.long_term, f, ensure_ascii=False, indent=2)

    def get_memory_context(self) -> dict:
        """ 
        返回综合记忆上下文
        格式：
        {
            "short_term": [·
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
        return {
            "short_term": self.short_term,
            "medium_term": self.medium_term,
            "long_term": self.long_term
        }

    def update_command_history(self, cmd: str, result: dict):
        """
        实时更新命令历史（在每次命令执行后调用）
        """
        # 更新短期记忆
        self.short_term.append({"cmd": cmd, "result": result})
        
        # 当短期记忆达到阈值时，移除最旧的记录
        if len(self.short_term) > self.short_history:
            self.short_term.pop(0)
            
            # 每累积 SHORT_HISTORY 条新记录才更新一次中期记忆
        self.update_counter += 1
        if self.update_counter >= self.short_history:
            self._update_medium_term_memory()
            self.update_counter = 0  # 重置计数器

    def _update_medium_term_memory(self):
        """更新中期记忆"""
        if not self.short_term:
            return
        print('存储中...')

        # 构建提示词
        prompt = "请分析以下命令历史，总结用户想做什么和做了些什么（100字以内）：\n"
        for item in self.short_term:
            # 只提取命令的实际输出，过滤掉提示符等无关信息
            output = item['result'].get('output', '')
            status = item['result'].get('status', 'success')
            
            # 移除 PowerShell 提示符和空行
            output_lines = [line for line in output.split('\n') 
                          if not line.strip().startswith('PS ') and line.strip()]
            clean_output = '\n'.join(output_lines)
            
            # 根据状态格式化输出
            if status == "error":
                prompt += f"命令: {item['cmd']}\n状态: 执行失败\n错误信息: {clean_output}\n"
            else:
                prompt += f"命令: {item['cmd']}\n状态: 执行成功\n输出: {clean_output}\n"

        # 调用 LLM 生成总结
        response = self.llm_client.generate(prompt, stream=False)
        self.medium_term = response

        print("存储成功了！")

    def update_long_term_memory(self, env_profile: str = None, user_profile: str = None):
        """更新长期记忆"""
        if env_profile:
            self.long_term["env_profile"] = env_profile
        if user_profile:
            self.long_term["user_profile"] = user_profile
        self._save_long_term_memory()