"""
现在已经实现的功能：通过 write 方法和内部中断交互
通过传入 stdin_func 和 stdout_func 来让收到终端对应输出时调用对应的方法
这里的很多功能还很不完善
"""

import subprocess
import threading
import queue
import re

def empty_func(str):
    pass

class TerminalSimulator:
    def __init__(self, command: str):
        self.command = command
        self.output_queue = queue.Queue()
        self.stdout_thread = None
        self.stderr_thread = None
        self.running = False

    def _read_stream(self, stream, func, is_error=False):
        # 检查流是否已关闭或running状态，避免阻塞
        while self.running:
            line = stream.readline()
            # print(f"{'[stderr]' if is_error else '[stdout]'} {line.strip()}", end = '\n')
            func(line)
            if not line:  # 流关闭时退出循环
                break
            self.output_queue.put((line, is_error))

    def run(self, stdout_func = print, stderr_func = print):
        self.process = subprocess.Popen(
            self.command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            errors='replace',
            encoding='utf-8',
            text=True,
            bufsize=0  # 禁用缓冲，确保及时读取
        )
        self.stdinStream = self.process.stdin
        self.stdoutStream = self.process.stdout
        self.stderrStream = self.process.stderr
        
        self.running = True
        self.stdout_thread = threading.Thread(target=self._read_stream, args=(self.stdoutStream, stdout_func, False))
        self.stderr_thread = threading.Thread(target=self._read_stream, args=(self.stderrStream, stderr_func, True))
        self.stdout_thread.daemon = True
        self.stderr_thread.daemon = True
        self.stdout_thread.start()
        self.stderr_thread.start()

    def write(self, data: str):
        if not self.process.stdin.closed and self.isalive():
            self.process.stdin.write(data + '\n')
            self.process.stdin.flush()

    def readLine(self):
        try:
            return self.output_queue.get_nowait()
        except queue.Empty:
            return None, None

    # def read(self):
    #     output = []
    #     c = 0
    #     while True:
    #         line, is_error = self.readLine()
    #         if line is None:
    #             continue
    #         # 检查命令提示符
    #         if re.search(r'PS [A-Za-z]:\\[^>]*>', line):
    #             c += 1
    #             if c == 1:
    #                 pass
    #             if c == 2:
    #                 return (output, line)
    #         else:
    #             output.append((line, is_error))

    def close(self):
        self.running = False
        # 先终止进程以确保流关闭
        self.process.terminate()
        # 强制关闭所有管道以确保readline返回
        if not self.stdinStream.closed:
            self.stdinStream.close()
        self.stdoutStream.close()
        self.stderrStream.close()
        # 等待线程结束
        if self.stdout_thread:
            self.stdout_thread.join(timeout=0.1)
        if self.stderr_thread:
            self.stderr_thread.join(timeout=0.1)
        self.process.wait()

    # def execute(self, command: str):
    #     self.write(command + '\n')
    #     return self.read()
    
    def isalive(self):
        return self.process.poll() is None
    
def print_stripped(str):
    print(str.strip())

if __name__ == "__main__":
    terminal = TerminalSimulator("powershell -NoExit -Command \"chcp 65001\"")
    terminal.run(print_stripped, print_stripped)
    while terminal.isalive():
        cmd = input()
        terminal.write(cmd + '\n')
    # cmd = ""
    # while terminal.isalive():
    #     output, currrent = terminal.execute(cmd)
    #     # for line, is_error in output:
    #     #     print(f"{'[stderr]' if is_error else '[stdout]'} {line.strip()}")
    #     # print(currrent[:-1], end = '')
    #     cmd = input()
    terminal.close()
