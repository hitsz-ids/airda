import datetime
import json

from httpx import AsyncClient
from overrides import override

from sql_agent.config import System
from sql_agent.llm import LLM


class ChatGPT(LLM):
    def __init__(self, system: System):
        super().__init__(system)
        self.system = system

    @override
    async def generate_completion_stream(self, prompt: str, session_id: str, model_name: str):
        print('开始请求OpenAI:', datetime.datetime.now())
        print('prompt:', prompt)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.system.settings.openai_api_key
        }
        params = {
            "model": model_name,
            "messages": [{'role': 'user', 'content': prompt}],
            "temperature": 0.7,
            "n": 1,
            "stream": True
        }
        # dataStr = json.dumps(params)
        async with AsyncClient() as client:
            async with client.stream(
                    "POST",
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=params,
                    timeout=60
            ) as response:
                async for line in response.aiter_lines():
                    if line.strip() == "":
                        continue
                    if line.startswith('data:'):
                        json_line = line[6:]
                        print(json_line)
                        if json_line.strip() == '[DONE]':
                            ret = {
                                "text": '',
                                "error_code": 0,
                                "finish_reason": 'stop',
                                "usage": {}
                            }
                            yield ret
                        else:
                            data = json.loads(json_line)
                            token = data["choices"][0]["delta"].get("content", "")
                            ret = {
                                "text": token,
                                "error_code": 0,
                                "usage": {}
                            }
                            yield ret
                    