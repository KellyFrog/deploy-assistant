"""
这个文件的目标是扩展终端的功能，实现一个 CLI，这里应该是整个程序的中心和入口，负责处理输入和调用各种工具。
在获取 stdin 之后在将命令通过 TerminalSimulator 写给终端的 stdin 之前截胡一下处理扩展的命令和组合键。
TODO:
- 设计合理的快捷调用（如使用 /? 之类的快捷命令）
- 可能可以在这里控制 Ctrl+C 之类的输入
"""

import re
import os
from terminal.terminal_simulator import TerminalSimulator
from LLM.LLM_core import LLMClient
from agent.agent import Agent

class CLI:
	def __init__(self, start_command: str):
		self.Agent = Agent()
		self.terminal = TerminalSimulator(start_command, self._stdout_listener)
		self.last_command = ''
		self.last_result = ''
		self.LLMClient = LLMClient()

	def clean_ansi(self, text):
		regex = r'\x1B\[[0-9;?]*[A-Za-z]'
		return re.sub(regex, '', text)
	
	def _stdout_listener(self, line: str):
		line = self.clean_ansi(line.strip())
		if(line == 'chcp 65001'):
			return
		self.last_result += line

	def _write(self, cmd : str):
		self.last_command = cmd
		self.terminal.write(cmd + '\r')
		
	def parse_command(self, cmd: str):
		if(self.last_command != ''):
			split_regex = re.compile(r"\r\n")
			parts = split_regex.split(self.last_result, maxsplit=1)
			if(len(parts) == 2):
				self.Agent.record_command(self.last_command, parts[1])
			self.last_command = ''
		self.last_result = ''
		cmd = cmd.strip()
		if(cmd.startswith("??")):
			cmd = self.Agent.gen_suggestion(user_comment = cmd[2:]);
			if(cmd == 'none'):
				return
		self._write(cmd)
	
	def keyBoardInterrupt(self):
		self._write("\003")
	
	def isalive(self):
		return self.terminal.isalive()
	
def CLI_test():
	cli = CLI("powershell -NoExit -Command \"chcp 65001\"")
	str = '\r\n'
	while cli.isalive():
		try:
			cli.parse_command(str)
			str = input()
		except KeyboardInterrupt:
			cli.keyBoardInterrupt()