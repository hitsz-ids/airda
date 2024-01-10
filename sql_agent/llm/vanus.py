import datetime
import json

from httpx import AsyncClient
from overrides import override

from sql_agent.config import System
from sql_agent.llm import LLM


class Vanus(LLM):
    def __init__(self, system: System):
        super().__init__(system)
        self.system = system

    @override
    async def generate_completion_stream(self, prompt: str, session_id: str, model_name: str):
        print('开始请求Vanus:', datetime.datetime.now())
        print('请求prompt', prompt)
        headers = {
            "Content-Type": "application/json",
            "x-vanusai-model": model_name,
            "x-vanusai-sessionid": session_id,  # 生成一个随机的 UUID
        }
        print('prompt:' + prompt)
        data = {
            "prompt": prompt,
            "stream": True,
            "no_search": True,
            "no_history": True,
            "system_prompt": ''
            # "history_window": {"num": 10, "peroid": 600000}
        }

        async with AsyncClient() as client:
            async with client.stream(
                    "POST",
                    f"https://app.ai.vanus.ai/api/v1/{self.system.settings.application_id}",
                    headers=headers,
                    json=data,
                    timeout=60
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        if line.startswith('data:'):
                            json_line = line[6:]
                            data = json.loads(json_line)
                            print(data)
                            if data['more']:
                                token = data['token']
                                print(token)
                                ret = {
                                    "text": token,
                                    "error_code": 0,
                                    "usage": {}
                                }
                                yield ret
                            else:
                                ret = {
                                    "text": '',
                                    "error_code": 0,
                                    "finish_reason": 'stop',
                                    "usage": {}
                                }
                                yield ret
