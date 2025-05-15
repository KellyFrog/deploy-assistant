from config.settings import Settings

class SecurityChecker:
    def __init__(self):
        self.risk_threshold = Settings.RISK_THRESHOLD

    @staticmethod
    def validate_command(suggestion: str) -> dict:
        """
        验证建议命令的安全性
        返回：
        {
            "risk_level": "high|medium|low",
            "safe_alternative": "替代安全命令",
            "warning": "风险警告信息",
            "confirmation_required": True/False
        }
        """
    @staticmethod
    def get_confirmation(prompt: str) -> bool:
        """
        获取用户确认（用于高风险操作）
        返回：用户确认结果（True/False）
        """