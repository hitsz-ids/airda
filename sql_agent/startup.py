import threading
from os import wait

from assistants.sql_assistant.assistant import SqlAssistant
from planner.planner import Planner

event = threading.Event()


def main():
    planner = Planner()
    task = planner.plan("帮我查找当前有多少用户")
    task.next()
    task.next()
    event.wait()


if __name__ == "__main__":
    main()
