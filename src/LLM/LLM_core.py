import os
import certifi
from cryptography.fernet import Fernet
from openai import OpenAI
from typing import Generator, Optional
from config.settings import Settings
from LLM.stream_write import StreamLineWriter

os.environ['SSL_CERT_FILE'] = certifi.where()

class SecureAPIKeyManager:
    """安全的API密钥管理类"""
    def __init__(self, key_file: str = "secret.key", enc_file: str = "api_key.enc"):
        self.key_file = key_file
        self.enc_file = enc_file
        self._initialize_encryption()

    def _initialize_encryption(self) -> None:
        """初始化加密环境"""
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        self.cipher_suite = Fernet(open(self.key_file, "rb").read())

    def save_api_key(self, api_key: str) -> None:
        """加密并保存API密钥"""
        encrypted_key = self.cipher_suite.encrypt(api_key.encode())
        with open(self.enc_file, "wb") as f:
            f.write(encrypted_key)

    def get_api_key(self) -> str:
        """获取解密后的API密钥"""
        try:
            with open(self.enc_file, "rb") as f:
                encrypted_key = f.read()
            return self.cipher_suite.decrypt(encrypted_key).decode()
        except FileNotFoundError:
            raise ValueError("API key not found. Please set your API key first.")

class LLMClient:
    """大语言模型交互类"""
    def __init__(self, url: str = 'https://api.siliconflow.cn/v1/', model: str = 'deepseek-ai/DeepSeek-R1'):
        self.url = url
        self.model = model
        self.key_manager = SecureAPIKeyManager()
        self._init_client()
        self.temperature = Settings.LLM_TEMPURATURE

    def _init_client(self) -> None:
        """初始化OpenAI客户端"""
        try:
            self.client = OpenAI(api_key=self.key_manager.get_api_key(), base_url=self.url)
        except ValueError as e:
            print(f"Error: {e}")
            self._handle_missing_api_key()

    def _handle_missing_api_key(self) -> None:
        """处理API密钥缺失情况"""
        api_key = input("请输入OpenAI API密钥：").strip()
        self.key_manager.save_api_key(api_key)
        self.client = OpenAI(api_key=api_key, base_url=self.url)

    def generate(
        self,
        prompt: str,
        stream: bool = False,
        write_console: bool = True,
    ) -> str:
        """
        生成文本响应，
        :param prompt: 输入的提示文本
        :param stream: 是否使用流式响应
        :param write_console: 是否将流式输出到终端
        :return: 返回内容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=stream,
                temperature=self.temperature
            )

            if stream:
                return self._handle_stream_response(response, write_console)
            return self._handle_full_response(response)

        except Exception as e:
            raise RuntimeError(f"API调用失败: {str(e)}") from e

    def _handle_stream_response(self, response, write_console) -> str:
        """处理流式响应"""
        writer = StreamLineWriter()
        result = []
        for chunk in response:
            if chunk.choices[0].delta.content:
                str = chunk.choices[0].delta.content
                if write_console:
                    writer.append(str)
                result.append(str)
            if chunk.choices[0].delta.reasoning_content:
                str = chunk.choices[0].delta.reasoning_content
                if write_console:
                    writer.append(str)
        if write_console:
            writer.end_line()
        print(''.join(result))
        return ''.join(result)

    def _handle_full_response(self, response) -> str:
        """处理完整响应"""
        return response.choices[0].message.content

    """"""

def test_llm():
    # 示例使用
    llm = LLMClient()
    
    # 流式响应演示
    print("流式响应演示：")
    response_stream = llm.generate(
        "Python中如何实现数据加密？",
        stream=True,
    )
    
    full_response = []
    for chunk in response_stream:
        print(chunk, end="", flush=True)
        full_response.append(chunk)
    
    print("\n\n完整响应：")
    print("".join(full_response))
    
    # 非流式响应演示
    print("\n非流式响应演示：")
    standard_response = llm.generate("Python中如何实现数据加密？")
    print(standard_response)
    

if __name__ == "__main__":
    test_llm()