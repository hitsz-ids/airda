from typing import TYPE_CHECKING, Optional

from overrides import overrides
from pydantic import BaseModel

from aida.agent import log
from aida.agent.storage.repositories.instruction_repository import (
    InstructionRepository,
)
from aida.framework.action.action_params import ActionParams
from aida.framework.action.action_result import ActionResult
from aida.framework.action.sync_action import SyncAction

if TYPE_CHECKING:
    from aida.framework.agent.context import Context

logger = log.getLogger()


class SearcherParams(BaseModel, ActionParams):
    question: str


class SearcherResult(BaseModel, ActionResult):
    tables_schema: Optional[str] = None
    kind: str


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
        from aida.agent.data_agent_context import DataAgentContext
        from aida.agent.storage import StorageKey
        from aida.agent.storage.repositories.datasource_repository import (
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
        return SearcherResult(tables_schema=tables_schema, kind=datasource.kind)
