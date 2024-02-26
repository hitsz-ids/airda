import json
from typing import Generator

from sql_agent.assistants.chat_assistant.assistant import ChatAssistant
from sql_agent.assistants.sql_assistant.assistant import SqlAssistant
from sql_agent.framework.assistant.base import Assistant
from sql_agent.planner.task import Task


assistant_map = {"Chat": ChatAssistant, "SQL": SqlAssistant}


class Planner:
    _prompt = """
你是一个AI助理总管，你拥有两个助理来辅助你的工作，他们有各自的能力和特点。你的任务是根据用户提出问题推荐或选择其中的一个或者多个来解决用户的问题。

两个助理的情况分别是：
SqlAssistant是一个专业的SQL助理，能力如下：
1.可以在明确数据表的前提下，能够解构类似于银行十几条业务规则等复杂任务，通过多轮对话式、引导确认式问答自动生成SQL语句。
2.可以对SQL给出易于人类理解的解释。
ChatAssistant是一个能力丰富的助手，能力如下：
1.他可以通过自然语言多轮对话式问答，帮助业务人员快速准确地找到需要的数据。
2.包括表、数据集、指标、口径、业务知识等。对SQL执行的数据结果。
3.整理成图表需要的数据格式来返回用于展示，给出对图表的数据洞察分析（如趋势分析、极值分析等）。

请注意，如果问题超出两个助理的能力范围，你可以回答`我还不擅长回答这些问题，您可以尝试换个问题继续提问`
例如：
xxxx

以下是用户的问题：
{question}
"""
    _assistants: list[Assistant]
    _question: str

    def plan(self, question: str, type: str) -> Task:
        self._question = question
        # 加一个黄赌毒，涉政的检查
        # 任务确认是否继续SQL、Chat、不相关（这版本前端选择）
        # 任务规划
        """
        请求大模型得到规划的结果
        {
            plan: [{name:"", actions: [], type: "ChatAssistant"}, {name:"", actions: [], type: "SqlAssistant"}]
        }
        """
        if type == "1":
            plan_result = ["Chat"]
        else:
            plan_result = ["SQL"]
        self._create_assistants(plan_result)
        return Task(question, self._assistants)

    def _create_assistants(self, plan_result: list[str]):
        assistants: list[Assistant] = []
        for item in plan_result:
            try:
                assistant = assistant_map[item]
                if assistant:
                    assistants.append(assistant())
            except KeyError:
                print(f"未知的助手类型: {item}")
                continue
        self._assistants = assistants
