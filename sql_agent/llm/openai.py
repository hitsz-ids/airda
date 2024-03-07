import datetime
import logging
import uuid
from typing import AsyncGenerator

import httpx
from overrides import override
from sql_agent.llm import LLM
from sql_agent.protocol import ChatMessage

logger = logging.getLogger(__name__)


class OpenAILLM(LLM):

    def __init__(self):
        super().__init__()
        self._api_key = self.system.env_settings.openai_api_key

    @override
    async def chat_completion(
            self,
            messages: list[ChatMessage],
            model_name="gpt-4-1106-preview",
            session_id=f"ChatGPT-{uuid.uuid4()}",
    ) -> AsyncGenerator[str, None]:
        logger.info(f"开始请求OpenAI: {datetime.datetime.now()}")
        logger.info(f"prompt: {messages[-1].get('content')}")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self._api_key,
        }
        params = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.7,
            "n": 1,
        }

        client = httpx.Client()
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=params,
            timeout=60,
        )
        # 检查响应状态码
        if response.status_code == 200:
            # 处理成功的响应
            return response.json()
        else:
            # 处理错误的响应
            logger.error(f"error:请求失败，状态码：{response.status_code}")
            raise Exception(f"SQL模型调用失败，状态码：{response.status_code}")

    @override
    async def chat_completion_stream(
            self,
            messages: list[ChatMessage],
            model_name="gpt-4-1106-preview",
            session_id=f"ChatGPT-{uuid.uuid4()}"
    ) -> AsyncGenerator[str, None]:

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self._api_key,
        }
        params = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.7,
            "n": 1,
            "stream": True,
        }
        async with httpx.AsyncClient() as client:
            async with client.stream(
                    "POST",
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=params,
                    timeout=60,
            ) as response:
                async for line in response.aiter_lines():
                    if line.strip() == "":
                        continue
                    if line.startswith("data:"):
                        logger.info(f"返回json数据:{line}")
                        yield line
