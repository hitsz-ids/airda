from typing import AsyncGenerator

from sql_agent.framework.assistant.base import Assistant
from sql_agent.protocol import ChatCompletionRequest


class Task:
    _steps: list[Assistant]

    def __init__(self, steps: list[Assistant]):
        self._steps = steps

    async def execute(self) -> AsyncGenerator[str, None]:
        for assistant in self._steps:
            async for item in assistant.run():
                yield item

    def stop(self):
        pass
