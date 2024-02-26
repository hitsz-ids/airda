from typing import Generator

from sql_agent.framework.assistant.base import Assistant


class Task:
    _steps: list[Assistant]
    _question: str = ""

    def __init__(self, question: str, steps: list[Assistant]):
        self._steps = steps
        self._question = question

    def execute(self) -> Generator:
        for item in self._steps:
            for action_result in item.run(self._question):
                yield action_result

    def stop(self):
        pass
