from terminal.CLI import CLI

if __name__ == '__main__':
    cli = CLI('powershell -NoExit -Command "chcp 65001"', dimensions=(800, 80))
    cli.launch()
