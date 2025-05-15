"""
这个文件的目标是扩展终端的功能，实现一个 CLI，这里应该是整个程序的中心和入口，负责处理输入和调用各种工具。
在获取 stdin 之后在将命令通过 TerminalSimulator 写给终端的 stdin 之前截胡一下处理扩展的命令和组合键。
TODO:
- 设计合理的快捷调用（如使用 /? 之类的快捷命令）
- 可能可以在这里控制 Ctrl+C 之类的输入
"""

import re
from terminal.terminal_simulator import TerminalSimulator
from LLM.LLM_core import LLMClient
from agent.agent import Agent

class CLI:
    def __init__(self, start_command: str):
        self.terminal = TerminalSimulator(start_command)
        self.LLMClient = LLMClient()
        self.console_history = []
        self.current_command_output = ''
        self.command_history = []
        self.in_command_line = True
        self.Agent = Agent()

    def _is_terminal_prompt(self, line: str):
        return re.search(r'PS [A-Za-z]:\\[^>]*>', line)
    
    def _stdout_listener(self, line: str):
        line = line.strip()
        if(self._is_terminal_prompt(line)):
            if len(self.current_command_output) > 0:
                self.console_history.append(self.current_command_output)
                self.current_command_output = ''
            if line[-1] != '>': # Non-Empty command line
                self.current_command_output += line + '\n'
        else:
            self.current_command_output += line + '\n'
        print(line)
        
    # def _stderr_listener(self, line: str):
    #     self.console_history.append(line)
    #     line = line.strip()
    #     print(line)

    def _write(self, cmd : str):
        if(self.in_command_line):
            self.command_history.append(cmd)
        self.in_command_line = False
        self.terminal.write(cmd + '\r\n')
        
    def parse_command(self, cmd: str):
        cmd = cmd.strip()
        if(cmd.startswith("??")):
            #print("".join(self.console_history))
            #for str in self.console_history:
            #    print(f"[\n{str}\n]")
            #self._write("")
            # response_stream = self.LLMClient.generate(
            #     "下面给出用户最近的若干次在windws powershell中的命令，请尽可能简要分析对于每条命令用户做\
            #         了什么以及是否遇到了问题，每条命令20个字以内：\n".join(self.console_history), 
            #     stream=True
            # )
            # self.LLMClient.print_response_stream(response_stream)
            print(self.Agent.gen_suggestion());
            pass
        else:
            self._write(cmd)
    
    def keyBoardInterrupt(self):
        self._write("\003")
        
    def run(self):
        self.terminal.run(self._stdout_listener, self._stdout_listener)
    
    def isalive(self):
        return self.terminal.isalive()
    
def CLI_test():
    cli = CLI("powershell -NoExit -Command \"chcp 65001\"")
    cli.run()
    str = 'echo "Hello World"\n'
    while cli.isalive():
        try:
            cli.parse_command(str)
            str = input()
        except KeyboardInterrupt:
            cli.keyBoardInterrupt()