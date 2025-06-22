import re
from terminal.terminal_simulator import TerminalSimulator
from agent.agent import Agent

class CLI:
	def __init__(self, start_command: str, dimensions = (24, 80)):
		self.Agent = Agent()
		self.terminal = TerminalSimulator(start_command, dimensions, self._stdout_listener)
		self.last_command = ''
		self.last_result = ''
		self.cwd = ''
		self.dimensions = dimensions

	def clean_ansi(self, text):
		regex = r'\x1B\[[0-9;?]*[A-Za-z]'
		return re.sub(regex, '', text)
	
	def _detect_powershell_prompt(self, s):
		# 匹配可能包含环境名的PowerShell提示符，并捕获路径
		pattern = r'(?:\(.*?\)\s+)?PS\s+([^>]+?)\s*>'
		match = re.search(pattern, s)
		if match:
			# 提取路径并去除前后空格
			path = match.group(1).strip()
			return True, path
		else:
			return False, None
	
	def _stdout_listener(self, line: str):
		line = self.clean_ansi(line.strip())
		if(line == 'chcp 65001'):
			return
		match, cwd = self._detect_powershell_prompt(line)
		if match:
			self.cwd = cwd
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

		# 处理退出命令
		if cmd.lower() in ['exit', 'quit']:
			# 发送退出命令
			self._write(cmd)
			print("保存用户画像...")
			try:
				# 生成并更新用户画像
				env_profile, user_profile = self.Agent.MemoryManager.generate_user_profiles()
				self.Agent.MemoryManager.update_long_term_memory(env_profile, user_profile)
			except KeyboardInterrupt:
				print("Interrupted")
			print("按 Enter 退出")
			return

		if(cmd.startswith("??")):
			print(f"starting at {self.cwd}")
			try:
				cmd = self.Agent.gen_suggestion(cwd=self.cwd, user_comment=cmd[2:])
			except KeyboardInterrupt:
				print("\nInterrupted")
				return
			if(cmd == 'none'):
				return
			
		if cmd.startswith("deploy "):
			request = cmd[7:].strip()
			result = self.Agent.handle_deployment(cwd=self.cwd, request=request)
        
			if "type" in result and result["type"] == "plan":
				print("\n部署计划:")
				for i, step in enumerate(result["plan"], 1):
					print(f"{i}. {step}")
        
			else:
				print(f"\n部署失败: {result.get('message', '未知错误')}")
			return
    
		self._write(cmd)
	
	def keyBoardInterrupt(self):
		self._write("\003")
	
	def isalive(self):
		return self.terminal.isalive()
	
	def launch(self):
		str = '\r\n'
		while self.isalive():
			try:
				self.parse_command(str)
				str = input()
			except KeyboardInterrupt:
				self.keyBoardInterrupt()
	