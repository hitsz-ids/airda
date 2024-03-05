from typing import Generator

from sql_agent.framework.assistant.base import Assistant
from sql_agent.protocol import ChatCompletionRequest


class Task:
    _steps: list[Assistant]

    def __init__(self, steps: list[Assistant]):
        self._steps = steps

    def execute(self) -> Generator:
        for assistant in self._steps:
            yield from assistant.run()

    def stop(self):
        pass
