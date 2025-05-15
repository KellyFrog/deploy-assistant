from config.settings import Settings
from LLM.LLM_core import LLMClient

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> 7db031632c6ed81023454c959f84dd0db7d6f5f1
def next_item (achar):
	return achar == ';' or achar == '；' or \
			achar == '{' or achar == '}'

def ignor (achar):
	return achar == "'" or achar == '"' or \
			next_item (achar) or achar == ' ' or \
			achar == '\n' or achar == '\r\n'


<<<<<<< HEAD
>>>>>>> origin/master
=======
>>>>>>> 7db031632c6ed81023454c959f84dd0db7d6f5f1
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
<<<<<<< HEAD
<<<<<<< HEAD
		return ""

	def response_parser(self, response):
		return ("command",[("echo 2025","no explanation","no notes"),("echo 0215","roselia 赛高","no notes")])
=======
		prompt = ""

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
			"在执行中遇到困难，或者遇到了未能处理的问题。" + \
			"如果我上面没有给你提供回应信息，请先返回一个'0'，然后返回一个疑问句，即你的询问，然后不再给出任何内容！" + \
			"否则先返回一个'1'，然后给我提供若干可供接下来执行的选项。" + \
			"每一个选项的格式是三元组'{该选项对应的可供执行的cmd命令;该选项的说明;该选项的注意事项}'。" + \
			"请你注意格式中的花括号{}，并且三元组都要给出内容，且以分号分隔。" + \
			"所有选项构成列表，每个选项后换行。" + \
			"请以我给你的格式，提供回复。回复中所有的标点符号均为英文符号！"
		
		result = self.LLMClient.generate (
			prompt = prompt,
			stream = False
		)
		return result	

	def response_parser(self, response):
=======
		prompt = ""

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
			"在执行中遇到困难，或者遇到了未能处理的问题。" + \
			"如果我上面没有给你提供回应信息，请先返回一个'0'，然后返回一个疑问句，即你的询问，然后不再给出任何内容！" + \
			"否则先返回一个'1'，然后给我提供若干可供接下来执行的选项。" + \
			"每一个选项的格式是三元组'{该选项对应的可供执行的cmd命令;该选项的说明;该选项的注意事项}'。" + \
			"请你注意格式中的花括号{}，并且三元组都要给出内容，且以分号分隔。" + \
			"所有选项构成列表，每个选项后换行。" + \
			"请以我给你的格式，提供回复。回复中所有的标点符号均为英文符号！"
		
		result = self.LLMClient.generate (
			prompt = prompt,
			stream = False
		)
		return result	

	def response_parser(self, response):
>>>>>>> 7db031632c6ed81023454c959f84dd0db7d6f5f1
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
			return ("ask", response)
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
<<<<<<< HEAD
			raise RuntimeError (f"LLM 返回格式错误")
>>>>>>> origin/master
=======
			raise RuntimeError (f"LLM 返回格式错误")
>>>>>>> 7db031632c6ed81023454c959f84dd0db7d6f5f1
