import logging
import os

from bson import ObjectId
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from overrides import override

from sql_agent.db import DB
from sql_agent.db.repositories.datasource import DatasourceRepository
from sql_agent.db.repositories.instructions import InstructionRepository
from sql_agent.db.repositories.sync_instructions import (
    InstructionEmbeddingRecordRepository,
)
from sql_agent.db.repositories.sync_knowledge import KnowledgeSyncRepository
from sql_agent.db.repositories.types import (
    Datasource,
    DBEmbeddingStatus,
    EmbeddingInstruction,
    Instruction,
    InstructionEmbeddingRecord,
)
from sql_agent.llm.embedding_model import EmbeddingModel
from sql_agent.planner.planner import Planner
from sql_agent.protocol import (
    ChatCompletionRequest,
    CompletionInstructionSyncRequest,
    CompletionInstructionSyncStatusRequest,
    CompletionKnowledgeLoadRequest,
    DatasourceAddRequest,
    ErrorResponse,
)
from sql_agent.protocol.response import BaseResponse
from sql_agent.rag.knowledge import KnowledgeDocIndex
from sql_agent.server.api import API
from sql_agent.setting import System
from sql_agent.utils import file

logger = logging.getLogger(__name__)


def create_error_response(code: int, message: str) -> JSONResponse:
    return JSONResponse(ErrorResponse(message=message, code=code).dict(), status_code=400)


def paginate_array(array, page_size):
    result = []
    for i in range(0, len(array), page_size):
        result.append(array[i : i + page_size])
    return result

    # 示例用法


class APIImpl(API):
    def __init__(self, system: System):
        super().__init__(system)
        self.system = system
        self.storage = self.system.get_instance(DB)
        self.csv_file_suffix = "_knowledge.csv"
        self.doc_collection = "doc_collection"
        self.doc_index = self.system.get_instance(KnowledgeDocIndex)
        self.embedding_model = EmbeddingModel()

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
        planner = Planner()
        task = planner.plan(question)
        for item in task.execute():
            yield item
        """ 获得规划后进行执行.
        方案1.按照langchain agent式进行调用.
        方案2.按照metagpt的方式,让assistant自己进行处理与调用
        """

    @override
    async def datasource_add(self, request: DatasourceAddRequest):
        datasource = Datasource(
            type=request.type,
            host=request.host,
            port=request.port,
            database=request.database,
            user_name=request.user_name,
            password=request.password,
            config=request.config,
        )

        datasourceRepository = DatasourceRepository(self.storage)
        datasourceRepository.insert(datasource)

        return BaseResponse(msg="成功", code=0, data={"id": datasource.id})

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
        knowledge_sync_repository = KnowledgeSyncRepository(self.storage)
        knowledge_sync_repository.insert()
        background_tasks.add_task(self.load_file_vector_store, file_path, file_id, file_name)
        return True

    @override
    async def instruction_sync(
        self,
        request: CompletionInstructionSyncRequest,
        background_tasks: BackgroundTasks,
    ):
        instructions = request.instructions
        if instructions:
            page_size = 20
            page_array = paginate_array(instructions, page_size)
        else:
            # 空数组 报错
            return BaseResponse(msg="请传入有效表结构", code=10001, data=None)
        datasource_id = request.datasource_id
        embedding_repository = InstructionEmbeddingRecordRepository(self.storage)
        sync_embedding_record = embedding_repository.find_one({"datasource_id": datasource_id})
        instruction_repository = InstructionRepository(self.storage)
        sync_embedding_record = embedding_repository.find_one({"datasource_id": datasource_id})
        if (
            sync_embedding_record is None
            or sync_embedding_record.status != DBEmbeddingStatus.EMBEDDING.value
        ):
            instruction_repository.delete_by({"datasource_id": datasource_id})
            if sync_embedding_record is None:
                sync_embedding_record = InstructionEmbeddingRecord(datasource_id=datasource_id)
                embedding_repository.insert(sync_embedding_record)
            else:
                sync_embedding_record.status = DBEmbeddingStatus.EMBEDDING.value
                embedding_repository.update(sync_embedding_record)
            self.save_instructions(instructions)
        else:
            return BaseResponse(msg="成功", code=0, data={"id": sync_embedding_record.id})
        success = True
        for page_data in page_array:
            save_result = self.process_page(page_data, sync_embedding_record.id)
            if isinstance(save_result, str) and save_result.startswith("Error"):
                logger.info(f"Error processing data  {save_result}")
                success = False
                break
            elif isinstance(save_result, bool) and not save_result:
                success = False
                logger.info(f"Error processing data  {save_result}")
                break
            else:
                logger.info(f"Successfully processed data")
        if success:
            sync_embedding_record.status = DBEmbeddingStatus.SUCCESS.value
        else:
            instruction_repository.delete_embedding_by(
                {"datasource_id": sync_embedding_record.datasource_id}
            )
            sync_embedding_record.status = DBEmbeddingStatus.FAILED.value
        embedding_repository.update(sync_embedding_record)
        return BaseResponse(msg="成功", code=0, data={"id": sync_embedding_record.id})

    @override
    async def instruction_sync_status(self, request: CompletionInstructionSyncStatusRequest):
        embedding_repository = InstructionEmbeddingRecordRepository(self.storage)
        sync_embedding_record = embedding_repository.find_one({"_id": request.id})
        if sync_embedding_record is None:
            return BaseResponse(msg="查询失败,未查到同步记录", code=10002, data={})
        else:
            return BaseResponse(msg="成功", code=0, data={"status": sync_embedding_record.status})

    @override
    async def instruction_sync_stop(self, request: CompletionInstructionSyncStatusRequest):
        embedding_repository = InstructionEmbeddingRecordRepository(self.storage)
        sync_embedding_record = embedding_repository.find_one({"_id": request.id})
        if (
            sync_embedding_record
            and sync_embedding_record.status == DBEmbeddingStatus.EMBEDDING.value
        ):
            sync_embedding_record.status = DBEmbeddingStatus.STOP.value
            embedding_repository.update(sync_embedding_record)

        return BaseResponse(msg="成功", code=0, data={})

    def process_page(self, schema_list: list[Instruction], sync_embedding_id: str):
        if len(schema_list) > 0:
            instruction_repository = InstructionRepository(self.storage)
            embedding_repository = InstructionEmbeddingRecordRepository(self.storage)
            embedding_record = embedding_repository.find_one({"_id": ObjectId(sync_embedding_id)})
            if embedding_record:
                if embedding_record.status == DBEmbeddingStatus.SUCCESS.value:
                    return True
                elif embedding_record.status != DBEmbeddingStatus.EMBEDDING.value:
                    return False
            else:
                return False
            try:
                table_comments = []
                table_fields = []
                for db_schema in schema_list:
                    table_schema = db_schema.instruction
                    if table_schema:
                        des = table_schema["description"]
                        columns = table_schema["columns"]
                        column_str = ""
                        for column in columns:
                            column_str += f" {column['name']} {column['description']}"
                        table_fields.append(column_str)
                        table_comments.append(des)
                comment_embedding = self.embedding_model.embed_query(table_comments).tolist()
                column_embedding = self.embedding_model.embed_query(table_fields).tolist()
                for idx in range(len(schema_list)):
                    db_schema = schema_list[idx]
                    table_schema = db_schema.instruction
                    if table_schema:
                        table_name = table_schema["table_name"]
                        table_comment_embedding = comment_embedding[idx]
                        table_column_embedding = column_embedding[idx]
                        db_embedding_instruction = EmbeddingInstruction(
                            table_name=table_name,
                            db_connection_id=db_schema.datasource_id,
                            database=db_schema.database,
                            table_comment=table_schema["description"],
                            table_comment_embedding=table_comment_embedding,
                            column_embedding=table_column_embedding,
                        )
                        logger.info(f"保存表向量结果: {db_schema.database}-{table_name}")
                        instruction_repository.insert_embedding(db_embedding_instruction)
                        logger.info(f"向量化Database: {db_schema.database} -> Table:{table_name} 结束")
            except Exception as e:
                logger.error(f"向量化数据异常:{e}")
                return f"Error 向量化数据失败"
            return f"Successful 向量化表结构成功"

    def load_file_vector_store(self, file_path, file_id, file_name):
        logger.info(f"知识库文件上传: {file_name}")
        # 当前版本限制为csv文件.
        extension = file.get_file_extension(file_name)
        if extension != "csv":
            return BaseResponse(msg="暂不支持csv以外文档", code=10003, data={})
        else:
            knowledge_csv = self.generator_knowledge_csv(file_path)
            self.doc_index.upload_doc(knowledge_csv, self.doc_collection)
        # 1.增加同步状态,同步完后修改为成功
        os.remove(file_path)

    def save_instructions(self, instructions: list[Instruction]):
        instruction_repository = InstructionRepository(self.storage)
        for instruction in instructions:
            instruction_repository.insert(instruction)

    def generator_knowledge_csv(self, file_path: str) -> str:
        df = pd.read_csv(file_path)
        new_df = pd.DataFrame()
        new_df["knowledge"] = (
            df.iloc[:, 0].astype(str)
            + "包含"
            + df.iloc[:, 1].astype(str)
            + ","
            + df.iloc[:, 1].astype(str)
            + "包含有"
            + df.iloc[:, 2].astype(str)
            + ","
            + df.iloc[:, 2].astype(str)
            + "的计算方法是"
            + df.iloc[:, 3].astype(str)
        )
        knowledge_csv = file_path.replace(".csv", self.csv_file_suffix)
        new_df.to_csv(knowledge_csv, index=False)
        return knowledge_csv
