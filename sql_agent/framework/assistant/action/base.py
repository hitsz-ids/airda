from abc import abstractmethod, ABC
from sql_agent.framework.assistant.action import ActionStatus


class Action:
    _result: str = ""
    _question: str = ""
    _name: str = ""
    _status: ActionStatus = ActionStatus.READY

    def __init__(self, question: str):
        self._question = question
        self._name = self.init_name()

    @abstractmethod
    def init_name(self) -> str:
        pass

    @abstractmethod
    def execute(self) -> bool:
        return False

    def get_result(self):
        return self._result

    def get_name(self) -> str:
        return self._name

    def set_status(self, status: ActionStatus):
        self._status = status
