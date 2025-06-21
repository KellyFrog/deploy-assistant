"""
现在已经实现的功能：通过 write 方法和内部中断交互
通过传入 stdin_func 和 stdout_func 来让收到终端对应输出时调用对应的方法
这里的很多功能还很不完善
"""

import msvcrt
import re
import subprocess
import threading
import queue
import winpty
import threading

def empty_func(str):
    pass

class TerminalSimulator:
    def read_output(self):
        while True:
            try:
                output = self.pty.read()
                # pattern = r'\x1b\[m'  # 删除上移光标的转义字符
                pattern = r'\x1B\[(\d+;\d+|\d+)H' # 删除形如 \x1b[4;36H 的转义符，它的作用是移动光标
                output = re.sub(pattern, '', output)
                self.func(output)
                if output:
                    print(output, end='', flush=True)
                    pass
            except EOFError:
                break

    def __init__(self, cmd, dimensions, func):
        # Create a new pseudo-terminal
        self.pty = winpty.PtyProcess.spawn(cmd, dimensions=dimensions)
        self.func = func
        # Start a thread to read the output
        output_thread = threading.Thread(target=self.read_output, args=(), daemon=True)
        output_thread.start()
    
    def write(self, cmd: str):
        self.pty.write(cmd)
    
    def isalive(self):
        return self.pty.isalive()

if __name__ == "__main__":
    terminal = TerminalSimulator("pwsh -NoExit -Command \"chcp 65001\"", empty_func)
    while terminal.isalive():
        try:
            # if msvcrt.kbhit():
            #     ch = msvcrt.getch().decode()
            #     terminal.write(ch)
            cmd = input().strip()
            terminal.write(cmd + '\r')
        except KeyboardInterrupt:
            terminal.write('\003')
            
