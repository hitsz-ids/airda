import os
import uuid
import json
import datetime
import requests
from overrides import override
from typing import Generator, Any, List
from sql_agent.api import API
from sql_agent.config import System
from sql_agent.db import DB
from sql_agent.llm import LLM
from fastapi import BackgroundTasks
from sql_agent.generator import prompt_generator
import pandas as pd
from sql_agent.protocol.types import GoldenRecord
from sql_agent.vector_store.doc_index import DocIndex
from sql_agent.context_store import ContextStore
from fastapi.responses import StreamingResponse, JSONResponse
from sql_agent.protocol import (
    ChatCompletionRequest,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    DeltaMessage,
    ErrorResponse,
    CompletionKnowledgeLoadRequest,
    CompletionKnowledgeDeleteRequest,
    CompletionGoldenSQLAddRequest
)
from sql_agent.protocol.types import GoldenRecord, Question


def create_error_response(code: int, message: str) -> JSONResponse:
    return JSONResponse(
        ErrorResponse(message=message, code=code).dict(), status_code=400
    )


class QuestionRequest:
    def __init__(self, file_path, db_connection_id, session_id, question, sql_type, question_type):
        self.file_path = file_path
        self.db_connection_id = db_connection_id
        self.session_id = session_id
        self.question = question
        self.sql_type = sql_type
        self.question_type = question_type

    def __str__(self):
        return (
            f"QuestionRequest:[question:{self.question},file_path:{self.file_path},"
            f"db_connection_id:{self.db_connection_id}session_id:{self.session_id},"
            f"sql_type:{self.sql_type},question_type:{self.question_type}]")


def get_file_extension(filename):
    # 使用split('.')将文件名拆分为文件名和后缀部分
    parts = filename.split('.')

    # 如果文件名中包含多个点，则最后一个点后的部分是后缀
    if len(parts) > 1:
        return parts[-1]
    else:
        # 如果文件名中没有点，或者只有一个点，则没有后缀
        return ""


def generate_knowledge(docs: list):
    knowledge = ''
    if docs:
        for doc in docs:
            knowledge += doc.page_content + '\n'
    print('知识库查询结果:', knowledge)
    if not knowledge:
        knowledge = ''
    return knowledge


def generate_few_shot(fewshot_examples: list):
    print('fewshot:', fewshot_examples)
    fewshot = ''
    for few_shot in fewshot_examples:
        fewshot += f"Question: {few_shot['nl_question']} -> SQL: {few_shot['sql_query']} \n"
    return fewshot


def generate_prompt(messages) -> QuestionRequest:
    question_request_str = ''
    if isinstance(messages, str):
        prompt = messages
    else:
        for message in messages:
            msg_role = message["role"]
            if msg_role == "user":
                question_request_str = message["content"]
            else:
                raise ValueError(f"Unknown role: {msg_role}")
    if question_request_str:
        question_request = json.loads(question_request_str)
        file_path = question_request['filePathList']
        session_id = question_request['sid']
        question = question_request['question']
        db_connection_id = question_request['dataSourceId']
        sql_type = question_request['dbType']
        question_type = question_request['questionType']
        return QuestionRequest(file_path, db_connection_id, session_id, question, sql_type, question_type)


class FastAPI(API):
    def __init__(self, system: System):
        super().__init__(system)
        self.system = system
        self.storage = self.system.instance(DB)
        self.llm = self.system.instance(LLM)
        self.doc_index = self.system.instance(DocIndex)
        self.doc_collection = 'doc_collection'
        self.csv_file_suffix = '_knowledge.csv'

    @override
    async def create_completion(self, request: ChatCompletionRequest):
        print('开始请求:', datetime.datetime.now())
        question_request = generate_prompt(request.messages)
        print('请求内容:', question_request.__str__())
        if not question_request:
            return create_error_response(10086, '请求参数错误')
        question = question_request.question
        file_path = question_request.file_path
        print('开始查询向量数据库')
        docs = self.doc_index.query_doc(query_texts=question, source=file_path, collection=self.doc_collection,
                                        num_results=10)
        knowledge = generate_knowledge(docs)
        question_type = question_request.question_type
        db_connection_id = question_request.db_connection_id
        if question_type == 'ask':
            print('开始SQL生成:', question)
            sql_type = question_request.sql_type
            context_store = self.system.instance(ContextStore)
            nl_question = Question(question=question, db_connection_id=db_connection_id)
            fewshot_examples = generate_few_shot(context_store.get_golden_records(nl_question, 5))
            key_word = 'oee'
            if key_word in question or key_word.upper() in question:
                fewshot_examples += 'Question: 计算OEE指标 -> SQL: SELECT  AVG(run_time / load_time) *  AVG((amount - unqualified) / amount) * AVG(yield) FROM dfs_metrics_device_oee\n'
            prompt = prompt_generator.generate_sql_prompt(
                question, db_connection_id, sql_type, fewshot_examples, knowledge
            )
        else:
            print('开始找数:', question)
            prompt = prompt_generator.generate_knowledge_prompt(question, db_connection_id, knowledge)
        print('prompt生成为:', prompt)
        prompt = prompt.replace("DEFAULT NULL", '')
        prompt = prompt.replace("NOT NULL", '')
        prompt = prompt.replace('COMMENT', '代表')
        session_id = question_request.session_id
        if request.stream:
            generator = self.chat_completion_stream_generator(
                prompt, self.system.settings.model_name, session_id,
                request.n
            )
            return StreamingResponse(generator, media_type="text/event-stream")

    @override
    async def knowledge_train(self, request: CompletionKnowledgeLoadRequest, background_tasks: BackgroundTasks):
        file_id = request.file_id
        file_path = request.file_path
        print('接收到待上传文件:' + file_path)
        if not os.path.exists(file_path):
            print('文件不存在')
            return create_error_response(404, '文件不存在')
        file_name = request.file_name
        background_tasks.add_task(self.load_file_vector_store, file_path, file_id, file_name)
        return True

    @override
    def delete_knowledge_file(self, request: CompletionKnowledgeDeleteRequest):
        file_path = request.file_path.replace('.csv', '_knowledge.csv')
        result = self.storage.find_one(self.doc_collection, {'file_path': file_path})
        if result:
            ids = result['ids']
            self.doc_index.delete_doc(ids, self.doc_collection)
            self.storage.delete_by_id(self.doc_collection, result['_id'])
        return True

    @override
    def add_golden_sql(self, request: CompletionGoldenSQLAddRequest):
        record = GoldenRecord(question=request.question,
                              sql_query=request.sql,
                              db_connection_id=request.db_connection_id)
        context_store = self.system.instance(ContextStore)
        records = [record]
        context_store.add_golden_records(records)
        return True

    async def chat_completion_stream_generator(self,
                                               prompt: str, model_name: str, session_id: str, n: int,
                                               ) -> Generator[str, Any, None]:
        """
        Event stream format:
        https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#event_stream_format
        """
        id = f"{session_id}"
        chat_session_id = session_id + str(uuid.uuid4())
        finish_stream_events = []
        for i in range(n):
            # First chunk with role
            choice_data = ChatCompletionResponseStreamChoice(
                index=i,
                delta=DeltaMessage(role="assistant"),
                finish_reason=None,
            )
            chunk = ChatCompletionStreamResponse(
                id=id, choices=[choice_data], model=model_name
            )
            yield f"data: {chunk.json(exclude_unset=True, ensure_ascii=False)}\n\n"
            previous_text = ""

            async for content in self.llm.generate_completion_stream(prompt, chat_session_id, model_name):
                if content["error_code"] != 0:
                    yield f"data: {json.dumps(content, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                decoded_unicode = content["text"].replace("\ufffd", "")
                delta_text = decoded_unicode

                if len(delta_text) == 0:
                    delta_text = None
                choice_data = ChatCompletionResponseStreamChoice(
                    index=i,
                    delta=DeltaMessage(content=delta_text),
                    finish_reason=content.get("finish_reason", None),
                )
                chunk = ChatCompletionStreamResponse(
                    id=id, choices=[choice_data], model=model_name
                )
                if delta_text is None:
                    if content.get("finish_reason", None) is not None:
                        finish_stream_events.append(chunk)
                    continue
                yield f"data: {chunk.json(exclude_unset=True, ensure_ascii=False)}\n\n"
        # There is not "content" field in the last delta message, so exclude_none to exclude field "content".
        for finish_chunk in finish_stream_events:
            yield f"data: {finish_chunk.json(exclude_none=True, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    def load_file_vector_store(self, file_path, file_id, file_name):
        print('知识库文件上传:' + file_name)
        is_used = 0  # 未使用
        # 当前版本限制为csv文件.
        extension = get_file_extension(file_name)
        if extension != 'csv':
            status = 7  # 训练失败
            self.send_result_to_business(status=status, file_id=file_id, is_used=is_used)
        else:
            try:
                knowledge_csv = self.generator_knowledge_csv(file_path)
                ids = self.doc_index.upload_doc(knowledge_csv, self.doc_collection)
                file_obj = {
                    'file_path': knowledge_csv,
                    'ids': ids
                }
                self.storage.insert_one(self.doc_collection, file_obj)
                is_used = 1  # 已使用
                status = 6  # 训练成功
                self.send_result_to_business(status=status, file_id=file_id, is_used=is_used, ids=ids)
            except Exception as e:
                status = 7  # 训练失败
                print('同步失败')
                print(f"发生异常：{e}")
                self.send_result_to_business(status=status, file_id=file_id, is_used=is_used)

    def send_result_to_business(self, status: int, file_id: str, is_used: int, ids: List[str]):
        data = {
            'fileId': file_id,
            'status': status,
            'isUsed': is_used,
            'ids': ids
        }
        # 发送POST请求
        max_attempts = 3
        for attempt in range(max_attempts):
            response = requests.post(
                self.system.settings.business_server_url + '/api/knowledge/file/status/update',
                json=data
            )
            if response.status_code == 200:
                print('请求成功！')
                break
            else:
                print(f"第 {attempt + 1} 次请求失败，状态码: {response.status_code}")

    def generator_knowledge_csv(self, file_path: str) -> str:
        df = pd.read_csv(file_path)
        new_df = pd.DataFrame()
        new_df[
            'knowledge'] = df.iloc[:, 0].astype(str) + '包含' + df.iloc[:, 1].astype(str) + ',' + df.iloc[:, 1].astype(
            str) + '包含有' + df.iloc[:, 2].astype(str) + ',' + df.iloc[:, 2].astype(str) + '的计算方法是' + df.iloc[:,
                                                                                                             3].astype(
            str)
        knowledge_csv = file_path.replace('.csv', self.csv_file_suffix)
        new_df.to_csv(knowledge_csv, index=False)
        return knowledge_csv
