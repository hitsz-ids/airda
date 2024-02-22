from abc import abstractmethod, ABC

from framework.assistant.action import ActionStatus


class Action:
    _result: str
    _question: str
    _name: str
    _status: ActionStatus

    def __init__(self):
        self._name = self.initName()
        self._result = ''
        _status = ActionStatus.READY

    @abstractmethod
    def initName(self) -> str:
        pass

    @abstractmethod
    def execute(self) -> bool:
        return False

    def getResult(self):
        return self._result

    def getName(self) -> str:
        return self._name

    def setStatus(self, status: ActionStatus):
        self._status = status
