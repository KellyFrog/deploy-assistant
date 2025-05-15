"""
现在已经实现的功能：通过 write 方法和内部中断交互
通过传入 stdin_func 和 stdout_func 来让收到终端对应输出时调用对应的方法
这里的很多功能还很不完善
"""

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
                self.func(output)
                if output:
                    print(output, end='', flush=True)
                    pass
            except EOFError:
                break

    def __init__(self, cmd, func):
        # Create a new pseudo-terminal
        self.pty = winpty.PtyProcess.spawn(cmd)
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
        cmd = input().strip()
        terminal.write(cmd + '\r')
    # cmd = ""
    # while terminal.isalive():
    #     output, currrent = terminal.execute(cmd)
    #     # for line, is_error in output:
    #     #     print(f"{'[stderr]' if is_error else '[stdout]'} {line.strip()}")
    #     # print(currrent[:-1], end = '')
    #     cmd = input()
    terminal.close()
