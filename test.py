from winpty import PtyProcess

pty = PtyProcess.spawn('cmd', dimensions=(80, 80))
# 设置代码页为UTF-8
pty.write('chcp 65001\r\n')
pty.read()  # 清除chcp命令的输出

# 现在可以正常显示中文了
pty.write('tests\\a.exe < tests\\a.in\r\n')
print(pty.read())

