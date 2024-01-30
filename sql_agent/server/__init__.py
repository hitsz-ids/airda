from abc import ABC, abstractmethod


class WebFrameworkServer(ABC):
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        self.config = self.read_config()

    @abstractmethod
    def read_config(self):
        pass

    @abstractmethod
    def create_app(self):
        pass

    @abstractmethod
    def run_server(self):
        pass

    @abstractmethod
    def add_routes(self, app):
        pass
