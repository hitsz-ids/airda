import logging
from typing import AsyncGenerator, cast

from overrides import overrides
from pydantic import BaseModel

from data_agent.agent.action.explainer import Explainer, ExplainerParams
from data_agent.agent.action.searcher import Searcher, SearcherParams
from data_agent.agent.action.sql_generator import SqlGenerator, SQLGeneratorParams
from data_agent.agent.assistants.sql_assistant.sql_strategy import (
    ExplainerStrategy,
    SearcherStrategy,
    SQLGeneratorStrategy,
)
from data_agent.agent.exception.action_type_error import ActionTypeError
from data_agent.agent.llm.data_agent_llm_keys import DataAgentLLMKeys
from data_agent.framework.action.action import Action
from data_agent.framework.agent.module.assistant_manager.assistant.assistant import (
    Assistant,
)
from data_agent.framework.agent.module.assistant_manager.assistant.assistant_params import (
    AssistantParams,
)
from data_agent.framework.agent.module.assistant_manager.assistant.assistant_result import (
    AssistantResult,
)

logger = logging.getLogger(__name__)


class SqlAssistantParams(BaseModel, AssistantParams):
    question: str


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
