from framework.assistant.action.llm_action import LlmAction

PROMPT = """
        system: 不要使用"IN"、"OR"、"LEFT JOIN"、"INNER JOIN"，因为它们可能导致额外的结果，可以使用"INTERSECT"或"EXCEPT"代替，当必要时记得使用"DISTINCT"或"LIMIT"。
        user:
        """


class Generator(LlmAction):
    def initName(self):
        return "生成sql"

    def execute(self):
        print("Generator")

    def initPrompt(self, _question):
        return self.prompt
