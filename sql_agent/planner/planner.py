from typing import Type, Generator

from assistants.chat_assistant.assistant import ChatAssistant
from assistants.sql_assistant.assistant import SqlAssistant
from framework.assistant.base import Assistant
from planner.task import Task


class Planner:
    _assistants: list[Assistant]
    _question: str

    def plan(self, question: str) -> Task:
        self._question = question
        # 加一个黄赌毒，涉政的检查
        # 任务确认是否继续type 1 type 2
        # 任务规划
        """
        请求大模型得到规划的结果
        {
            plan: [{name:"", actions: [], type: "ChatAssistant"}, {name:"", actions: [], type: "SqlAssistant"}]
        }
        """
        self._assistants = [ChatAssistant(), SqlAssistant()]
        steps = self._execute()
        return Task(steps, 3)

    def _execute(self) -> Generator[Assistant, None, None]:
        size = len(self._assistants)
        for i in range(size):
            i = yield i
            self._assistants[i].run(self._question)
