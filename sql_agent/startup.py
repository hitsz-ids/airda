import threading
from os import wait

from sql_agent.planner.planner import Planner

event = threading.Event()


def main():
    planner = Planner()
    task = planner.plan("帮我查找当前有多少用户", "2")
    for item in task.execute():
        print(item)
    # event.wait()


if __name__ == "__main__":
    main()
