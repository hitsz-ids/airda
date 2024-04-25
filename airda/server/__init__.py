from abc import ABC, abstractmethod

from airda.server.api import API


class WebFrameworkServer(ABC):
    def __init__(self, host="0.0.0.0", port=8888):
        self.host = host
        self.port = port
        self.app = self.create_app()
        # self.settings = env_settings
        # self.system = system
        self._api = self.init_api()
        self.add_routes()

    @abstractmethod
    def create_app(self):
        pass

    @abstractmethod
    def run_server(self):
        pass

    @abstractmethod
    def add_routes(self):
        pass

    @abstractmethod
    def init_api(self):
        pass
