import logging
from typing import AsyncGenerator, cast

from overrides import overrides
from pydantic import BaseModel

from airda.agent.action.explainer import Explainer, ExplainerParams
from airda.agent.action.searcher import Searcher, SearcherParams
from airda.agent.action.sql_generator import SqlGenerator, SQLGeneratorParams
from airda.agent.assistants.sql_assistant.sql_strategy import (
    ExplainerStrategy,
    SearcherStrategy,
    SQLGeneratorStrategy,
)
from airda.agent.exception.action_type_error import ActionTypeError
from airda.agent.llm.data_agent_llm_keys import DataAgentLLMKeys
from airda.framework.action.action import Action
from airda.framework.agent.module.assistant_manager.assistant.assistant import Assistant
from airda.framework.agent.module.assistant_manager.assistant.assistant_params import (
    AssistantParams,
)
from airda.framework.agent.module.assistant_manager.assistant.assistant_result import (
    AssistantResult,
)

logger = logging.getLogger(__name__)


class SqlAssistantParams(BaseModel, AssistantParams):
    question: str
    datasource_name: str


class SqlAssistant(Assistant[SqlAssistantParams]):
    @overrides
    def init_actions(self) -> list[type[Action]]:
        return [Searcher, SqlGenerator, Explainer]

    @overrides
    def before(self, cls: type[Action]) -> Action:
        m_action = None
        previous = self.get_previous()
        if cls == Searcher:
            params = SearcherParams(**vars(self.get_params))
            SearcherStrategy().concat(params, previous)
            m_action = Searcher(params)
        elif cls == SqlGenerator:
            params = SQLGeneratorParams(
                question=self.get_params.question,
            )
            SQLGeneratorStrategy().concat(params, previous)
            m_action = SqlGenerator(params, self.context.get_llm(DataAgentLLMKeys.SqlLLM))
        elif cls == Explainer:
            params = ExplainerParams(question=self.get_params.question)
            ExplainerStrategy().concat(params, previous)
            m_action = Explainer(params, self.context.get_llm(DataAgentLLMKeys.ChatLLM))
        return m_action

    @overrides
    async def start(self, m_action: Action) -> AsyncGenerator[AssistantResult, None]:
        if isinstance(m_action, Searcher):
            searcher = cast(Searcher, m_action)
            yield AssistantResult(searcher.execute(self.context), None)
        elif isinstance(m_action, SqlGenerator):
            sql = cast(SqlGenerator, m_action)
            async for result in sql.execute(self.context):
                yield AssistantResult(result, result.sql)
        elif isinstance(m_action, Explainer):
            explainer = cast(Explainer, m_action)
            async for result in explainer.execute(self.context):
                yield AssistantResult(result, result.session_token)
        else:
            raise ActionTypeError("不支持的action类型: {}".format(type(m_action)))

    @overrides
    def after(self, m_action: Action) -> type[Action]:
        return type(m_action)
