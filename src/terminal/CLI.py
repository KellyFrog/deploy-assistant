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
		self.current_out = ''
		self.current_err = ''
		self.current_cmd = ''
		self.Agent = Agent()

	def _is_terminal_prompt(self, line: str):
		return re.search(r'PS [A-Za-z]:\\[^>]*>', line)
	
	def _stdout_listener(self, line: str):
		line = line.strip()
		if(line[:16] != 'Active code page'):
			if(self._is_terminal_prompt(line)):
				if(line[-1] == '>'):
					status = 'success'
					output = self.current_out
					if(self.current_err != ''):
						output += '错误信息：'+self.current_err
						status = 'error'
					self.Agent.record_command(self.current_cmd, output, status)
					self.current_cmd = ''
					self.current_err = ''
					self.current_out = ''
				else:
					self.current_cmd = line
			else:
				self.current_out += line + '\n'
		print(line)
		
	def _stderr_listener(self, line: str):
		line = line.strip()
		self.current_err += line + '\n'
		print(line)

	def _write(self, cmd : str):
		self.terminal.write(cmd + '\r\n')
		
	def parse_command(self, cmd: str):
		cmd = cmd.strip()
		if(cmd.startswith("??")):
			cmd = self.Agent.gen_suggestion(user_comment = cmd[2:]);
			if(cmd == 'none'):
				return
		self._write(cmd)
	
	def keyBoardInterrupt(self):
		self._write("\003")
		
	def run(self):
		self.terminal.run(self._stdout_listener, self._stderr_listener)
	
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