from dg_agent.config import Settings, System
from dg_agent.api import API

__settings = Settings()
__version__ = "V1.0 Alpha"


def client(settings: Settings = __settings) -> API:
    """Return a running dg_agent.API instance"""

    system = System(settings)
    api = system.instance(API)
    system.start()
    return api
