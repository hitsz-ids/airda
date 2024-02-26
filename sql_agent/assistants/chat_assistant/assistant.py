from sql_agent.assistants.action.searcher import Searcher
from sql_agent.framework.assistant.action.base import Action
from sql_agent.framework.assistant.base import Assistant


class ChatAssistant(Assistant):
    _prompt: "我是一个什么xxx"

    def before(self, action: Action):
        pass

    def after(self, action: Action):
        pass

    def init_actions(self) -> list[type[Action]]:
        return [Searcher]

    def prepare(self, action: Action):
        pass

    def complete(self, action: Action) -> bool:
        return False
