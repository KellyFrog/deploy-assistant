import re
from typing import List, Dict, Tuple
from .github_deploy import GitHubDeployer

class DeployEngine:
    def __init__(self, agent):
        self.agent = agent
        self.github_deployer = GitHubDeployer(agent)
        self.current_plan = []
    
    def handle_request(self, request: str, cwd: str) -> Dict:
        """处理部署请求的统一入口"""
        # 检测是否为GitHub URL
        if self._is_github_url(request):
            return self.github_deployer.deploy_from_github(request)
        # 普通部署请求
        print(f"正在生成部署计划: {request}")
        self.current_plan = self.generate_plan(request, cwd)
        return {
            "type": "plan",
            "plan": self.current_plan,
        }
    
    def generate_plan(self, user_request: str, cwd: str) -> List[str]:
        """生成部署计划"""
        prompt = f"""
为以下任务生成简洁的安装步骤：
任务：{user_request}
要求：
1. 步骤数量不超过5个
2. 每个步骤描述不超过15个汉字
3. 返回格式必须是Python列表格式：["步骤1描述", "步骤2描述", ...]
4. 只返回列表，不要包含其他任何文本
"""
        memory = {
            "short_term": [],
            "medium_term": "",
            "long_term": {
                "env_profile": "",
                "user_profile": ""
            }
        }

        response = self.agent.LLMHandler.gen_response(  
            context=self.agent.get_env_context(cwd),
            memory=memory,
            user_comment=prompt,
            user_response=[]
        )
        
        # 解析响应
        try:
            import ast
            plan = ast.literal_eval(response)
            if isinstance(plan, list) and all(isinstance(step, str) for step in plan):
                return plan
        
            # 如果整个响应不是列表，尝试提取列表部分
            matches = re.findall(r'\[.*?\]', response)
            if matches:
                longest_match = max(matches, key=len)
                plan = ast.literal_eval(longest_match)
                if isinstance(plan, list):
                    return plan
        except:
            pass
        
        # 如果解析失败，打印警告信息
        print(f"警告：无法解析LLM响应，使用默认计划。响应内容：{response}")
        return [
            f"准备{user_request}的安装资源",
            f"执行{user_request}的安装",
            "验证安装结果"
        ]

    def _is_github_url(self, text: str) -> bool:
        """检查是否为GitHub URL"""
        pattern = r'https?://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+'
        return re.match(pattern, text) is not None
    