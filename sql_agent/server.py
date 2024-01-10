import uvicorn
import sys
import os

# 获取当前文件所在目录的上两层目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(os.path.abspath(current_dir))
# 添加上两层目录到sys.path
sys.path.append(project_dir)

import sql_agent
from sql_agent.server.fastapi import FastAPI

settings = sql_agent.config.Settings()
server = FastAPI(settings)
if __name__ == "__main__":
    app = server.app()
    uvicorn.run(app, host='0.0.0.0', port=8888, log_level="info")
