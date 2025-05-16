import os
import platform
from typing import Dict, List
from memory.memory_manager import MemoryManager
from LLM.LLM_handler import LLMHandler
from security.validator import SecurityChecker

class Agent:
    def __init__(self):
        self.MemoryManager = MemoryManager()
        self.LLMHandler = LLMHandler()
        self.SecurityChecker = SecurityChecker()

    def get_env_context(self) -> dict:
        current_cwd = os.getcwd()
        try:
            dir_contents = os.listdir(current_cwd)
        except PermissionError:
            dir_contents = ["<permission denied>"]
        safe_env_vars = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "USER": os.environ.get("USER", ""),
            "LANG": os.environ.get("LANG", "en_US.UTF-8"),
            "SHELL": os.environ.get("SHELL", "/bin/bash")
        }
        return {
            "cwd": current_cwd,
            "dir_contents": sorted(dir_contents),  # 有序列表更友好
            "env_vars": safe_env_vars,
            "system_info": {
                "os": platform.system(),
                "os_release": platform.release()
            }
        }

    def get_user_choice(self, tmp):
        header = f"\n{' 可用命令列表 ':=^40}"
        print(header)
        m = len(tmp)
        #print(tmp)
        for i in range(m):
            (cmd, exp, note) = tmp[i]
            output = [
                f"【选项 {i}】",
                f"▶ 命令：{cmd}",
                f"✏️ 说明：{exp}",
                f"❗️ 注意：{note}",    
                "-"*30
            ]
            print("\n".join(output))
        while True:
            try:
                choice = input("\n请选择要执行的命令编号 (输入 Q 退出): ")
                if(choice == "Q"):
                    return "none"
                choice = int(choice)
                if 0 <= choice <= m:
                    (cmd, exp, note) = tmp[choice]
                    return cmd
                print(f"错误：请输入0-{m}之间的有效数字")
            except ValueError:
                print("错误：请输入数字类型")

    def security_protection(self, command: str):
        val = self.SecurityChecker.validate_command(command)
        if(val["confirmation_required"] == False):
            return command
        else:
            if(self.SecurityChecker.get_confirmation(val["warning"])):
                return command
            else:
                return "none"

    
    def gen_suggestion(self, user_comment = "", user_response = []) -> dict:
        context = self.get_env_context()
        memory = self.MemoryManager.get_memory_context()
        response = self.LLMHandler.gen_response(context, memory, user_comment, user_response)
        (response_type, tmp) = self.LLMHandler.response_parser(response)
        if response_type == "ask":
            print("为了更好帮助您，可能需要您回答一下这个问题喵："+tmp)
            str = input()
            if(str == "Q"):
                return "none"
            else:
                return self.gen_suggestion(user_comment, user_response + [(tmp, str)])
        else:
            return self.security_protection(self.get_user_choice(tmp))
        

    def record_command(self, command, output):
        #print('>>>>>> current command = '+command)
        #print('>>>>>> result = '+output)
        self.MemoryManager.update_command_history(command,output)


