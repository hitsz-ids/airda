import logging
from typing import TYPE_CHECKING, Optional

from overrides import overrides
from pydantic import BaseModel

from data_agent.agent.storage.entity.instruction import Instruction
from data_agent.agent.storage.repositories.instruction_repository import (
    InstructionRepository,
)
from data_agent.framework.action.action_params import ActionParams
from data_agent.framework.action.action_result import ActionResult
from data_agent.framework.action.sync_action import SyncAction

if TYPE_CHECKING:
    from data_agent.framework.agent.context import Context

logger = logging.getLogger(__name__)


class SearcherParams(BaseModel, ActionParams):
    question: str
    datasource_id: str
    database: str


class SearcherResult(BaseModel, ActionResult):
    tables_schema: Optional[str] = None


class Searcher(SyncAction[SearcherParams, SearcherResult]):
    # doc_index = None
    # schema_linking = None
    @overrides
    def init_name(self) -> str:
        return "Explainer"

    @overrides
    def execute(self, context: "Context") -> SearcherResult:
        """
        调用RAG，得到搜索内容
        """
        from data_agent.agent.data_agent_context import DataAgentContext
        from data_agent.agent.storage import StorageKey
        from data_agent.agent.storage.repositories.datasource_repository import (
            DatasourceRepository,
        )

        data_agent_context = context.convert(DataAgentContext)
        datasource_repository = data_agent_context.get_repository(StorageKey.DATASOURCE).convert(
            DatasourceRepository
        )
        datasource = datasource_repository.find_enable()
        if datasource is None:
            logger.debug("No datasource found")
            return SearcherResult(
                knowledge="", tables_description="", tables_schema="", few_shot_example=""
            )
        limit_score_result, top_k_result = data_agent_context.get_rag().search(
            self.params.question, datasource.id, datasource.database
        )
        if len(limit_score_result) < 0:
            table_names = top_k_result
        else:
            table_names = limit_score_result[:5]
        instruction_repository = data_agent_context.get_repository(StorageKey.INSTRUCTION).convert(
            InstructionRepository
        )
        tables_schema = ""
        for table in table_names:
            query = {
                "table_name": table,
                "datasource_id": datasource.id,
                "database": datasource.database,
            }
            instruction = instruction_repository.find_one(query=query)
            if instruction:
                tables_schema += instruction.table_schema + "\n"
                pass
        return SearcherResult(tables_schema=tables_schema)

    def _get_table_instruction(
        self, table_names: list[str], datasource_id: str, database: str
    ) -> list[Instruction]:
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

    def _search_knowledge(self):
        """
        todo 需要调用rag服务的接口获取相关知识库的内容
        """
        return ""

    def _search_tables(self):
        """
        todo 需要调用rag服务的接口获取到表信息
        """
        return []

    def _search_golden_sql(self):
        """
        todo 需要调用rag服务的接口获取golden_sql
        """
        return ""
