class AgentError(Exception):
    CODE = -1

    def __init__(self, msg: str = None):
        super().__init__(msg)
