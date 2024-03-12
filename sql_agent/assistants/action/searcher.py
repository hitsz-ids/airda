import logging

from sql_agent.db import Storage
from sql_agent.db.repositories.instructions import InstructionRepository
from sql_agent.db.repositories.types import TableDescription
from sql_agent.framework.assistant.action import ActionResultScope
from sql_agent.framework.assistant.action.base import Action
from sql_agent.protocol import ChatCompletionRequest
from sql_agent.rag.knowledge.service import KnowledgeServiceImpl
from sql_agent.rag.schema_linking.service import SchemaLinkingImpl
from sql_agent.setting import System, env_settings

logger = logging.getLogger(__name__)

system = System()


class Searcher(Action):
    def __init__(self, request: ChatCompletionRequest, action_results: dict[str, dict]):
        super().__init__(request, action_results)
        self.storage = system.get_module(Storage)
        self.doc_index = KnowledgeServiceImpl()
        self.schema_linking = SchemaLinkingImpl()
        self.instruction_repository = InstructionRepository(self.storage)

    def init_name(self):
        return "Searcher"

    def execute(self):
        """
        调用RAG，得到搜索内容
        """
        knowledge = self._search_knowledge()
        tables_description = self._search_tables()
        # few_shot = self._search_few_shot()

        result = {
            "knowledge": knowledge,
            "tables_description": tables_description,
            "tables_schema": extract_table_schema(tables_description),
            "few_shot_example": "",
        }
        self.set_result(result, ActionResultScope.internal)

    def _search_knowledge(self):
        file_id = self._request.file_id
        file_name = self._request.file_name
        logger.info("开始查询知识库")
        source = []
        if file_id and file_name:
            source = [
                f"{env_settings.knowledge_path}/{file_id}/{file_name.replace('.csv', '_knowledge.csv')}"
            ]

        docs = self.doc_index.query_doc(
            query_texts=self._request.question,
            source=source,
            num_results=2,
        )
        knowledge = ""
        if docs:
            for doc in docs:
                knowledge += doc.page_content + "\n"
        logger.info(f"知识库查询结果:{knowledge}")
        if not knowledge:
            knowledge = ""
        return knowledge

    def _search_tables(self):
        question = self._request.question
        datasource_id = self._request.datasource_id
        database = self._request.database
        limit_score_result, top_k_result = self.schema_linking.search(
            question, datasource_id, database
        )
        if len(limit_score_result) < 0:
            table_names = top_k_result
        else:
            table_names = limit_score_result[:5]

        return self._get_table_instruction(table_names, datasource_id, database)

    def _get_table_instruction(
        self, table_names: list[str], datasource_id: str, database: str
    ) -> list[TableDescription]:
        results = []
        for table in table_names:
            query = {
                "table_name": table,
                "datasource_id": datasource_id,
                "database": database,
            }

            table_description = self.instruction_repository.find_one(query=query)

            if not table_description:
                continue
            results.append(table_description)
        return results

    def _search_few_shot(self):
        # database = self._request.database
        # datasource_id = self._request.datasource_id
        # context_store = system.get_module(ContextStore)
        # nl_question = Question(
        #     question=question,
        #     datasource_id=datasource_id,
        #     database=database,
        # )
        # few_shot_examples = context_store.get_golden_records(nl_question, 5)
        # format_few_shot(few_shot_examples)
        pass


def format_few_shot(few_shot_examples: list):
    few_shot = "\n"
    for example in few_shot_examples:
        few_shot += (
            f"Question: {example['nl_question']} -> SQL: {example['sql_query']} \n"
        )
    return few_shot + "\n"


def extract_table_schema(tables_description: list[TableDescription]) -> str:
    if len(tables_description) > 0:
        return "\n".join(item.table_schema for item in tables_description) + "\n"
    else:
        return []
