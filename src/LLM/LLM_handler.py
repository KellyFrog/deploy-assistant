from config.settings import Settings
from LLM.LLM_core import LLMClient
from utils.stream_write import StreamLineWriter

def next_item (achar):
	return achar == 'ಠ'

def ignor (achar):
	return next_item (achar) or achar == ' ' or \
			achar == '\n' or achar == '\r\n'


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
		prompt = ""

		# add context
		prompt = prompt + \
			"先向你提供环境信息。这些信息为了让你明白当前目录在哪，以及操作系统信息。" + \
			"不需要，也不允许针对这些信息发问！他们只是我固定提供给你的前置知识。" + \
			"如果我在下文没有给出问题或不能明确需求，请向我提问而不是给出选项！"
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
		
		# add comment
		if user_comment != "":
			prompt = prompt + \
				f"现在用户需求是：{user_comment}。"
		
		# add response
		if user_response != []:
			prompt = prompt + \
				"现在向你补充一些可能出现的问题（这些问题是你之前未能处理的）以及用户给出的回应："
			idx = 0
			for item in user_response:
				idx = idx + 1 
				prompt = prompt + \
					f"你的问题{idx}：{item[0]}。"\
					f"用户对问题{idx}的回复：{item[1]}。"
		
		# summary
		prompt = prompt + \
			"请你结合环境信息、记忆信息、用户需求和补充问题，向我提供回复。" + \
			"如果你没有收到请求，或者觉得用户用词模糊，或不足够清楚自己要做什么任务，或者在执行中遇到困难，或者遇到了未能处理的问题。" + \
			"请先返回一个'0'，然后返回一个疑问句，即你的询问，然后不再给出任何内容！询问后也不用添加ಠ！" + \
			"否则先返回一个'1'，然后给我提供若干可供接下来执行的选项。" + \
			"选项不用太多，要求内容精简直接，数量最多五个。" + \
			"每一个选项的格式是三元组：该选项对应的可供执行的Powershell cmd命令（一定是能在终端执行的命令！）ಠ该选项的说明ಠ该选项的注意事项ಠ。" + \
			"并且三元组都要给出内容，且以ಠ分隔，注意每一项后面都要加ಠ。并且，Powershell cmd命令中，请不要含有任何特殊的emoji等符号。" + \
			"不要添加'命令：'、'说明：'、'注意：'等前缀，直接提供内容。" + \
			"所有选项构成列表，每个选项后换行。" + \
			"请以我给你的格式，提供回复。回复中所有的标点符号均为英文符号！"
		
		result = self.LLMClient.generate (
			prompt = prompt,
			stream = True,
			write_console = True
		)
		return result

	def response_parser(self, response):	
		idx = 0
		response_type = -1
		for idx in range (len (response)):
			if ignor (response[idx]): continue
			if response[idx] == '0' or response[idx] == '1':
				response_type = int (response[idx])
				idx = idx + 1
				break 
		while ignor (response[idx]):
			idx = idx + 1
		response = response[idx : ]
		if response_type == 0:
			fix = len (response)
			while next_item (response[fix - 1]):
				fix = fix - 1
			return ("ask", response[ : fix])
		elif response_type == 1:
			options_list = []
			limit = len (response)
			idx = 0
			while idx < limit:
				item = ["" for i in range (3)]
				for i in range (3):
					while idx < limit and ignor (response[idx]):
						idx = idx + 1
					while idx < limit and (not next_item (response[idx])):
						item[i] = item[i] + response[idx]
						idx = idx + 1
				options_list.append (( item[0], item[1], item[2] ))
				idx = idx + 1
				while idx < len (response) and ignor (response[idx]):
					idx = idx + 1
			return ("command", options_list)	
		else:
			raise RuntimeError (f"LLM 返回格式错误")