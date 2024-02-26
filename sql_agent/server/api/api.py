import logging
import os

from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from overrides import override

from sql_agent.config import System
from sql_agent.protocol import (
    ChatCompletionRequest,
    CompletionInstructionSyncRequest,
    CompletionKnowledgeLoadRequest,
    ErrorResponse,
)
from sql_agent.rag.knowledge import KnowledgeDocIndex
from sql_agent.server.api import API
from sql_agent.utils import file

logger = logging.getLogger(__name__)


def create_error_response(code: int, message: str) -> JSONResponse:
    return JSONResponse(ErrorResponse(message=message, code=code).dict(), status_code=400)


class APIImpl(API):
    def __init__(self, system: System):
        super().__init__(system)
        self.system = system
        self.doc_index = self.system.instance(KnowledgeDocIndex)

    @override
    async def create_completion(self, request: ChatCompletionRequest):
        knowledge_index = request.knowledge
        datasource = request.datasource
        database = request.database
        # 考虑是否本地缓存对话结果
        question = request.messages
        # 判断数据源,数据库是否存在

        # 获取知识库内容
        knowledge = self.doc_index.query_doc(question)
        # 获取assistants
        assistants = {}
        """ 获得规划后进行执行.
        方案1.按照langchain agent式进行调用.
        方案2.按照metagpt的方式,让assistant自己进行处理与调用
        """

    @override
    async def knowledge_train(
        self, request: CompletionKnowledgeLoadRequest, background_tasks: BackgroundTasks
    ):
        # 保存文件到指定路径
        file_contents = await request.file.read()
        save_path = f"{self.system.settings.knowledge_path}/{request.file_id}"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = f"{save_path}/{request.file_name}"
        with open(file_path, "wb") as f:
            f.write(file_contents)
        file_id = request.file_id
        logger.info(f"接收到待上传文件:{file_path}")
        if not os.path.exists(file_path):
            logger.info("文件不存在")
            return create_error_response(404, "文件不存在")
        file_name = request.file_name
        background_tasks.add_task(self.load_file_vector_store, file_path, file_id, file_name)
        return True

    @override
    def instruction_sync(
        self, request: CompletionInstructionSyncRequest, background_tasks: BackgroundTasks
    ):
        # 创建同步记录
        # 开始同步表结构
        pass

    def load_file_vector_store(self, file_path, file_id, file_name):
        logger.info(f"知识库文件上传: {file_name}")
        is_used = 0  # 未使用
        # 当前版本限制为csv文件.
        extension = file.get_file_extension(file_name)
        # 1.增加同步状态,同步完后修改为成功
        os.remove(file_path)
