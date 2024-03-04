from typing import Generator

from sql_agent.framework.assistant.base import Assistant


class Task:
    _steps: list[Assistant]
    _question: str = ""

    def __init__(self, question: str, steps: list[Assistant]):
        self._question = question
        self._steps = steps

    def execute(self) -> Generator:
        for item in self._steps:
            print('item:', item)
            yield from item.run(self._question)
        yield "[DONE]"

    def stop(self):
        pass
