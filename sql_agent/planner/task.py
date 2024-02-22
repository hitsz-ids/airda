from typing import Generator

from framework.assistant.base import Assistant


class Task:
    _steps: Assistant

    def __init__(self, steps: Assistant, size: int):
        self._steps = steps
        self._size = size
        next(self._steps)
        pass

    def next(self):
        try:
            next(self._steps)
        except StopIteration:
            self.stop()

    def stop(self):
        self._steps.close()
