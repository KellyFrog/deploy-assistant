from config.settings import Settings
from LLM.LLM_core import LLMClient
import re

class SecurityChecker:
    def __init__(self):
        self.risk_threshold = Settings.RISK_THRESHOLD
        self.llm_client = LLMClient(model = 'Qwen/Qwen2.5-7B-Instruct')
        # 危险命令关键词列表
        self.dangerous_keywords = [
            "rm", "del", "remove", "delete",  # 删除文件
            "format", "mkfs",  # 格式化
            "chmod", "chown", "attrib",  # 修改权限
            "shutdown", "reboot", "restart",  # 系统控制
            "net", "ipconfig", "ifconfig",  # 网络配置
            "reg", "registry",  # 注册表
            "taskkill", "kill",  # 进程控制
            ">", ">>", "|",  # 重定向和管道
            "sudo", "su", "runas",  # 提权
            "wget", "curl", "ftp",  # 网络下载
            "echo", "type", "cat",  # 文件内容
            "set", "export",  # 环境变量
        ]

    def validate_command(self, suggestion: str) -> dict:
        """
        验证建议命令的安全性
        先检测关键词 检测到危险关键词时 再调用 LLM 判定命令是否危险 否则可以直接判定为安全
        返回：
        {
            "risk_level": "high|medium|low",
            "safe_alternative": "替代安全命令",
            "warning": "风险警告信息",
            "confirmation_required": True/False
        }
        """
        # 检查是否包含危险关键词
        has_dangerous_keyword = any(keyword in suggestion.lower() for keyword in self.dangerous_keywords)
        
        if not has_dangerous_keyword:
            return {
                "risk_level": "low",
                "warning": "",
                "confirmation_required": False
            }

        # 构建提示词
        print("检测命令安全性中...")
        prompt = f"""请分析以下命令的安全性，并给出建议：

命令：{suggestion}

请从以下几个方面分析：
1. 命令的风险等级（high/medium/low）
2. 具体的风险警告信息
3. 是否需要用户确认

请以JSON格式返回，格式如下：
{{
    "risk_level": "high|medium|low",
    "warning": "警告信息",
    "confirmation_required": true/false
}}"""

        # 调用 LLM 进行分析
        response = self.llm_client.generate(prompt, stream=False)
        
        try:
            # 解析 LLM 返回的 JSON
            import json
            result = json.loads(response)
            return result
        except:
            # 如果解析失败，返回保守的结果
            return {
                "risk_level": "high",
                "warning": "命令包含潜在风险，建议谨慎执行",
                "confirmation_required": True
            }

    def get_confirmation(self, prompt: str) -> bool:
        """
        获取用户确认（用于高风险操作）
        返回：用户确认结果（True/False）
        """
        print(f"\n⚠️ 警告：{prompt}")
        while True:
            response = input("是否继续执行？(y/n): ").lower()
            if response in ['y', 'yes', 'Y', 'Yes', 'YES']:
                return True
            elif response in ['n', 'no', 'N', 'No', 'NO']:
                return False
            print("请输入 y 或 n")