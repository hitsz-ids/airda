from sql_agent.server.fastapi import SQLAgentServer


# 获取当前文件所在目录的上两层目录的绝对路径
def start():
    server = SQLAgentServer()
    server.run_server()


if __name__ == "__main__":
    start()
