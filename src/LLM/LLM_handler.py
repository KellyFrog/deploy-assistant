from config.settings import Settings
from LLM.LLM_core import LLMClient

class LLMHandler:
	def __init__(self):
		self.LLMClient = LLMClient()

	def print_response_stream(self, response_stream):
		full_response = []
		for chunk in response_stream:
			print(chunk, end="", flush=True)
			full_response.append(chunk)
		print("".join(full_response))
		return full_response

	def gen_response(self, context, memory, user_comment="", user_response=[]):
		return ""

	def response_parser(self, response):
		return ("command",[("echo 2025","no explanation","no notes"),("echo 0215","roselia 赛高","no notes")])