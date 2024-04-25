import concurrent.futures
from concurrent.futures.process import ProcessPoolExecutor

from aida.agent.env import DataAgentEnv
from aida.framework.utils import singleton


@singleton
class DataAgentProcessPool:
    pool_executor = ProcessPoolExecutor

    def __init__(self):
        self.pool_executor = concurrent.futures.ProcessPoolExecutor(
            max_workers=int(DataAgentEnv().max_works)
        )

    def submit(self, fn, /, *args, **kwargs):
        return self.pool_executor.submit(fn, *args, **kwargs)

    def as_completed(self, fs, timeout=None):
        return concurrent.futures.as_completed(fs, timeout)
