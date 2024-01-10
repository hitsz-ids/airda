from sql_agent.config import Settings, System
from sql_agent.api import API

__settings = Settings()
__version__ = "V1.0 Alpha"


def client(settings: Settings = __settings) -> API:
    """Return a running sql_agent.API instance"""

    system = System(settings)
    api = system.instance(API)
    system.start()
    return api
