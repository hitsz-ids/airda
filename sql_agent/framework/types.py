import threading


class Singleton(type):
    _instance_lock = threading.Lock()
    _instances = {}

    def __call__(cls, *args, **kwargs):
        with cls._instance_lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
