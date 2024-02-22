from framework.assistant.action.base import Action
from framework.assistant.base import Assistant
from .action.explainer import Explainer
from .action.generator import Generator
from assistants.action.searcher import Searcher


class SqlAssistant(Assistant):

    def initActions(self) -> list[Action]:
        return [Searcher(), Generator(), Explainer()]

    def before(self, action: Action):
        pass

    def after(self, action: Action):
        action.getResult()
        pass
