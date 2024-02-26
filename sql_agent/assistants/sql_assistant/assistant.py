from sql_agent.framework.assistant.action.base import Action
from sql_agent.framework.assistant.base import Assistant
from .action.explainer import Explainer
from .action.generator import Generator
from sql_agent.assistants.action.searcher import Searcher


class SqlAssistant(Assistant):

    def init_actions(self) -> list[type[Action]]:
        return [Searcher, Generator, Explainer]

    def before(self, action: Action):
        pass

    def after(self, action: Action):
        action.get_result()
        pass
