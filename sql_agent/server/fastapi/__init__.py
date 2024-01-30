import configparser

from fastapi import FastAPI

from sql_agent.server import WebFrameworkServer


class FastAPIServer(WebFrameworkServer):
    def read_config(self):
        # 实现FastAPIServer的配置读取
        config = configparser.ConfigParser()
        config.read("fastapi_server_config.ini")
        return config

    def create_app(self):
        return FastAPI()

    def run_server(self):
        app = self.create_app()
        self.initialize_configurations(app)
        self.add_routes(app)
        import uvicorn

        uvicorn.run(app, host=self.host, port=self.port)

    def initialize_configurations(self, app):
        # 从self.config读取配置值并初始化变量或对象
        # 例如：app.config['SOME_KEY'] = self.config.get('Section', 'Key', fallback='default_value')
        pass

    def add_routes(self, app):
        pass
