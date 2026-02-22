"""Ollama LLM adapter implementation."""

import os

import httpx
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import ConfigDict

from ...config import settings


class CustomOllamaChat(BaseChatModel):
    """Custom ChatOllama implementation that supports API key authentication."""

    model_config = ConfigDict(extra="ignore")

    model: str = "gpt-oss:20b"
    temperature: float = 0.7
    base_url: str = "https://ollama.com"

    @property
    def _llm_type(self) -> str:
        return "custom_ollama"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager=None,
        **kwargs,
    ) -> ChatResult:
        is_remote = "localhost" not in self.base_url and "127.0.0.1" not in self.base_url
        headers = {}

        if is_remote:
            api_key = (
                settings.ollama_api_key
                or os.getenv("OLLAMA_API_KEY")
                or os.getenv("OLLAMA_AUTH_TOKEN")
            )
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

        prompt = messages[-1].content

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "temperature": self.temperature,
                },
                headers=headers,
            )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        content = result["message"]["content"]

        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])
