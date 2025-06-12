import requests
import re
import os
from typing import Dict, List
from config.settings import Settings
from LLM.LLM_core import LLMClient

class GitHubDeployer:
    def __init__(self, agent):
        self.agent = agent
    
    def deploy_from_github(self, context, memory, url: str) -> Dict:

        print(f"正在从 GitHub 项目生成部署计划:  {url}")

        readme = self._fetch_readme(url)
        if not readme:
            return {
                "type": "error", 
                "message": "无法获取README内容",
            }
        
        plan = self._generate_plan_from_readme(context, memory, url, readme)
        
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
    
    def _generate_plan_from_readme(self, context, memory, url, readme: str) -> List[str]:
        """从README生成部署计划"""

        prompt = "你现在要部署地址为 " + url + " 的 github 仓库"

        # add context
        prompt = prompt + \
            "先向你提供环境信息。这些信息为了让你明白当前目录在哪，以及操作系统信息。"
        prompt = prompt + \
            f"当前文件目录：{context["cwd"]}。" + \
            f"当前目录下文件和文件夹名字列表：{context["dir_contents"]}。" + \
            f"操作系统名称：{context["system_info"]["os"]}" + \
            f"操作系统的发布版本：{context["system_info"]["os_release"]}"
        prompt = prompt + \
            "所有环境信息提供完毕！"

        # add memory
        any_memory = False
        if memory["short_term"] != []:
            any_memory = True
            prompt = prompt + \
                "向你提供记忆信息。以下是你最近执行的命令与你的处理结果。"
            for i in range (len (memory["short_term"])):
                prompt = prompt + \
                    f"最近倒数第{Settings.SHORT_HISTORY - i}" + \
                    f"条消息，命令为：{memory["short_term"][i]["cmd"]}," + \
                    f"你的执行结果是：{memory["short_term"][i]["result"]}。"
        if memory["medium_term"] != "":
            any_memory = True
            prompt = prompt + \
                "向你提供你之前总结的，近一段时间的处理记忆。" + \
                "'" + memory["medium_term"] + "'。"
        if memory["long_term"]["env_profile"] != "":
            any_memory = True
            prompt = prompt + \
                f"向你提供你之前总结的系统环境简档：{memory["long_term"]["env_profile"]}。"
        if memory["long_term"]["user_profile"] != "":
            any_memory = True
            prompt = prompt + \
                f"向你提供你之前总结的用户习惯简档：{memory["long_term"]["user_profile"]}。"
        if any_memory == True:
            prompt = prompt + \
                "所有记忆信息提供完毕！"
        
        prompt = f"""
现在 根据以下GitHub项目的README内容，生成具体的安装步骤：
README内容：
{readme[:3000]}... [内容截断]
要求：
1. 提取关键安装步骤
2. 返回格式必须是Python列表格式：["步骤1描述", "步骤2描述", ...]
3. 只返回列表，不要包含其他任何文本
4. 对于每个步骤，如果可以在本命令行环境下直接通过输入命令的方式得到，请在描述后面跟上命令，否则说明白用户在在这一步具体需要做什么
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