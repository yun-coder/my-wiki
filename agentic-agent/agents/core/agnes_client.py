"""Agnes AI API 客户端 — OpenAI 兼容接口。"""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path

from openai import OpenAI


class AgnesClient:
    """Agnes AI API 客户端，完全兼容 OpenAI 接口格式。"""

    def __init__(self, api_key: str, base_url: str, model: str = "agnes-2.0-flash"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
    ) -> Dict[str, Any]:
        """发送聊天完成请求。"""
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            params["tools"] = tools
        if tool_choice:
            params["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**params)
        return {
            "content": response.choices[0].message.content,
            "tool_calls": response.choices[0].message.tool_calls,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }

    def is_mock(self) -> bool:
        """检查是否处于 mock 模式（未配置 API Key）。"""
        return self.api_key == "your_api_key_here" or not self.api_key

    def mock_completion(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock 模式下的降级实现，用于开发测试。"""
        last_msg = messages[-1]["content"] if messages else ""
        return {
            "content": f"[MOCK MODE] 收到消息: {last_msg[:100]}...\n\n请先在 .env 中配置 AGNES_API_KEY 以启用真实模型。",
            "tool_calls": None,
            "finish_reason": "stop",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    def complete(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """统一的完成接口，自动切换 mock 模式。"""
        if self.is_mock():
            return self.mock_completion(messages)
        return self.chat_completion(messages, **kwargs)


def get_client() -> AgnesClient:
    """从配置获取 API 客户端实例。"""
    from agents.core.config import config

    return AgnesClient(
        api_key=config.agnes_api_key,
        base_url=config.agnes_base_url,
        model=config.agnes_model,
    )
