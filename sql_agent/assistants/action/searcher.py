from framework.assistant.action.base import Action


class Searcher(Action):
    def initName(self):
        return "搜索对应的表信息"

    def execute(self):
        """
        调用RAG，得到搜索内容
        """
        print("Searcher")
