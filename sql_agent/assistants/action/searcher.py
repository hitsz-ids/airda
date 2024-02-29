from sql_agent.framework.assistant.action.base import Action


class Searcher(Action):
    def init_name(self):
        return "Seacher"

    def execute(self):
        """
        调用RAG，得到搜索内容
        """
        print("Searcher")
