from abc import ABC, abstractmethod

from sql_agent import config
from sql_agent.config import System


class WebFrameworkServer(ABC):
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        self.app = self.create_app()
        self.settings = config.settings
        self.system = System(self.settings)
        self._api = self.init_api()

    @abstractmethod
    def create_app(self):
        pass

    @abstractmethod
    def run_server(self):
        pass

    @abstractmethod
    def add_routes(self, app):
        pass

    def init_api(self):
        return self.system.instance(API)
