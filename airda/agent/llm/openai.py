import datetime
import logging
import uuid
from typing import AsyncGenerator

import httpx
from overrides import overrides

from airda.framework.agent.module.llm_manager.llm.llm import LLM, ChatMessage

logger = logging.getLogger()


class OpenAILLM(LLM):
    api_key: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs["key"]

    @overrides
    def chat_completion(
        self,
        messages: list[ChatMessage],
        model_name="gpt-3.5-turbo",
        session_id=f"ChatGPT-{uuid.uuid4()}",
    ) -> str:
        logger.debug(f"开始请求OpenAI: {datetime.datetime.now()}")
        logger.debug(f"prompt: {messages[-1].get('content')}")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key,
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

    @overrides
    async def chat_completion_stream(
        self,
        messages: list[ChatMessage],
        model_name="gpt-3.5-turbo",
        session_id=f"ChatGPT-{uuid.uuid4()}",
    ) -> AsyncGenerator[str, None]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key,
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
                        logger.debug(f"返回json数据:{line}")
                        yield line
