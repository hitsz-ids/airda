from sql_agent.server.fastapi import FastAPIServer


# 获取当前文件所在目录的上两层目录的绝对路径
def start():
    server = FastAPIServer()
    server.run_server()


if __name__ == "__main__":
    start()
