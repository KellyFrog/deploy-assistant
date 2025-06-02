import requests
import re
import os
from typing import Dict, List

class GitHubDeployer:
    def __init__(self, agent):
        self.agent = agent
    
    def deploy_from_github(self, url: str) -> Dict:

        print(f"正在从 GitHub 项目生成部署计划:  {url}")

        readme = self._fetch_readme(url)
        if not readme:
            return {
            "status": "error", 
            "message": "无法获取README内容",
            }
        
        plan = self._generate_plan_from_readme(readme)
        
        return {
            "type": "plan",
            "plan": plan,
        }
    
    def _fetch_readme(self, url: str) -> str:
        """获取GitHub项目的README内容"""
        try:
            # 转换URL为raw README URL
            repo_path = url.replace("https://github.com/", "")
            if "/" in repo_path:
                repo_path = repo_path.split("/")[0] + "/" + repo_path.split("/")[1]
            raw_url = f"https://raw.githubusercontent.com/{repo_path}/main/README.md"
            
            response = requests.get(raw_url, timeout=10)
            if response.status_code == 200:
                return response.text
            
        except Exception as e:
            print(f"获取README失败: {str(e)}")
        return ""
    
    def _generate_plan_from_readme(self, readme: str) -> List[str]:
        """从README生成部署计划"""
        
        prompt = f"""
根据以下GitHub项目的README内容，生成简洁的安装步骤：
README内容：
{readme[:2000]}... [内容截断]
要求：
1. 提取关键安装步骤
2. 步骤数量不超过5个
3. 每个步骤描述不超过15个汉字
4. 返回格式必须是Python列表格式：["步骤1描述", "步骤2描述", ...]
5. 只返回列表，不要包含其他任何文本
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
            context=self.agent.get_env_context(os.getcwd()),
            memory=memory,
            user_comment=prompt,
            user_response=[]
        )
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
        
        return self.agent.deploy_engine.generate_plan("GitHub项目安装")