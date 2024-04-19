from data_agent.agent import DataAgentKey, log
from data_agent.agent.planner.data_agent_pipeline import DataAgentPipeline
from data_agent.agent.planner.data_agent_planner_params import DataAgentPlannerParams
from data_agent.agent.rag.data_agent_rag import DataAgentRag
from data_agent.agent.storage import StorageKey
from data_agent.agent.storage.entity.instruction import Instruction
from data_agent.agent.storage.storage import DataAgentStorage
from data_agent.framework.agent.context import Context

logger = log.getLogger()


class DataAgentContext(Context):
    def plan(self, params: DataAgentPlannerParams) -> DataAgentPipeline:
        return DataAgentPipeline(params, self)

    def load_storage(self):
        super().load(DataAgentKey.STORAGE, DataAgentStorage)

    def load_rag(self):
        super().load(DataAgentKey.RAG, DataAgentRag)

    def get_rag(self) -> DataAgentRag:
        return super().get(DataAgentKey.RAG, DataAgentRag)

    def get_repository(self, storage_key: StorageKey):
        return super().get(DataAgentKey.STORAGE, DataAgentStorage).get_repositories(storage_key)

    def get_storage(self) -> DataAgentStorage:
        return super().get(DataAgentKey.STORAGE, DataAgentStorage)

    def delete_instruction(self, datasource_id: str, database: str):
        from data_agent.agent.storage.repositories.instruction_repository import (
            InstructionRepository,
        )

        repository = self.get_repository(StorageKey.INSTRUCTION).convert(InstructionRepository)
        repository.delete(datasource_id, database)
        pass

    def sync_instruction(self, instruction: Instruction):
        from data_agent.agent.storage.repositories.instruction_repository import (
            InstructionRepository,
        )

        repository = self.get_repository(StorageKey.INSTRUCTION).convert(InstructionRepository)
        instruction.table_comment_embedding = (
            self.get_rag().get_embedding_model().embed_query(instruction.table_comment).tolist()[0]
        )
        column_str = ""
        for column in instruction.columns:
            column_str += f" {column.name} {column.description}"
        instruction.table_column_embedding = (
            self.get_rag().get_embedding_model().embed_query(column_str).tolist()[0]
        )
        logger.debug(f"保存表向量结果: {instruction.database}-{instruction.table_name}")
        repository.insert(instruction)
        logger.debug(f"向量化Database: {instruction.database} -> Table:{instruction.table_name} 结束")
