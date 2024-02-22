from framework.assistant.action.llm_action import LlmAction


class Explainer(LlmAction):
    prompt = """请帮哦我解释生成的结果"""

    def initName(self):
        return "解释sql结果"

    def execute(self):
        print("Explainer")

    def initPrompt(self, _question):
        pass
